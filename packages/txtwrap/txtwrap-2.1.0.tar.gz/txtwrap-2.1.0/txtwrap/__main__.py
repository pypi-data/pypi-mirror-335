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
    epilog='for example: {} -m txtwrap "Lorem ipsum odor amet, consectetuer adipiscing '
           'elit." -w 20 -m word -a center'.format(pyname)
)

parser.add_argument(
    'text',
    type=str,
    help='Target text'
)

parser.add_argument(
    '-v', '--version',
    action='version',
    version=version,
    help='Show the version of the txtwrap'
)

parser.add_argument(
    '-w', '--width',
    type=int,
    default=None,
    metavar='<int>',
    help='Width of the text wrapping (default: current width terminal or 70)'
)

parser.add_argument(
    '-s', '--start',
    type=int,
    default=0,
    metavar='<int>',
    help='start index of the text to be shorten (default: 0)'
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
    choices={'left', 'center', 'right', 'fill', 'fill-left', 'fill-center', 'fill-right'},
    default='left',
    metavar='{left|center|right|fill|fill-left|fill-center|fill-right}',
    help='Alignment of the text (default: "left")'
)

parser.add_argument(
    '-f', '--fillchar',
    type=str,
    default=' ',
    metavar='<str>',
    help='Fill character (default: " ")'
)

parser.add_argument(
    '-p', '--placeholder',
    type=str,
    default='...',
    metavar='<str>',
    help='Placeholder to be used when shortening the text (default: "...")'
)

parser.add_argument(
    '-x', '--prefix',
    type=str,
    default=None,
    metavar='<str>',
    help='Prefix to be added (indent) or remove (dedent) to the text'
)

parser.add_argument(
    '-r', '--separator',
    type=str,
    default=None,
    metavar='<str>',
    help='The separator used between words'
)

parser.add_argument(
    '-n', '--neglect-empty',
    action='store_false',
    help='Neglect empty lines in the text'
)

parser.add_argument(
    '-i', '--use-minimum-width',
    action='store_true',
    help='Whether to use the minimum detected width'
)

parser.add_argument(
    '-j', '--justify-last-line',
    action='store_true',
    help='Whether to adjust the alignment of the last line'
)

parser.add_argument(
    '-b', '--not-break-on-hyphens',
    action='store_false',
    help="Doesn't break on hyphens"
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

    print(shorten(args.text, args.width, args.start, args.fillchar, args.placeholder,
                  args.separator))

else:
    printwrap(
        args.text,
        width=args.width,
        method=args.method,
        alignment=args.alignment,
        fillchar=args.fillchar,
        separator=args.separator,
        preserve_empty=args.neglect_empty,
        use_minimum_width=args.use_minimum_width,
        justify_last_line=args.justify_last_line,
        break_on_hyphens=args.not_break_on_hyphens
    )