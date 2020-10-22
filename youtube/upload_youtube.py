import os
import sys
import json
import subprocess
video_path = r"G:\repo\bilibili-subtile-uploader\video\Python FBX SDK 入门教程 Introduction to the Python FBX SDK - bilibili\Videos\Introduction to the Python FBX SDK - Part 1 - Accessing the Textures in a Scene.mp4"
DIR = os.path.dirname(os.path.abspath(__file__))
youtubeuploader = os.path.join(DIR, "youtubeuploader.exe")
secrets = os.path.join(DIR, "client_secrets.json")
token = os.path.join(DIR, "request.token")

res = subprocess.check_output(
    [
        youtubeuploader,
        "-filename",
        video_path,
        "-secrets",
        secrets,
        "-cache",
        token,
    ]
)

# TODO 获取上传的 id
print(res)



