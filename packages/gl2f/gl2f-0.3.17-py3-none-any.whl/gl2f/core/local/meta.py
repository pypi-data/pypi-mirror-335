import os, json
from . import fs

class Metadata:
	def __init__(self, **kwargs):
		self._type = Metadata.__name__
		self.important = kwargs.get('important', False)

	def merge(self, other):
		self.important |= other.important

	def __eq__(self, other):
		if not isinstance(other, self.__class__):
			return False

		if self.important != other.important:
			return False

		return True


def create(**kwargs):
	return Metadata(**kwargs)

class MetadataEncoder(json.JSONEncoder):
	def default(self, o):
		if isinstance(o, Metadata):
			return o.__dict__
		return json.JSONEncoder.default(self, o)

class MetadataDecoder(json.JSONDecoder):
	def __init__(self, *args, **kwargs):
		json.JSONDecoder.__init__(self, object_hook=self._object_hook, *args, **kwargs)

	def _object_hook(self, o):
		if o.get('_type') == Metadata.__name__:
			return Metadata(**o)
		return o


def load(i=None, filepath=None):
	if filepath is None:
		filepath = os.path.join(fs.refdir('contents'), 'meta.json')

	if not os.path.isfile(filepath):
		return {} if i is None else create()

	with open(filepath, encoding='utf-8') as f:
		data = json.load(f, cls=MetadataDecoder)
		if i is None:
			return data
		return data.get(i, Metadata())

def dump_archive(archive):
	with open(os.path.join(fs.refdir('contents'), 'meta.json'), 'w', encoding='utf-8') as f:
		json.dump(archive, f, cls=MetadataEncoder, sort_keys=True, indent=2, ensure_ascii=False)

def dump_entry(i, data):
	archive = load()
	if i in archive:
		archive[i].merge(data)
	else:
		archive[i] = data

	dump_archive(archive)
