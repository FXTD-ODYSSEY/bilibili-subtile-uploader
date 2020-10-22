# -*- coding: utf-8 -*-
"""
youtube dl 获取 Private 字幕 (失败了)
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

__author__ = 'timmyliang'
__email__ = '820472580@qq.com'
__date__ = '2020-10-22 14:06:47'


import os
import sys
import subprocess
import glob
DIR = os.path.dirname(os.path.abspath(__file__))
youtube_dl = os.path.join(DIR, "youtube-dl.exe")
youtube_dlc = os.path.join(DIR, "youtube-dlc.exe")
output = os.path.join(DIR, "238638782")
cookies = os.path.join(DIR, "cookies.txt")
cookie = "Cookie:"
dump = os.path.join(DIR, "dump.html")
subprocess.call(
    [
        youtube_dlc,
        "https://www.youtube.com/watch?v=vGFPQYGFgfY",
        # "https://www.youtube.com/watch?v=lIDqeWbE0GE",
        "-o",
        output,
        "--convert-subs=srt",
        "--write-auto-sub",
        "--skip-download",
        # "--get-title",
        # "--force-generic-extractor",
        "--verbose",
        # '--add-header',
        # cookie,
        '--cookies',
        cookies,
        '--ignore-config',
        '--proxy',
        'http://127.0.0.1:12639',
        # '-u',
        # '820472580tim@gmail.com',
        # '-p',
        # '852456abc',
    ]
)

# for path in glob.iglob(f"{DIR}\\*.*.vtt", recursive=True):
#     name = os.path.splitext(path)[0]
#     subprocess.call(['ffmpeg','-i',path,f"{name}.srt"])




