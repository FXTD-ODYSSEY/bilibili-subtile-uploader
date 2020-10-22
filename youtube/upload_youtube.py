import os
import re
import sys
import json
import subprocess
video_path = r"G:\repo\bilibili-subtile-uploader\video\Python FBX SDK 入门教程 Introduction to the Python FBX SDK - bilibili\Videos\Introduction to the Python FBX SDK - Part 2 - Searching for Texture Usage in the.mp4"
DIR = os.path.dirname(os.path.abspath(__file__))
youtubeuploader = os.path.join(DIR, "youtubeuploader.exe")
secrets = os.path.join(DIR, "client_secrets.json")
token = os.path.join(DIR, "request.token")
command = " ".join([
        youtubeuploader,
        "-filename",
        video_path,
        "-secrets",
        secrets,
        "-cache",
        token,
    ])
# print(command)
res = subprocess.check_output(command)

# TODO 获取上传的 id
res = res.decode("utf-8")
print(res)

regx = re.compile(r"Video ID: (.*)")
grp = regx.search(res)
if grp:
    match = grp.group(1)
    print(match)
    print('asd')



