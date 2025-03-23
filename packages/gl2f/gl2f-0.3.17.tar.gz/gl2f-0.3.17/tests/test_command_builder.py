import time
import gl2f

class New_Subcommand:
	@staticmethod
	def add_to():
		return 'gl2f', 'new'

	@staticmethod
	def add_args(parser):
		parser.set_defaults(handler = lambda _:'new command')

class Overwright_Subcommand:
	@staticmethod
	def add_to():
		return 'gl2f', 'auth'

	@staticmethod
	def add_args(parser):
		parser.set_defaults(handler = lambda _:'overwritten auth')

class Overwright_Nested_Subcommand:
	@staticmethod
	def add_to():
		return 'gl2f.local', 'serve'

	@staticmethod
	def add_args(parser):
		parser.set_defaults(handler = lambda _:'overwritten local.serve')


def run_command(parser, arg_string, expected):
	args = parser.parse_args(arg_string)
	if hasattr(args, 'handler'):
		ret = args.handler(args)
		return expected == ret
	return False

def has_subcommand(tree, command, subcommand):
	return subcommand in tree[command].choices.keys()


def test_builtin_command_tree():
	parser, tree = gl2f.command_builder.build(gl2f.command_builder.builtin)
	assert {'gl2f', 'gl2f.auth', 'gl2f.config', 'gl2f.local', 'gl2f.pages'} == tree.keys()
	assert {
		'sixel', 'auth', 'cat', 'completion', 'config',
		'dl','local','ls','open', 'pages', 'search',
	} ==  tree['gl2f'].choices.keys()
	assert {'login', 'remove', 'set-token', 'update'} == tree['gl2f.auth'].choices.keys()
	assert {'create', 'path', 'view', 'edit'} == tree['gl2f.config'].choices.keys()
	assert {
		'clear-cache', 'dir', 'export', 'import', 'index', 'install', 'ls', 'open',
		'send-command', 'serve', 'shutdown', 'stat', 'status',
	} == tree['gl2f.local'].choices.keys()
	assert {
		'add-definition', 'remove-definition',
		'add-to-today', 'remove-from-today',
		'show-today',
		'filter-page-data'
	} == tree['gl2f.pages'].choices.keys()


def test_addons():
	registrars = [
		New_Subcommand,
		Overwright_Subcommand,
		Overwright_Nested_Subcommand,
	]
	parser, tree = gl2f.command_builder.build(gl2f.command_builder.builtin + registrars)


	assert has_subcommand(tree, 'gl2f', 'new')
	assert run_command(parser, ['new'], 'new command')

	assert has_subcommand(tree, 'gl2f', 'auth')
	assert run_command(parser, ['auth'], 'overwritten auth')

	assert has_subcommand(tree, 'gl2f.local', 'serve')
	assert run_command(parser, ['local', 'serve'], 'overwritten local.serve')


def time_build(n=1):
	elapsed_times = []
	for _ in range(n):
		t0 = time.time()
		parser, tree = gl2f.command_builder.build(gl2f.command_builder.builtin)
		t1 = time.time()
		elapsed_times.append(t1-t0)
	return elapsed_times

def test_build_time():
	n = 10
	assert sum(time_build(n))/n < 0.02


if __name__ == '__main__':
	print('command tree build time')
	n = 10
	elapsed = time_build(n)
	for t in elapsed:
		print(t)
	print(f'average: {sum(elapsed)/n}')
