
import requests
import json
import re
import requests

url = "https://www.youtube.com/watch?v=iMTvTh5J5Og"

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


pattern = re.escape(r'"captionTracks":[{"baseUrl":')
regx = re.search(f'{pattern}"(.*?)"',html)
if regx:
    url = regx.group(1)
    url_line = []
    for param in url.split(r'\u0026'):
    # #     if param.startswith('lang'):
    # #         param = 'lang=zh'
        url_line.append(param)
    # url_line.append('fmt=vtt')
    url = url.replace(r'\u0026',"&")
    url += "&fmt=vtt"
    # print(url)
    vtt = requests.request("GET", url)
    print(vtt.text)
