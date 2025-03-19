import random
import signal
import string
import subprocess
import click
import requests
import os
import sys
import json
import uvicorn
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from threading import Thread, Event
from rich.live import Live
from rich.markdown import Markdown
from .ChatGPT import Chatbot
from .code_execution import *
import psutil
from rich import print
from rich.syntax import Syntax
from rich.text import Text
import time
import platform

sys.stdin.reconfigure(encoding='utf-8')

@click.command()
def hello():
	"""Say hello"""
	click.echo('Hello, world!')

@click.group()
def dxr():
	"""Figlu command line tool"""
	# 默认调用bash函数
	pass

def get_bash_scripts():
	url = 'http://39.101.69.111:4000/bash'
	r = requests.get(url)
	scripts = r.json()
	return scripts

def get_bash_script_dir(script):
	url = f'http://39.101.69.111:4000/bash/{script}'
	r = requests.get(url)
	scripts = r.json()
	return scripts

def get_bash_script(script, sub_script):
	url = f'http://39.101.69.111:4000/bash/{script}/{sub_script}'
	r = requests.get(url)
	script = r.text
	return script

def chatgpt_explanation(language, error_message, model, maxtoken):
	query = construct_query(language, error_message)
	base_url, api_key = get_api_key()
	chatbot = Chatbot(api_key=api_key, base_url=base_url, engine=model, max_tokens=maxtoken)
	res = chatbot.ask_stream(query)
	return res

def choose_script(scripts, step=1):
	script_index = 0
	while True:
		click.clear()
		click.echo('Select a script:')
		for i, script in enumerate(scripts):
			if i == script_index:
				click.echo(f'> {script}')
			else:
				click.echo(f'  {script}')
		key = click.getchar()
		# 上下键选择，左键返回，右键进入
		if key == '\r':
			return scripts[script_index], step + 1
		elif key == '\x1b[A':
			script_index = (script_index - 1) % len(scripts)
		elif key == '\x1b[B':
			script_index = (script_index + 1) % len(scripts)
		elif key == '\x1b[D':
			return None, step - 1
		elif key == '\x1b[C':
			return scripts[script_index], step + 1


@dxr.command()
def bash():
	"""执行云端上的脚本"""
	import os
	# scripts = get_bash_scripts()
	# script = choose_script(scripts)
	# sub_scripts = get_bash_script_dir(script)
	# sub_script = choose_script(sub_scripts)
	# bash_script = get_bash_script(script, sub_script)
	# print("=" * 80)
	# click.echo(bash_script)
	# print("=" * 80)
	# click.echo('Run this script?')
	# if click.confirm('Continue?'):
	#     os.system(bash_script)
	step = 1
	while True:
		if step == 0:
			break
		if step == 1:
			scripts = get_bash_scripts()
			script, step = choose_script(scripts, step)
		elif step == 2:
			sub_scripts = get_bash_script_dir(script)
			sub_script, step = choose_script(sub_scripts, step)
		elif step == 3:
			bash_script = get_bash_script(script, sub_script)
			print("=" * 80)
			click.echo(bash_script)
			print("=" * 80)
			click.echo('Run this script?')
			if click.confirm('Continue?'):
				os.system(bash_script)
				break
			step = 2

def get_api_key():
	api_key = os.environ.get("OPENAI_API_KEY", '')
	if api_key == '':
		url = f'http://39.101.69.111:4000/chat/get_api_key'
		r = requests.get(url)
		base_url_and_api_key = r.text
		base_url, api_key = base_url_and_api_key.split(',')
	return base_url, api_key

@click.command()
@click.option("--model", default="gpt-3.5-turbo", help="Specify which GPT model to use")
@click.option("--maxtoken", default=4096, help="Maximum number of tokens in a single prompt")
def chat(model, maxtoken):
	"""Chat with GPT-3 or GPT-4"""
	base_url, api_key = get_api_key()
	bot = Chatbot(api_key=api_key, base_url=base_url, engine=model, max_tokens=maxtoken)
	while True:
		text = input("You: ")
		if text.strip() == "exit":
			break
		response = bot.ask_stream(text)
		md = Markdown("")
		with Live(md, auto_refresh=False) as live:
			tmp = ""
			for r in response:
				tmp += r
				md = Markdown(tmp)
				live.update(md, refresh=True)


@click.command()
@click.option("--model", default="gpt-3.5-turbo", help="Specify which GPT model to use")
@click.option("--maxtoken", default=4096, help="Maximum number of tokens in a single prompt")
def git(model, maxtoken):
	"""问问关于git的问题"""
	print("这是一个git命令行助手,你可以通过这个助手来学习git命令")
	# use openai to generate git scripts
	base_url, api_key = get_api_key()
	bot = Chatbot(api_key=api_key, base_url=base_url, system_prompt="""
    你是一个很好的git命令行助手，你可以帮助我更好的使用git, 
    根据我的问题,你可以给我提供一些git命令
    """, engine=model, max_tokens=maxtoken)
	while True:
		text = input("请输入你的问题: ")
		if text.strip() == "exit":
			break
		response = bot.ask_stream(text)
		print("=" * 80)
		tmp = ""
		for r in response:
			tmp += r
			print(r, end='', flush=True)
		print()
		print("=" * 80)

# dxr python test.py --model gpt-3.5-turbo --maxtoken 4096
# 用来直接运行python脚本，并且获取运行时的错误输出，
# 将错误输出 发送给openai，让openai来帮助我们解决这个问题
@click.command()
@click.option("--model", default="gpt-3.5-turbo", help="Specify which GPT model to use")
@click.option("--maxtoken", default=4096, help="Maximum number of tokens in a single prompt")
@click.option("--binary", default="python", help="Specify which binary to use")
@click.argument('script', type=click.Path(exists=True))
def python(model, maxtoken, binary, script):
	args = [binary, script]
	language = binary
	if not language:
		print_invalid_language_message()
		return
	error_message = execute_code(args, language)
	if not error_message:
		return
	with LoadingMessage():
		res = chatgpt_explanation(language, error_message, model, maxtoken)
	md = Markdown("")
	with Live(md, auto_refresh=True) as live:
		tmp = ""
		for r in res:
			tmp += r
			md = Markdown(tmp)
			live.update(md, refresh=True)


@click.command()
@click.option("--model", default="gpt-3.5-turbo", help="Specify which GPT model to use")
@click.option("--maxtoken", default=4096, help="Maximum number of tokens in a single prompt")
@click.argument('script', type=click.Path(exists=True))
def python3(model, maxtoken, script):
	args = ['python3', script]
	language = get_language(args)
	print(language)
	if not language:
		print_invalid_language_message()
		return
	error_message = execute_code(args, language)
	if not error_message:
		return
	with LoadingMessage():
		res = chatgpt_explanation(language, error_message, model, maxtoken)
	md = Markdown("")
	with Live(md, auto_refresh=True) as live:
		tmp = ""
		for r in res:
			tmp += r
			md = Markdown(tmp)
			live.update(md, refresh=True)


@click.command()
@click.argument('args', nargs=-1)
@click.option("--model", default="gpt-3.5-turbo", help="Specify which GPT model to use")
@click.option("--maxtoken", default=4096, help="Maximum number of tokens in a single prompt")
@click.option("--lines", default=100, help="Number of lines before and after the error to capture as context")
def run(args, model, maxtoken, lines):
	"""
    接收不固参数的命令，并执行它们。如果发生错误，将捕获并显示错误输出及其上下文。
    """
	try:
		language = get_language(args)
		# 将参数元组转换为列表，并将其递给subprocess.run函数
		result = subprocess.run(
			list(args), stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, check=True
		)
	except subprocess.CalledProcessError as e:
		# 找出可能涉及文件
		source_files = [arg for arg in args if os.path.isfile(arg)]
		file_contents = []

		for file in source_files:
			# 检查文件字数是否超过2000
			num_chars = os.stat(file).st_size
			if num_chars <= 2000:
				with open(file, 'r', encoding='utf-8') as f:
					content = f.read()
			else:
				# 取前后各100行的代码
				# with open(file, 'r', encoding='utf-8') as f:
				#     head_lines = [next(f) for _ in range(lines)]
				# with open(file, 'r', encoding='utf-8') as f:
				#     tail_lines = f.readlines()[-lines:]
				with open(file, 'r', encoding='utf-8') as f:
					head_lines = [next(f, '') for _ in range(lines)]
				with open(file, 'r', encoding='utf-8') as f:
					tail_lines = [line for _, line in zip(range(lines), f.readlines())]

				content = "".join(head_lines) + "\n...\n" + "".join(tail_lines)

			file_contents.append(content)

		# 获取错误输出
		error_output = e.stderr

		# 打印错误输出
		click.echo(error_output)

		# 将文件内容与错误输出合并
		total_input = f"Error Output:\n{error_output}\n\n"
		for i, content in enumerate(file_contents):
			total_input += f"File Content ({source_files[i]}):\n{content}\n\n"

		# 使用GPT模型处理整个输入
		with LoadingMessage():
			response = chatgpt_explanation(language, total_input, model, maxtoken)

		# 使用Rich库将结果显示为Markdown
		md = Markdown("")
		with Live(md, auto_refresh=True) as live:
			tmp = ""
			for r in response:
				tmp += r
				md = Markdown(tmp)
				live.update(md, refresh=True)
	else:
		click.echo(result.stdout)


def main():
	print("Hello world!")

app = FastAPI()
server_thread = None
stop_event = Event()

class LoginData(BaseModel):
	user: str
	password: str = None
	token: str = None


# 在文件开头添加以下函数
def ensure_dxr_dir():
	if platform.system() == "Windows":
		dxr_dir = os.path.join(os.environ.get("USERPROFILE", ""), ".dxr")
	else:
		dxr_dir = os.path.join(os.path.expanduser("~"), ".dxr")
	if not os.path.exists(dxr_dir):
		os.makedirs(dxr_dir)
	return dxr_dir


# 修改 SERVER_PID_FILE 的定义
DXR_DIR = ensure_dxr_dir()
SERVER_PID_FILE = os.path.join(DXR_DIR, "fastapi_server.pid")

# 修改 SERVER_LOG_FILE 的定义
SERVER_LOG_FILE = os.path.join(DXR_DIR, "fastapi_server.log")


# 修改 load_user_data 函数
def load_user_data(username):
	file_path = os.path.join(DXR_DIR, f"{username}.json")
	if os.path.exists(file_path):
		with open(file_path, 'r') as f:
			return json.load(f)
	return None

@app.post("/login")
async def login(login_data: LoginData):
	user_data = load_user_data(login_data.user)
	print(user_data)
	whitelist_json = load_whitelist()
	if not user_data:
		return {"status": "failed", "permission": 1, "token": "", "whitelist": []}
	if login_data.token:
		if login_data.token == user_data.get("token"):
			return {"status": "success", "permission": user_data["permission"], "token": user_data["token"],
			        "whitelist": whitelist_json}
	elif login_data.password:
		if login_data.password == user_data["password"]:
			return {"status": "success", "permission": user_data["permission"], "token": user_data["token"],
			        "whitelist": whitelist_json}

	return {"status": "failed", "permission": 1, "token": "", "whitelist": []}


async def run_server():
	config = uvicorn.Config(app, host="0.0.0.0", port=9002, loop="asyncio")
	server = uvicorn.Server(config)
	await server.serve()

def start_server_thread():
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	loop.run_until_complete(run_server())


def is_server_running():
	if os.path.exists(SERVER_PID_FILE):
		with open(SERVER_PID_FILE, 'r') as f:
			pid = int(f.read().strip())
		return psutil.pid_exists(pid)
	return False

@dxr.command()
def start_server():
	"""启动FastAPI服务器"""
	if is_server_running():
		click.echo("FastAPI服务器已经在运行中。")
		return

	click.echo("正在启动FastAPI服务器...")

	# 使用subprocess启动一个新的Python进程来运行服务器
	server_process = subprocess.Popen(
		["python", "-c",
		 f"from dxr_cli.cli import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=9002, log_config={{'version': 1, 'formatters': {{'default': {{'format': '%(asctime)s - %(levelname)s - %(message)s', 'datefmt': '%Y-%m-%d %H:%M:%S'}}}}, 'handlers': {{'default': {{'class': 'logging.FileHandler', 'filename': '{SERVER_LOG_FILE}', 'formatter': 'default'}}}}, 'root': {{'level': 'INFO', 'handlers': ['default']}}}})"],
		stdout=subprocess.DEVNULL,
		stderr=subprocess.DEVNULL,
		start_new_session=True
	)

	# 将PID保存到文件中
	with open(SERVER_PID_FILE, 'w') as f:
		f.write(str(server_process.pid))

	click.echo(f"FastAPI服务器已在后台启动，PID: {server_process.pid}")

@dxr.command()
def stop_server():
	"""停止FastAPI服务器"""
	if not is_server_running():
		click.echo("FastAPI服务器未在运行。")
		return

	click.echo("正在停止FastAPI服务器...")

	with open(SERVER_PID_FILE, 'r') as f:
		pid = int(f.read().strip())

	try:
		os.killpg(os.getpgid(pid), signal.SIGTERM)
		click.echo("FastAPI服务器已停止。")
	except ProcessLookupError:
		click.echo("无法找到服务器进程，可能已经停止。")
	finally:
		os.remove(SERVER_PID_FILE)

def generate_token(length=32):
	return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@dxr.command()
@click.argument('username')
@click.argument('password')
@click.argument('permission', type=click.Choice(['0', '1']))
def add(username, password, permission):
	"""添加新用户"""
	user_data = {
		"username": username,
		"password": password,
		"permission": int(permission),
		"token": generate_token(),
		"expiry_date": "2099-12-31"
	}

	file_path = os.path.join(DXR_DIR, f"{username}.json")
	with open(file_path, "w") as f:
		json.dump(user_data, f, indent=2)

	click.echo(f"用户 {username} 已成功添加。文件保存在 {file_path}")


# 修改 load_whitelist 和 save_whitelist 函数
def load_whitelist():
	whitelist_path = os.path.join(DXR_DIR, 'whitelist.json')
	try:
		with open(whitelist_path, 'r', encoding='utf-8') as f:
			return set(json.load(f))
	except (FileNotFoundError, json.JSONDecodeError):
		return set()


def save_whitelist(whitelist):
	whitelist_path = os.path.join(DXR_DIR, 'whitelist.json')
	with open(whitelist_path, 'w', encoding='utf-8') as f:
		json.dump(list(whitelist), f, ensure_ascii=False)

@dxr.command()
@click.option('--lines', default=50, help='Number of lines to show initially')
def server_logs(lines):
	"""实时查看FastAPI服务器日志"""
	if not os.path.exists(SERVER_LOG_FILE):
		click.echo("日志文件不存在。服务器可能还没有启动或没有生成日志。")
		return

	click.echo("正在实时显示服务器日志。按 Ctrl+C 退出。")

	try:
		process = subprocess.Popen(['tail', '-n', str(lines), '-f', SERVER_LOG_FILE],
		                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
		                           text=True, bufsize=1, universal_newlines=True)

		with Live(auto_refresh=True) as live:
			while True:
				output = process.stdout.readline()
				if output == '' and process.poll() is not None:
					break
				if output:
					text = Text(output.strip())
					if "ERROR" in output:
						text.stylize("bold red")
					elif "WARNING" in output:
						text.stylize("bold yellow")
					elif "INFO" in output:
						text.stylize("bold green")
					live.update(text)

	except KeyboardInterrupt:
		click.echo("\n停止查看日志。")
	finally:
		if process:
			process.terminate()

# 在文件中添加以下新函数

def add_to_whitelist(topics):
	"""添加话题到白名单"""
	if not topics:
		click.echo("请提供至少一个话题")
		return

	whitelist = load_whitelist()
	new_topics = set(topic.strip() for topic in ','.join(topics).split(',') if topic.strip())

	existing_topics = new_topics.intersection(whitelist)
	actually_added = new_topics - whitelist

	whitelist.update(new_topics)
	save_whitelist(whitelist)

	if existing_topics:
		click.echo(f"以下话题已经存在于白名单中：{', '.join(existing_topics)}")

	if actually_added:
		click.echo(f"已添加以下新话题到白名单：{', '.join(actually_added)}")
	else:
		click.echo("没有新话题被添加到白名单")

def remove_whitelist(topics):
	"""从白名单中删除话题"""
	if not topics:
		click.echo("请提供至少一个话题")
		return

	whitelist = load_whitelist()
	remove_topics = set(topic.strip() for topic in ','.join(topics).split(',') if topic.strip())
	whitelist -= remove_topics
	save_whitelist(whitelist)

	click.echo(f"已从白名单中删除以下话题：{', '.join(remove_topics)}")

def list_whitelist():
	"""列出白名单"""
	whitelist = load_whitelist()
	click.echo(f"当前白名单：{', '.join(whitelist)}")

@dxr.command()
@click.argument('command', type=click.Choice(['add', 'remove', 'list']))
@click.argument('topics', nargs=-1)
def whitelist(command, topics):
	"""管理白名单"""
	if command == 'add':
		add_to_whitelist(topics)
	elif command == 'remove':
		remove_whitelist(topics)
	elif command == 'list':
		list_whitelist()

@dxr.command()
@click.argument('topics', nargs=-1)
def add_whitelist(topics):
	"""添加话题到白名单"""
	add_to_whitelist(topics)

# 确保所有命令都被添加到 dxr 命令组中
dxr.add_command(hello)
dxr.add_command(bash)
dxr.add_command(chat)
dxr.add_command(git)
dxr.add_command(python)
dxr.add_command(python3)
dxr.add_command(run)
dxr.add_command(add)
dxr.add_command(start_server)
dxr.add_command(stop_server)
# dxr.add_command(server_logs)
dxr.add_command(whitelist)  # Add this
dxr.add_command(add_whitelist)

if __name__ == '__main__':
	dxr()