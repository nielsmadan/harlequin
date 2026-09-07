default:
    @just --list

# Show the latest version tag.
current-version:
    @git tag --list 'v*' --sort=-v:refname | head -1

[positional-arguments]
release *args:
    python3 scripts/release.py "$@"
