from .core import lister, pretty
from .ayame import terminal as term

def merge(ranges):
	if len(ranges) == 0: return []

	ret = []
	cur = ranges[0]
	for j in range(1, len(ranges)):
		if cur[1] < ranges[j][0]:
			ret.append(cur)
			cur = ranges[j]
		else:
			cur = cur[0], ranges[j][1]
	ret.append(cur)
	return ret


def subcommand(args):
	from .core import article
	import re

	keywords = list(filter(len, sum((k.split('　') for k in args.keywords), [])))


	fm = pretty.from_args(args)
	fm.reset_index(digits=len(str(args.number)))

	hi = re.compile( fr"(?P<match>{'|'.join(keywords)})" )

	items = lister.list_contents(args)
	texts = [''.join(article.lines(i, 'plain', False)) for i in items]
	counts = [
		sum(int(k in te) + int(k in ti) for k in keywords)
		for te, ti in zip(texts, [i['values']['title'] for i in items])
	]

	for c, t, i in sorted(zip(counts, texts, items), reverse=True, key=lambda x:x[0]):
		if c == 0: break

		term.write_with_encoding(hi.sub(
			term.mod(r'\g<match>', term.color('yellow'), term.inv()),
			fm.format(i)
		) + '\n', args.encoding)

		ranges = [(i.start()-20, i.end()+20) for i in hi.finditer(t)]
		merged = merge(ranges)
		if len(merged)>5:
			merged = merged[:5]

		for begin, end in merged:
			term.write_with_encoding('> ' + hi.sub(
				term.mod(r'\g<match>', term.color('yellow')),
				t[max(0, begin):min(len(t), end)] + term.reset()
			) + '\n', args.encoding)

		term.write_with_encoding('\n', args.encoding)


def add_to():
	return 'gl2f', 'search'

def add_args(parser):
	parser.description = 'Search in articles'

	lister.add_args(parser)
	pretty.add_args(parser)

	parser.set_defaults(date='%m/%d', number=30)

	parser.add_argument('keywords', nargs='+')
	parser.add_argument('--encoding')

	parser.set_defaults(handler=subcommand)

def set_compreply():
	return '__gl2f_complete_list_args'
