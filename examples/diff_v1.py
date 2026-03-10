import re
from typing import Any

FLAGS = re.VERBOSE | re.MULTILINE | re.DOTALL
NaN = float('nan')
PosInf = float('inf')
NegInf = float('-inf')


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
        errmsg = '%s: line %d column %d (char %d)' % (msg, lineno, colno, pos)
        ValueError.__init__(self, errmsg)
        self.msg = msg
        self.doc = doc
        self.pos = pos
        self.lineno = lineno
        self.colno = colno

    def __reduce__(self):
        return self.__class__, (self.msg, self.doc, self.pos)


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


def scanstring(string: str, end: int, strict: bool = True) -> tuple[str, int]:
    """Scan a JSON string starting at the given index."""
    chunks: list[str] = []
    begin = end - 1

    while True:
        chunk = STRINGCHUNK.match(string, end)
        if chunk is None:
            raise JSONDecodeError("Unterminated string", string, begin)

        content, terminator = chunk.groups()
        end = chunk.end()

        if content:
            chunks.append(content)

        if terminator == '"':
            break
        elif terminator != '\\':
            if strict:
                msg = "Invalid control character at"
                raise JSONDecodeError(msg, string, end - 1)
            else:
                chunks.append(terminator)
                continue

        esc = string[end]
        end += 1

        if esc in BACKSLASH:
            chunks.append(BACKSLASH[esc])
        elif esc == 'u':
            hex_str = string[end:end + 4]
            uni = int(hex_str, 16)
            chunks.append(chr(uni))
            end += 4

    return ''.join(chunks), end
