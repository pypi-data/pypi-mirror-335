import os
from gl2f.core.local import archive, meta

left_root = 'tests/data/contents'
right_root = 'tests/data/contents1'

def test_import_checker():
	checker = archive.ImportChecker(left_root, right_root)

	assert len(checker.right_only) == 0
	assert len(list(checker.new_files())) == 0

	assert set(checker.right_only_metadata) == {'1'}
	assert set(checker.diff_metadata) == {'2'}


def test_merge_metadata():
	meta_left = meta.load(filepath = os.path.join(left_root, 'meta.json'))
	meta_right = meta.load(filepath = os.path.join(right_root, 'meta.json'))
	meta_2_left = meta_left['2']
	meta_2_right = meta_right['2']
	assert meta_2_left.important == False
	assert meta_2_right.important == True
	meta_2_left.merge(meta_2_right)
	assert meta_2_left.important == True
