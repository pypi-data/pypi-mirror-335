import os
import sys
import subprocess
import requests
from packaging import version

# 定义常量
PYTHON_FILE = "easynotes.py"  # 要执行的 Python 文件名
PACKAGE_NAME = "easynotes"    # 对应的 PyPI 包名

# 获取当前目录
current_file_path = __file__
current_directory = os.path.dirname(os.path.abspath(current_file_path))

# 拼接文件的完整路径
python_file_path = os.path.join(current_directory, PYTHON_FILE)

# 获取当前运行脚本的 Python 解释器名称
#python_executable = sys.executable
import shutil
python_executable = shutil.which('python3') or shutil.which('python')
print(f"当前 Python 解释器路径: {python_executable}")

# 获取 PyPI 上指定包的最新版本
def get_latest_version(package_name):
    """获取 PyPI 上指定包的最新版本"""
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=5)
        response.raise_for_status()
        return response.json()["info"]["version"]
    except Exception as e:
        print(f"错误: 无法从 PyPI 获取 {package_name} 的最新版本: {e}")
        return None

# 获取当前安装的指定包版本
def get_installed_version(package_name):
    """获取当前安装的指定包的版本"""
    try:
        # 使用 python -m pip show 获取包信息
        result = subprocess.run(
            [python_executable, "-m", "pip", "show", package_name],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        for line in result.stdout.splitlines():
            if line.startswith("Version:"):
                return line.split(":")[1].strip()
        return None
    except subprocess.CalledProcessError as e:
        print(f"错误: 无法获取 {package_name} 的安装版本: {e.stderr}")
        return None
    except FileNotFoundError as e:
        print(f"错误: 未找到 Python 或 pip 命令: {e}")
        return None

# 更新指定包到最新版本
def update_package(package_name):
    """更新指定包到最新版本"""
    try:
        print(f"正在更新 {package_name} 包...")
        subprocess.run(
            [python_executable, "-m", "pip", "install", "--upgrade", package_name],
            check=True,
        )
        print(f"{package_name} 包已更新到最新版本。")
    except subprocess.CalledProcessError as e:
        print(f"错误: 更新 {package_name} 包失败: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"错误: 未找到 Python 或 pip 命令: {e}")
        sys.exit(1)

# 检查并更新指定包
def check_and_update_package(package_name):
    """检查并更新指定包"""
    latest_version = get_latest_version(package_name)
    if not latest_version:
        print(f"警告: 无法获取 {package_name} 的最新版本，跳过更新。")
        return

    installed_version = get_installed_version(package_name)
    if not installed_version:
        print(f"{package_name} 未安装，正在安装最新版本...")
        update_package(package_name)
        return

    if version.parse(installed_version) < version.parse(latest_version):
        print(f"当前安装的 {package_name} 版本 ({installed_version}) 不是最新的，最新版本为 {latest_version}。")
        update_package(package_name)
    else:
        print(f"{package_name} 已是最新版本 ({installed_version})。")

# 主逻辑
def main():
    # 检查并更新包
    check_and_update_package(PACKAGE_NAME)

    # 检查文件是否存在
    if not os.path.exists(python_file_path):
        print(python_file_path)
        print(f"错误: 当前目录下未找到 {PYTHON_FILE} 文件。")
        sys.exit(1)

    # 执行文件
    try:
        #print(f"正在执行 {PYTHON_FILE} 文件...")
        subprocess.run([python_executable, python_file_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"执行 {PYTHON_FILE} 文件时出错: {e.stderr}")
    except FileNotFoundError as e:
        print(f"错误: 未找到 Python 或文件: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")

main()
