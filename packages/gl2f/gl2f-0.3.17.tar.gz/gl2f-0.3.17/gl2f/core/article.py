import re, html, os
from . import local
from ..ayame import sixel, terminal as term
from . import auth
from .config import data as config
from .board import content_url

ptn_paragraph = re.compile(r'<p.*?>(?P<paragraph>.*?)</p>')
ptn_media = re.compile(r'<fns-media.*?media-id="(?P<id>.+?)".*?type="(?P<type>.+?)".*?></fns-media>')
ptn_link = re.compile(r'<a href="(?P<url>.+?)".*?>(?P<text>.+?)</a>')
ptn_strong = re.compile(r'<strong.*?>(?P<content>.*?)</strong>')
ptn_span = re.compile(r'<span.*?>(?P<content>.*?)</span>')
ptn_http = re.compile(r'(?P<url>https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*))')
ptn_ignore = re.compile(r'￼|&nbsp;|<br.*?>')
ptn_hashtag = re.compile(r'(?P<tag>#[^\s.,#]+)')

def rep_none(p):
	return ptn_media.sub('', p)

def rep_type(p):
	return ptn_media.sub(term.mod(r'[\g<type>]', term.dim()), p)

def rep_type_id(p):
	return ptn_media.sub(term.mod(r'[\g<type>](\g<id>)', term.dim()), p)

def rep_type_url(p, boardId, contentId, xauth):
	ma = ptn_media.search(p)
	if not ma:
		return p
	i, t = ma.group('id', 'type')
	meta, _ = dl_medium(boardId, contentId, i, head=True, xauth=xauth)
	url = meta['originalUrl'] if t == 'video' else meta['accessUrl']
	return term.mod(f'[{t}] {url}', term.dim())

def rep_sixel(p, boardId, contentId, max_size, xauth):
	from io import BytesIO
	from PIL import Image

	match = ptn_media.search(p)
	if not match:
		return p
	i, t = match.group('id', 'type')

	if file:=local.content.search_image(i, contentId):
		image = Image.open(file)
	else:
		_, data = dl_medium(boardId, contentId, i, video_url_key='thumbnailAccessUrl', xauth=xauth)
		if data.ok:
			with open(os.path.join(local.fs.refdir('cache'), i), 'wb') as f:
				f.write(data.content)
		image = Image.open(BytesIO(data.content))

	image = sixel.limit(image, max_size)
	if t == 'video':
		return f'{sixel.to_sixel(image)}\n{rep_type_url(p, boardId, contentId, xauth)}'
	else:
		return sixel.to_sixel(image)

def to_media_style(article_style, boardId, contentId, use_sixel, max_size=None):
	from functools import partial

	if article_style == 'compressed':
		return rep_type

	if article_style == 'plain':
		return rep_none

	if use_sixel and sixel.init():
		local.fs.refdir('cache')
		max_size = max_size if max_size else config.get('max-image-size', (1000, 1000))
		return partial(rep_sixel, boardId=boardId, contentId=contentId, max_size=max_size, xauth=auth.update(auth.load()))

	if article_style == 'full':
		return partial(rep_type_url, boardId=boardId, contentId=contentId, xauth=auth.update(auth.load()))

	return rep_type

def anchor(p):
	ma = ptn_link.search(p)
	if not ma:
		return p
	text, url = ma.group('text', 'url')
	return ptn_link.sub(url, p) if text == url else ptn_link.sub(f'[{term.mod(text, term.bold())}]( {url} )', p)

def line_kernel(p, mediarep):
	p = ptn_strong.sub(term.mod(r'\g<content>', term.color('white', 'fl'), term.bold(), term.underline()), p)
	p = anchor(p)
	p = ptn_span.sub(r'\g<content>', p)
	p = ptn_ignore.sub('', p)

	# after processing text tags
	p = html.unescape(p)
	p = ptn_http.sub(term.mod(r'\g<url>', term.color('blue', 'fl')), p)
	url_spans = [ma.span() for ma in ptn_http.finditer(p)]
	starts = [0] + [end for _, end in url_spans]
	ends = [start for start, _ in url_spans] + [len(p)]
	replaced = [ptn_hashtag.sub(term.mod(r'\g<tag>', term.color('blue', 'fl')), p[start:end]) for start, end in zip(starts, ends)]
	p = ''.join(f+s for f, s in zip(replaced, (p[start:end] for start, end in url_spans))) + replaced[-1]

	p = mediarep(p)
	return p


def lines(item, style, use_sixel, max_size=None):
	from concurrent.futures import ThreadPoolExecutor
	from functools import partial

	f = partial(line_kernel, mediarep=to_media_style(style, item['boardId'], item['contentId'], use_sixel, max_size))

	with ThreadPoolExecutor(max_workers=5) as e:
		body = item['values'].get('body')
		if not body:
			yield term.mod('Article not available on terminal. Visit the web site.\n', term.inv())
			yield content_url(item)
			return
		results = e.map(f, (p.group('paragraph') for p in ptn_paragraph.finditer(body)))

		if style == 'full':
			yield from (f'{r}\n' for r in results)

		elif style == 'compact':
			yield from (f'{r}\n' for r in results if len(r))

		elif style == 'compressed':
			yield from (f'{r} ' for r in results if len(r))
			yield '\n'

		elif style == 'plain':
			yield from results


def dl_medium(boardId, contentId, mediaId, head=False, request_as_stream=False, video_url_key='originalUrl', xauth=None):
	import requests

	class bad_response:
		ok = False

	response = requests.get(
		f'https://yomo-api.girls2-fc.jp/web/v1/sites/girls2-fc/boards/{boardId}/contents/{contentId}/medias/{mediaId}',
		headers={
	    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
			'origin': 'https://girls2-fc.jp',
			'x-authorization': xauth if xauth else auth.update(auth.load()),
			'x-from': 'https://girls2-fc.jp',
		})

	if not response.ok:
		return response, bad_response

	meta = response.json()
	url = meta[video_url_key] if meta['type'] == 'video' else meta['accessUrl']

	if head:
		return meta, requests.head(url)
	else:
		return meta, requests.get(url, stream=request_as_stream)

def media_stat(body):
	types = [t for _, t in  ptn_media.findall(body)]
	return {key: types.count(key) for key in ['image', 'video']}
