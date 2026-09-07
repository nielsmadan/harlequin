# AGENTS.md

Vim colorscheme. The entire scheme is one file: `colors/harlequin.vim`. There is no build
step or CI for the colorscheme. Release tooling has Python standard-library tests.

## Gotchas

- **`GALLERY.md` screenshots are stale the moment colors change.** They are rendered from
  the files in `examples/` and committed as PNGs under `screenshots/`. Editing highlight
  groups without regenerating them leaves the gallery lying about the scheme.
- **Release from a clean, current `master`.** `just release` proposes a `vMAJOR.MINOR` version,
  runs the release tests, and asks for confirmation or an override. Confirmation atomically
  pushes `master` and the annotated tag. There is no version-file preparation commit.
- **Two distribution channels.** Tagging covers git consumers; vim.org is a separate manual
  upload and does not happen automatically.
- **Don't write `hi` lines directly.** The palette is a set of `s:<name> = ['#RRGGBB', N]`
  pairs — GUI hex plus 256-color terminal index — consumed by the `s:Highlight()` helper.
  A new color needs *both* halves, or the scheme silently degrades in one of the two
  environments. Passing an empty string to the helper means "use the default" (fg / bg /
  none), which is not the same as passing the fg color.

## Commands

`just` lists `current-version` and `release`. Use `just release --dry-run` to preview, or
`just release major` / `just release 3.0` to override. `patch` is invalid for two-part versions.
`--yes` explicitly confirms noninteractive use. See the README for release behavior.
