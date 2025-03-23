import json
from .core import board

def add_def(args):
	if not args.key:
		d = args.page_id.lower()
		args.key = input(f'set a custom key? (defualt={d})') or d

	if not args.activate:
		args.activate = 'y' == input('set as today\'s page? (y/N)').lower()

	data, reports = board.add_definition(args.page_id, args.key, args.activate)
	if data:
		board.save(data)
		for r in reports:
			print(r)
		print('update completion with [eval "$(gl2f completion)"]')
	else:
		for r in reports:
			print(r)

def remove_def(key):
	board.save(board.remove(key))

def add_today(key):
	data = board.definitions()
	data['active'].append(key)
	board.save(data)

def remove_today(key):
	data = board.definitions()
	data['active'].remove(key)
	board.save(data)

def show_today():
	print(' '.join(sorted(board.definitions()['active'])))

def merge_page_data(page):
	pageId = page['pageId']
	status, content_type, content = board.fetch_page_data(pageId)
	page['data'] = {
		'status': status,
		'type': content_type,
		'content': content,
	}
	return page

def all_page_data():
	from concurrent.futures import ThreadPoolExecutor
	all_pages = board.fetch_pages()
	with ThreadPoolExecutor() as e:
		yield from e.map(merge_page_data, all_pages)

def get_content(i):
	data = i['data']
	if (not data['status']) or (not board.is_json_meme_type(data['type'])):
		return None
	return data['content']

def has_content(l):
	for i in l:
		content = get_content(i)
		if content:
			yield i, content

def with_components(i, components):
	i['data']['content']['result']['pageContext']['def']['components'] = components
	return i


def list_type_filter(l):
	return filter(lambda i:i.get('type') == 'list', l)

def list_board_filter(l):
	l = list_type_filter(l)
	for i, content in has_content(l):
		components = content['result']['pageContext']['def']['components']
		components = list(filter(lambda c: 'list' in c['hbs'], components))
		if components:
			yield with_components(i, components)

def existing_ids_filter(l, reverse):
	definitions = board.definitions()
	for i, content in has_content(l):
		existing = {p['page'] for p in definitions['pages']}
		path = board.map_board_alias(content['path'].split('/')[-1])
		if reverse:
			if path not in existing:
				yield i
		else:
			if path in existing:
				yield i

		# components = content['result']['pageContext']['def']['components']
		# existing = [p['id'] for p in definitions['pages']]

		# if reverse:
		# 	d = lambda c: c['attributes'].get('board-id') not in existing
		# else:
		# 	d = lambda c: c['attributes'].get('board-id') in existing

		# components = list(filter(d, components))
		# if components:
		# 	yield with_components(i, components)

def board_id_filter(l, boardIds):
	for i, content in has_content(l):
		components = content['result']['pageContext']['def']['components']
		if any(c['attributes'].get('board-id') in boardIds for c in components):
			yield i

def apply_filters(filters, load=None, dump=None):
	if load:
		with open(load, encoding='utf-8') as f:
			page_data = json.load(f)
	else:
		page_data = all_page_data()

	if dump:
		with open(dump, mode='w', encoding='utf-8') as f:
			f.write(json.dumps(list(page_data), indent=2, ensure_ascii=False))

	filtered = page_data
	for f, kwargs in filters:
		filtered = f(filtered, **kwargs)

	return filtered


def extract(i):
	paths = [
		['label'],
		['type'],
		['pageId'],
		['data', 'type'],
		['data', 'content', 'path'],
		['data', 'content', 'result', 'pageContext', 'def', 'components'],
	]

	ret = {}
	for keys in paths:
		src = i
		for key in keys:
			try:
				src = src[key]
			except:
				print(f'key not found: \'{key}\' of {keys}')
				ret['.'.join(keys)] = None
				break
		else:
			ret['.'.join(keys)] = src
	return ret

def filter_page_data(args):
	filters = []
	for f in args.filter:
		if f == 'list-board':
			filters.append((list_board_filter, {}))
		elif f == 'existing':
			filters.append((existing_ids_filter, {'reverse': False}))
		elif f == 'not-existing':
			filters.append((existing_ids_filter, {'reverse': True}))
		elif f.startswith('board-id'):
			filters.append((board_id_filter, {'boardIds': f.split(':')[1:]}))

	filtered = apply_filters(filters, args.load, args.dump)
	for i in filtered:
		if not args.raw:
			i = extract(i)
		print(json.dumps(i, indent=2, ensure_ascii=False))
		print()


def add_to():
	return 'gl2f', 'pages'

def add_args(parser):
	parser.description = 'Manage page definitions'

	sub = parser.add_subparsers()

	p = sub.add_parser('add-definition', description='Add a page definition')
	p.add_argument('page_id', type=str)
	p.add_argument('--key', type=str, help='set page name used as command argument')
	p.add_argument('--activate', action='store_true', help='set as today page')
	p.set_defaults(handler=add_def)

	p = sub.add_parser('filter-page-data', description='Fetch page data and apply filters')
	p.add_argument('--load', type=str, help='Load local data')
	p.add_argument('--dump', type=str, nargs='?', const='./page-data-cache.json', help='Save page data')
	p.add_argument('-f', '--filter', type=str, nargs='*', default=['list-board', 'not-existing'], help='Add filters')
	p.add_argument('--no-filter', dest='filter',action='store_const', const=[], help='Do not apply any filter')
	p.add_argument('--raw', action='store_true', help='Print all properties of results')
	p.set_defaults(handler=filter_page_data)

	p = sub.add_parser('remove-definition', description='Remove a page definition')
	p.add_argument('key', type=str)
	p.set_defaults(handler=lambda a:remove_def(a.key))

	p = sub.add_parser('add-to-today', description='Add to today pages')
	p.add_argument('page')
	p.set_defaults(handler=lambda a:add_today(a.page))

	p = sub.add_parser('remove-from-today', description='Remove from today pages')
	p.add_argument('page')
	p.set_defaults(handler=lambda a:remove_today(a.page))

	sub.add_parser('show-today', description='Show today pages').set_defaults(handler=lambda _:show_today())

	return sub

def set_compreplies():
	today = ' '.join(board.definitions()['active'])
	return {
		'remove-definition': '__gl2f_complete_list_args',
		'add-to-today': '__gl2f_complete_list_args',
		'remove-from-today': f'COMPREPLY=( $(compgen -W "{today}" -- $cur) )'
	}
