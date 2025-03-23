import os, json, re
from . import fs
from .. import util

def load(i):
	return util.read_json(os.path.join(fs.refdir('contents'), i, f'{i}.json'))

def get_ids():
	root = fs.refdir_untouch('contents')
	return sorted((i for i in fs.listdir('contents') if os.path.isdir(os.path.join(root, i))), key=int)

def stat():
	return {os.path.basename(p): {
		'count': len(os.listdir(p)),
		'size': sum(sum( os.path.getsize(os.path.join(d,_f)) for _f in f ) for d,_,f in os.walk(p))
	} for p in filter(lambda x:x, map(fs.refdir_untouch, ['contents', 'cache']))}


def search_image(mediaId, contentId=None):
	if ret := search_image_in_cache(mediaId):
		return ret

	if ret := search_image_in_content(mediaId, contentId):
		return ret

	return search_image_all_contents(mediaId)

def search_image_in_cache(mediaId):
	cache_dir = fs.refdir_untouch('cache')
	if cache_dir:
		cache = os.path.join(cache_dir, mediaId)
		if os.path.isfile(cache):
			return cache

def search_image_in_content(mediaId, contentId):
	if not contentId:
		return None
	content_dir = fs.refdir_untouch(os.path.join('contents', contentId))
	if not content_dir:
		return None

	pattern = re.compile(rf'{mediaId}\.(?!mp4$|mov$)')
	li = filter(pattern.match, os.listdir(content_dir))

	try:
		return os.path.join(content_dir, next(li))
	except:
		return None

def search_image_all_contents(mediaId):
	import glob
	exclude = ['.mp4', '.mov']
	try:
		files = glob.iglob(f'{os.path.abspath(fs.home())}/contents/*/{mediaId}.*')
		return os.path.relpath(next(f for f in files if not any(f.endswith(e) for e in exclude)))
	except StopIteration:
		return None
	except Exception as e:
		print(e)
		raise RuntimeError()
