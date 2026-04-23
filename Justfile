default:
    @just --list

# Show the latest version tag.
current-version:
    @git tag --list 'v*' --sort=-v:refname | head -1

# Create an annotated tag for the next minor release (vMAJOR.MINOR+1).
tag-release-minor:
    #!/usr/bin/env bash
    set -euo pipefail
    latest=$(git tag --list 'v*' --sort=-v:refname | head -1)
    if [[ -z "$latest" ]]; then
        next="v0.1"
    else
        major=$(echo "$latest" | sed -E 's/^v([0-9]+)\.[0-9]+$/\1/')
        minor=$(echo "$latest" | sed -E 's/^v[0-9]+\.([0-9]+)$/\1/')
        next="v${major}.$((minor + 1))"
    fi
    echo "Tagging ${next} (previous: ${latest:-none})"
    git tag -a "$next" -m "Release $next"
    echo "Push with: git push origin $next"

# Create an annotated tag for the next major release (vMAJOR+1.0).
tag-release-major:
    #!/usr/bin/env bash
    set -euo pipefail
    latest=$(git tag --list 'v*' --sort=-v:refname | head -1)
    if [[ -z "$latest" ]]; then
        next="v1.0"
    else
        major=$(echo "$latest" | sed -E 's/^v([0-9]+)\.[0-9]+$/\1/')
        next="v$((major + 1)).0"
    fi
    echo "Tagging ${next} (previous: ${latest:-none})"
    git tag -a "$next" -m "Release $next"
    echo "Push with: git push origin $next"
