from . import command_builder

def main():
	parser, _ = command_builder.build(command_builder.builtin + command_builder.get_addon_registrars())
	args = parser.parse_args()
	if hasattr(args, 'handler'):
		args.handler(args)

if __name__ == '__main__':
	main()
