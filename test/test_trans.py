import os
import subprocess

srt_path = r"G:\repo\bilibili-subtile-uploader\video\Python FBX SDK 入门教程 Introduction to the Python FBX SDK - bilibili\Videos\206840794.srt"
autosub = os.path.join(__file__,'..','..',"autosub","autosub.exe")
autosub = os.path.abspath(autosub)
args = [autosub,'-i',f'"{srt_path}"','-SRC','"en"','-D','"zh-cn"']
command = " ".join(args)
print(command)
subprocess.call(command)
