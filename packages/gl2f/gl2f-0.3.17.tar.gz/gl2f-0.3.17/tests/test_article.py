from sys import stdout
import importlib
from gl2f.core import article
from gl2f.ayame import terminal as term

class VirtualTty:
	_default_isatty = stdout.isatty

	def __enter__(self):
		stdout.isatty = lambda:True
		importlib.reload(term)

	def __exit__(self, *args):
		stdout.isatty = VirtualTty._default_isatty
		importlib.reload(term)


sample_url = 'https://an.url/of/somewhere#including-hashtag'

media = '<fns-media class="fr-fic fr-dib fr-draggable" src="https://img.url.jpg?many&amp;parameters" site-id="girls2-fc" media-id="media-id" board-id="board-id" content-id="content-id" type="type"></fns-media>'

anchor_with_url = f'<a href="{sample_url}" rel="noopener noreferrer" target="_blank">{sample_url}</a>'
anchor_with_text = f'<a href="{sample_url}" rel="noopener noreferrer" target="_blank">a link to somewhere</a>'
url_as_text = f'go to {sample_url} for nothing'

strong = '<strong>a strong text</strong>'
strong_break = '<strong>another strong followed by a break<br></strong>'

strong_in_span = '<span style="font-size: 14px;"><strong>strong in span</strong></span>'
text_in_span = '<span style="font-size: 14px;">plain text in span</span>'
text_and_anchor_in_span = f'<span style="font-size: 14px;">another plain text in span, <a href="{sample_url}">an anchor, </a>and plain text again</span>'
only_br_in_span = '<span style="font-size: 14px;"><br></span>'


def kernel(p):
	return article.line_kernel(p, article.rep_none)


def test_media():
	with VirtualTty():
		assert ('media-id', 'type') == article.ptn_media.search(media).group('id', 'type')

		assert '' == article.line_kernel(media, article.rep_none)
		assert '\x1b[2m[type]\x1b[m' == article.line_kernel(media, article.rep_type)
		assert '\x1b[2m[type](media-id)\x1b[m' == article.line_kernel(media, article.rep_type_id)

def test_url():
	with VirtualTty():
		assert (sample_url, 'a link to somewhere') == article.ptn_link.search(anchor_with_text).group('url', 'text')

		assert f'\x1b[94m{sample_url}\x1b[m' == kernel(anchor_with_url)
		assert f'[\x1b[1ma link to somewhere\x1b[m]( \x1b[94m{sample_url}\x1b[m )' == kernel(anchor_with_text)
		assert f'go to \x1b[94m{sample_url}\x1b[m for nothing' == kernel(url_as_text)

def test_strong_span():
	with VirtualTty():
		assert '\x1b[97;1;4ma strong text\x1b[m' == kernel(strong)
		assert '\x1b[97;1;4manother strong followed by a break\x1b[m' == kernel(strong_break)

		pairs = [
			('\x1b[97;1;4mstrong in span\x1b[m', strong_in_span),
			('plain text in span', text_in_span),
			(f'another plain text in span, [\x1b[1man anchor, \x1b[m]( \x1b[94m{sample_url}\x1b[m )and plain text again', text_and_anchor_in_span),
			('', only_br_in_span),
		]

		for expected, source in pairs:
			assert expected == kernel(source)

		assert ''.join(e for e, _ in pairs) == kernel(''.join(s for _, s in pairs)), 'fail with multiple spans'

def test_hashtag():
	with VirtualTty():
		tags = '#Girls2 の#小田柚葉 様 #ｷｮｳﾉﾐｻｷﾓｼﾞ　#鶴屋美咲 さん　#ﾄﾂｹﾞｷﾕｳﾜ#比嘉優和 ちゃん ＃Lucky2'
		expected = '\x1b[94m#Girls2\x1b[m の\x1b[94m#小田柚葉\x1b[m 様 \x1b[94m#ｷｮｳﾉﾐｻｷﾓｼﾞ\x1b[m　\x1b[94m#鶴屋美咲\x1b[m さん　\x1b[94m#ﾄﾂｹﾞｷﾕｳﾜ\x1b[m\x1b[94m#比嘉優和\x1b[m ちゃん ＃Lucky2'
		assert expected == kernel(tags)

		tags_not_in_url = f'{sample_url} only #hashtags {sample_url} in plain text {sample_url} match and also#tagwithoutspace match {sample_url}'
		expected_only_plain = f'\x1b[94m{sample_url}\x1b[m only \x1b[94m#hashtags\x1b[m \x1b[94m{sample_url}\x1b[m in plain text \x1b[94m{sample_url}\x1b[m match and also\x1b[94m#tagwithoutspace\x1b[m match \x1b[94m{sample_url}\x1b[m'
		assert expected_only_plain == kernel(tags_not_in_url)

def test_paragraph():
	body_source = [
		'<p>aaaaa</p>',
		'<p><br></p>',
		'<p><br></p>',
		f'<p class="fr-fns-active">{media}</p>',
		'<p>bbbbb</p>',

		f'<p>{anchor_with_url}</p>',
		f'<p>{anchor_with_text}</p>',
		f'<p>{url_as_text}</p>',
		f'<p>{strong}</p>',
		f'<p>{strong_break}</p>',

		f'<p>{strong_in_span}</p>',
		f'<p>{text_in_span}</p>',
		f'<p>{text_and_anchor_in_span}</p>',
		f'<p>{only_br_in_span}</p>',
	]
	body = ''.join(body_source)

	paragraph_contents = [
		'aaaaa',
		'<br>',
		'<br>',
		media,
		'bbbbb',

		anchor_with_url,
		anchor_with_text,
		url_as_text,

		strong,
		strong_break,

		strong_in_span,
		text_in_span,
		text_and_anchor_in_span,
		only_br_in_span,
	]

	matches = list(ma for ma in article.ptn_paragraph.finditer(body) if ma)
	assert len(body_source) == len(matches)
	assert all(a == b.group('paragraph') for a, b in zip( paragraph_contents, matches))
