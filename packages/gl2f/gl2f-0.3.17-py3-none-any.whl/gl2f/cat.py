from .core import lister, pretty, article, util
from .ayame import terminal as term

def cat(i, args):
	from .dl import save

	if args.dl:
		save(i, args)
	fm = pretty.Formatter()
	fm.print(i, encoding=args.encoding)
	for s in article.lines(i, args.style, args.sixel, args.max_size):
		term.write_with_encoding(s, encoding=args.encoding, errors='ignore')
	term.write_with_encoding('\n', encoding=args.encoding)


def subcommand(args):
	args.max_size = (args.width, args.height) if (args.width or args.height) else None

	if args.board.startswith('https'):
		cat(lister.fetch_content(args.board, dump=args.dump), args)
		return

	items = lister.list_contents(args)

	if args.all:
		for i in items:
			cat(i, args)
	elif args.pick:
		for i in util.pick(items, args.pick):
			cat(i, args)
	else:
		fm = pretty.from_args(args, items)
		for i in term.selected(items, fm.format):
			cat(i, args)

def add_to():
	return 'gl2f', 'cat'

def add_args(parser):
	parser.description = 'Display articles'

	lister.add_args(parser)
	pretty.add_args(parser)
	parser.set_defaults(format='author:title')

	parser.add_argument('--encoding')

	parser.add_argument('--style', type=str, choices={'full', 'compact', 'compressed', 'plain'}, default='compact')
	parser.add_argument('--no-image', dest='sixel', action='store_false',
		help='not use sixel image')
	parser.add_argument('-a', '--all', action='store_true',
		help='preview all items')
	parser.add_argument('--pick', type=int, nargs='+',
		help='select articles to show')
	parser.add_argument('--dl', action='store_true',
		help='also downloads the article')
	parser.add_argument('-W', '--width', type=int,
		help='set max image width')
	parser.add_argument('-H', '--height', type=int,
		help='set max image height')

	# options from dl
	parser.add_argument('--stream', action='store_true',
		help='save video files as stream')
	parser.add_argument('--skip', action='store_true',
		help='not actually download video files')
	parser.add_argument('-F', '--force', action='store_true',
		help='force download to overwrite existing files')
	parser.add_argument('-o', type=str, default='',
		help='output path')

	parser.set_defaults(handler=subcommand)


def set_compreply():
	return '__gl2f_complete_list_args'
