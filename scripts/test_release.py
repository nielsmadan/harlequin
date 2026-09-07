import importlib.util
import io
import json
import os
import pty
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).with_name("release.py")
SPEC = importlib.util.spec_from_file_location("release", SCRIPT)
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.root = self.directory / "checkout"
        self.remote = self.directory / "origin.git"
        self.root.mkdir()
        self.env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
        self.command("git", "init", "--bare", str(self.remote))
        self.command("git", "init", "-b", "main")
        self.git("config", "user.name", "Release test")
        self.git("config", "user.email", "release@example.invalid")
        self.git("remote", "add", "origin", str(self.remote))
        (self.root / "scripts").mkdir()
        shutil.copyfile(SCRIPT, self.root / "scripts/release.py")
        (self.root / "scripts/prepare.py").write_text(
            "from pathlib import Path\nimport sys\nPath('VERSION').write_text(sys.argv[1] + '\\n')\n"
        )
        self.config = {
            "name": "Fixture",
            "branch": "main",
            "components": 3,
            "initial_version": "0.1.0",
            "tools": ["git", "python3"],
            "checks": [],
            "publication": "Version tag for fixture consumers",
            "stages": [
                {
                    "files": ["VERSION"],
                    "message": "chore: release {version}",
                    "commands": [[sys.executable, "scripts/prepare.py", "{version}"]],
                }
            ],
        }
        self.save_config()
        (self.root / "VERSION").write_text("1.2.0\n")
        self.commit("chore: initial fixture")
        self.git("tag", "-a", "v1.2.0", "-m", "Fixture release")
        (self.root / "source.txt").write_text("fixed\n")
        self.commit("fix: correct behavior")
        self.git("push", "origin", "main", "--tags")
        self.initial_head = self.git("rev-parse", "HEAD")

    def command(self, *args, cwd=None):
        result = subprocess.run(
            args, cwd=cwd or self.root, env=self.env, text=True, capture_output=True, check=True
        )
        return result.stdout.strip()

    def git(self, *args):
        return self.command("git", *args)

    def commit(self, message):
        self.git("add", ".")
        self.git("commit", "-m", message)

    def save_config(self):
        (self.root / "scripts/release.json").write_text(json.dumps(self.config))

    def invoke(self, *args, answers=None):
        command = [sys.executable, "scripts/release.py", *args]
        if answers is None:
            return subprocess.run(
                command,
                cwd=self.root,
                env=self.env,
                text=True,
                input="",
                capture_output=True,
                check=False,
            )
        master, slave = pty.openpty()
        try:
            process = subprocess.Popen(
                command,
                cwd=self.root,
                env=self.env,
                stdin=slave,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            os.close(slave)
            slave = None
            os.write(master, answers.encode())
            stdout, stderr = process.communicate(timeout=30)
            return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
        finally:
            os.close(master)
            if slave is not None:
                os.close(slave)

    def assert_original_release(self):
        self.assertEqual(self.git("tag", "--list"), "v1.2.0")
        self.assertEqual(self.git("rev-parse", "HEAD"), self.initial_head)
        self.assertEqual((self.root / "VERSION").read_text(), "1.2.0\n")
        self.assertEqual(
            self.git("ls-remote", "origin", "refs/heads/main").split()[0], self.initial_head
        )

    def test_version_policy(self):
        cases = [
            ((1, 2, 0), ["fix: repair"], 3, "1.2.1"),
            ((1, 2, 0), ["feat: add"], 3, "1.3.0"),
            ((1, 2, 0), ["feat!: replace"], 3, "2.0.0"),
            ((0, 2, 0), ["fix: change\n\nBREAKING CHANGE: wire format"], 3, "0.3.0"),
            ((2, 3), ["fix: repair"], 2, "2.4"),
            ((2, 3), ["feat!: replace"], 2, "3.0"),
            ((1, 2, 0), ["chore: dependencies"], 3, None),
        ]
        for base, messages, components, expected in cases:
            with self.subTest(messages=messages, components=components):
                self.assertEqual(release.suggested(base, messages, components)[0], expected)

    def test_dry_run_preserves_checkout_and_origin(self):
        result = self.invoke("--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Proposed:  v1.2.1", result.stdout)
        self.assert_original_release()
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_noninteractive_execution_requires_explicit_confirmation(self):
        result = self.invoke()
        self.assertEqual(result.returncode, 1)
        self.assertIn("needs a terminal", result.stderr)
        self.assert_original_release()

    def test_cancel_preserves_checkout_and_origin(self):
        result = self.invoke(answers="\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Release cancelled", result.stdout)
        self.assert_original_release()
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_override_is_shown_and_confirmed_before_publishing(self):
        result = self.invoke(answers="minor\ny\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Proposed:  v1.2.1", result.stdout)
        self.assertIn("Proposed:  v1.3.0", result.stdout)
        self.assertEqual((self.root / "VERSION").read_text(), "1.3.0\n")
        self.assertEqual(self.git("show", "v1.3.0:VERSION"), "1.3.0")
        self.assertEqual(
            self.git("ls-remote", "origin", "refs/tags/v1.3.0^{}").split()[0],
            self.git("rev-parse", "HEAD"),
        )

    def test_explicit_version_with_yes_publishes_a_tagged_commit(self):
        result = self.invoke("1.4.2", "--yes")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git("show", "v1.4.2:VERSION"), "1.4.2")
        self.assertEqual(self.git("log", "-1", "--format=%s"), "chore: release 1.4.2")
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_invalid_or_old_versions_preserve_release(self):
        for version in ["1.2.0", "1.1.9", "v1.02.1", "1.3", "1.3.0;touch bad"]:
            with self.subTest(version=version):
                result = self.invoke(version, "--yes")
                self.assertEqual(result.returncode, 1)
                self.assert_original_release()

    def test_unrelated_staged_work_is_preserved(self):
        (self.root / "unrelated.txt").write_text("user work\n")
        self.git("add", "unrelated.txt")
        result = self.invoke("--yes")
        self.assertEqual(result.returncode, 1)
        self.assertIn("must be clean", result.stderr)
        self.assertEqual(self.git("diff", "--cached", "--name-only"), "unrelated.txt")
        self.assert_original_release()

    def test_failed_check_stops_before_preparation(self):
        self.config["checks"] = [[sys.executable, "-c", "raise SystemExit(7)"]]
        self.save_config()
        self.commit("chore: configure check")
        result = self.invoke("--yes")
        self.assertEqual(result.returncode, 1)
        self.assertIn("failed (7)", result.stderr)
        self.assertEqual((self.root / "VERSION").read_text(), "1.2.0\n")
        self.assertEqual(self.git("tag", "--list"), "v1.2.0")

    def test_unexpected_preparation_changes_stop_before_commit(self):
        self.config["stages"][0]["commands"].append(
            [
                sys.executable,
                "-c",
                "from pathlib import Path; Path('other.txt').write_text('unexpected')",
            ]
        )
        self.save_config()
        self.commit("chore: configure preparation")
        before = self.git("rev-parse", "HEAD")
        result = self.invoke("--yes")
        self.assertEqual(result.returncode, 1)
        self.assertIn("unexpected files: other.txt", result.stderr)
        self.assertEqual(self.git("rev-parse", "HEAD"), before)
        self.assertEqual(self.git("tag", "--list"), "v1.2.0")

    def test_failed_push_preserves_remote_branch_and_tag_set(self):
        hook = self.remote / "hooks/pre-receive"
        hook.write_text("#!/bin/sh\nexit 1\n")
        hook.chmod(0o755)
        result = self.invoke("--yes")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            self.git("ls-remote", "origin", "refs/heads/main").split()[0], self.initial_head
        )
        remote_tags = self.command("git", "--git-dir", str(self.remote), "tag", "--list")
        self.assertEqual(remote_tags, "v1.2.0")
        self.assertEqual(self.git("show", "v1.2.1:VERSION"), "1.2.1")

    def test_remote_advance_blocks_release(self):
        other = self.directory / "other"
        self.command("git", "clone", "-b", "main", str(self.remote), str(other))
        self.command("git", "config", "user.name", "Other author", cwd=other)
        self.command("git", "config", "user.email", "other@example.invalid", cwd=other)
        (other / "advance.txt").write_text("remote change\n")
        self.command("git", "add", ".", cwd=other)
        self.command("git", "commit", "-m", "fix: remote change", cwd=other)
        self.command("git", "push", "origin", "main", cwd=other)
        result = self.invoke("--yes")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(self.git("rev-parse", "HEAD"), self.initial_head)
        self.assertEqual(self.git("tag", "--list"), "v1.2.0")

    def test_two_part_policy_rejects_patch_override(self):
        with self.assertRaisesRegex(release.ReleaseError, "MAJOR.MINOR"):
            release.bumped((2, 3), "patch", 2)

    def test_first_release_uses_initial_version(self):
        self.git("tag", "-d", "v1.2.0")
        self.git("push", "origin", ":refs/tags/v1.2.0")
        result = self.invoke("--yes")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git("show", "v0.1.0:VERSION"), "0.1.0")
        self.assertEqual(
            self.git("ls-remote", "origin", "refs/tags/v0.1.0^{}").split()[0],
            self.git("rev-parse", "HEAD"),
        )

    def test_chores_require_an_explicit_version(self):
        self.git("tag", "-a", "v1.2.1", "-m", "Fixture release")
        (self.root / "source.txt").write_text("maintenance\n")
        self.commit("chore: maintain source")
        self.git("push", "origin", "main", "--tags")
        result = self.invoke("--yes")
        self.assertEqual(result.returncode, 1)
        self.assertIn("No automatic release is due", result.stderr)
        result = self.invoke("patch", "--yes")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git("show", "v1.2.2:VERSION"), "1.2.2")

    def test_two_part_tag_only_release_preserves_commit(self):
        self.config.update(components=2, initial_version="0.1", stages=[])
        self.save_config()
        self.commit("chore: configure two-part releases")
        self.git("tag", "-a", "v2.3", "-m", "Fixture release")
        (self.root / "source.txt").write_text("two-part fix\n")
        self.commit("fix: correct behavior")
        self.git("push", "origin", "main", "--tags")
        before = self.git("rev-parse", "HEAD")
        result = self.invoke("--yes")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git("rev-parse", "v2.4^{commit}"), before)
        self.assertEqual(self.git("rev-parse", "HEAD"), before)

    def test_second_stage_pins_the_prepared_version_commit(self):
        self.config["stages"].append(
            {
                "files": ["REVISION"],
                "message": "chore: pin installer",
                "commands": [
                    [
                        sys.executable,
                        "-c",
                        "from pathlib import Path; Path('REVISION').write_text('{revision}')",
                    ]
                ],
            }
        )
        self.save_config()
        self.commit("chore: configure installer pin")
        result = self.invoke("--yes")
        self.assertEqual(result.returncode, 0, result.stderr)
        revision = self.git("show", "v1.2.1:REVISION")
        self.assertEqual(self.git("show", revision + ":VERSION"), "1.2.1")
        self.assertEqual(self.git("rev-parse", "HEAD^"), revision)

    def test_check_that_edits_tracked_files_stops_before_preparation(self):
        self.config["checks"] = [
            [
                sys.executable,
                "-c",
                "from pathlib import Path; Path('source.txt').write_text('formatted')",
            ]
        ]
        self.save_config()
        self.commit("chore: configure formatting check")
        result = self.invoke("--yes")
        self.assertEqual(result.returncode, 1)
        self.assertIn("must be clean", result.stderr)
        self.assertEqual((self.root / "VERSION").read_text(), "1.2.0\n")
        self.assertEqual((self.root / "source.txt").read_text(), "formatted")

    def test_extra_push_destinations_are_rejected(self):
        self.git("config", "--add", "remote.origin.pushurl", str(self.remote))
        self.git("config", "--add", "remote.origin.pushurl", str(self.directory / "other.git"))
        result = self.invoke("--yes")
        self.assertEqual(result.returncode, 1)
        self.assertIn("one matching fetch and push destination", result.stderr)
        self.assert_original_release()

    def test_global_follow_tags_does_not_publish_unreviewed_tags(self):
        self.git("tag", "-a", "experiment", "-m", "Unreviewed local tag")
        self.git("config", "push.followTags", "true")
        result = self.invoke("--yes")
        self.assertEqual(result.returncode, 0, result.stderr)
        remote_tags = self.command("git", "--git-dir", str(self.remote), "tag", "--list")
        self.assertEqual(remote_tags.splitlines(), ["v1.2.0", "v1.2.1"])

    def test_publication_waits_for_matching_tag_and_reports_success(self):
        config = {"workflow": "release.yml", "repository": "owner/repo"}
        responses = [
            json.dumps(
                [
                    {"databaseId": 1, "headBranch": "other", "url": "other"},
                    {"databaseId": 2, "headBranch": "v1.2.1", "url": "workflow-url"},
                ]
            ),
            json.dumps({"status": "completed", "conclusion": "success"}),
            json.dumps({"url": "release-url", "isDraft": False}),
        ]
        with (
            patch.object(release, "run", side_effect=responses) as runner,
            patch("sys.stdout", new_callable=io.StringIO) as output,
        ):
            release.publication(self.root, config, "v1.2.1", "revision")
        self.assertIn("Released: release-url", output.getvalue())
        self.assertIn("2", runner.call_args_list[1].args)

    def test_draft_release_is_reported_without_publication(self):
        config = {"workflow": "release.yml", "repository": "owner/repo", "draft": True}
        responses = [
            json.dumps([{"databaseId": 2, "headBranch": "v1.2.1", "url": "workflow-url"}]),
            json.dumps({"status": "completed", "conclusion": "success"}),
            json.dumps({"url": "draft-url", "isDraft": True}),
        ]
        with (
            patch.object(release, "run", side_effect=responses) as runner,
            patch("sys.stdout", new_callable=io.StringIO) as output,
        ):
            release.publication(self.root, config, "v1.2.1", "revision")
        self.assertIn("Draft release ready: draft-url", output.getvalue())
        self.assertEqual(runner.call_args_list[-1].args[1:4], ("gh", "release", "view"))
        self.assertEqual(runner.call_count, 3)

    def test_release_state_must_match_the_configured_policy(self):
        for expected_draft in [True, False]:
            with self.subTest(expected_draft=expected_draft):
                config = {
                    "workflow": "release.yml",
                    "repository": "owner/repo",
                    "draft": expected_draft,
                }
                responses = [
                    json.dumps([{"databaseId": 2, "headBranch": "v1.2.1", "url": "workflow-url"}]),
                    json.dumps({"status": "completed", "conclusion": "success"}),
                    json.dumps({"url": "release-url", "isDraft": not expected_draft}),
                ]
                with (
                    patch.object(release, "run", side_effect=responses),
                    self.assertRaisesRegex(
                        release.ReleaseError, "Expected a .* release: release-url"
                    ),
                ):
                    release.publication(self.root, config, "v1.2.1", "revision")

    def test_publication_failure_is_an_error(self):
        config = {"workflow": "release.yml", "repository": "owner/repo"}
        responses = [
            json.dumps([{"databaseId": 2, "headBranch": "v1.2.1", "url": "workflow-url"}]),
            json.dumps({"status": "completed", "conclusion": "failure"}),
        ]
        with (
            patch.object(release, "run", side_effect=responses),
            self.assertRaisesRegex(release.ReleaseError, "failure: workflow-url"),
        ):
            release.publication(self.root, config, "v1.2.1", "revision")


if __name__ == "__main__":
    unittest.main()
