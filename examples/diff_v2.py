import re
from typing import Any

FLAGS = re.VERBOSE | re.MULTILINE | re.DOTALL
NaN = float('nan')
PosInf = float('inf')
NegInf = float('-inf')

DEFAULT_ENCODING = 'utf-8'


class JSONDecodeError(ValueError):
    """Subclass of ValueError with additional diagnostic properties.

    Attributes:
        msg: The unformatted error message
        doc: The JSON document being parsed
        pos: The start index where parsing failed
        lineno: The line corresponding to pos
        colno: The column corresponding to pos
    """

    def __init__(self, msg: str, doc: str, pos: int) -> None:
        lineno = doc.count('\n', 0, pos) + 1
        colno = pos - doc.rfind('\n', 0, pos)
        errmsg = f'{msg}: line {lineno} column {colno} (char {pos})'
        ValueError.__init__(self, errmsg)
        self.msg = msg
        self.doc = doc
        self.pos = pos
        self.lineno = lineno
        self.colno = colno

    def __reduce__(self):
        return self.__class__, (self.msg, self.doc, self.pos)

    def __str__(self):
        return f'JSONDecodeError at line {self.lineno}, col {self.colno}: {self.msg}'


_CONSTANTS = {
    '-Infinity': NegInf,
    'Infinity': PosInf,
    'NaN': NaN,
}

HEXDIGITS = re.compile(r'[0-9A-Fa-f]{4}', FLAGS)
STRINGCHUNK = re.compile(r'(.*?)(["\\\x00-\x1f])', FLAGS)

BACKSLASH = {
    '"': '"', '\\': '\\', '/': '/',
    'b': '\b', 'f': '\f', 'n': '\n', 'r': '\r', 't': '\t',
}


def scanstring(source: str, end: int, strict: bool = True) -> tuple[str, int]:
    """Scan a JSON string starting at the given index.

    Returns a tuple of the decoded string and the index past
    the closing quote character.
    """
    chunks: list[str] = []
    begin = end - 1

    while True:
        chunk = STRINGCHUNK.match(source, end)
        if chunk is None:
            raise JSONDecodeError("Unterminated string", source, begin)

        content, terminator = chunk.groups()
        end = chunk.end()

        if content:
            chunks.append(content)

        if terminator == '"':
            break
        elif terminator != '\\':
            if strict:
                msg = "Invalid control character at"
                raise JSONDecodeError(msg, source, end - 1)
            else:
                chunks.append(terminator)
                continue

        esc = source[end]
        end += 1

        if esc in BACKSLASH:
            chunks.append(BACKSLASH[esc])
        elif esc == 'u':
            hex_str = source[end:end + 4]
            uni = int(hex_str, 16)
            chunks.append(chr(uni))
            end += 4

    return ''.join(chunks), end
