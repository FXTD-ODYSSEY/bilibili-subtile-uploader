from selenium_firefox import YouTubeUploader
import os
import json
uploader = YouTubeUploader("")
uploader.bilibili_login()
youtube_folder = os.path.join(__file__, "..", "youtube2oid")
for j in os.listdir(youtube_folder):
    if not j.endswith(".json"):
        continue

    output = os.path.join(youtube_folder, j)
    bvid = j[:-5]
    with open(output, "r") as f:
        info = json.load(f)
        if info.get("upload"):
            continue
    
    print(f"上传 {j}")
    youtube2oid = info.get("youtube2oid")
    for youtube_id, oid in youtube2oid.items():
        uploader.bilibili_upload(bvid,oid)
        break

# uploader.quit()