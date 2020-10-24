import pysrt
import pyvtt
import time
from datetime import datetime
import json
import re
import os


class BccParserMixin(object):
    @staticmethod
    def srt2bcc(srt_path):
        """srt2bcc 将 srt 转换为 bcc B站字幕格式

        :param srt_path: srt 路径
        :type srt_path: srt
        :return: bcc json 数据
        :rtype: srt
        """
        subs = pysrt.open(srt_path)
        bcc = {
            "font_size": 0.4,
            "font_color": "#FFFFFF",
            "background_alpha": 0.5,
            "background_color": "#9C27B0",
            "Stroke": "none",
            "body": [
                {
                    "from": sub.start.ordinal / 1000,
                    "to": sub.end.ordinal / 1000,
                    "location": 2,
                    "content": sub.text,
                }
                for sub in subs
            ],
        }
        return bcc if subs else {}

    @staticmethod
    def vtt2bcc(path,threshold=0.1,word=True):
        path = path if path else ""
        if os.path.exists(path):
            subs = pyvtt.open(path)
        else:
            subs = pyvtt.from_string(path)
        # NOTE 按照 vtt 的断词模式分隔 bcc
        caption_list = []
        if not word:
            caption_list = [
                {
                    "from": sub.start.ordinal / 1000,
                    "to": sub.end.ordinal / 1000,
                    "location": 2,
                    "content": sub.text_without_tags.split("\n")[-1],
                }
                for sub in subs
            ]
        else:
            for i, sub in enumerate(subs):
                text = sub.text

                start = sub.start.ordinal / 1000
                end = sub.end.ordinal / 1000
                try:
                    idx = text.index("<")
                    pre_text = text[:idx]
                    regx = re.compile(r"<(.*?)><c>(.*?)</c>")
                    for t_str, match in regx.findall(text):
                        pre_text += match
                        t = datetime.strptime(t_str, r"%H:%M:%S.%f")
                        sec = (
                            t.hour * 3600
                            + t.minute * 60
                            + t.second
                            + t.microsecond / 10 ** len((str(t.microsecond)))
                        )
                        final_text = pre_text.split("\n")[-1]

                        if caption_list and (
                            sec - start <= threshold
                            or caption_list[-1]["content"] == final_text
                        ):
                            caption_list[-1].update(
                                {
                                    "to": sec,
                                    "content": final_text,
                                }
                            )
                        else:
                            caption_list.append(
                                {
                                    "from": start,
                                    "to": sec,
                                    "location": 2,
                                    "content": final_text,
                                }
                            )
                        start = sec
                except:
                    final_text = sub.text.split("\n")[-1]
                    if caption_list and caption_list[-1]["content"] == final_text:
                        caption_list[-1].update(
                            {
                                "to": end,
                                "content": final_text,
                            }
                        )
                    else:
                        if caption_list and end - start < threshold:
                            start = caption_list[-1]["to"]
                        caption_list.append(
                            {
                                "from": start,
                                "to": end,
                                "location": 2,
                                "content": final_text,
                            }
                        )

        # NOTE 避免超出视频长度
        last = caption_list[-1]
        last["to"] = last.get("from") + .1
        print(len(caption_list))
        bcc = {
            "font_size": 0.4,
            "font_color": "#FFFFFF",
            "background_alpha": 0.5,
            "background_color": "#9C27B0",
            "Stroke": "none",
            "body": caption_list,
        }

        return bcc if subs else {}


from urllib import parse

path = "test/test.vtt"
bcc = BccParserMixin.vtt2bcc(path,word=1)
# print(bcc)
with open("test/test.bcc", "w", encoding="utf-8") as f:
    json.dump(bcc, f, ensure_ascii=False)
    # data = parse.urlencode({"data":json.dumps(bcc)})
    # f.write(data)
