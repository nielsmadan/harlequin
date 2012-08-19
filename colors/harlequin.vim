" Color scheme based on Monokai by Tomas Restrepo and badwolf by Steve Losh.
"
" Author: Niels Madan
" URL: github.com/nielsmadan/harlequin

hi clear

set background=dark

if exists("syntax_on")
    syntax reset
endif

let colors_name = "harlequin"

let s:text = '#F8F8F2'
let s:text_bg = '#1C1B1A'

let s:white = '#FFFFFF'
let s:black = '#000000'
let s:greys = ['#BEBEBE', '#808080', '#696969', '#343434', '#080808']

let s:cerise = '#FF2C4B'

let s:lime = '#AEEE00'

let s:gold = '#FFB829'

let s:lilac = '#AE81FF'

let s:frost = '#7BC7E8' 

let s:straw = '#F4CF86'

let s:mordant = '#AE0C00'

let s:midnight = {'guifg': '#465457', 'guibg': '#000000'}

let s:cursor = {'guifg': s:greys[4], 'guibg': s:white}

" group_name, guifg, guibg, gui, guisp, '' means use default
" defaults: guifg - fg, guibg - NONE, gui - none, guisp - fg
function! s:HI(group_name, colors_dict)
    let guifg = get(a:colors_dict, 'guifg', 'fg')
    let guibg = get(a:colors_dict, 'guibg', 'NONE')
    let gui = get(a:colors_dict, 'gui', 'none')
    let guisp = get(a:colors_dict, 'guisp', 'fg')

    exe 'hi ' . a:group_name . ' guifg=' . guifg . ' guibg=' . guibg . ' gui=' . gui . ' guisp=' . guisp
endfunction

function! s:HIx(group_name, colors_dict)
    let hi_str = 'hi ' . a:group_name . ' '

    for [key, val] in items(a:colors_dict)
        let hi_str = hi_str . key . '=' . val . ' '
    endfor

    exe hi_str
endfunction

call s:HI('Normal',          {'guifg': s:text, 'guibg': s:text_bg})

call s:HI('Statement',       {'guifg': s:cerise, 'gui': 'bold'})
call s:HI('Keyword',         {'guifg': s:cerise, 'gui': 'bold'})
call s:HI('Conditional',     {'guifg': s:cerise, 'gui': 'bold'})
call s:HI('Operator',        {'guifg': s:cerise})
call s:HI('Label',           {'guifg': s:cerise})
call s:HI('Repeat',          {'guifg': s:cerise, 'gui': 'bold'})

call s:HI('Type',            {'guifg': s:cerise, 'gui': 'bold'})
call s:HI('StorageClass',    {'guifg': s:cerise})
call s:HI('Structure',       {'guifg': s:cerise})
call s:HI('TypeDef',         {'guifg': s:cerise, 'gui': 'bold'})

call s:HI('Exception',       {'guifg': s:lime, 'gui': 'bold'})
call s:HI('Include',         {'guifg': s:lime, 'gui': 'bold'})

call s:HI('PreProc',         {'guifg': s:lime})
call s:HI('Macro',           {'guifg': s:lime})
call s:HI('Define',          {'guifg': s:lime})
call s:HI('Delimiter',       {'guifg': s:lime})
call s:HI('Ignore',          {'guifg': s:lime})
call s:HI('PreCondit',       {'guifg': s:lime, 'gui': 'bold'})
call s:HI('Debug',           {'guifg': s:lime, 'gui': 'bold'})

call s:HI('Function',        {'guifg': s:gold})
call s:HI('Identifier',      {'guifg': s:gold})

call s:HI('Comment',         {'guifg': s:frost})
call s:HI('SpecialComment',  {'guifg': s:frost, 'gui': 'bold'})
call s:HI('Todo',            {'guifg': s:frost, 'gui': 'bold'})

call s:HI('String',          {'guifg': s:straw}) 

call s:HI('Boolean',         {'guifg': s:lilac, 'gui': 'bold'})
call s:HI('Character',       {'guifg': s:lilac, 'gui': 'bold'})
call s:HI('Number',          {'guifg': s:lilac, 'gui': 'bold'})
call s:HI('Constant',        {'guifg': s:lilac, 'gui': 'bold'})
call s:HI('Float',           {'guifg': s:lilac, 'gui': 'bold'})

call s:HI('FoldColumn',      s:midnight) 
call s:HI('Folded',          s:midnight)

call s:HI('MatchParen',      {'guifg': s:black, 'guibg': s:gold, 'gui': 'bold'})

call s:HI('LineNr',          {'guifg': s:greys[2]})

call s:HI('Cursor',          s:cursor)
call s:HI('vCursor',         s:cursor)
call s:HI('iCursor',         s:cursor)

" StatusLine is the status line of the currently active split, StatusLineNC of the others.
call s:HI('StatusLine',      {'guifg': s:white, 'guibg': s:black, 'gui': 'bold'})
call s:HI('StatusLineNC',    {'guifg': s:greys[1], 'guibg': s:greys[4], 'gui': 'bold'})
call s:HI('VertSplit',       {'guifg': s:greys[1], 'guibg': s:greys[4], 'gui': 'bold'})

call s:HI('ModeMsg',         {'guifg': s:straw, 'gui': 'bold'})

if has("spell")
    call s:HI('SpellBad',    {'guisp': '#FF0000', 'gui': 'undercurl'})
    call s:HI('SpellCap',    {'guisp': '#7070F0', 'gui': 'undercurl'})
    call s:HI('SpellLocal',  {'guisp': '#70F0F0', 'gui': 'undercurl'})
    call s:HI('SpellRare',   {'guisp': '#FFFFFF', 'gui': 'undercurl'})
endif

call s:HIx('VisualNOS',      {'guibg': s:greys[3]})
call s:HIx('Visual',         {'guibg': s:greys[3]})
call s:HI('Search',          {'guifg': s:black, 'guibg': s:gold})
call s:HI('IncSearch',       {'guifg': s:black, 'guibg': s:gold})

call s:HI('Pmenu',          {'guifg': s:black, 'guibg': s:gold})
call s:HI('PmenuSel',       {'guifg': s:gold, 'guibg': s:black, 'gui': 'bold'})
call s:HI('Pmenu',          {'guibg': s:greys[4]})
call s:HI('Pmenu',          {'guifg': '#66D9EF'})

call s:HI('DiffDelete',      {'guifg': s:black, 'guibg': s:black})
call s:HI('DiffText',        {'guifg': s:white, 'guibg': '#13354A', 'gui': 'bold'})
call s:HI('DiffChange',      {'guibg': '#13354A'})
call s:HI('DiffAdd',         {'guibg': '#13354A'})

call s:HI('Error',           {'guifg': s:mordant, 'guibg': s:black})
call s:HI('ErrorMsg',        {'guifg': s:mordant, 'guibg': s:black, 'gui': 'bold'})
call s:HI('WarningMsg',      {'guifg': s:mordant, 'guibg': s:black})

call s:HI('Underlined',      {'gui': 'underline'})

call s:HI('Directory',       {'guifg': s:lilac})

call s:HI('Title',           {'gui': 'underline'})

call s:HI('Tag',             {'gui': 'bold'})

" Look into: WildMenu, CursorLine, CursorColumn, NonText, Question, SignColumn, MoreMsg
"            SignColumn, SpecialChar, Special, SpecialKey.

"*** PYTHON ***
call s:HI('pythonException',     {'guifg': s:lime, 'gui': 'bold'})
call s:HI('pythonExceptions',    {'guifg': s:lime})
