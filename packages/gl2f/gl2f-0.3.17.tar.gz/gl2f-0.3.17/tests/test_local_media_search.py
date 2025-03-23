import pytest
import os, shutil
from gl2f.core import local

def home():
	return local.fs.return_dir(os.path.join('tests', 'data'))

local.fs.home = home
print(f'home: {local.fs.home()}')

cache_dir = local.fs.refdir('cache')
contents_dir = local.fs.refdir('contents')
content1_dir = local.fs.refdir(os.path.join('contents', '1'))
content2_dir = local.fs.refdir(os.path.join('contents', '2'))

paths = [
	os.path.join(cache_dir, 'only_in_cache'),

	os.path.join(content1_dir, 'only_in_first_image.jpeg'),

	os.path.join(cache_dir, 'cache_and_first_image'),
	os.path.join(content1_dir, 'cache_and_first_image.jpeg'),

	os.path.join(content1_dir, 'first_and_second_image.jpeg'),
	os.path.join(content2_dir, 'first_and_second_image.jpeg'),


	os.path.join(cache_dir, 'cache_and_first_mp4'),
	os.path.join(cache_dir, 'cache_and_first_mov'),
	os.path.join(cache_dir, 'cache_and_first_mp4.mp4'),
	os.path.join(cache_dir, 'cache_and_first_mov.mov'),

	os.path.join(content1_dir, 'first_mp4.mp4'),
	os.path.join(content1_dir, 'first_mov.mov'),
	os.path.join(content1_dir, 'first_unknown_type.xxx')
]


def test_fallback():
	assert local.content.search_image('only_in_cache') == os.path.join(cache_dir, 'only_in_cache')
	assert local.content.search_image('only_in_cache', '1') == os.path.join(cache_dir, 'only_in_cache')
	assert local.content.search_image('only_in_cache', '2') == os.path.join(cache_dir, 'only_in_cache')

	assert local.content.search_image('cache_and_first_image') == os.path.join(cache_dir, 'cache_and_first_image')
	assert local.content.search_image('cache_and_first_image', '1') == os.path.join(cache_dir, 'cache_and_first_image')
	assert local.content.search_image('cache_and_first_image', '2') == os.path.join(cache_dir, 'cache_and_first_image')

	assert local.content.search_image('only_in_first_image') == os.path.join(content1_dir, 'only_in_first_image.jpeg')
	assert local.content.search_image('only_in_first_image', '1') == os.path.join(content1_dir, 'only_in_first_image.jpeg')
	assert local.content.search_image('only_in_first_image', '2') == os.path.join(content1_dir, 'only_in_first_image.jpeg')

	assert local.content.search_image('first_and_second_image') in [
		os.path.join(content1_dir, 'first_and_second_image.jpeg'),
		os.path.join(content2_dir, 'first_and_second_image.jpeg')
	]
	assert local.content.search_image('first_and_second_image', '1') == os.path.join(content1_dir, 'first_and_second_image.jpeg')
	assert local.content.search_image('first_and_second_image', '2') == os.path.join(content2_dir, 'first_and_second_image.jpeg')

def test_thumbnail():
	assert local.content.search_image('cache_and_first_mp4') == os.path.join(cache_dir, 'cache_and_first_mp4')
	assert local.content.search_image('cache_and_first_mov') == os.path.join(cache_dir, 'cache_and_first_mov')

	assert local.content.search_image('first_mp4') == None
	assert local.content.search_image('first_mov') == None
	assert local.content.search_image('first_unknown_type') == os.path.join(content1_dir, 'first_unknown_type.xxx')
