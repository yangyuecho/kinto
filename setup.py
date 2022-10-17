#!/usr/bin/env python3
import time, os, subprocess, shlex, platform, argparse
from subprocess import PIPE, Popen
from enum import Enum


class Platform(Enum):
	linux = "Linux"
	win = "Windows"
	other = "Other"


def cmdline(command: str):
	# todo: 这里的几个参数并不是十分了解
	# 如果把universal_newlines 设置成True，则子进程的stdout和stderr被视为文本对象，
	# 并且不管是*nix的行结束符（'/n'），还是老mac格式的行结束符（'/r' ），还是windows 格式的行结束符（'/r/n' ）都将被视为 '/n'
	# 一个可以被用于 Popen 的stdin 、stdout 和stderr 3个参数的特输值，表示需要创建一个新的管道
	# 在linux下，当shell=True时，如果arg是个字符串，就使用shell来解释执行这个字符串。如果args是个列表，则第一项被视为命令，其余的都视为是给shell本身的参数
	process = Popen(
		args=command,
		stdout=PIPE,
		universal_newlines=True,
		shell=True
	)
	return process.communicate()[0]


def init_config_file(homedir: str):
	config_path = homedir + "/.config/kinto"
	if os.path.isdir(config_path) is False:
		os.mkdir(config_path)
		time.sleep(0.5)


def log_version():
	# 1.2-13 build e106710
	# --abbrev = 0
	# 使用默认的7位十六进制数字作为缩写对象名称，而不是使用<n>数字或根据需要的数字来组成一个唯一的对象名称。0 的<n>将抑制长格式，只显示最接近的标签。
	# 获取最新commit id或者说sha的简短结果
	# git rev-parse --short HEAD
	kintover = cmdline('echo "$(git describe --tag --abbrev=0 | head -n 1)" "build" "$(git rev-parse --short HEAD)"')
	print("\nKinto " + kintover + "Type in Linux like it's a Mac.\n")


def check_platform() -> str:
	# 检查系统平台
	if platform.system() == 'Windows':
		print("\nYou are detected as running Windows.")
		return Platform.win.value

	check_x11_command = "(env | grep -i x11 || loginctl show-session \"$XDG_SESSION_ID\" -p Type) | awk -F= '{print $2}'"
	check_x11 = cmdline(check_x11_command).strip()

	if len(check_x11) == 0:
		if os.name != 'nt':
			print("You are not using x11, please logout and back in using x11/Xorg")
			return Platform.other.value
		else:
			print("\nYou are detected as running Windows.")
			# windows_setup()
			return Platform.win.value
	return Platform.linux.value


def linux_setup(homedir, args):
	init_config_file(homedir)
	# 更新代码
	cmdline("git fetch")

	log_version()

	# 卸载
	if args.uninstall:
		# 与 call 方法类似，不同在于如果命令行执行成功，check_call返回返回码 0，否则抛出subprocess.CalledProcessError异常。
		# 当使用比较复杂的 shell 语句时，可以先使用 shlex 模块的 shlex.split() 方法来帮助格式化命令，然后在传递给 run() 方法或 Popen
		subprocess.check_call(shlex.split("./xkeysnail_service.sh uninstall"))
		exit()
	# 安装
	subprocess.check_call(shlex.split("./xkeysnail_service.sh"))


def main():
	parser = argparse.ArgumentParser()
	# 卸载 kinto
	parser.add_argument('-r', dest='uninstall', action='store_true', help="uninstall kinto")
	parser.add_argument('--remove', dest='uninstall', action='store_true', help="uninstall kinto")

	args = parser.parse_args()
	# 将参数中开头部分的 ~ 或 ~user 替换为当前用户的家目录并返回
	homedir = os.path.expanduser("~")

	plat_form = check_platform()
	command_map = {
		Platform.linux.value: linux_setup
	}
	action = command_map.get(plat_form)
	print(action, platform)
	if action:
		action(homedir, args)


if __name__ == "__main__":
	main()