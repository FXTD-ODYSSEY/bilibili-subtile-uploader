import json
import requests

bvid = "BV1iV41127nj"
url = f"http://api.bilibili.com/x/web-interface/view?bvid={bvid}"

response = requests.request("GET", url)

data = json.loads(response.text.encode('utf8'))
data = {p.get("part"):p.get("cid") for p in data.get("data",{}).get("pages",{})}

print(data)
