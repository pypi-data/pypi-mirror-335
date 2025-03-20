from argparse import ArgumentParser
from os import name, get_terminal_size
from txtwrap import version, printwrap, indent, dedent, shorten

if name == 'nt':
    pyname = 'python|py'
elif name == 'posix':
    pyname = 'python3'
else:
    pyname = 'python'

parser = ArgumentParser(
    prog='txtwrap',
    description='Command-line tool for wrapping, aligning, or shortening text.',
    epilog=f'for example: {pyname} -m txtwrap "Lorem ipsum odor amet, consectetuer adipiscing '
            'elit." -w 20 -m word -a center'
)

parser.add_argument(
    'text',
    type=str,
    help='Text to be wrapped, aligned, or shorted'
)

parser.add_argument(
    '-v', '--version',
    action='version',
    version=version,
    help='Show the version of the txtwrap'
)

parser.add_argument(
    '-f', '--fillchar',
    type=str,
    default=' ',
    metavar='<str (1 character)>',
    help='Fill character (default: " ")'
)

parser.add_argument(
    '-w', '--width',
    type=int,
    default=None,
    metavar='<int>',
    help='Width of the text wrapping (default: current width terminal or 70)'
)

parser.add_argument(
    '-m', '--method',
    type=str,
    choices={'word', 'mono', 'indent', 'dedent', 'shorten'},
    default='word',
    metavar='{word|mono|indent|dedent|shorten}',
    help='Method to be applied to the text (default: "word")'
)

parser.add_argument(
    '-a', '--alignment',
    type=str,
    choices={'left', 'center', 'right', 'fill'},
    default='left',
    metavar='{left|center|right|fill}',
    help='Alignment of the text (default: "left")'
)

parser.add_argument(
    '-n', '--neglect-empty',
    action='store_false',
    help='Neglect empty lines in the text'
)

parser.add_argument(
    '-x', '--prefix',
    type=str,
    default=None,
    metavar='<str>',
    help='Prefix to be added (indent) or remove (dedent) to the text'
)

parser.add_argument(
    '-s', '--start',
    type=int,
    default=0,
    metavar='<int>',
    help='start index of the text to be shorten (default: 0)'
)

parser.add_argument(
    '-p', '--placeholder',
    type=str,
    default='...',
    metavar='<str>',
    help='Placeholder to be used when shortening the text (default: "...")'
)

parser.add_argument(
    '-b', '--not-break-on-hyphens',
    action='store_false',
    help="Doesn't break on hyphens"
)

parser.add_argument(
    '-j', '--justify-last-line',
    action='store_true',
    help='Justify the last line of the text'
)

parser.add_argument(
    '-r', '--no-strip',
    action='store_false',
    help='Do not strip the space in the text'
)

args = parser.parse_args()

if args.method == 'indent':
    if args.prefix is None:
        raise ValueError('The prefix (-x, --prefix) is required for the indent method')
    print(indent(args.text, args.prefix))
elif args.method == 'dedent':
    print(dedent(args.text, args.prefix))
elif args.method == 'shorten':
    if args.width is None:
        try:
            args.width = get_terminal_size().columns
        except:
            args.width = 70
    print(
        shorten(
            args.text,
            args.width,
            args.start,
            placeholder=args.placeholder,
            strip_space=args.no_strip
        )
    )
else:
    printwrap(
        args.text,
        fillchar=args.fillchar,
        width=args.width,
        method=args.method,
        alignment=args.alignment,
        preserve_empty=args.neglect_empty,
        break_on_hyphens=args.not_break_on_hyphens,
        justify_last_line=args.justify_last_line
    )