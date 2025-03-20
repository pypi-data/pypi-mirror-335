# TxTWrap🔡
A tool for wrapping a text.🔨

## All constants, functions, and classes❕
- `LOREM_IPSUM_WORDS`
- `LOREM_IPSUM_SENTENCES`
- `LOREM_IPSUM_PARAGRAPHS`
- `TextWrapper` (New)
- `mono` (from TextWrapper)
- `word` (from TextWrapper)
- `wrap` (from TextWrapper)
- `align` (from TextWrapper)
- `fillstr` (from TextWrapper)
- `printwrap` (from fillstr)
- `indent` (from TextWrapper)
- `dedent` (from TextWrapper)
- `shorten` (from TextWrapper)

## Documents📄

### Wrapper📦
```py
class TextWrapper:

    def __init__(

        self,
        width: Union[int, float] = 70,
        start: int = 0,
        linegap: Union[int, float] = 0,
        sizefunc: Callable[[str], Tuple[Union[int, float],
                                        Union[int, float]]] = lambda s : (len(s), 1),
        predicate: Callable[[str], bool] = lambda line: line.strip(),
        method: Literal['mono', 'word'] = 'word',
        alignment: Literal['left', 'center', 'right', 'fill'] = 'left',
        fillchar: str = ' ',
        placeholder: str = '...',
        prefix: Optional[str] = None,
        preserve_empty: bool = True,
        use_minimum_width: bool = True,
        break_on_hyphens: bool = True,
        justify_last_line: bool = False,
        strip_space: bool = True

    ) -> None
```

> **width** : _int | float_
=> The maximum width of the wrapped line. Default: 70.

> **start** : _SupportsIndex_
=> The starting index of the text (specific to the shorten method). Default: 0.

> **linegap** : _int | float_
=> The gap between lines (specific to the align method). Default: 0.

> **sizefunc** : _(str) -> tuple[int | float, int | float]_
=> A function to calculate the width and height of the text. The default is a lambda function
returning the text length as width and 1 as height.

> **predicate** : _(str) -> bool_
=> A function to filter lines (specific to indent and dedent methods). The default is a lambda
function that trims empty lines from the left and right.

> **method** : _Literal['mono', 'word']_
=> The text wrapping method. Default: 'word'.

> **alignment** : _Literal['left', 'center', 'right', 'fill']_
=> The text alignment (specific to align and fillstr method). Default: 'left'.

> **fillchar** : _str_
=> The character used for padding (specific to the fillstr method). Default: ' '.

> **placeholder** : _str_
=> The placeholder used when shortening text (specific to the shorten method). Default: '...'.

> **prefix** : _Optional[str]_
=> A prefix to add or remove (for the indent method, it must be a string and will be added at the
beginning of each line. For dedent, it is optional and removes the prefix from the beginning of each
line). Default: None.

> **preserve_empty** : _bool_
=> Whether to retain empty lines. Default: True.

> **use_minimum_width** : _bool_
=> Whether to use the minimum detected width (specific to the align method). Default: True.

> **break_on_hyphens** : _bool_
=> Whether to allow breaking words at hyphens (-) (specific to align and fillstr methods).
Default: True.

> **justify_last_line** : _bool_
=> Whether to adjust the alignment of the last line (applies to align and fillstr methods, but only
for non-wrapped text and only for fill alignment). Default: False.

> **strip_space** : _bool_
=> Whether to remove excessive spaces (applies only to the shorten method and does not affect other
wrapping methods). Default: True.

### Mod📦 `python -m txtwrap`
```
usage: txtwrap [-h] [-v] [-f <str (1 character)>] [-w <int>] [-m {word|mono|indent|dedent|shorten}]
               [-a {left|center|right|fill}] [-n] [-x <str>] [-s <int>] [-p <str>] [-b] [-j] [-r]
               text

Command-line tool for wrapping, aligning, or shortening text.

positional arguments:
  text                  Text to be wrapped, aligned, or shorted

options:
  -h, --help            show this help message and exit
  -v, --version         Show the version of the txtwrap
  -f <str (1 character)>, --fillchar <str (1 character)>
                        Fill character (default: " ")
  -w <int>, --width <int>
                        Width of the text wrapping (default: current width terminal or 70)
  -m {word|mono|indent|dedent|shorten}, --method {word|mono|indent|dedent|shorten}
                        Method to be applied to the text (default: "word")
  -a {left|center|right|fill}, --alignment {left|center|right|fill}
                        Alignment of the text (default: "left")
  -n, --neglect-empty   Neglect empty lines in the text
  -x <str>, --prefix <str>
                        Prefix to be added (indent) or remove (dedent) to the text
  -s <int>, --start <int>
                        start index of the text to be shorten (default: 0)
  -p <str>, --placeholder <str>
                        Placeholder to be used when shortening the text (default: "...")
  -b, --not-break-on-hyphens
                        Doesn't break on hyphens
  -j, --justify-last-line
                        Justify the last line of the text
  -r, --no-strip        Do not strip the space in the text

for example: python|py -m txtwrap "Lorem ipsum odor amet, consectetuer adipiscing elit." -w 20 ^
             -m word -a center
```

## Examples❓

### Render a wrap text in PyGame🎮
```py
from typing import Literal, Optional
from txtwrap import align, LOREM_IPSUM_PARAGRAPHS
import pygame

def render_wrap(

    font: pygame.Font,
    text: str,
    width: int,
    antialias: bool,
    color: pygame.Color,
    background: Optional[pygame.Color] = None,
    linegap: int = 0,
    method: Literal['word', 'mono'] = 'word',
    alignment: Literal['left', 'center', 'right', 'fill'] = 'left',
    preserve_empty: bool = True,
    break_on_hyphens: bool = True,
    use_minimum_width: bool = True,
    justify_last_line: bool = False,

) -> pygame.Surface:

    align_info = align(
        text_or_wrapped=str(text),
        width=width,
        linegap=linegap,
        sizefunc=font.size,
        method=method,
        alignment=alignment,
        preserve_empty=preserve_empty,
        break_on_hyphens=break_on_hyphens,
        use_minimum_width=use_minimum_width,
        justify_last_line=justify_last_line,
        return_details=True
    )

    surface = pygame.Surface(align_info['size'], pygame.SRCALPHA)

    if background is not None:
        surface.fill(background)

    for x, y, text in align_info['aligned']:
        surface.blit(font.render(text, antialias, color), (x, y))

    return surface

# Example usage:
pygame.init()
pygame.display.set_caption("Lorem Ipsum")

running = True
wscrn, hscrn = 600, 600
screen = pygame.display.set_mode((wscrn, hscrn))
clock = pygame.time.Clock()
surface = render_wrap(
    font=pygame.font.Font(None, 20),
    text=LOREM_IPSUM_PARAGRAPHS,
    width=wscrn,
    antialias=True,
    color='#ffffff',
    background='#303030',
    alignment='fill'
)

wsurf, hsurf = surface.get_size()
pos = ((wscrn - wsurf) / 2, (hscrn - hsurf) / 2)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill('#000000')
    screen.blit(surface, pos)
    pygame.display.flip()
    clock.tick(60)
```

### Print a wrap text to terminal🔡
```py
from txtwrap import printwrap, LOREM_IPSUM_WORDS

printwrap(LOREM_IPSUM_WORDS, width=20, alignment='left')
print('=' * 20)
printwrap(LOREM_IPSUM_WORDS, width=20, alignment='center')
print('=' * 20)
printwrap(LOREM_IPSUM_WORDS, width=20, alignment='right')
print('=' * 20)
printwrap(LOREM_IPSUM_WORDS, width=20, alignment='fill')
```

### Short a long text🔤
```py
from txtwrap import shorten, LOREM_IPSUM_SENTENCES

short_lorem = shorten(LOREM_IPSUM_SENTENCES, width=20, placeholder='…')
test = shorten('  Helllo,   \t\n World!!\f', width=20, placeholder='…', strip_space=True)

print(short_lorem)
print(test)
```

### Bonus🎁 - Print a colorfull text to terminal🔥
```py
# Run this code in a terminal that supports ansi characters

from re import compile
from random import randint
from txtwrap import printwrap, LOREM_IPSUM_PARAGRAPHS

# Set the text to be printed here
text = LOREM_IPSUM_PARAGRAPHS

remove_ansi_regex = compile(r'\x1b\[(K|.*?m)').sub

def len_no_ansi(s: str):
    return len(remove_ansi_regex('', s))

while True:
    printwrap(
        ''.join(f'\x1b[{randint(31, 36)}m{char}' for char in text) + '\x1b[0m',
        end='\x1b[H\x1b[J',
        alignment='fill',
        lenfunc=len_no_ansi
    )
```