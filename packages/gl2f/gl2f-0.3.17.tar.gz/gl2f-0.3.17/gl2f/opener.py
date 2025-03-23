from .core import lister, pretty, util
from .ayame import terminal as term

def open_url(i):
	from .core import board
	util.open_url(board.content_url(i), new=0, autoraise=True)


def subcommand(args):
	items = lister.list_contents(args)
	fm = pretty.from_args(args, items)

	if args.all:
		for i in items:
			fm.print(i)
			open_url(i)
	elif args.pick:
		for i in util.pick(items, args.pick):
			fm.print(i)
			open_url(i)
	else:
		for i in term.selected(items, fm.format):
			open_url(i)

def add_to():
	return 'gl2f', 'open'

def add_args(parser):
	parser.description = 'Open pages in the browser'

	lister.add_args(parser)
	pretty.add_args(parser)
	parser.set_defaults(format='author:title')
	parser.add_argument('-a', '--all', action='store_true',
		help='open all items')
	parser.add_argument('--pick', type=int, nargs='+',
		help='select articles to show')

	parser.set_defaults(handler=subcommand)

def set_compreply():
	return '__gl2f_complete_list_args'
