#!/usr/bin/env python3
"""
构建脚本 - 用于构建和发布 kerykeion-mcp 包
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(cmd, cwd=None, check=True):
    """运行命令并返回结果"""
    print(f"执行: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"命令失败: {e}")
        if e.stderr:
            print(f"错误输出: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def check_uv():
    """检查 uv 是否安装"""
    try:
        run_command(["uv", "--version"], check=False)
        return True
    except FileNotFoundError:
        return False


def build_with_uv():
    """使用 uv 构建包"""
    print("使用 uv 构建包...")
    run_command(["uv", "build"])
    print("构建完成!")


def build_with_python():
    """使用 Python 构建包"""
    print("使用 Python 构建包...")
    try:
        import build
        print("使用 build 模块构建...")
    except ImportError:
        print("安装 build 模块...")
        run_command([sys.executable, "-m", "pip", "install", "build"])

    run_command([sys.executable, "-m", "build"])
    print("构建完成!")


def test_package():
    """测试构建的包"""
    print("测试包安装...")
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("dist 目录不存在，请先构建包")
        return False

    # 找到最新的 wheel 文件
    wheel_files = list(dist_dir.glob("*.whl"))
    if not wheel_files:
        print("未找到 wheel 文件")
        return False

    latest_wheel = max(wheel_files, key=lambda x: x.stat().st_mtime)
    print(f"测试安装: {latest_wheel.name}")

    # 在临时环境中测试安装
    run_command([sys.executable, "-m", "pip", "install", str(latest_wheel), "--force-reinstall"])

    # 测试导入（在子进程中避免当前目录干扰）
    print("测试导入...")
    test_script = """
import sys
import os
# 确保不从当前目录导入
sys.path = [p for p in sys.path if p != os.getcwd()]
try:
    import kerykeion_mcp
    print(f"成功导入 kerykeion_mcp 版本: {kerykeion_mcp.__version__}")
    print("包测试成功!")
    sys.exit(0)
except ImportError as e:
    print(f"导入失败: {e}")
    sys.exit(1)
"""

    # 写入临时测试脚本
    test_file = Path("test_import.py")
    test_file.write_text(test_script)

    try:
        run_command([sys.executable, str(test_file)])
        return True
    except subprocess.CalledProcessError:
        return False
    finally:
        # 清理临时文件
        test_file.unlink(missing_ok=True)


def publish_package():
    """发布包到 PyPI"""
    print("发布包到 PyPI...")

    # 检查是否已安装 twine
    try:
        import twine
    except ImportError:
        print("安装 twine...")
        run_command([sys.executable, "-m", "pip", "install", "twine"])

    # 上传到 PyPI
    print("上传到 PyPI...")
    run_command(["python", "-m", "twine", "upload", "dist/*"])

    print("发布完成!")


def main():
    """主函数"""
    print("Kerykeion MCP 包构建脚本")
    print("=" * 40)

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
    else:
        command = "build"

    if command == "build":
        # 构建包
        if check_uv():
            build_with_uv()
        else:
            build_with_python()

        # 测试包
        if test_package():
            print("\n构建和测试成功!")
            print("\n如需发布到 PyPI，请运行:")
            print("python build.py publish")
        else:
            print("\n构建成功但测试失败，请检查问题")
            sys.exit(1)

    elif command == "test":
        # 只测试
        if test_package():
            print("测试成功!")
        else:
            print("测试失败!")
            sys.exit(1)

    elif command == "publish":
        # 发布包
        confirm = input("确定要发布到 PyPI 吗? (y/N): ")
        if confirm.lower() in ['y', 'yes']:
            publish_package()
        else:
            print("取消发布")

    elif command == "clean":
        # 清理构建文件
        print("清理构建文件...")
        run_command(["rm", "-rf", "dist", "build", "*.egg-info"])
        print("清理完成!")

    else:
        print(f"未知命令: {command}")
        print("可用命令: build, test, publish, clean")
        sys.exit(1)


if __name__ == "__main__":
    main()
