# AGENTS.md

Vim colorscheme. The entire scheme is one file: `colors/harlequin.vim`. There is no build
step, no test suite, and no CI.

## Gotchas

- **`GALLERY.md` screenshots are stale the moment colors change.** They are rendered from
  the files in `examples/` and committed as PNGs under `screenshots/`. Editing highlight
  groups without regenerating them leaves the gallery lying about the scheme.
- **Releases are tags, not commits.** `just tag-release-minor` (or `-major`) creates an
  annotated `vMAJOR.MINOR` tag from the latest existing tag. It deliberately does not push —
  run `git push origin <tag>` yourself.
- **Two distribution channels.** Tagging covers git consumers; vim.org is a separate manual
  upload and does not happen automatically.
- **Don't write `hi` lines directly.** The palette is a set of `s:<name> = ['#RRGGBB', N]`
  pairs — GUI hex plus 256-color terminal index — consumed by the `s:Highlight()` helper.
  A new color needs *both* halves, or the scheme silently degrades in one of the two
  environments. Passing an empty string to the helper means "use the default" (fg / bg /
  none), which is not the same as passing the fg color.

## Commands

`just` lists everything. Only `current-version`, `tag-release-minor`, and
`tag-release-major` exist — all release plumbing.
