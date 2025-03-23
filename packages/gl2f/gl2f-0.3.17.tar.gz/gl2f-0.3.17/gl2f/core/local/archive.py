import os, json
from . import fs, content, meta
from .. import pretty

def colored_diff_lines(left, right):
	import difflib
	from ...ayame import terminal as term

	try:
		with open(left, encoding='utf-8') as l, open(right, encoding='utf-8') as r:
			return map(lambda l:
					term.mod(l, term.color('green')) if l.startswith('+')
					else term.mod(l, term.color('red')) if l.startswith('-')
					else l,
				difflib.unified_diff(l.readlines(), r.readlines(), fromfile=left, tofile=right)
			)
	except UnicodeDecodeError:
		return [
			'Not text files\n',
			term.mod(f'- {left}\n', term.color('red')),
			term.mod(f'+ {right}\n', term.color('green')),
		]

class ImportChecker:
	def __init__(self, left, right):
		from filecmp import dircmp, cmpfiles

		self.right_dirs = [i for i in os.listdir(right) if os.path.isdir(os.path.join(right, i))]

		self.common = [i for i in self.right_dirs if os.path.isdir(os.path.join(left, i))]
		self.right_only = [i for i in self.right_dirs if i not in self.common]
		self.compare = {i:dircmp(os.path.join(left, i), os.path.join(right, i)) for i in self.common}

		self.identical = [k for k, v in self.compare.items() if not v.diff_files]
		self.diff_files = {k:v.diff_files for k, v in self.compare.items() if v.diff_files}
		self.right_only_files = {k: list(filter(
			lambda f: os.path.isfile(os.path.join(right, k, f)),
			v.right_only))
			for k, v in self.compare.items()
		}
		self.unknown = {k: list(filter(
			lambda i:os.path.isdir(os.path.join(right, k, i)),
			v.right_list))
			for k, v in self.compare.items()
		}


		_left_dirs = content.get_ids()
		_left_metadata = meta.load(filepath = os.path.join(left, 'meta.json'))
		_right_metadata = meta.load(filepath = os.path.join(right, 'meta.json'))

		self.right_only_metadata = {k for k in _right_metadata.keys() if k in _left_dirs and k not in _left_metadata}
		_keys = _left_metadata.keys() & _right_metadata.keys()
		self.diff_metadata = {k for k in _keys if _left_metadata[k] != _right_metadata[k]}


	def report(self):
		print(f'{len(self.right_dirs)} total contents')
		print('\t', ' '.join(self.right_dirs))

		print(f'{len(self.identical)} same contents')
		print('\t', ' '.join(self.identical))

		print(f'{len(self.right_only)} new contents')
		print(' '.join(self.right_only))

		print(f'{sum(map(len, self.right_only_files.values()))} new files')
		print('\n'.join(f'\t{k}\n\t\t{v}' for k, v in self.right_only_files.items() if v))

		print(f'{sum(map(len, self.diff_files.values()))} diff files')
		print('\n'.join(f'\t{k}\n\t\t{v}' for k, v in self.diff_files.items() if v))

		print(f'{sum(map(len, self.unknown.values()))} unchecked subdirs')
		print('\n'.join(f'\t{k}\n\t\t{v}' for k, v in self.unknown.items() if v))


		print(f'{len(self.right_only_metadata)} new metadata')
		print(' '.join(self.right_only_metadata))
		print()

		print(f'{len(self.diff_metadata)} diff metadata')
		print(' '.join(self.diff_metadata))
		print()


	def all_diff_files(self):
		from itertools import chain
		return chain.from_iterable((os.path.join(c, f) for f in files) for c, files in self.diff_files.items())

	def new_files(self):
		from itertools import chain
		return chain.from_iterable((os.path.join(k, i) for i in v) for k, v in self.right_only_files.items())


class Command:
	def __init__(self, name, command, can_execute, default):
		self.name = name
		self.execute = command
		self.can_execute = can_execute
		self.default = default


def import_contents(src):
	import shutil, tempfile
	from ...ayame import terminal as term

	left = fs.refdir('contents')
	tempdir = tempfile.TemporaryDirectory()
	right = tempdir.name

	print(f'extracting archive ({os.path.getsize(src)/1024**3:.2f} GB).')
	shutil.unpack_archive(src, extract_dir=right)

	checker = ImportChecker(left, right)
	checker.report()

	def list_new_contents():
		fm = pretty.Formatter(f='id:date-p:author:title', fd='%m/%d')
		for i in checker.right_only:
			filepath = os.path.join(right, i, f'{i}.json')
			with open(filepath, encoding='utf-8') as f:
				fm.print(json.load(f))

	def copy_new_contents():
		for i in checker.right_only:
			shutil.copytree(os.path.join(right, i), os.path.join(left, i))
			meta.dump_entry(i, meta.load(i, filepath = os.path.join(right, 'meta.json')))
			print(f'copied: {i}')
		print()

	def copy_new_files():
		for file in checker.new_files():
			_left = os.path.join(left, file)
			if os.path.exists(_left):
				print(term.mod(f'file already exists {_left}', term.color('red')))
				continue
			shutil.copy2(os.path.join(right, file), _left)
			print(f'copied: {file}')
		print()

	def show_diff():
		nonlocal src
		diffs = [''.join(colored_diff_lines(os.path.join(left, f), os.path.join(right, f))) for f in checker.all_diff_files()]
		for diff in diffs:
			print(diff)

		if 'n' != input('Freeze conflicting files? (Y/n)').lower():
			default = os.path.splitext(f'diff-{os.path.basename(src)}')[0]
			o = input(f'Enter output directory name ({default})')
			if not o:
				o = default

			os.makedirs(o, exist_ok=True)

			with open(os.path.join(o, 'diff'), 'w', encoding='utf-8') as f:
				f.write(term.declip('\n'.join(diffs)))

			for file in checker.all_diff_files():
				src = os.path.join(right, file)
				dst = os.path.join(o, file)
				os.makedirs(os.path.dirname(dst), exist_ok=True)
				shutil.copy(src, dst)

	def merge_all_metadata():
		_left_metadata = meta.load()
		_right_metadata = meta.load(filepath = os.path.join(right, 'meta.json'))

		for i in filter(lambda i: i in _right_metadata, content.get_ids()):
			if i in _left_metadata:
				_left_metadata[i].merge(_right_metadata[i])
			else:
				_left_metadata[i] = _right_metadata[i]
		meta.dump_archive(_left_metadata)


	commands = list(filter(lambda x:x.can_execute, [
		Command('list new contents', list_new_contents, len(checker.right_only), False),
		Command('copy new contents', copy_new_contents, len(checker.right_only), True),
		Command('copy new files', copy_new_files, any(checker.new_files()), True),
		Command('merge_metadata', merge_all_metadata, checker.right_only_metadata or checker.diff_metadata, True),
		Command('show diff', show_diff, len(checker.diff_files), False)
	]))

	if commands:
		for c in term.selected(commands, format=lambda c:c.name, default=[c.default for c in commands]):
			c.execute()
	else:
		print('Nothing to do. Exit.')

def export_contents(out):
	import shutil
	from datetime import datetime

	contents = fs.refdir_untouch('contents')
	if not contents:
		print('contents not found')
		return

	out = os.path.abspath(out)
	if os.path.isdir(out):
		now = datetime.now().strftime("%Y%m%d%H%M%S")
		base = os.path.join(out, f'gl2f-contents-{now}')
	else:
		par, chi = os.path.split(out)
		if not os.path.isdir(par):
			print(f'{par} is not a directory')
			return

		base = out

	sizeInGb = content.stat()["contents"]["size"]/1024**3
	print(f'zipping contents into {base}.zip ({sizeInGb:.2f} GB)')
	shutil.make_archive(base, 'zip', root_dir=contents)
