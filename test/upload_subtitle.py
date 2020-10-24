import os
import sys
import json
import webbrowser
import requests
from urllib import parse

GET_INFO = False

url = "https://api.bilibili.com/x/v2/dm/subtitle/draft/save"

bvid = "BV1qf4y1B7D3"
oid = "245340306"

if GET_INFO:
    webbrowser.open_new_tab(f"http://api.bilibili.com/x/web-interface/view?bvid={bvid}")
    sys.exit(0)

config = os.path.join(__file__,'..','..','config.json')
with open(config,'r') as f:
    config = json.load(f)

csrf = ""
cookie = config.get('bilibili_cookie','')
for line in cookie.split(";"):
    line = line.strip()
    if line.startswith("bili_jct="):
        csrf = line[len("bili_jct=") :]

with open('test/test.bcc','r') as f:
    subtitle = f.read()

lang = "en-US"

payload = f'lan={lang}&submit=true&csrf={csrf}&sign=false&bvid={bvid}&type=1&oid={oid}&{parse.urlencode({"data":subtitle})}'

headers = {
    'Cookie': 'bfe_id=6f285c892d9d3c1f8f020adad8bed553; bili_jct=9f0d2f125fb02375a2938581cb08a373; sid=kq8c5ukb; DedeUserID=12895307; DedeUserID__ckMd5=4786945f2e41f323; SESSDATA=90c4a3a0%2C1611422137%2C5c6a6*71',
    'Content-Type': 'application/x-www-form-urlencoded'
}

response = requests.request("POST", url, headers=headers, data = payload)

print(response.text)
