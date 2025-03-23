import os
from . import util

class Warn_once:
	printed = set()

	@staticmethod
	def print(message):
		from ..ayame import terminal as term
		if message not in Warn_once.printed:
			print(term.mod(message, term.color('yellow'), term.inv(), term.bold()))
			Warn_once.printed.add(message)

def filepath():
	from . import local
	return os.path.join(local.fs.home(), 'auth')

def file():
	path = filepath()
	if os.path.exists(path):
		return path
	else:
		Warn_once.print('authorization info not found')
		return None

def load():
	if path := file():
		with open(path) as f:
			return f.readline().rstrip('\n')
	else:
		return ''


def save(token):
	util.write_all_text(filepath(), token)

def remove():
	path = file()
	if path	and 'n' != input(f'removing {path} (Y/n)').lower():
		os.remove(path)


first_unauthorized = True
def verify(au):
	import requests
	res = requests.get(
		'https://yomo-api.girls2-fc.jp/web/v1/auth/token/verify',
		cookies={},
		headers={
	    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
	    'origin': 'https://girls2-fc.jp',
	    'x-authorization': au,
	    'x-from': 'https://girls2-fc.jp/',
	    'x-root-origin': 'https://girls2-fc.jp',
		}).json()
	if res['success']:
		return res['token']
	else:
		Warn_once.print('unauthorized')
		return None

def update(au):
	token = verify(au)
	if not token:
		return ''

	if token != au:
		save(token)
	return token


def login(email, password):
	import requests
	res = requests.post('https://yomo-api.girls2-fc.jp/web/v1/auth/email/signin',
		headers={
			'Accept': 'application/json',
			'Content-Type': 'application/json',
			'Referer': 'https://girls2-fc.jp/',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
			'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
			'sec-ch-ua-mobile': '?0',
			'sec-ch-ua-platform': '"Windows"',
	    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
			'x-from': 'https://girls2-fc.jp/',
			'x-platform-id': 'web',
			'x-root-origin': 'https://girls2-fc.jp',
		},
		json={
		'email': email,
		'password': password,
		})

	if not res.ok:
		print('fail:', res.reason)
		return None

	token = verify(res.json()['token'])
	if token:
		save(token)
	return token
