import sys
import platform
from pathlib import Path
import subprocess

def run(cmd: list):
    print("\n>>>", " ".join(map(str, cmd)))
    subprocess.run(cmd, check=True)

def main():
    env_name = "warelytic"
    cwd = Path.cwd()
    env_path = cwd / env_name

    print(f"📦 当前目录: {cwd}")
    print(f"🔧 创建虚拟环境: {env_name}")

    # 1) 创建虚拟环境（使用当前解释器）
    run([sys.executable, "-m", "venv", str(env_path)])

    # 2) 定位虚拟环境的 python 与 pip
    if platform.system() == "Windows":
        python_exe = env_path / "Scripts" / "python.exe"
        activate_cmd = fr"{env_path}\Scripts\activate"
    else:
        python_exe = env_path / "bin" / "python"
        activate_cmd = f"source {env_path}/bin/activate"

    # 3) 升级 pip 并安装依赖
    req_file = cwd / "requirements.txt"
    if not req_file.exists():
        print("⚠️ 未找到 requirements.txt，已仅创建虚拟环境（未安装依赖）。")
    else:
        print("📦 开始安装依赖包...")
        run([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"])
        run([str(python_exe), "-m", "pip", "install", "-r", str(req_file)])

    print("\n🎉 环境部署完成！")
    print(f'👉 激活命令：\n   source "{env_path}/bin/activate"')
    if platform.system() == "Windows":
        print("   * PowerShell:  ".ljust(18), f"{env_path}\\Scripts\\Activate.ps1")
        print("   * CMD:        ".ljust(18), f"{env_path}\\Scripts\\activate.bat")

if __name__ == "__main__":
    main()

