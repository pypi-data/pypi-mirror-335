from os import get_terminal_size
from re import compile

hyphenated_re = compile(r'(?<=-)(?=(?!-).)')
version = '2.1.0'

def sizelen(s):
    return (len(s), 1)

def stripstr(s):
    return s.strip()

def align_left(aligned_positions, text, width, text_width, offset_y, separator, fillchar):
    aligned_positions.append((0, offset_y, text.replace(separator, fillchar)))

def align_center(aligned_positions, text, width, text_width, offset_y, separator, fillchar):
    aligned_positions.append(((width - text_width) / 2, offset_y, text.replace(separator,
                                                                               fillchar)))

def align_right(aligned_positions, text, width, text_width, offset_y, separator, fillchar):
    aligned_positions.append((width - text_width, offset_y, text.replace(separator, fillchar)))

def fillstr_left(text, width, text_width, separator, fillchar):
    return text.replace(separator, fillchar) + fillchar * (width - text_width) + '\n'

def fillstr_center(text, width, text_width, separator, fillchar):
    extra_space = width - text_width
    left_space = extra_space // 2
    return fillchar * left_space + text.replace(separator,
                                                fillchar) + fillchar * (extra_space -
                                                                        left_space) + '\n'

def fillstr_right(text, width, text_width, separator, fillchar):
    return fillchar * (width - text_width) + text.replace(separator, fillchar) + '\n'

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

class TextWrapper:

    """ A class for text wrapping. """

    __slots__ = ('_d',)

    def __init__(self, width=70, start=0, linegap=0, method='word', alignment='left', fillchar=' ',
                 placeholder='...', prefix=None, separator=None, preserve_empty=True,
                 use_minimum_width=True, justify_last_line=False, break_on_hyphens=True,
                 sizefunc=sizelen, predicate=stripstr):

        """
        Initialize the wrapper.

        Parameters:
            width (int | float): The maximum width of the wrapped line. Default: 70.
            start (SupportsIndex): The starting index of the text (specific to the shorten method).
                                   Default: 0.
            linegap (int | float): The gap between lines (specific to the align method). Default: 0.
            method (Literal['mono', 'word']): The text wrapping method. Default: 'word'.
            alignment (Literal['left', 'center', 'right', 'fill',
                               'fill-left', 'fill-center', 'fill-right']): The text alignment
                                                                           (specific to align and
                                                                           fillstr method).
                                                                           Default: 'left'.
            fillchar (str): The character used for padding. Default: ' '.
            placeholder (str): The placeholder used when shortening text
                               (specific to the shorten method). Default: '...'.
            prefix (Optional[str]): A prefix to add or remove (for the indent method,
                                    it must be a string and will be added at the beginning of
                                    each line. For dedent, it is optional and removes the prefix
                                    from the beginning of each line). Default: None.
            separator (Optional[str]): The separator used between words. Default: None.
            preserve_empty (bool): Whether to retain empty lines. Default: True.
            use_minimum_width (bool): Whether to use the minimum detected width
                                      (specific to the align and fillstr methods). Default: True.
            justify_last_line (bool): Whether to adjust the alignment of the last line 
                                      (applies to align and fillstr methods, but only for
                                      fill alignment). Default: False.
            break_on_hyphens (bool): Whether to allow breaking words at hyphens (-). Default: True.
            sizefunc ((str) -> tuple[int | float, int | float]): A function to calculate the width 
                                                                 and height of the text. The default 
                                                                 is a lambda function returning the
                                                                 text length as width and 1 as
                                                                 height.
            predicate ((str) -> bool): A function to filter lines (specific to indent and
                                       dedent methods). The default is a lambda function that trims
                                       empty lines from the left and right.
        """

        self._d = {}

        self.width = width
        self.start = start
        self.linegap = linegap
        self.method = method
        self.alignment = alignment
        self.fillchar = fillchar
        self.placeholder = placeholder
        self.prefix = prefix
        self.separator = separator
        self.preserve_empty = preserve_empty
        self.use_minimum_width = use_minimum_width
        self.justify_last_line = justify_last_line
        self.break_on_hyphens = break_on_hyphens
        self.sizefunc = sizefunc
        self.predicate = predicate

    def __copy__(self):
        return self.copy()

    def __deepcopy__(self, memo):
        return self.copy()

    @property
    def width(self):
        return self._d['width']

    @property
    def start(self):
        return self._d['start']

    @property
    def linegap(self):
        return self._d['linegap']

    @property
    def method(self):
        return self._d['method']

    @property
    def alignment(self):
        return self._d['alignment']

    @property
    def fillchar(self):
        return self._d['fillchar']

    @property
    def placeholder(self):
        return self._d['placeholder']

    @property
    def prefix(self):
        return self._d['prefix']

    @property
    def separator(self):
        return self._d['separator']

    @property
    def preserve_empty(self):
        return self._d['preserve_empty']

    @property
    def use_minimum_width(self):
        return self._d['use_minimum_width']

    @property
    def justify_last_line(self):
        return self._d['justify_last_line']

    @property
    def break_on_hyphens(self):
        return self._d['break_on_hyphens']

    @property
    def sizefunc(self):
        return self._d['sizefunc']

    @property
    def predicate(self):
        return self._d['predicate']

    @width.setter
    def width(self, new):
        if not isinstance(new, (int, float)):
            raise TypeError("width must be an integer or float")
        if new <= 0:
            raise ValueError("width must be greater than 0")
        self._d['width'] = new

    @start.setter
    def start(self, new):
        if not isinstance(new, int):
            raise TypeError("start must be an integer")
        if new < 0:
            raise ValueError("start must be equal to or greater than 0")
        self._d['start'] = new

    @linegap.setter
    def linegap(self, new):
        if not isinstance(new, (int, float)):
            raise TypeError("linegap must be a integer or float")
        if new < 0:
            raise ValueError("linegap must be equal to or greater than 0")
        self._d['linegap'] = new

    @method.setter
    def method(self, new):
        if not isinstance(new, str):
            raise TypeError("method must be a string")
        new = new.strip().lower()
        if new not in {'mono', 'word'}:
            raise ValueError("method={} is invalid, must be 'mono' or 'word'".format(new))
        self._d['method'] = new
        if new == 'mono':
            self._d['wrapfunc'] = self.mono
        elif new == 'word':
            self._d['wrapfunc'] = self.word

    @alignment.setter
    def alignment(self, new):
        if not isinstance(new, str):
            raise TypeError("alignment must be a string")
        new = new.strip().lower()
        if new not in {'left', 'center', 'right', 'fill', 'fill-left', 'fill-center', 'fill-right'}:
            raise ValueError("alignment={} is invalid, must be 'left', 'center', 'right', "
                             "'fill', 'fill-left', 'fill-center', or 'fill-right'".format(new))
        new = self._d['alignment'] = 'fill-left' if new == 'fill' else new
        if 'left' in new:
            self._d['align_justify'] = align_left
            self._d['fillstr_justify'] = fillstr_left
        elif 'center' in new:
            self._d['align_justify'] = align_center
            self._d['fillstr_justify'] = fillstr_center
        elif 'right' in new:
            self._d['align_justify'] = align_right
            self._d['fillstr_justify'] = fillstr_right

    @fillchar.setter
    def fillchar(self, new):
        if not isinstance(new, str):
            raise TypeError("fillchar must be a string")
        self._d['fillchar'] = new
        self._d['fillchar_with'] = None

    @placeholder.setter
    def placeholder(self, new):
        if not isinstance(new, str):
            raise TypeError("placeholder must be a string")
        self._d['placeholder'] = new

    @prefix.setter
    def prefix(self, new):
        if not isinstance(new, (str, type(None))):
            raise TypeError("prefix must be a string or none type")
        self._d['prefix'] = new

    @separator.setter
    def separator(self, new):
        if not isinstance(new, (str, type(None))):
            raise TypeError("separator must be a string or none type")
        self._d['separator'] = new
        self._d['string_separator'] = ' ' if new is None else new

    @preserve_empty.setter
    def preserve_empty(self, new):
        self._d['preserve_empty'] = new

    @use_minimum_width.setter
    def use_minimum_width(self, new):
        self._d['use_minimum_width'] = new

    @justify_last_line.setter
    def justify_last_line(self, new):
        self._d['justify_last_line'] = new

    @break_on_hyphens.setter
    def break_on_hyphens(self, new):
        self._d['break_on_hyphens'] = new

    @sizefunc.setter
    def sizefunc(self, new):
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
    def predicate(self, new):
        if not callable(new):
            raise TypeError("predicate must be a callable")
        new('test')
        self._d['predicate'] = new

    def _split(self, text):
        separator = self._d['separator']
        if separator is None:
            return text.split()
        return [s for s in text.split(separator) if s]

    def _wrap(self, text):
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        preserve_empty = self._d['preserve_empty']
        wrapfunc = self._d['wrapfunc']

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

    def _align(self, text):
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        width = self._d['width']
        linegap = self._d['linegap']
        alignment = self._d['alignment']
        align_justify = self._d['align_justify']
        fillchar = self._d['fillchar']
        string_separator = self._d['string_separator']
        use_minimum_width = self._d['use_minimum_width']
        sizefunc = self._d['sizefunc']

        self._d['fillchar_with'] = string_separator
        wrap_info = self._wrap(text)
        self._d['fillchar_with'] = None

        wrapped = wrap_info['wrapped']
        line_indiced = wrap_info['indiced']

        aligned_positions = []
        offset_y = 0

        lines_size = {i: sizefunc(line) for i, line in enumerate(wrapped)}

        if use_minimum_width:
            use_width = max(size[0] for size in lines_size.values())
        else:
            use_width = width

        if alignment in {'left', 'center', 'right'}:
            for i, line in enumerate(wrapped):
                width_line, height_line = lines_size[i]
                align_justify(
                    aligned_positions,
                    line,
                    use_width,
                    width_line,
                    offset_y,
                    string_separator,
                    fillchar
                )
                offset_y += height_line + linegap

        else:
            lines_word = {i: self._split(line) for i, line in enumerate(wrapped)}
            no_fill_last_line = not self._d['justify_last_line']

            if use_minimum_width and any(
                    len(line) > 1 and not (no_fill_last_line and i in line_indiced)
                    for i, line in enumerate(lines_word.values())
                ): use_width = width if wrapped else 0

            for i, line in enumerate(wrapped):
                width_line, height_line = lines_size[i]
                words = lines_word[i]

                if no_fill_last_line and i in line_indiced:
                    align_justify(
                        aligned_positions,
                        line,
                        use_width,
                        width_line,
                        offset_y,
                        string_separator,
                        fillchar
                    )

                else:
                    total_words = len(words)

                    if total_words > 1:
                        all_word_width = {j: sizefunc(w)[0] for j, w in enumerate(words)}
                        extra_space = width - sum(all_word_width.values())
                        space_between_words = extra_space / (total_words - 1)
                        offset_x = 0

                        for j, w in enumerate(words):
                            aligned_positions.append((offset_x, offset_y, w))
                            offset_x += all_word_width[j] + space_between_words

                    else:
                        align_justify(
                            aligned_positions,
                            line,
                            use_width,
                            width_line,
                            offset_y,
                            string_separator,
                            fillchar
                        )

                offset_y += height_line + linegap

        return {
            'aligned': aligned_positions,
            'wrapped': wrapped,
            'indiced': line_indiced,
            'size': (use_width, offset_y - linegap)
        }

    def copy(self):
        return TextWrapper(
            width=self._d['width'],
            start=self._d['start'],
            linegap=self._d['linegap'],
            method=self._d['method'],
            alignment=self._d['alignment'],
            fillchar=self._d['fillchar'],
            placeholder=self._d['placeholder'],
            prefix=self._d['prefix'],
            separator=self._d['separator'],
            preserve_empty=self._d['preserve_empty'],
            use_minimum_width=self._d['use_minimum_width'],
            justify_last_line=self._d['justify_last_line'],
            break_on_hyphens=self._d['break_on_hyphens'],
            sizefunc=self._d['sizefunc'],
            predicate=self._d['predicate']
        )

    def mono(self, text):
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

    def word(self, text):
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        width = self._d['width']
        fillchar = self._d['fillchar']
        fillchar_with = self._d['fillchar_with']
        break_on_hyphens = self._d['break_on_hyphens']
        lenfunc = self._d['lenfunc']

        if fillchar_with:
            fillchar = fillchar_with

        lines = []
        current_line = ''

        for word in self._split(text):
            test_line = current_line + fillchar + word if current_line else word

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

    def wrap(self, text):
        return self._wrap(text)['wrapped']

    def align(self, text):
        return self._align(text)['aligned']

    def fillstr(self, text):
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        width = self._d['width']
        alignment = self._d['alignment']
        fillchar = self._d['fillchar']
        fillstr_justify = self._d['fillstr_justify']
        string_separator = self._d['string_separator']
        use_minimum_width = self._d['use_minimum_width']
        lenfunc = self._d['lenfunc']

        self._d['fillchar_with'] = string_separator
        wrap_info = self._wrap(text)
        self._d['fillchar_with'] = None

        wrapped = wrap_info['wrapped']
        line_indiced = wrap_info['indiced']

        justified_lines = ''

        lines_width = {i: lenfunc(line) for i, line in enumerate(wrapped)}

        if use_minimum_width:
            use_width = max(lines_width.values())
        else:
            use_width = width

        if alignment in {'left', 'center', 'right'}:
            for i, line in enumerate(wrapped):
                justified_lines += fillstr_justify(
                    line,
                    use_width,
                    lines_width[i],
                    string_separator,
                    fillchar
                )

        else:
            lines_word = {i: self._split(line) for i, line in enumerate(wrapped)}
            no_fill_last_line = not self._d['justify_last_line']

            if use_minimum_width and any(
                    len(line) > 1 and not (no_fill_last_line and i in line_indiced)
                    for i, line in enumerate(lines_word.values())
                ): use_width = width if wrapped else 0

            for i, line in enumerate(wrapped):
                width_line = lines_width[i]
                words = lines_word[i]

                if no_fill_last_line and i in line_indiced:
                    justified_lines += fillstr_justify(
                        line,
                        use_width,
                        width_line,
                        string_separator,
                        fillchar
                    )
                else:
                    total_words = len(words)

                    if total_words > 1:
                        extra_space = width - sum(lenfunc(w) for w in words)
                        space_between_words = extra_space // (total_words - 1)
                        extra_padding = extra_space % (total_words - 1)
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

                    else:
                        justified_lines += fillstr_justify(
                            line,
                            use_width,
                            width_line,
                            string_separator,
                            fillchar
                        )

        return justified_lines[:-1]

    def indent(self, text):
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        prefix = self._d['prefix']
        predicate = self._d['predicate']

        if prefix is None:
            raise ValueError("prefix require")

        return '\n'.join(prefix + line for line in text.splitlines() if predicate(line))

    def dedent(self, text):
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        prefix = self._d['prefix']
        predicate = self._d['predicate']

        return '\n'.join(line.lstrip(prefix) for line in text.splitlines() if predicate(line))

    def shorten(self, text):
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        width = self._d['width']
        start = self._d['start']
        placeholder = self._d['placeholder']
        lenfunc = self._d['lenfunc']

        if width < lenfunc(placeholder):
            raise ValueError("width must be greater than length of the placeholder")

        text = self._d['fillchar'].join(self._split(text))

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

# Interface ----------------------------------------------------------------------------------------

def mono(text, width=70, lenfunc=len):
    return TextWrapper(
        width=width,
        sizefunc=lambda s : (lenfunc(s), 1)
    ).mono(text)

def word(text, width=70, fillchar=' ', separator=None, break_on_hyphens=True, lenfunc=len):
    return TextWrapper(
        width=width,
        fillchar=fillchar,
        separator=separator,
        break_on_hyphens=break_on_hyphens,
        sizefunc=lambda s : (lenfunc(s), 1)
    ).word(text)

def wrap(text, width=70, method='word', fillchar=' ', separator=None, preserve_empty=True,
         break_on_hyphens=True, return_details=False, lenfunc=len):
    wrap_info = TextWrapper(
        width=width,
        method=method,
        fillchar=fillchar,
        separator=separator,
        preserve_empty=preserve_empty,
        break_on_hyphens=break_on_hyphens,
        sizefunc=lambda s : (lenfunc(s), 1),
    )._wrap(text)
    if return_details:
        return wrap_info
    return wrap_info['wrapped']

def align(text, width=70, linegap=0, method='word', alignment='left', fillchar=' ', separator=None,
          preserve_empty=True, use_minimum_width=True, justify_last_line=False,
          break_on_hyphens=True, return_details=False, sizefunc=sizelen):
    align_info = TextWrapper(
        width=width,
        linegap=linegap,
        method=method,
        alignment=alignment,
        fillchar=fillchar,
        separator=separator,
        preserve_empty=preserve_empty,
        use_minimum_width=use_minimum_width,
        justify_last_line=justify_last_line,
        break_on_hyphens=break_on_hyphens,
        sizefunc=sizefunc
    )._align(text)
    if return_details:
        return align_info
    return align_info['aligned']

def fillstr(text, width=70, method='word', alignment='left', fillchar=' ', separator=None,
            preserve_empty=True, use_minimum_width=True, justify_last_line=False,
            break_on_hyphens=True, lenfunc=len):
    return TextWrapper(
        width=width,
        method=method,
        alignment=alignment,
        fillchar=fillchar,
        separator=separator,
        preserve_empty=preserve_empty,
        use_minimum_width=use_minimum_width,
        justify_last_line=justify_last_line,
        break_on_hyphens=break_on_hyphens,
        sizefunc=lambda s : (lenfunc(s), 1)
    ).fillstr(text)

def printwrap(*values, sep=' ', end='\n', wrap=None, file=None, flush=False, width=None,
              default_width=70, use_minimum_width=False, **kwargs):

    text = (' ' if sep is None else sep).join(map(str, values))

    if wrap is None:
        if width is None:
            try:
                width = get_terminal_size().columns
            except:
                width = default_width
        string = fillstr(text, width=width, use_minimum_width=use_minimum_width, **kwargs)
    elif isinstance(wrap, TextWrapper):
        string = wrap.fillstr(text)
    else:
        raise ValueError("invalid wrap argument")

    print(string, end=end, file=file, flush=flush)

def indent(text, prefix, predicate=stripstr):
    return TextWrapper(
        prefix=prefix,
        predicate=predicate
    ).indent(text)

def dedent(text, prefix=None, predicate=stripstr):
    return TextWrapper(
        prefix=prefix,
        predicate=predicate
    ).dedent(text)

def shorten(text, width=70, start=0, fillchar=' ', placeholder='...', separator=None, lenfunc=len):
    return TextWrapper(
        width=width,
        start=start,
        fillchar=fillchar,
        placeholder=placeholder,
        separator=separator,
        sizefunc=lambda s : (lenfunc(s), 1)
    ).shorten(text)