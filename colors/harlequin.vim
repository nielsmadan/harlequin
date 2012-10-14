" Color scheme based on Molokai by Tomas Restrepo and badwolf by Steve Losh.
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
let s:greys = ['#BEBEBE', '#808080', '#696969', '#545454', '#343434', '#080808']

let s:cerise = '#FF0033'

let s:lime = '#AEEE00'

let s:gold = '#FFB829'

let s:brick = '#CB4154'

let s:lilac = '#AE81FF'

let s:frost = '#2C89C7' 

let s:sunny = '#FFFC7F'

let s:mordant = '#AE0C00'

let s:auburn = '#7C0A02'
let s:moss = '#004225'

let s:cursor = {'guifg': s:greys[5], 'guibg': s:white}

" group_name, guifg, guibg, gui, guisp, '' means use default
" defaults: guifg - fg, guibg - NONE, gui - none, guisp - fg
function! s:HI(group_name, colors_dict)
    let guifg = get(a:colors_dict, 'guifg', 'fg')
    let guibg = get(a:colors_dict, 'guibg', 'NONE')
    let gui = get(a:colors_dict, 'gui', 'none')
    let guisp = get(a:colors_dict, 'guisp', 'fg')

    exe 'hi ' . a:group_name . ' guifg=' . guifg . ' guibg=' . guibg . ' gui=' . gui . ' guisp=' . guisp
endfunction

" Function without defaults.
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

call s:HI('Type',            {'guifg': s:brick})
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
call s:HI('CommentEmail',    {'guifg': s:frost, 'gui': 'underline'})
call s:HI('CommentUrl',      {'guifg': s:frost, 'gui': 'underline'})
call s:HI('SpecialComment',  {'guifg': s:frost, 'gui': 'bold'})
call s:HI('Todo',            {'guifg': s:frost, 'gui': 'bold'})

call s:HI('String',          {'guifg': s:sunny}) 
call s:HI('SpecialKey',      {'guifg': s:lilac, 'gui': 'bold'})
call s:HI('Special',         {'guifg': s:lilac, 'gui': 'bold'})
call s:HI('SpecialChar',     {'guifg': s:lilac, 'gui': 'bold'})

call s:HI('Boolean',         {'guifg': s:lilac, 'gui': 'bold'})
call s:HI('Character',       {'guifg': s:lilac, 'gui': 'bold'})
call s:HI('Number',          {'guifg': s:lilac, 'gui': 'bold'})
call s:HI('Constant',        {'guifg': s:lilac, 'gui': 'bold'})
call s:HI('Float',           {'guifg': s:lilac, 'gui': 'bold'})

call s:HI('FoldColumn',      {'guifg': s:greys[1], 'guibg': s:black}) ", 'gui': 'bold'})
call s:HI('Folded',          {'guifg': s:greys[1], 'guibg': s:black}) ", 'gui': 'bold'})

call s:HI('MatchParen',      {'guifg': s:black, 'guibg': s:gold, 'gui': 'bold'})

call s:HI('LineNr',          {'guifg': s:greys[2]})
call s:HI('NonText',         {'guifg': s:greys[2]})
call s:HIx('CursorColumn',   {'guibg': s:greys[5]})
call s:HIx('CursorLine',     {'guibg': s:greys[5]})
call s:HI('SignColumn',      {'guibg': s:greys[5]})
call s:HIx('ColorColumn',    {'guibg': s:greys[5]})

call s:HI('Error',           {'guifg': s:mordant, 'guibg': s:greys[5], 'gui': 'bold'})
call s:HI('ErrorMsg',        {'guifg': s:mordant, 'gui': 'bold'})
call s:HI('WarningMsg',      {'guifg': s:mordant})

call s:HI('Cursor',          s:cursor)
call s:HI('vCursor',         s:cursor)
call s:HI('iCursor',         s:cursor)

call s:HI('StatusLine',      {'guifg': s:white, 'guibg': s:black, 'gui': 'bold'})
call s:HI('StatusLineNC',    {'guifg': s:greys[1], 'guibg': s:greys[5], 'gui': 'bold'})
call s:HI('VertSplit',       {'guifg': s:greys[1], 'guibg': s:greys[5], 'gui': 'bold'})

call s:HI('ModeMsg',         {'guifg': s:sunny, 'gui': 'bold'})

if has("spell")
    call s:HIx('SpellBad',    {'guisp': '#FF0000', 'gui': 'undercurl'})
    call s:HIx('SpellCap',    {'guisp': '#7070F0', 'gui': 'undercurl'})
    call s:HIx('SpellLocal',  {'guisp': '#70F0F0', 'gui': 'undercurl'})
    call s:HIx('SpellRare',   {'guisp': '#FFFFFF', 'gui': 'undercurl'})
endif

call s:HIx('VisualNOS',      {'guibg': s:greys[4]})
call s:HIx('Visual',         {'guibg': s:greys[4]})
call s:HI('Search',          {'guifg': s:black, 'guibg': s:gold})
call s:HI('IncSearch',       {'guifg': s:black, 'guibg': s:sunny})

call s:HI('Pmenu',           {'guifg': s:black, 'guibg': s:gold})
call s:HI('PmenuSel',        {'guifg': s:gold, 'guibg': s:black, 'gui': 'bold'})
call s:HI('Pmenu',           {'guibg': s:greys[5]})
call s:HI('Pmenu',           {'guifg': '#66D9EF'})

call s:HIx('DiffDelete',     {'guifg': s:auburn, 'guibg': s:auburn})
call s:HIx('DiffText',       {'guibg': s:greys[3]})
call s:HIx('DiffChange',     {'guibg': s:greys[4]})
call s:HIx('DiffAdd',        {'guibg': s:moss})

call s:HIx('Underlined',     {'gui': 'underline'})

call s:HI('Directory',       {'guifg': s:lime})
call s:HI('Question',        {'guifg': s:lime})
call s:HI('MoreMsg',         {'guifg': s:lime})
  
call s:HI('WildMenu',        {'guifg': s:black, 'guibg': s:lilac, 'gui': 'bold'})

call s:HI('Title',           {'gui': 'underline'})

call s:HIx('Tag',            {'gui': 'bold'})

"*** PYTHON ***
call s:HI('pythonDecorator',     {'guifg': s:cerise})
call s:HI('pythonException',     {'guifg': s:lime, 'gui': 'bold'})
call s:HI('pythonExceptions',    {'guifg': s:lime})

"*** RUBY ***
call s:HI('rubyModule',            {'guifg': s:lime})
call s:HI('rubyModuleNameTag',     {'guifg': s:text})
call s:HI('rubyPseudoVariable',    {'guifg': s:text})
call s:HI('rubyClass',             {'guifg': s:cerise})
call s:HI('rubyClassNameTag',      {'guifg': s:gold})
call s:HI('rubyDefine',            {'guifg': s:cerise})
call s:HI('rubyConstant',          {'guifg': s:text})
call s:HI('rubyStringDelimiter',   {'guifg': s:sunny})
call s:HI('rubyInterpolation',     {'guifg': s:lilac})
call s:HI('rubyInterpolationDelimiter',     {'guifg': s:lilac})

"*** JAVASCRIPT ***
call s:HI('javaScriptNull',        {'guifg': s:lilac, 'gui': 'bold'})
call s:HI('javaScriptNumber',      {'guifg': s:lilac, 'gui': 'bold'})
call s:HI('javaScriptFunction',    {'guifg': s:cerise})
call s:HI('javaScriptOperator',    {'guifg': s:cerise, 'gui': 'bold'})
call s:HI('javaScriptBraces',      {'guifg': s:text})
call s:HI('javaScriptIdentifier',  {'guifg': s:brick})
call s:HI('javaScriptMember',      {'guifg': s:gold})
call s:HI('javaScriptType',        {'guifg': s:gold})

"*** CLOJURE ***
call s:HI('clojureDefine',         {'guifg': s:cerise})
call s:HI('clojureSpecial',        {'guifg': s:cerise})
call s:HI('clojureCond',           {'guifg': s:cerise})
call s:HI('clojureParen0',         {'guifg': s:text})
call s:HI('clojureMacro',          {'guifg': s:lime, 'gui': 'bold'})
call s:HI('clojureDispatch',       {'guifg': s:lilac, 'gui': 'bold'})

"*** SCALA ***
call s:HI('scalaClassName',        {'guifg': s:gold})
call s:HI('scalaConstructor',      {'guifg': s:text})

"*** VIMSCRIPT ***
call s:HI('vimCommentTitle',       {'guifg': s:frost, 'gui': 'bold'})
call s:HI('vimParenSep',           {'guifg': s:text})
call s:HI('vimSep',                {'guifg': s:text})
call s:HI('vimOper',               {'guifg': s:text})

"*** XML ***
call s:HI('xmlProcessingDelim',       {'guifg': s:brick})
call s:HI('xmlNamespace',             {'guifg': s:gold})
call s:HI('xmlTag',                   {'guifg': s:gold})
call s:HI('xmlTagName',               {'guifg': s:gold})
call s:HI('xmlEndTag',                {'guifg': s:gold})
call s:HI('xmlAttrib',                {'guifg': s:brick})
call s:HI('xmlAttribPunct',           {'guifg': s:brick})
call s:HI('xmlEntity',                {'guifg': s:lilac, 'gui': 'bold'})
call s:HI('xmlEntityPunct',           {'guifg': s:lilac})

"*** HTML ***
call s:HI('htmlTagName',              {'guifg': s:gold})
call s:HI('htmlTag',                  {'guifg': s:gold})
call s:HI('htmlTagN',                 {'guifg': s:gold})
call s:HI('htmlEvent',                {'guifg': s:brick})
call s:HI('htmlEventDQ',              {'guifg': s:lime})
call s:HI('htmlH1',                   {'gui': 'bold'})
call s:HI('htmlH2',                   {'gui': 'bold'})
call s:HI('htmlH3',                   {'gui': 'italic'})
call s:HI('htmlH4',                   {'gui': 'italic'})
call s:HI('htmlScriptTag',            {'guifg': s:lime})

"*** HTML/JAVASCRIPT ***
call s:HI('javaScript',               {'guifg': s:text})

"*** CSS ***
call s:HI('cssSelectorOp',            {'guifg': s:text})
call s:HI('cssSelectorOp2',           {'guifg': s:text})
call s:HI('cssBraces',                {'guifg': s:text})
call s:HI('cssPseudoClass',           {'guifg': s:lime})
call s:HI('cssValueNumber',           {'guifg': s:lilac})
call s:HI('cssValueLength',           {'guifg': s:lilac})
call s:HI('cssColor',                 {'guifg': s:lilac})
call s:HI('cssImportant',             {'guifg': s:lime, 'gui': 'bold'})
call s:HI('cssCommonAttr',            {'guifg': s:lilac, 'gui': 'bold'})
call s:HI('cssRenderAttr',            {'guifg': s:lilac, 'gui': 'bold'})
call s:HI('cssBoxAttr',               {'guifg': s:lilac, 'gui': 'bold'})
call s:HI('cssUIAttr',                {'guifg': s:lilac, 'gui': 'bold'})
call s:HI('cssTextAttr',              {'guifg': s:lilac, 'gui': 'bold'})
call s:HI('cssTableAttr',             {'guifg': s:lilac, 'gui': 'bold'})
call s:HI('cssColorAttr',             {'guifg': s:lilac, 'gui': 'bold'})

"*** minibufexpl ***
call s:HI('MBENormal',                 {'guifg': s:greys[1]})
call s:HI('MBEVisibleNormal',          {'guifg': s:white, 'gui': 'bold'})
call s:HI('MBEVisibleActive',          {'guifg': s:frost, 'gui': 'bold'})
call s:HI('MBEChanged',                {'guifg': s:greys[1], 'gui': 'italic'})
call s:HI('MBEVisibleChanged',         {'guifg': s:white, 'gui': 'bold,italic'})
call s:HI('MBEVisibleChangedActive',   {'guifg': s:frost, 'gui': 'bold,italic'})

"*** vim-easymotion ***
call s:HI('EasyMotionTarget',          {'guifg': s:cerise, 'gui': 'bold'})
call s:HI('EasyMotionShade',           {'guifg': s:greys[2]})

"*** CtrlP ***
call s:HI('CtrlPNoEntries',            {'guifg': s:mordant})
call s:HI('CtrlPPrtBase',              {'gui': 'bold'})
