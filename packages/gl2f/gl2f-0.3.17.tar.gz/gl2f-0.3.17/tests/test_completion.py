import subprocess
from gl2f import completion as comp

def test_generation():
	assert isinstance(comp.generate(), str)
