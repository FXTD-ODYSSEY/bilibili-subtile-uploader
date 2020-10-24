
import requests
import json
import re
import requests

url = "https://www.youtube.com/watch?v=r2PJpoHNzh4"

payload = {}
headers = {
    'authority': 'www.youtube.com',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3775.400 QQBrowser/10.6.4209.400',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    # 'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cookie': ''
}

response = requests.request("GET", url, headers=headers, data = payload)

html = response.text
# print(html)

# with open('test.html','w') as f:
#     f.write(html)


pattern = re.escape(r'"captionTracks":[{"baseUrl":')
regx = re.search(f'{pattern}"(.*?)"',html)
if regx:
    url = regx.group(1)
    url = url.replace(r'\u0026',"&")
    url += "&fmt=vtt"
    # url += "&tlang=zh-Hans"
    vtt = requests.request("GET", url)
    # # NOTE 清除 youtube vtt 第5行 空行
    text = vtt.text
    text = "\n".join([line for i,line in enumerate(text.splitlines()) if i != 5])
    with open('test.vtt','w',encoding="utf-8") as f:
        f.write(text)
else:
    print("not match")