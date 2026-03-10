#!/bin/sh
# Opens each example file in MacVim with harlequin colorscheme
# at a consistent window size for taking screenshots.
#
# Usage: ./take_screenshots.sh [file]
#   No arguments: opens all example files one by one
#   With argument: opens just that file
#
# Take a screenshot of each window with Cmd+Shift+4, Space, click.
# Save to ../screenshots/ with the appropriate name.

LINES=45
COLS=120
DIFF_COLS=160
DIR="$(cd "$(dirname "$0")" && pwd)"

open_file() {
    echo "Opening: $1"
    mvim -c "colorscheme harlequin" -c "set lines=$LINES columns=$COLS" "$1"
    echo "  Take screenshot, then press Enter to continue..."
    read _
}

open_diff() {
    echo "Opening diff: $1 vs $2"
    mvim -d -c "set lines=$LINES columns=$DIFF_COLS" -c "colorscheme harlequin" "$1" "$2"
    echo "  Take screenshot, then press Enter to continue..."
    read _
}

# Single file mode
if [ -n "$1" ]; then
    open_file "$1"
    exit 0
fi

# Batch mode: all examples
for ext in c cpp rs go java kt swift py rb ts sh html css sql json yaml md; do
    open_file "$DIR/example.$ext"
done

# Diff mode
open_diff "$DIR/diff_v1.py" "$DIR/diff_v2.py"

echo "Done! Save screenshots to screenshots/ directory."
