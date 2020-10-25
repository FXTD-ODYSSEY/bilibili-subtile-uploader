import os
import subprocess

srt_path = r"G:\repo\bilibili-subtile-uploader\video\【Houdini】游戏快速上手教程 GAMES QUICKSTART - bilibili\Videos\Games Quickstart 1 _ Interface Overview.en-us.srt"
autosub = os.path.join(__file__,'..','..',"autosub","autosub.exe")
autosub = os.path.abspath(autosub)
args = [autosub,'-i',f'"{srt_path}"','-SRC','"en"','-D','"zh-cn"']
command = " ".join(args)
print(command)
subprocess.call(command)
