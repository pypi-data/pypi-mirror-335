from .core import lister, pretty

def subcommand(args):
	items = lister.list_contents(args)

	fm = pretty.from_args(args, items)

	for i in items:
		fm.print(i, encoding=args.encoding)

def add_to():
	return 'gl2f', 'ls'

def add_args(parser):
	parser.description = 'List pages'

	lister.add_args(parser)
	pretty.add_args(parser)
	parser.set_defaults(handler=subcommand)
	parser.add_argument('--encoding')

def set_compreply():
	return '__gl2f_complete_list_args'
