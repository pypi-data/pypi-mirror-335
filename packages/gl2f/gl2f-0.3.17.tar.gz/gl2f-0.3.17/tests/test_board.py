import pytest
from gl2f.core import board

def test_active_boards():
	defs = board.definitions()
	keys = {i['key'] for i in  defs['pages']}
	assert set(defs['active']).issubset(keys)
