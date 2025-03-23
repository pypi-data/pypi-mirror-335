# This stub files supports in Python 3.9+

from typing import Callable, Dict, IO, List, Literal, Optional, Set, SupportsIndex, Tuple, Union

# Identities ---------------------------------------------------------------------------------------

__version__: str
__author__: str
__license__: str

# Constants ----------------------------------------------------------------------------------------

LOREM_IPSUM_WORDS: str
LOREM_IPSUM_SENTENCES: str
LOREM_IPSUM_PARAGRAPHS: str

# Wrapper ------------------------------------------------------------------------------------------

class TextWrapper:

    def __init__(

        self,
        width: Union[int, float] = 70,
        start: SupportsIndex = 0,
        linegap: Union[int, float] = 0,
        method: Literal['mono', 'word'] = 'word',
        alignment: Literal['left', 'center', 'right', 'fill',
                           'fill-left', 'fill-center', 'fill-right'] = 'left',
        fillchar: str = ' ',
        placeholder: str = '...',
        prefix: Optional[str] = None,
        separator: Optional[str] = None,
        preserve_empty: bool = True,
        use_minimum_width: bool = True,
        justify_last_line: bool = False,
        break_on_hyphens: bool = True,
        sizefunc: Callable[[str], Tuple[Union[int, float],
                                        Union[int, float]]] = lambda s : (len(s), 1),
        predicate: Callable[[str], bool] = lambda line: line.strip()

    ) -> None: ...

    def __copy__(self) -> 'TextWrapper': ...
    def __deepcopy__(self, memo: dict) -> 'TextWrapper': ...

    # Properties -----------------------------------------------------------------------------------

    @property
    def width(self) -> Union[int, float]: ...
    @property
    def start(self) -> SupportsIndex: ...
    @property
    def linegap(self) -> Union[int, float]: ...
    @property
    def method(self) -> Literal['mono', 'word']: ...
    @property
    def alignment(self) -> Literal['left', 'center', 'right', 'fill',
                                   'fill-left', 'fill-center', 'fill-right']: ...
    @property
    def fillchar(self) -> str: ...
    @property
    def placeholder(self) -> str: ...
    @property
    def prefix(self) -> Union[str, None]: ...
    @property
    def separator(self) -> Union[str, None]: ...
    @property
    def preserve_empty(self) -> bool: ...
    @property
    def use_minimum_width(self) -> bool: ...
    @property
    def justify_last_line(self) -> bool: ...
    @property
    def break_on_hyphens(self) -> bool: ...
    @property
    def sizefunc(self) -> Callable[[str], Tuple[Union[int, float], Union[int, float]]]: ...
    @property
    def predicate(self) -> Callable[[str], bool]: ...

    # Setter ---------------------------------------------------------------------------------------

    @width.setter
    def width(self, new: Union[int, float]) -> None: ...
    @start.setter
    def start(self, new: SupportsIndex) -> None: ...
    @linegap.setter
    def linegap(self, new: Union[int, float]) -> None: ...
    @method.setter
    def method(self, new: Literal['mono', 'word']) -> None: ...
    @alignment.setter
    def alignment(self, new: Literal['left', 'center', 'right', 'fill',
                                     'fill-left', 'fill-center', 'fill-right']) -> None: ...
    @fillchar.setter
    def fillchar(self, new: str) -> None: ...
    @placeholder.setter
    def placeholder(self, new: str) -> None: ...
    @prefix.setter
    def prefix(self, new: Optional[str]) -> None: ...
    @separator.setter
    def separator(self, new: Optional[str]) -> None: ...
    @preserve_empty.setter
    def preserve_empty(self, new: bool) -> None: ...
    @use_minimum_width.setter
    def use_minimum_width(self, new: bool) -> None: ...
    @justify_last_line.setter
    def justify_last_line(self, new: bool) -> None: ...
    @break_on_hyphens.setter
    def break_on_hyphens(self, new: bool) -> None: ...
    @sizefunc.setter
    def sizefunc(self, new: Callable[[str], Tuple[Union[int, float],
                                                  Union[int, float]]]) -> None: ...
    @predicate.setter
    def predicate(self, new: Callable[[str], bool]) -> None: ...

    # Methods --------------------------------------------------------------------------------------

    def _wrap(self, text: str) -> Dict[Literal['wrapped', 'indiced'], Union[List[str],
                                                                            Set[int]]]: ...
    def _align(self, text: str) -> Dict[Literal['aligned',
                                                'wrapped',
                                                'indiced',
                                                'size'], Union[List[Tuple[Union[int, float],
                                                                          Union[int, float],
                                                                          str]],
                                                               List[str],
                                                               Set[int],
                                                               Tuple[Union[int, float],
                                                                     Union[int, float]]]]: ...
    def copy(self) -> 'TextWrapper': ...
    def mono(self, text: str) -> List[str]: ...
    def word(self, text: str) -> List[str]: ...
    def wrap(self, text: str) -> List[str]: ...
    def align(self, text: str) -> List[Tuple[Union[int, float], Union[int, float], str]]: ...
    def fillstr(self, text: str) -> str: ...
    def indent(self, text: str) -> str: ...
    def dedent(self, text: str) -> str: ...
    def shorten(self, text: str) -> str: ...

# Interfaces ---------------------------------------------------------------------------------------

def mono(
    text: str,
    width: Union[int, float] = 70,
    lenfunc: Callable[[str], Union[int, float]] = len
) -> List[str]: ...

def word(
    text: str,
    width: Union[int, float] = 70,
    fillchar: str = ' ',
    separator: Optional[str] = None,
    break_on_hyphens: bool = True,
    lenfunc: Callable[[str], Union[int, float]] = len,
) -> List[str]: ...

def wrap(
    text: str,
    width: Union[int, float] = 70,
    method: Literal['mono', 'word'] = 'word',
    fillchar: str = ' ',
    separator: Optional[str] = None,
    preserve_empty: bool = True,
    break_on_hyphens: bool = True,
    return_details: bool = False,
    lenfunc: Callable[[str], Union[int, float]] = len,
) -> Union[List[str],
           Dict[Literal['wrapped', 'indiced'], Union[List[str], Set[int]]]]: ...

def align(
    text: str,
    width: Union[int, float] = 70,
    linegap: Union[int, float] = 0,
    method: Literal['mono', 'word'] = 'word',
    alignment: Literal['left', 'center', 'right', 'fill',
                       'fill-left', 'fill-center', 'fill-right'] = 'left',
    fillchar: str = ' ',
    separator: Optional[str] = None,
    preserve_empty: bool = True,
    use_minimum_width: bool = True,
    justify_last_line: bool = False,
    break_on_hyphens: bool = True,
    return_details: bool = False,
    sizefunc: Callable[[str], Tuple[Union[int, float], Union[int, float]]] = lambda s : (len(s), 1)
) -> Union[List[Tuple[Union[int, float], Union[int, float], str]],
           Dict[Literal['aligned',
                        'wrapped',
                        'indiced',
                        'size'], Union[List[Tuple[Union[int, float], Union[int, float], str]],
                                       List[str],
                                       Set[int],
                                       Tuple[Union[int, float], Union[int, float]]]]]: ...

def fillstr(
    text: str,
    width: int = 70,
    method: Literal['mono', 'word'] = 'word',
    alignment: Literal['left', 'center', 'right', 'fill',
                       'fill-left', 'fill-center', 'fill-right'] = 'left',
    fillchar: str = ' ',
    separator: Optional[str] = None,
    preserve_empty: bool = True,
    use_minimum_width: bool = True,
    justify_last_line: bool = False,
    break_on_hyphens: bool = True,
    lenfunc: Callable[[str], int] = len
) -> str: ...

def printwrap(
    *values: object,
    sep: Optional[str] = ' ',
    end: Optional[str] = '\n',
    wrap: Optional[TextWrapper] = None,
    file: Optional[IO] = None,
    flush: bool = False,
    width: Optional[int] = None,
    default_width: int = 70,
    use_minimum_width: bool = False,
    **kwargs
) -> None: ...

def indent(
    text: str,
    prefix: str,
    predicate: Callable[[str], bool] = lambda line: line.strip()
) -> str: ...

def dedent(
    text: str,
    prefix: Optional[str] = None,
    predicate: Callable[[str], bool] = lambda line: line.strip()
) -> str: ...

def shorten(
    text: str,
    width: Union[int, float] = 70,
    start: SupportsIndex = 0,
    fillchar: str = ' ',
    placeholder: str = '...',
    separator: Optional[str] = None,
    lenfunc: Callable[[str], Union[int, float]] = len
) -> str: ...