from .core import auth

def set_token(token=None):
	if token == None:
		token = input('enter token:')

	if auth.update(token):
		print('success')
		auth.save(token)


def update_cli():
	before = auth.load()
	if not before:
		return
	after = auth.update(before)

	if after == '':
		pass
	elif before == after:
		print('up to date')
	else:
		print('token updated')


def login(email, password):
	if not email:
		email = input('email: ')

	if not password:
		password = input('password: ')

	if auth.login(email, password):
		print('success')


def add_to():
	return 'gl2f', 'auth'

def add_args(parser):
	parser.description = 'Manage authentication for GL2 family'
	sub = parser.add_subparsers()

	p = sub.add_parser('login', description='Login to GL2 family')
	p.add_argument('-u', '--email', type=str, default=None)
	p.add_argument('-p', '--password', type=str, default=None)
	p.set_defaults(handler=lambda args: login(args.email, args.password))

	sub.add_parser('remove', description='Remove authorization token').set_defaults(handler=lambda _:auth.remove())

	p = sub.add_parser('set-token', description='Set authorization token manually')
	p.add_argument('token', nargs='?', type=str)
	p.set_defaults(handler=lambda args:set_token(args.token))

	sub.add_parser('update', description='Update authentication').set_defaults(handler=lambda _:update_cli())

	return sub

def set_compreplies():
	return {}
