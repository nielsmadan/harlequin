import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

SEMVER_PARTS = 3
TWO_PART_VERSION = 2


class ReleaseError(Exception):
    pass


def run(root, *args, capture=True):
    result = subprocess.run(args, cwd=root, text=True, capture_output=capture, check=False)
    if result.returncode:
        detail = (result.stderr or result.stdout or "").strip() if capture else ""
        raise ReleaseError(f"{' '.join(args)} failed ({result.returncode}). {detail}")
    return result.stdout.strip() if capture else ""


def version_tuple(value, components):
    value = value.removeprefix("v")
    if not re.fullmatch(r"(0|[1-9][0-9]*)(\.(0|[1-9][0-9]*)){" + str(components - 1) + "}", value):
        raise ReleaseError(f"Expected a {components}-part version, got {value!r}.")
    return tuple(int(part) for part in value.split("."))


def bumped(base, kind, components):
    parts = list(base)
    if kind == "patch" and components == TWO_PART_VERSION:
        raise ReleaseError("This project uses MAJOR.MINOR; choose minor or an exact version.")
    index = {"major": 0, "minor": 1, "patch": 2}[kind]
    parts[index] += 1
    parts[index + 1 :] = [0] * (components - index - 1)
    return ".".join(map(str, parts))


def suggested(base, messages, components):
    counts = {"features": 0, "fixes": 0, "breaking": 0}
    for message in messages:
        header = message.splitlines()[0]
        match = re.match(r"(\w+)(?:\([^\n]*\))?(!)?:", header)
        if not match:
            continue
        if match[2] or re.search(r"^BREAKING[ -]CHANGE:", message, re.MULTILINE):
            counts["breaking"] += 1
        if match[1] == "feat":
            counts["features"] += 1
        elif match[1] in {"fix", "perf"}:
            counts["fixes"] += 1
    if counts["breaking"]:
        kind = "minor" if components == SEMVER_PARTS and base[0] == 0 else "major"
    elif counts["features"] or (components == TWO_PART_VERSION and counts["fixes"]):
        kind = "minor"
    elif counts["fixes"]:
        kind = "patch"
    else:
        return None, counts
    return bumped(base, kind, components), counts


def remote_refs(root):
    result = run(root, "git", "ls-remote", "--heads", "--tags", "origin")
    return dict(line.split()[::-1] for line in result.splitlines())


def clean(root):
    status = run(root, "git", "status", "--porcelain", "--untracked-files=all")
    if status:
        raise ReleaseError("The checkout must be clean before releasing:\n" + status)


def inspect(root, config):
    clean(root)
    branch = run(root, "git", "symbolic-ref", "--short", "HEAD")
    if branch != config["branch"]:
        raise ReleaseError(f"Release from {config['branch']}, not {branch}.")
    if run(root, "git", "rev-parse", "--is-shallow-repository") == "true":
        raise ReleaseError("Release calculation requires complete Git history and tags.")
    origin = run(root, "git", "remote", "get-url", "--all", "origin")
    if "\n" in origin or origin != run(
        root, "git", "remote", "get-url", "--push", "--all", "origin"
    ):
        raise ReleaseError("origin must have one matching fetch and push destination.")
    if config.get("workflow"):
        match = re.search(r"github\.com[:/]([^/]+/[^/]+?)(?:\.git)?$", origin)
        if not match or match[1] != config["repository"]:
            raise ReleaseError("origin does not match the configured GitHub release repository.")
    refs = remote_refs(root)
    head = run(root, "git", "rev-parse", "HEAD")
    remote_head = refs.get("refs/heads/" + branch)
    if not remote_head:
        raise ReleaseError(f"origin/{branch} does not exist.")
    try:
        run(root, "git", "merge-base", "--is-ancestor", remote_head, head)
    except ReleaseError as error:
        raise ReleaseError(
            f"Update this checkout to include origin/{branch} before releasing."
        ) from error
    components = config["components"]
    pattern = r"v(?:0|[1-9][0-9]*)(?:\.(?:0|[1-9][0-9]*)){" + str(components - 1) + "}"
    tags = [
        tag
        for tag in run(root, "git", "tag", "--list", "v*").splitlines()
        if re.fullmatch(pattern, tag)
    ]
    published = [ref[10:] for ref in refs if re.fullmatch("refs/tags/" + pattern, ref)]
    latest = max(tags, key=lambda tag: version_tuple(tag, components), default=None)
    remote_latest = max(published, key=lambda tag: version_tuple(tag, components), default=None)
    if latest != remote_latest:
        raise ReleaseError("Local and origin release tags differ; reconcile them before releasing.")
    if latest:
        target = run(root, "git", "rev-parse", latest + "^{commit}")
        if target != refs.get("refs/tags/" + latest + "^{}", refs["refs/tags/" + latest]):
            raise ReleaseError(f"Local {latest} does not match origin.")
        run(root, "git", "merge-base", "--is-ancestor", latest, head)
    revision_range = latest + "..HEAD" if latest else "HEAD"
    messages = run(root, "git", "log", "--format=%B%x00", revision_range).split("\0")
    messages = [message.strip() for message in messages if message.strip()]
    if not messages:
        raise ReleaseError("There are no commits to release.")
    ahead = run(root, "git", "rev-list", "--count", remote_head + "..HEAD")
    return {"head": head, "refs": refs, "latest": latest, "messages": messages, "ahead": ahead}


def select_version(value, state, config):
    components = config["components"]
    base = version_tuple(state["latest"] or config["initial_version"], components)
    candidate = bumped(base, value, components) if value in {"patch", "minor", "major"} else value
    parsed = version_tuple(candidate, components)
    if state["latest"] and parsed <= base:
        raise ReleaseError(f"The release must be newer than {state['latest']}.")
    candidate = ".".join(map(str, parsed))
    return candidate


def preview(config, state, version, counts):
    print(f"\n{config['name']} release", flush=True)
    print(f"Current:   {state['latest'] or '(first release)'}")
    print(f"Proposed:  {'v' + version if version else '(no automatic bump)'}")
    print(
        f"Changes:   {counts['features']} features, {counts['fixes']} fixes, {counts['breaking']} breaking"
    )
    print(
        f"Push:      origin/{config['branch']} ({state['ahead']} existing local commits) and release tag"
    )
    for stage in config["stages"]:
        print("Prepare:   " + ", ".join(stage["files"]))
    print("Publish:   " + config["publication"])


def confirm(config, state, version, counts):
    while True:
        preview(config, state, version, counts)
        answer = input(
            "Confirm [y], enter a version/patch/minor/major, or cancel [Enter]: "
        ).strip()
        if answer.lower() in {"", "n", "no", "q", "quit"}:
            return None
        if answer.lower() in {"y", "yes"}:
            if version:
                return version
            print("Choose an explicit version or bump first.")
            continue
        try:
            version = select_version(answer, state, config)
        except ReleaseError as error:
            print(error)


def changed_paths(root):
    paths = set()
    for arguments in [
        ["diff", "--name-only", "-z"],
        ["diff", "--cached", "--name-only", "-z"],
        ["ls-files", "--others", "--exclude-standard", "-z"],
    ]:
        paths.update(run(root, "git", *arguments).split("\0"))
    return paths - {""}


def prepare(root, config, version):
    for stage in config["stages"]:
        clean(root)
        values = {"version": version, "revision": run(root, "git", "rev-parse", "HEAD")}
        for command in stage["commands"]:
            run(root, *(argument.format(**values) for argument in command), capture=False)
        paths = changed_paths(root)
        unexpected = {
            path
            for path in paths
            if not any(
                path == allowed or path.startswith(allowed + "/") for allowed in stage["files"]
            )
        }
        if unexpected:
            raise ReleaseError(
                "Preparation changed unexpected files: " + ", ".join(sorted(unexpected))
            )
        if paths:
            run(root, "git", "add", "--", *sorted(paths), capture=False)
            run(
                root,
                "git",
                "commit",
                "--only",
                "-m",
                stage["message"].format(**values),
                "--",
                *sorted(paths),
                capture=False,
            )
        clean(root)


def publication(root, config, tag, revision):
    if not config.get("workflow"):
        print(f"Published {tag}. {config['publication']}")
        return
    deadline = time.monotonic() + 120
    while time.monotonic() < deadline:
        runs = json.loads(
            run(
                root,
                "gh",
                "run",
                "list",
                "--repo",
                config["repository"],
                "--workflow",
                config["workflow"],
                "--event",
                "push",
                "--commit",
                revision,
                "--json",
                "databaseId,headBranch,url",
                "--limit",
                "20",
            )
        )
        matches = [item for item in runs if item["headBranch"] == tag]
        if matches:
            workflow_run = matches[0]
            break
        time.sleep(3)
    else:
        raise ReleaseError(
            f"{tag} was pushed, but its release workflow has not appeared. Check GitHub Actions."
        )
    print("Publication: " + workflow_run["url"], flush=True)
    deadline = time.monotonic() + 7200
    while time.monotonic() < deadline:
        result = json.loads(
            run(
                root,
                "gh",
                "run",
                "view",
                str(workflow_run["databaseId"]),
                "--repo",
                config["repository"],
                "--json",
                "status,conclusion",
            )
        )
        if result["status"] == "completed":
            if result["conclusion"] != "success":
                raise ReleaseError(
                    f"Publication finished with {result['conclusion']}: {workflow_run['url']}"
                )
            published = json.loads(
                run(
                    root,
                    "gh",
                    "release",
                    "view",
                    tag,
                    "--repo",
                    config["repository"],
                    "--json",
                    "url,isDraft",
                )
            )
            expected_draft = config.get("draft", False)
            if published["isDraft"] != expected_draft:
                expected = "draft" if expected_draft else "published"
                raise ReleaseError(f"Expected a {expected} release: {published['url']}")
            label = "Draft release ready: " if expected_draft else "Released: "
            print(label + published["url"])
            return
        time.sleep(5)
    raise ReleaseError("Publication is still running: " + workflow_run["url"])


def proposal(root, config, state, override):
    components = config["components"]
    base = version_tuple(state["latest"] or config["initial_version"], components)
    version, counts = suggested(base, state["messages"], components)
    if not state["latest"]:
        version = config["initial_version"]
    if not override and config.get("suggest") and state["latest"]:
        candidate = run(root, *config["suggest"]).removeprefix("v")
        version = candidate if version_tuple(candidate, components) > base else None
    if override:
        version = select_version(override, state, config)
    return version, counts


def main():
    parser = argparse.ArgumentParser(description="Preview, confirm, and publish a release.")
    parser.add_argument("version", nargs="?", help="patch, minor, major, or an exact version")
    parser.add_argument(
        "--yes", action="store_true", help="confirm the proposed release without a prompt"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="inspect and preview; do not run checks or publish"
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    config = json.loads((root / "scripts/release.json").read_text())
    if not args.yes and not args.dry_run and not sys.stdin.isatty():
        raise ReleaseError(
            "Interactive confirmation needs a terminal; use --dry-run or explicit --yes."
        )
    for tool in config["tools"]:
        if not shutil.which(tool):
            raise ReleaseError(f"Required release tool is missing: {tool}")
    state = inspect(root, config)
    if config.get("workflow") and not args.dry_run:
        run(root, "gh", "repo", "view", config["repository"], "--json", "nameWithOwner")
    version, counts = proposal(root, config, state, args.version)
    if args.dry_run:
        preview(config, state, version, counts)
        for command in config["checks"]:
            print("Check:     " + " ".join(command))
        print("Dry run: checks and publication were not run.")
        return
    if args.yes and not version:
        raise ReleaseError("No automatic release is due. Supply an explicit version or bump.")
    for command in config["checks"]:
        print("Checking: " + " ".join(command), flush=True)
        run(root, *command, capture=False)
    clean(root)
    if run(root, "git", "rev-parse", "HEAD") != state["head"]:
        raise ReleaseError("HEAD changed while checking the release.")
    if args.yes:
        preview(config, state, version, counts)
    else:
        version = confirm(config, state, version, counts)
    if not version:
        print("Release cancelled.")
        return
    if inspect(root, config) != state:
        raise ReleaseError("The checkout or origin changed during review. Run release again.")
    prepare(root, config, version)
    tag = "v" + version
    run(root, "git", "tag", "-a", "-m", f"Release {tag}", tag, capture=False)
    run(
        root,
        "git",
        "push",
        "--atomic",
        "--no-follow-tags",
        "origin",
        "HEAD:refs/heads/" + config["branch"],
        "refs/tags/" + tag,
        capture=False,
    )
    publication(root, config, tag, run(root, "git", "rev-parse", "HEAD"))


if __name__ == "__main__":
    try:
        main()
    except (ReleaseError, OSError, EOFError, KeyboardInterrupt) as error:
        print(f"Release stopped: {error}", file=sys.stderr)
        sys.exit(1)
