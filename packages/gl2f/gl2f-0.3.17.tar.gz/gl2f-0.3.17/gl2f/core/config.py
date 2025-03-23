import os, importlib
from .local import fs
from ..__version__ import version

def default():
	import socket
	return {
		'version': version,
		'host-name': socket.gethostname(),
		'max-image-size': [1000, 1000],
		'serve-port': 7999,
		'listener-port': 8999,
		'addons': []
	}

def filepath():
	return os.path.join(fs.home(), 'config.json')

def load():
	import json
	path = filepath()
	if os.path.isfile(path):
		with open(path, encoding='utf-8') as f:
			return json.loads(f.read())
	return {}

def save(data):
	import json
	with open(filepath(), 'w', encoding='utf-8') as f:
		f.write(json.dumps(data, indent=2, ensure_ascii=False))

def sanitize(data):
	return {k:data[k] for k in data.keys() & default().keys()}

def validate_addons(addons):
	valid = []
	error = []
	for addon in addons:
		try:
			importlib.import_module(addon)
			valid.append(addon)
		except Exception as e:
			error.append((addon, e))
	return valid, error

data = {**default(), **load()}
