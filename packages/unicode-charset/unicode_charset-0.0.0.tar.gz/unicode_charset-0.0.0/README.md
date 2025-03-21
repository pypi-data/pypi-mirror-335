# unicode-charset

---

`unicode-charset` is a package that uses generators to return all characters of a given charset.

The main purpose is to efficently get random characters of specific encodings for testing purposes.

## Install

```cmd
pip install unicode-charset
```

## Usage

```python
from charset import charset

# print the first 10 charset of ansi charset
for c in charset("ansi", n=10, random=False):
    print(c, c.name)
```

```cmd
  SPACE
! EXCLAMATION MARK
" QUOTATION MARK
# NUMBER SIGN
$ DOLLAR SIGN
% PERCENT SIGN
& AMPERSAND
' APOSTROPHE
( LEFT PARENTHESIS
) RIGHT PARENTHESIS
```
