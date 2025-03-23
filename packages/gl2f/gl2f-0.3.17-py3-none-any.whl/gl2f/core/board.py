import os, json
from .local.fs import home

def path():
	return os.path.join(home(), 'pages.json')

def definitions():
	p = path()
	if os.path.isfile(p):
		with open(p) as f:
			return json.load(f)
	return {
		'pages': [
			# blogs
			{
				'id': '271474317252887717',
				'key': 'blogs/girls2',
				'group': 'girls2',
				'page': 'blogs',
			},
			{
				'id': '436708526618837819',
				'key': 'blogs/lovely2',
				'group': 'lovely2',
				'page': 'lovely2blogs',
			},
			{
				'id': '540071536506176315',
				'key': 'blogs/lucky2',
				'group': 'lucky2',
				'page': 'lucky2blogs',
			},
			{
				'id': '920124413225992193',
				'key': 'blogs/staff',
				'page': 'staffdiary',
			},

			# news
			{
				'id': '540067120025699131',
				'key': 'news/family',
				'page': 'familyNews',
			},
			{
				'id': '270441012457899173',
				'key': 'news/girls2',
				'group': 'girls2',
				'page': 'news',
			},
			{
				'id': '415001844964656065',
				'key': 'news/lovely2',
				'group': 'lovely2',
				'page': 'lovely2news',
			},
			{
				'id': '540071356465677115',
				'key': 'news/lucky2',
				'group': 'lucky2',
				'page': 'lucky2news',
			},
			{
				'id': '270810062216233612',
				'key': 'news/mirage2',
				'group': 'mirage2',
				'page': 'mirage2news',
			},

			# radio
			{
				'id': '455630760846558145',
				'key': 'radio/girls2',
				'group': 'girls2',
				'page': 'girls2radio',
			},
			{
				'id': '540071136604455739',
				'key': 'radio/lucky2',
				'group': 'lucky2',
				'page': 'lucky2radio',
			},

			# gtube
			{
				'id': '270809837141492901',
				'key': 'gtube',
				'page': 'gtube',
			},

			# commercial movie
			{
				'id': '504468501197489089',
				'key': 'cm',
				'page': 'commercialmovie',
			},

			{
				'id': '297314731440473169',
				'key': 'others',
				'page': 'others',
			},

			{
				'id': '689409591506633568',
				'key': 'shangrila',
				'page': 'ShangrilaPG',
			},

			{
				'id': '666819802651689824',
				'key': 'brandnewworld/cheer',
				'page': 'FirstLiveCheerForL2',
			},

			{
				'id': '664746725843403713',
				'key': 'brandnewworld/photo',
				'page': 'Lucky2FirstLivePG',
			},

			# daijoubu
			{
				'id': '660050132594590761',
				'key': 'daijoubu/photo',
				'page': '3rdAnnivPG',
			},
			{
				'id': '653506325782725569',
				'key': 'daijoubu/cheer',
				'page': '3rdAnnivCheerForG2',
			},

			{
				'id': '935769953628323842',
				'key': 'wearegirls2thelive',
				'page': '5thAnivPG',
			},

			# CL special live
			{
				'id': '639636551948567355',
				'key': 'cl',
				'page': 'CLsplivepg',
			},

			# fan meeting
			{
				'id': '613606146413953985',
				'key': 'fm/girls2-2022',
				'group': 'girls2',
				'page': 'G2fcmeetingpg',
			},
			{
				'id': '613607790937637825',
				'key': 'fm/lucky2-2022',
				'group': 'lucky2',
				'page': 'L2fcmeetingpg',
			},
			{
				'id': '770515521794737285',
				'key': 'fm/girls2-2023',
				'group': 'girls2',
				'page': 'G2FanMeetingPG2',
			},
			{
				'id': '789417493352416266',
				'key': 'fm/girls2-open',
				'group': 'girls2',
				'page': 'G2OpenFanMeetingPG'
			},

			{
				'id': '750275859142673638',
				'key': 'fm/lucky2-2023',
				'group': 'lucky2',
				'page': 'L2FanMeetingPG2'
			},
			{
				"id": "885485242628964352",
				"key": "fm/lucky2-2024",
				"page": "Lucky2FanMeeting2024PG"
			},

			# enjoy the good days
			{
				'id': '558593359405384641',
				'key': 'enjoythegooddays',
				'group': 'girls2',
				'page': 'EnjoyTheGoodDaysBackstage',
			},

			# famitok
			{
				'id': '550521936032039739',
				'key': 'famitok/girls2',
				'group': 'girls2',
				'page': 'Girls2famitok',
			},
			{
				'id': '550521867736187707',
				'key': 'famitok/lucky2',
				'group': 'lucky2',
				'page': 'Lucky2famitok',
			},

			# lovely2 special live
			{
				'id': '527414639852520385',
				'key': 'lovely2live',
				'page': 'lovely2Live2021Diary',
			},

			# garugaku live
			{
				'id': '499846974107812667',
				'key': 'garugakulive',
				'page': 'garugakuliveDiary',
			},

			# chuwapane
			{
				'id': '357805845389509857',
				'key': 'chuwapane',
				'page': 'chuwapaneDiary',
			},

			# onlinelive
			{
				'id': '449506330521109545',
				'key': 'onlinelive2020',
				'page': 'onlineliveDiary',
			},

			# wallpaper
			{
				'id': '516921408022905897',
				'key': 'wallpaper',
				'page': 'wallpaper'
			},

			# ticket
			{
				'id': '335268051140216033',
				'key': 'ticket',
				'page': 'ticket',
			},

			# history
			{
				'id': '801380069393040517',
				'key': 'history/girls2',
				'page': 'Girls2history',
			},

			# Happy Summer
			{
				'id': '809652098881814530',
				'key': 'happysummer/pg',
				'page': 'HappySummerPG',
			},

			# activate
			{
				'id': '836873836174508033',
				'key': 'activate/pg',
				'page': 'activatePG',
			},

			# not a post found
			# {
			# 	'id': '385773910110503958',
			# 	'key': 'information',
			# 	'page': 'information'
			# },

			{
				'id': '289220886836282449',
				'key': 'pass',
				'page': 'miraclepass'
			},

			{
				'id': '570095770410156859',
				'key': 'checkin',
				'page': 'CheckInPhoto'
			},
		],
		'active': [
			'wearegirls2thelive',
			'blogs/girls2',
			'blogs/lucky2',
			'news/family',
			'radio/girls2',
			'radio/lucky2',
			'gtube',
			'cm',
			'wallpaper',
			'pass',
		]
	}

def map_board_alias(key):
	to_blogs = {'yuzuhaBlog', 'momokaBlog', 'misakiBlog', 'youkaBlog', 'kureaBlog', 'minamiBlog', 'kiraBlog', 'toaBlog', 'ranBlog'}
	if key in to_blogs:
		return 'blogs'
	return key


def get(k, v):
	try:
		pages = definitions()['pages']
		return next(x for x in pages if x[k] == v)
	except StopIteration:
		return None

def save(data):
	with open(path(), 'w', encoding='utf-8') as f:
		f.write(json.dumps(normalize(data), indent=2, ensure_ascii=False))

def is_json_meme_type(t):
	return t.startswith('application/json')

def get_first_list_board_id(components):
	for component in filter(lambda c:'list' in c['hbs'], components):
		return component['attributes']['board-id']
	return None

def add_definition(page_id, key, active=False):
	data = definitions()

	status, content_type, content = fetch_page_data(page_id)
	if not (status and is_json_meme_type(content_type)):
		return None, ['failed to find board data']

	components = content['result']['pageContext']['def']['components']
	i = get_first_list_board_id(components)

	if i is None:
		return None, ['failed to find board id']

	d = {
		'id': i,
		'key': key,
		'page': page_id
	}
	data['pages'] = [p for p in data['pages'] if p['key'] != key]
	data['pages'].append(d)

	reports = [f'added definition: {d}']

	if active:
		data['active'] = list(set(data['active']) | {key})
		reports.append('added to active pages')
	return data, reports

def remove(key):
	data = definitions()
	data['pages'] = [i for i in data['pages'] if i['key'] != key]
	data['active'] = [i for i in data['active'] if i != key]
	return data


def normalize(data):
	data['pages'] = sorted(data['pages'], key=lambda i:i['key'])
	data['active'] = sorted(list(set(data['active']) & {i['key'] for i in data['pages']}))
	return data

def content_url(item):
	page = get('id', item['boardId'])['page']
	content = item['contentId']
	return f'https://girls2-fc.jp/page/{page}/{content}'


def tree():
	from . import member

	keys = [i['key'] for i in definitions()['pages']]

	first = {k.split('/')[0] for k in keys} | {'today'}
	tree = {
		f:{k.split('/')[1] for k in filter(lambda i:i.startswith(f'{f}/'), keys)}
		for f in first
	}

	mem_G2 = member.of_group('girls2').keys()
	mem_L2 = member.of_group('lucky2').keys()
	mem_l2 = member.of_group('lovely2').keys()

	tree['news'] |= {'today'}
	tree['blogs'] |= (mem_G2 | mem_L2 | mem_l2 | {'today'})
	tree['radio'] |= (mem_G2 | mem_L2)

	return tree


def fetch_pages():
	import requests

	size = 99
	page = 1

	results = []
	while True:
		response = requests.get('https://yomo-api.girls2-fc.jp/web/v1/sites/girls2-fc/pages',
			params={
				'size': str(size),
				'page': str(page),
			},
			headers={
		    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
			})

		if not response.ok:
			break

		data = response.json()
		yield from data['list']

		if data['totalCount'] <= size * data['currentPage']:
			return
		page += 1

def fetch_page_data(pageId):
	import requests

	res = requests.get(f'https://girls2-fc.jp/page-data/page/{pageId}/page-data.json',
		headers={
	    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
		})
	if not res.ok:
		return False, None, None

	content_type = res.headers.get('Content-Type')
	if is_json_meme_type(content_type):
		content = res.json()
	else:
		content = str(res.content)
	return True, content_type, content
