import os

def return_dir(path):
	if not os.path.exists(path):
		os.makedirs(path)
	return path


def home():
	path = os.path.join(os.path.expanduser('~'), 'gl2f')
	return return_dir(path)

def refdir(path):
	return return_dir(os.path.join(home(), path))

def refdir_untouch(path):
	p = os.path.join(home(), path)
	return p if os.path.exists(p) else False

def listdir(path):
	p = refdir_untouch(path)
	if p:
		li = os.listdir(p)
		if '.DS_Store' in li:
			li.remove('.DS_Store')
		return li
	else:
		return []

def package_data(f=''):
	import gl2f
	d, _ = os.path.split(gl2f.__file__)
	return os.path.join(d, 'data', f)
