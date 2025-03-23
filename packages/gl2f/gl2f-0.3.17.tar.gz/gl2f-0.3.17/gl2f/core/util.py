from datetime import datetime
import os, json

def to_datetime(t):
	return datetime.fromtimestamp(t/1000)

def dump(loc, name, data):
	now = datetime.now().strftime('%y%m%d%H%M%S')
	filepath = os.path.join(loc, f'{name}-{now}.json')
	write_json(filepath, data)
	print('saved', filepath)

def pick(items, indices):
	yield from (items[i-1] for i in indices if 0 < i <= len(items))

def read_all_text(path):
	with open(path, encoding='utf-8') as f:
		return f.read()

def write_all_text(path, text):
	with open(path, 'w', encoding='utf-8') as f:
		print(text, file=f)

def read_json(path):
	return json.loads(read_all_text(path))

def write_json(path, data):
	write_all_text(path, json.dumps(data, indent=2, ensure_ascii=False))

def open_url(url, *args, **kwargs):
	import webbrowser
	webbrowser.register("termux-open '%s'", None)
	webbrowser.open(url, *args, **kwargs)
