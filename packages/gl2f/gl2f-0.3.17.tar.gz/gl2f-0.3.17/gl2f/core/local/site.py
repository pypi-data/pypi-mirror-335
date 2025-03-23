import os, re, json, http.server, socket, requests
from .. import util
from ..config import data as config
from . import fs, content, index


def update_site(full=False):
	site = fs.refdir_untouch('site')
	if not site:
		return 'site is not installed'

	index.main(full=full)

	table_code = f'const _table={util.read_all_text(index.get_path())};'
	util.write_all_text(os.path.join(site, 'index.js'), table_code)


def install():
	import shutil

	src = fs.package_data('site')
	dst = fs.refdir('site')

	shutil.copytree(src, dst, dirs_exist_ok=True)

	site_contents = os.path.join(dst, 'contents')
	if os.path.isdir(site_contents):
		os.remove(site_contents)
	os.symlink(fs.refdir('contents'), site_contents)

	update_site()


def get_config(url=None):
	if url is None:
		return {
			'listener-port': config['listener-port']
		}

	config_url = f'http://{find_root(url)}/config'

	try:
		res = requests.get(config_url)
		return res.json()
	except Exception as e:
		print('Failed to find listener port')
		print(e)

class Handler(http.server.SimpleHTTPRequestHandler):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, directory=fs.refdir_untouch('site'), **kwargs)

	def end_headers(self):
		self.send_header('Accept-Ranges', 'bytes')
		self.send_header('X-Server-Name', config['host-name'])
		super().end_headers()

	def do_GET(self):
		if self.path == '/config': # always listen
			self.send_response(200)
			self.send_header("Content-type", "application/json")
			self.end_headers()
			self.wfile.write(json.dumps(get_config()).encode())
		elif getattr(self.server, 'reject', False):
			self.send_response(503)
			self.end_headers()
			self.wfile.write(b'Server is refusing connections.')
		else:
			super().do_GET()


def serve(port, browse=False):
	import socketserver, threading

	print('Checking existing server...')
	status, url = send_command('find')
	if status:
		print(f'Found running server. {url}')
		if browse:
			util.open_url(url)
		return

	install()

	url = f'http://{get_local_ip()}:{port}'
	with socketserver.ThreadingTCPServer(('0.0.0.0', port), Handler) as httpd:
		httpd.reject = False
		print(f'Serving at {url}')

		commandset = create_commandset(httpd)
		listender_thread = threading.Thread(target=command_listener, args=(commandset,), daemon=True)
		listender_thread.start()

		server_thread = threading.Thread(target=httpd.serve_forever)
		server_thread.start()

		if browse:
			util.open_url(url)

		server_thread.join()

def create_commandset(httpd):
	def shutdown_command():
		print("[Server] Shutting down...")
		with socket.create_connection(('127.0.0.1', httpd.server_address[1])):
			pass
		httpd.shutdown()

	def reject():
		httpd.reject = True

	def resume():
		httpd.reject = False

	def status():
		_, port = httpd.server_address
		host = get_local_ip()
		state = {
			'address': f'http://{host}:{port}',
			'reject': httpd.reject,
		}
		return json.dumps(state)

	return {
		'reject': reject,
		'resume': resume,
		'shutdown': shutdown_command,
		'status': status,
	}

def send_command(command, url=None):
	host = get_local_ip() if url is None else find_ip(url)
	if not host:
		return False, 'Could not find the host address.'
	config = get_config(url)
	if not config:
		return False, 'Could not find config.'
	port = config.get('listener-port')
	if port is None:
		return False, 'Could not find the command listener port.'

	try:
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
			client.connect((host, port))
			client.sendall(command.encode())
			result = json.loads(client.recv(1024).decode())
			return result.get('status', False), result.get('value', '')
	except Exception as e:
		return False, f'Could not connect to {host}:{port}. Server may not be running.\n{e}'


# move to util
def execute_command(commandset, key):
	f = commandset.get(key)
	if not f:
		return {'status': False, 'value': f'Unknown command "{key}"'}
	try:
		value = f() or ''
		return {'status': True, 'value': value}
	except Exception as e:
		return {'status': False, 'value': e}

def command_listener(commandset):
	host, port = get_local_ip(), config['listener-port']
	with socket.create_server((host, port)) as server_socket:
		print(f"[Server] Listening for commands on port {port}...")
		server_socket.listen(5)

		while True:
			try:
				client_socket, _ = server_socket.accept()
				with client_socket:
					command = client_socket.recv(1024).decode().strip()
					result = execute_command(commandset, command)
					client_socket.sendall(json.dumps(result).encode())

			except Exception as e:
				print(e)

_local_ip = None
def get_local_ip():
	global _local_ip
	if _local_ip:
		return _local_ip

	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		s.connect(('8.8.8.8', 80))
		_local_ip = s.getsockname()[0]
		return _local_ip
	except:
		return 'localhost'
	finally:
		s.close()

def find_ip(url):
	try:
		return re.sub(r'.+://', '', url).split(':')[0]
	except:
		return None

def find_root(url):
	try:
		return re.sub(r'.+://', '', url).split('/')[0]
	except:
		return None
