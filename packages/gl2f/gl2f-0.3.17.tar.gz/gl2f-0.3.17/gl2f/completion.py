from .core import local, board, pretty, util
from . import command_builder

def add_no_desc(words):
	return {(i, None) for i in words}

def generate_compreply_nohelp(words, cur='$cur', prefix=None):
	w = ' '.join(w for w, _ in words)
	p = '' if prefix == None else f'-P "{prefix}"'
	return f'''COMPREPLY=( $(compgen -W $'{w}' {p} -- "{cur}") )'''

def generate_compreply(words, cur='$cur', prefix=None):
	width = max(len(w) for w, _ in words)
	w = '\\n'.join(f'{w.ljust(width)} ({d})' if d else w for w, d in words)
	p = '' if prefix == None else f'-P "{prefix}"'
	return f'''local OLDIFS="$IFS"
local IFS=$'\\n'
COMPREPLY=( $(compgen -W $'{w}' {p} -- "{cur}") )
IFS="$OLDIFS"
if [[ ${{#COMPREPLY[*]}} -eq 1 ]]; then
  COMPREPLY=( ${{COMPREPLY[0]%% *}} )
fi'''

def indent(string, level):
	return '\n'.join(f'{"  "*level}{line}' for line in string.splitlines())

def if_else(condition, _if, _else=None):
	if _else:
		return f'''if [[ {condition} ]]; then
{indent(_if, 1)}
else
{indent(_else, 1)}
fi'''
	else:
		return f'''if [[ {condition} ]]; then
{indent(_if, 1)}
fi'''

def make_case(key, process):
	return f'''{key})
{indent(process, 1)}
  ;;
'''


def generate():
	source = util.read_all_text(local.fs.package_data('completion.bash'))

	boards = board.tree()
	parser, commands = command_builder.build(command_builder.builtin + command_builder.get_addon_registrars())
	fm = pretty.Formatter()

	return source.replace('## REPLACE_PAGES_FIRST',
		generate_compreply(add_no_desc(k + ('/' if len(v)>0 else '') for k, v in boards.items()))
	).replace('## REPLACE_PAGES_SECOND',
		indent(''.join(make_case(k, generate_compreply(add_no_desc(v), '$realcur', prefix='$prefix/'))
		for k, v in sorted(boards.items()) if len(v)>0), 3)
	).replace('## REPLACE_FORMAT',
		generate_compreply(add_no_desc(fm.functions.keys()), '$realcur')
	).replace('## REPLACE_COMMAND_TREE', indent(gen_tree('gl2f', parser, commands), 1))

def prepend_option_completion(parser, body):
	return if_else('$cur == -*',
		generate_compreply(sum(([(i, a.help.replace('\'', '\\\'') if a.help else None) for i in a.option_strings] for a in parser._actions), [])),
		body)

def gen_tree(current_parent, parent_parser, tree):
	commands = command_builder.builtin + command_builder.get_addon_registrars()

	# cases (1 or 2) and 3 are supposed to be exclusive
	cases = []
	for command, (parent, name) in filter(lambda t:t[1][0] == current_parent, zip(commands, (c.add_to() for c in commands))):
		current_name = f'{parent}.{name}'
		current_parser = tree[parent].choices[name]

		if current_name in tree.keys():
			# 1 an explicitly registered sub-parser
			cases.append(make_case(name, gen_tree(current_name, current_parser, tree)))

		else:
			# 2 an explicitly registered leaf
			choice_cases = [make_case(' | '.join(a.option_strings), generate_compreply(add_no_desc(a.choices))) for a in current_parser._actions if a.choices]
			custom_reply = command.set_compreply() if hasattr(command, 'set_compreply') else ''

			if choice_cases:
				if custom_reply:
					choice_cases.append(make_case('*', custom_reply))
				body = f'case $prev in\n{indent("".join(choice_cases), 1)}\nesac'
			else:
				body = custom_reply

			cases.append(make_case(name, prepend_option_completion(current_parser, body)))

	if not any(k.startswith(f'{current_parent}.') for k in tree.keys()):
		# 3 leaves in registered sub-parsers that cannot be found in commands
		command = next(c for c in commands if current_parent == '.'.join(c.add_to()))
		custom_replies = command.set_compreplies() if hasattr(command, 'set_compreplies') else {}
		cases += [make_case(k, prepend_option_completion(v, custom_replies.get(k))) for k, v in tree[current_parent].choices.items()]

	reply = prepend_option_completion(parent_parser, generate_compreply({(k, v.description) for k, v in tree[current_parent].choices.items()}))
	if cases:
		depth = current_parent.count('.') + 1
		return if_else(f'$cword == {depth}', reply, f'case ${{words[{depth}]}} in\n{indent("".join(cases), 1)}\nesac')
	else:
		return reply


def add_to():
	return 'gl2f', 'completion'

def add_args(parser):
	parser.set_defaults(handler=lambda _:print(generate()))
	parser.description = 'Generate bash completion'

def set_compreply():
	return ''
