import json
import requests

bvid = "BV1Yi4y1j7uV"
url = f"http://api.bilibili.com/x/web-interface/view?bvid={bvid}"

response = requests.request("GET", url)

data = response.json()
data = data.get("data", {})
data = {
    "pages": {p.get("part"): p.get("cid") for p in data.get("pages", {})},
    "title": data.get("title"),
}

with open("test/test.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4,ensure_ascii=False)

# print(json.dumps(data).encode('utf-8').decode('utf-8'))
