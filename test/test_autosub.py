import json
import subprocess
import os

src = r"G:\repo\bilibili-subtile-uploader\video\【Houdini】游戏快速上手教程 GAMES QUICKSTART - bilibili\Videos\Games Quickstart 1 _ Interface Overview.mp4"
autosub = os.path.join(__file__,'..','..',"autosub","autosub.exe")
proxy = "http://127.0.0.1:12639"

# NOTE 调用 autosub 进行视频字幕生成
args = [autosub, "-i", f'"{src}"', "-S", "en-US"]
args.extend(["-hsp", proxy]) if proxy.startswith("http") else None

command = " ".join(args)

subprocess.call(command)
