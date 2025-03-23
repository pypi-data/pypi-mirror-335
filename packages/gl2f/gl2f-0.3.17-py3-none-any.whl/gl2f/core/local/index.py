import os, json
from .. import util
from . import fs, content

def get_path():
	return os.path.join(fs.refdir_untouch('contents'), 'index.json')

def load():
	path = get_path()
	if not os.path.isfile(path):
		return {}
	return util.read_json(path)

def build_body(item):
	from .. import article

	i = item['contentId']
	media_list = fs.listdir(f'contents/{i}')

	def up(match):
		m, t = match.groups()
		try:
			p = next(p for p in media_list if p.startswith(m))
		except:
			return ''

		if t == 'image':
			return f'<img src=../contents/{i}/{p}></img>'
		elif t == 'video':
			return f'<video controls autoplay muted loop src=../contents/{i}/{p}></video>'
		else:
			return ''

	return article.ptn_media.sub(up, item['values']['body'])

def create_value(i):
	from .. import board, article

	item = content.load(i)
	media = [i for i, _ in article.ptn_media.findall(item['values']['body'])]
	return {
		'title': item['values']['title'],
		'board': board.get('id', item['boardId'])['page'],
		'author': item.get('category', {'name':''})['name'],
		'date': item['openingAt'],
		'media': [''.join(x) for x in sorted(
			filter(lambda x:x[0] in media,
				(os.path.splitext(i) for i in fs.listdir(os.path.join('contents', i)))
			),
			key=lambda x:media.index(x[0])
		)],
		'expired': item.get('closingAt', None),
		'body': build_body(item)
	}

def create_table(contents):
	from concurrent.futures import ThreadPoolExecutor
	with ThreadPoolExecutor() as e:
		values = e.map(create_value, contents)
	return {k:v for k, v in zip(contents, values)}

def main(full=False):
	out = get_path()
	if not os.path.isdir(os.path.split(out)[0]):
		return 'no contents'

	if full:
		table = create_table(content.get_ids())
	else:
		prev = load()
		diff = set(content.get_ids()).difference(prev.keys())
		table = prev | create_table(diff)

	util.write_all_text(out, json.dumps(table, separators=(',', ':'), ensure_ascii=False))
	return f'updated index.: {out}'
