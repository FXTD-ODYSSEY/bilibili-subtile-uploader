import re
import json
import requests

bvid = "BV1554y117vk"
url = f"http://api.bilibili.com/x/web-interface/view?bvid={bvid}"
# url = f"https://api.bilibili.com/x/player/pagelist?bvid={bvid}&jsonp=jsonp"

response = requests.request("GET", url)

def repair_filename(filename):
    """ 修复不合法的文件名 """
    def to_full_width_chr(matchobj):
        char = matchobj.group(0)
        full_width_char = chr(ord(char) + ord('？') - ord('?'))
        return full_width_char
    # 路径非法字符，转全角
    regex_path = re.compile(r'[\\/:*?"<>|]')
    # 空格类字符，转空格
    regex_spaces = re.compile(r'\s+')
    # 不可打印字符，移除
    regex_non_printable = re.compile(
        r'[\001\002\003\004\005\006\007\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
        r'\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a]')

    filename = regex_path.sub(to_full_width_chr, filename)
    filename = regex_spaces.sub(' ', filename)
    filename = regex_non_printable.sub('', filename)
    filename = filename.strip()
    filename = filename if filename else 'file_{:04}'.format(random.randint(0, 9999))
    return filename

data = response.json()
data = data.get("data", {})
data = {
    "pages": {repair_filename(p.get("part")): p.get("cid") for p in data.get("pages", {})},
    "title": data.get("title"),
}

with open("test/test.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False)

# print(json.dumps(data).encode('utf-8').decode('utf-8'))
