from typing import (
    Any, Callable, Dict, IO, List, Literal, Optional, Sequence, SupportsIndex, Tuple, Union
)
from os import get_terminal_size
from re import compile

hyphenated_re = compile(r'(?<=-)(?=(?!-).)')
version = '2.0.0'

# Constants ----------------------------------------------------------------------------------------

LOREM_IPSUM_WORDS = 'Lorem ipsum odor amet, consectetuer adipiscing elit.'
LOREM_IPSUM_SENTENCES = (
    'Lorem ipsum odor amet, consectetuer adipiscing elit. In malesuada eros natoque urna felis '
    'diam aptent donec. Cubilia libero morbi fusce tempus, luctus aenean augue. Mus senectus '
    'rutrum phasellus fusce dictum platea. Eros a integer nec fusce erat urna.'
)
LOREM_IPSUM_PARAGRAPHS = (
    'Lorem ipsum odor amet, consectetuer adipiscing elit. Nulla porta ex condimentum velit '
    'facilisi; consequat congue. Tristique duis sociosqu aliquam semper sit id. Nisi morbi purus, '
    'nascetur elit pellentesque venenatis. Velit commodo molestie potenti placerat faucibus '
    'convallis. Himenaeos dapibus ipsum natoque nam dapibus habitasse diam. Viverra ac porttitor '
    'cras tempor cras. Pharetra habitant nibh dui ipsum scelerisque cras? Efficitur phasellus '
    'etiam congue taciti tortor quam. Volutpat quam vulputate condimentum hendrerit justo congue '
    'iaculis nisl nullam.\n\nInceptos tempus nostra fringilla arcu; tellus blandit facilisi risus. '
    'Platea bibendum tristique lectus nunc placerat id aliquam. Eu arcu nisl mattis potenti '
    'elementum. Dignissim vivamus montes volutpat litora felis fusce ultrices. Vulputate magna '
    'nascetur bibendum inceptos scelerisque morbi posuere. Consequat dolor netus augue augue '
    'tristique curabitur habitasse bibendum. Consectetur est per eros semper, magnis interdum '
    'libero. Arcu adipiscing litora metus fringilla varius gravida congue tellus adipiscing. '
    'Blandit nulla mauris nullam ante metus curae scelerisque.\n\nSem varius sodales ut volutpat '
    'imperdiet turpis primis nullam. At gravida tincidunt phasellus lacus duis integer eros '
    'penatibus. Interdum mauris molestie posuere nascetur dignissim himenaeos; magna et quisque. '
    'Dignissim malesuada etiam donec vehicula aliquet bibendum. Magna dapibus sapien semper '
    'parturient id dis? Pretium orci ante leo, porta tincidunt molestie. Malesuada dictumst '
    'commodo consequat interdum nisi fusce cras rhoncus feugiat.\n\nHimenaeos mattis commodo '
    'suspendisse maecenas cras arcu. Habitasse id facilisi praesent justo molestie felis luctus '
    'suspendisse. Imperdiet ipsum praesent nunc mauris mattis curabitur. Et consectetur morbi '
    'auctor feugiat enim ridiculus arcu. Ultricies magna blandit eget; vivamus sollicitudin nisl '
    'proin. Sollicitudin sociosqu et finibus elit vestibulum sapien nec odio euismod. Turpis '
    'eleifend amet quis auctor cursus. Vehicula pharetra sapien praesent amet purus ante. Risus '
    'blandit cubilia lorem hendrerit penatibus in magnis.\n\nAmet posuere nunc; maecenas consequat '
    'risus potenti. Volutpat leo lacinia sapien nulla sagittis dignissim mauris ultrices aliquet. '
    'Nisi pretium interdum luctus donec magna suscipit. Dapibus tristique felis natoque malesuada '
    'augue? Justo faucibus tincidunt congue arcu sem; fusce aliquet proin. Commodo neque nibh; '
    'tempus ad tortor netus. Mattis ultricies nec maximus porttitor non mauris?'
)

# Wrapper ------------------------------------------------------------------------------------------

class TextWrapper:

    """ A class for text wrapping. """

    def __init__(

        self,
        width: Union[int, float] = 70,
        start: SupportsIndex = 0,
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

    ) -> None:

        """
        Initialize the wrapper.

        Parameters:
            width (int | float): The maximum width of the wrapped line. Default: 70.
            start (SupportsIndex): The starting index of the text (specific to the shorten method).
                                   Default: 0.
            linegap (int | float): The gap between lines (specific to the align method). Default: 0.
            sizefunc ((str) -> tuple[int | float, int | float]): A function to calculate the width 
                                                                 and height of the text. The default 
                                                                 is a lambda function returning the
                                                                 text length as width and 1 as
                                                                 height.
            predicate ((str) -> bool): A function to filter lines (specific to indent and
                                       dedent methods). The default is a lambda function that trims
                                       empty lines from the left and right.
            method (Literal['mono', 'word']): The text wrapping method. Default: 'word'.
            alignment (Literal['left', 'center', 'right', 'fill']): The text alignment
                                                                    (specific to align and fillstr
                                                                    method). Default: 'left'.
            fillchar (str): The character used for padding (specific to the fillstr method).
                            Default: ' '.
            placeholder (str): The placeholder used when shortening text
                               (specific to the shorten method). Default: '...'.
            prefix (Optional[str]): A prefix to add or remove (for the indent method,
                                    it must be a string and will be added at the beginning of
                                    each line. For dedent, it is optional and removes the prefix
                                    from the beginning of each line). Default: None.
            preserve_empty (bool): Whether to retain empty lines. Default: True.
            use_minimum_width (bool): Whether to use the minimum detected width
                                      (specific to the align method). Default: True.
            break_on_hyphens (bool): Whether to allow breaking words at hyphens (-) 
                                    (specific to align and fillstr methods). Default: True.
            justify_last_line (bool): Whether to adjust the alignment of the last line 
                                      (applies to align and fillstr methods, but only for
                                      non-wrapped text and only for fill alignment). Default: False.
            strip_space (bool): Whether to remove excessive spaces (applies only to the shorten
                                method and does not affect other wrapping methods). Default: True.
        """

        self._d = {}

        self.width = width
        self.start = start
        self.linegap = linegap
        self.sizefunc = sizefunc
        self.predicate = predicate
        self.method = method
        self.alignment = alignment
        self.fillchar = fillchar
        self.placeholder = placeholder
        self.prefix = prefix
        self.preserve_empty = preserve_empty
        self.use_minimum_width = use_minimum_width
        self.break_on_hyphens = break_on_hyphens
        self.justify_last_line = justify_last_line
        self.strip_space = strip_space

    def __copy__(self) -> 'TextWrapper':
        return TextWrapper(
            width=self._d['width'],
            start=self._d['start'],
            linegap=self._d['linegap'],
            sizefunc=self._d['sizefunc'],
            predicate=self._d['predicate'],
            method=self._d['method'],
            alignment=self._d['alignment'],
            fillchar=self._d['fillchar'],
            placeholder=self._d['placeholder'],
            prefix=self._d['prefix'],
            preserve_empty=self._d['preserve_empty'],
            use_minimum_width=self._d['use_minimum_width'],
            break_on_hyphens=self._d['break_on_hyphens'],
            justify_last_line=self._d['justify_last_line'],
            strip_space=self._d['strip_space']
        )

    def __deepcopy__(self, memo: dict) -> 'TextWrapper':
        return self.__copy__()

    @property
    def width(self) -> Union[int, float]:
        return self._d['width']

    @property
    def start(self) -> SupportsIndex:
        return self._d['start']

    @property
    def linegap(self) -> Union[int, float]:
        return self._d['linegap']

    @property
    def sizefunc(self) -> Callable[[str], Tuple[Union[int, float], Union[int, float]]]:
        return self._d['sizefunc']

    @property
    def predicate(self) -> Callable[[str], bool]:
        return self._d['predicate']

    @property
    def method(self) -> Literal['mono', 'word']:
        return self._d['method']

    @property
    def alignment(self) -> Literal['left', 'center', 'right', 'fill']:
        return self._d['alignment']

    @property
    def fillchar(self) -> str:
        return self._d['fillchar']

    @property
    def placeholder(self) -> str:
        return self._d['placeholder']

    @property
    def prefix(self) -> Union[str, None]:
        return self._d['prefix']

    @property
    def preserve_empty(self) -> bool:
        return self._d['preserve_empty']

    @property
    def use_minimum_width(self) -> bool:
        return self._d['use_minimum_width']

    @property
    def break_on_hyphens(self) -> bool:
        return self._d['break_on_hyphens']

    @property
    def justify_last_line(self) -> bool:
        return self._d['justify_last_line']

    @property
    def strip_space(self) -> bool:
        return self._d['strip_space']

    @width.setter
    def width(self, new: Union[int, float]) -> None:
        if not isinstance(new, (int, float)):
            raise TypeError("width must be an integer or float")
        if new <= 0:
            raise ValueError("width must be greater than 0")
        self._d['width'] = new

    @start.setter
    def start(self, new: SupportsIndex) -> None:
        if not isinstance(new, int):
            raise TypeError("start must be an integer")
        if new < 0:
            raise ValueError("start must be equal to or greater than 0")
        self._d['start'] = new

    @linegap.setter
    def linegap(self, new: Union[int, float]) -> None:
        if not isinstance(new, (int, float)):
            raise TypeError("linegap must be a integer or float")
        if new < 0:
            raise ValueError("linegap must be equal to or greater than 0")
        self._d['linegap'] = new

    @sizefunc.setter
    def sizefunc(self, new: Callable[[str], Tuple[Union[int, float], Union[int, float]]]) -> None:
        if not callable(new):
            raise TypeError("sizefunc must be a callable")
        test = new('test')
        if not isinstance(test, tuple):
            raise TypeError("sizefunc must be returned a tuple")
        if len(test) != 2:
            raise ValueError("sizefunc must be returned a tuple of length 2")
        if not isinstance(test[0], (int, float)):
            raise TypeError("sizefunc must be returned a tuple of two integers or floats. "
                            "Detected invalid at width")
        if not isinstance(test[1], (int, float)):
            raise TypeError("sizefunc must be returned a tuple of two integers or floats. "
                            "Detected invalid at height")
        if test[0] < 0:
            raise ValueError("sizefunc returned width must be equal to or greater than 0")
        if test[1] < 0:
            raise ValueError("sizefunc returned height must be equal to or greater than 0")
        self._d['sizefunc'] = new
        self._d['lenfunc'] = lambda s : new(s)[0]

    @predicate.setter
    def predicate(self, new: Callable[[str], bool]) -> None:
        if not callable(new):
            raise TypeError("predicate must be a callable")
        new('test')
        self._d['predicate'] = new

    @method.setter
    def method(self, new: Literal['mono', 'word']) -> None:
        if not isinstance(new, str):
            raise TypeError("method must be a string")
        new = new.strip().lower()
        if new not in {'mono', 'word'}:
            raise ValueError(f"method={new!r} is invalid, must be 'mono' or 'word'")
        self._d['method'] = new
        if new == 'mono':
            self._d['wrapfunc'] = self.mono
        elif new == 'word':
            self._d['wrapfunc'] = self.word

    @alignment.setter
    def alignment(self, new: Literal['left', 'center', 'right', 'fill']) -> None:
        if not isinstance(new, str):
            raise TypeError("alignment must be a string")
        new = new.strip().lower()
        if new not in {'left', 'center', 'right', 'fill'}:
            raise ValueError(f"alignment={new!r} is invalid, must be 'left', 'center', 'right', or "
                             "'fill'")
        self._d['alignment'] = new

    @fillchar.setter
    def fillchar(self, new: str) -> None:
        if not isinstance(new, str):
            raise TypeError("fillchar must be a string")
        if self._d['lenfunc'](new) != 1:
            raise ValueError("fillchar must be a single length")
        self._d['fillchar'] = new

    @placeholder.setter
    def placeholder(self, new: str) -> None:
        if not isinstance(new, str):
            raise TypeError("placeholder must be a string")
        self._d['placeholder'] = new

    @prefix.setter
    def prefix(self, new: Optional[str]) -> None:
        if not isinstance(new, (str, type(None))):
            raise TypeError("prefix must be a string or none type")
        self._d['prefix'] = new

    @preserve_empty.setter
    def preserve_empty(self, new: bool) -> None:
        self._d['preserve_empty'] = new

    @use_minimum_width.setter
    def use_minimum_width(self, new: bool) -> None:
        self._d['use_minimum_width'] = new

    @break_on_hyphens.setter
    def break_on_hyphens(self, new: bool) -> None:
        self._d['break_on_hyphens'] = new

    @justify_last_line.setter
    def justify_last_line(self, new: bool) -> None:
        self._d['justify_last_line'] = new

    @strip_space.setter
    def strip_space(self, new: bool) -> None:
        self._d['strip_space'] = new

    def _wrap(self, text: str) -> Dict[Literal['wrapped', 'indiced'], Any]:
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        wrapfunc = self._d['wrapfunc']
        preserve_empty = self._d['preserve_empty']

        wrapped_lines = []
        line_indices = set()

        for line in text.splitlines():
            wrapped_line = wrapfunc(line)
            if wrapped_line:
                wrapped_lines.extend(wrapped_line)
                line_indices.add(len(wrapped_lines) - 1)
            elif preserve_empty:
                wrapped_lines.append('')

        return {
            'wrapped': wrapped_lines,
            'indiced': line_indices
        }

    def _align(self, text_or_wrapped: Union[str, Sequence[str]]) -> Dict[Literal['aligned',
                                                                                 'wrapped',
                                                                                 'size'], Any]:
        width = self._d['width']
        linegap = self._d['linegap']
        sizefunc = self._d['sizefunc']
        use_minimum_width = self._d['use_minimum_width']
        alignment = self._d['alignment']

        aligned_positions = []
        offset_y = 0

        if isinstance(text_or_wrapped, str):
            use_text = True
            wrap_info = self._wrap(text_or_wrapped)
            wrapped = wrap_info['wrapped']
            line_indiced = wrap_info['indiced']
        elif isinstance(text_or_wrapped, Sequence):
            use_text = False
            wrapped = text_or_wrapped
        else:
            raise TypeError("text_or_wrapped must be a string or a sequence of strings")

        size_wrapped = {i: sizefunc(line) for i, line in enumerate(wrapped)}

        if use_minimum_width:
            max_width = max(size[0] for size in size_wrapped.values())
            use_width = max_width
        else:
            use_width = width

        if alignment == 'left':
            for i, line in enumerate(wrapped):
                aligned_positions.append((0, offset_y, line))
                offset_y += size_wrapped[i][1] + linegap

        elif alignment == 'center':
            for i, line in enumerate(wrapped):
                width_line, height_line = size_wrapped[i]
                aligned_positions.append(((use_width - width_line) / 2, offset_y, line))
                offset_y += height_line + linegap

        elif alignment == 'right':
            for i, line in enumerate(wrapped):
                width_line, height_line = size_wrapped[i]
                aligned_positions.append((use_width - width_line, offset_y, line))
                offset_y += height_line + linegap

        elif alignment == 'fill':
            no_spaces = True
            enable_justify_last_line = use_text and not self._d['justify_last_line']

            for i, line in enumerate(wrapped):
                if enable_justify_last_line and i in line_indiced:
                    aligned_positions.append((0, offset_y, line))
                else:
                    words = line.split()
                    total_words = len(words)
                    word_widths = {j: sizefunc(w)[0] for j, w in enumerate(words)}
                    extra_space = width - sum(word_widths.values())
                    offset_x = 0

                    if total_words > 1:
                        space_between_words = extra_space / (total_words - 1)
                        no_spaces = False
                    else:
                        space_between_words = extra_space

                    for j, w in enumerate(words):
                        aligned_positions.append((offset_x, offset_y, w))
                        offset_x += word_widths[j] + space_between_words

                offset_y += size_wrapped[i][1] + linegap

        if use_minimum_width and alignment == 'fill':
            if no_spaces:
                size_width = max_width
            elif text_or_wrapped:
                size_width = width
            else:
                size_width = 0
        else:
            size_width = use_width

        return {
            'aligned': aligned_positions,
            'wrapped': wrapped,
            'size': (size_width, offset_y - linegap)
        }

    def mono(self, text: str) -> List[str]:
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        width = self._d['width']
        lenfunc = self._d['lenfunc']

        parts = []
        current_char = ''

        for char in text:
            if lenfunc(current_char + char) <= width:
                current_char += char
            else:
                parts.append(current_char)
                current_char = char

        if current_char:
            parts.append(current_char)

        return parts

    def word(self, text: str) -> List[str]:
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        width = self._d['width']
        lenfunc = self._d['lenfunc']
        break_on_hyphens = self._d['break_on_hyphens']

        lines = []
        current_line = ''

        for word in text.split():
            test_line = f'{current_line} {word}' if current_line else word

            if lenfunc(test_line) <= width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)

                current_line = ''

                if break_on_hyphens:
                    for part in hyphenated_re.split(word):
                        for wrapped_part in self.mono(part):
                            if lenfunc(current_line + wrapped_part) <= width:
                                current_line += wrapped_part
                            else:
                                if current_line:
                                    lines.append(current_line)
                                current_line = wrapped_part
                else:
                    for part in self.mono(word):
                        if lenfunc(current_line + part) <= width:
                            current_line += part
                        else:
                            if current_line:
                                lines.append(current_line)
                            current_line = part

        if current_line:
            lines.append(current_line)

        return lines

    def wrap(self, text: str) -> List[str]:
        return self._wrap(text)['wrapped']

    def align(self, text_or_wrapped: Union[str, Sequence[str]]) -> List[Tuple[Union[int, float],
                                                                              Union[int, float],
                                                                              str]]:
        return self._align(text_or_wrapped)['aligned']

    def fillstr(self, text_or_wrapped: Union[str, Sequence[str]]) -> str:
        width = self._d['width']
        lenfunc = self._d['lenfunc']
        fillchar = self._d['fillchar']
        alignment = self._d['alignment']

        justified_lines = ''

        if isinstance(text_or_wrapped, str):
            use_text = True
            wrap_info = self._wrap(text_or_wrapped)
            wrapped = wrap_info['wrapped']
            line_indiced = wrap_info['indiced']
        elif isinstance(text_or_wrapped, Sequence):
            use_text = False
            wrapped = text_or_wrapped
        else:
            raise TypeError("text_or_wrapped must be a string or a sequence of strings")

        if alignment == 'left':
            for line in wrapped:
                justified_lines += line + fillchar * (width - lenfunc(line)) + '\n'

        elif alignment == 'center':
            for line in wrapped:
                extra_space = width - lenfunc(line)
                left_space = extra_space // 2
                justified_lines += (fillchar * left_space + line +
                                    fillchar * (extra_space - left_space) + '\n')

        elif alignment == 'right':
            for line in wrapped:
                justified_lines += fillchar * (width - lenfunc(line)) + line + '\n'

        elif alignment == 'fill':
            enable_justify_last_line = use_text and not self._d['justify_last_line']

            for i, line in enumerate(wrapped):
                if enable_justify_last_line and i in line_indiced:
                    justified_lines += line + fillchar * (width - lenfunc(line)) + '\n'
                else:
                    words = line.split()
                    total_words = len(words)
                    total_words_width = sum(lenfunc(w) for w in words)
                    extra_space = width - total_words_width

                    if total_words > 1:
                        space_between_words = extra_space // (total_words - 1)
                        extra_padding = extra_space % (total_words - 1)
                    else:
                        space_between_words = extra_space
                        extra_padding = 0

                    justified_line = ''
                    for i, word in enumerate(words):
                        justified_line += word
                        if i < total_words - 1:
                            justified_line += fillchar * (space_between_words +
                                                          (1 if i < extra_padding else 0))

                    if justified_line:
                        justified_lines += justified_line + '\n'
                    else:
                        justified_lines += fillchar * width + '\n'

        return justified_lines[:-1]

    def indent(self, text: str) -> str:
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        prefix = self._d['prefix']
        predicate = self._d['predicate']

        if prefix is None:
            raise ValueError("prefix require")

        return '\n'.join(prefix + line for line in text.splitlines() if predicate(line))

    def dedent(self, text: str) -> str:
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        prefix = self._d['prefix']
        predicate = self._d['predicate']

        return '\n'.join(line.lstrip(prefix) for line in text.splitlines() if predicate(line))

    def shorten(self, text: str) -> str:
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        width = self._d['width']
        start = self._d['start']
        lenfunc = self._d['lenfunc']
        placeholder = self._d['placeholder']
        strip_space = self._d['strip_space']

        if width < lenfunc(placeholder):
            raise ValueError("width must be greater than length of the placeholder")

        if strip_space:
            text = ' '.join(text.split())

        if start == 0:
            current_char = ''
        elif start >= len(text):
            return ''
        else:
            current_char = placeholder

        for char in text[start:]:
            if lenfunc(current_char + char + placeholder) <= width:
                current_char += char
            else:
                current_char += placeholder
                if lenfunc(current_char) > width:
                    return placeholder
                return current_char

        return current_char

    copy = __copy__

# Interface ----------------------------------------------------------------------------------------

def mono(
    text: str,
    width: Union[int, float],
    lenfunc: Callable[[str], Union[int, float]] = len
) -> List[str]:
    return TextWrapper(
        width=width,
        sizefunc=lambda s : (lenfunc(s), 1)
    ).mono(text)

def word(
    text: str,
    width: Union[int, float],
    lenfunc: Callable[[str], Union[int, float]] = len,
    break_on_hyphens: bool = True
) -> List[str]:
    return TextWrapper(
        width=width,
        sizefunc=lambda s : (lenfunc(s), 1),
        break_on_hyphens=break_on_hyphens
    ).word(text)

def wrap(
    text: str,
    width: Union[int, float],
    lenfunc: Callable[[str], Union[int, float]] = len,
    method: Literal['mono', 'word'] = 'word',
    preserve_empty: bool = True,
    break_on_hyphens: bool = True
) -> List[str]:
    return TextWrapper(
        width=width,
        sizefunc=lambda s : (lenfunc(s), 1),
        method=method,
        preserve_empty=preserve_empty,
        break_on_hyphens=break_on_hyphens
    )._wrap(text)['wrapped']

def align(
    text_or_wrapped: Union[str, Sequence[str]],
    width: Union[int, float] = 70,
    linegap: Union[int, float] = 0,
    sizefunc: Callable[[str], Tuple[Union[int, float], Union[int, float]]] = lambda s : (len(s), 1),
    method: Literal['mono', 'word'] = 'word',
    alignment: Literal['left', 'center', 'right', 'fill'] = 'left',
    preserve_empty: bool = True,
    break_on_hyphens: bool = True,
    use_minimum_width: bool = True,
    justify_last_line: bool = False,
    return_details: bool = False
) -> Union[Dict[Literal['aligned', 'wrapped', 'size'], Any],
           List[Tuple[Union[int, float], Union[int, float], str]]]:
    align_info = TextWrapper(
        width=width,
        linegap=linegap,
        sizefunc=sizefunc,
        method=method,
        alignment=alignment,
        preserve_empty=preserve_empty,
        break_on_hyphens=break_on_hyphens,
        use_minimum_width=use_minimum_width,
        justify_last_line=justify_last_line
    )._align(text_or_wrapped)
    if return_details:
        return align_info
    return align_info['aligned']

def fillstr(
    text_or_wrapped: Union[str, Sequence[str]],
    width: int = 70,
    fillchar: str = ' ',
    lenfunc: Callable[[str], int] = len,
    method: Literal['mono', 'word'] = 'word',
    alignment: Literal['left', 'center', 'right', 'fill'] = 'left',
    preserve_empty: bool = True,
    break_on_hyphens: bool = True,
    justify_last_line: bool = False
) -> str:
    return TextWrapper(
        width=width,
        fillchar=fillchar,
        sizefunc=lambda s : (lenfunc(s), 1),
        method=method,
        alignment=alignment,
        preserve_empty=preserve_empty,
        break_on_hyphens=break_on_hyphens,
        justify_last_line=justify_last_line
    ).fillstr(text_or_wrapped)

def printwrap(

    *values: object,
    sep: Optional[str] = ' ',
    end: Optional[str] = '\n',
    wrap: Optional[TextWrapper] = None,
    file: Optional[IO] = None,
    flush: bool = False,
    width: Optional[int] = None,
    default_width: int = 70,
    is_wrapped: bool = False,
    **kwargs

) -> None:

    map_values = [str(x) for x in values]
    text = map_values if is_wrapped else (' ' if sep is None else sep).join(map_values)

    if wrap is None:
        if width is None:
            try:
                width = get_terminal_size().columns
            except:
                width = default_width
        string = fillstr(text, width=width, **kwargs)
    else:
        string = wrap.fillstr(text)

    print(string, end=end, file=file, flush=flush)

def indent(
    text: str,
    prefix: str,
    predicate: Callable[[str], bool] = lambda line: line.strip()
) -> str:
    return TextWrapper(
        prefix=prefix,
        predicate=predicate
    ).indent(text)

def dedent(
    text: str,
    prefix: Optional[str] = None,
    predicate: Callable[[str], bool] = lambda line: line.strip()
) -> str:
    return TextWrapper(
        prefix=prefix,
        predicate=predicate
    ).dedent(text)

def shorten(
    text: str,
    width: Union[int, float] = 70,
    start: SupportsIndex = 0,
    lenfunc: Callable[[str], Union[int, float]] = len,
    placeholder: str = '...',
    strip_space: bool = True
) -> str:
    return TextWrapper(
        width=width,
        start=start,
        sizefunc=lambda s : (lenfunc(s), 1),
        placeholder=placeholder,
        strip_space=strip_space
    ).shorten(text)