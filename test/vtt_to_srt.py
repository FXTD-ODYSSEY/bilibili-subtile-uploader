import pysrt
import pyvtt
import time
from datetime import datetime
import json
import re


class BccParserMixin(object):
    @staticmethod
    def srt2bcc(cls, srt_path):
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
    def vtt2bcc(cls, path):
        
        subs = pyvtt.open(path)
        # NOTE 按照 vtt 的断词模式分隔 srt
        # caption_list = []
        # for i, sub in enumerate(subs):
        #     text = sub.text
        #     start = sub.start.ordinal / 1000
        #     try:
        #         idx = text.index("<")
        #         pre_text = text[:idx]
        #         regx = re.compile(r"<(.*?)><c>(.*?)</c>")
        #         match_list = regx.findall(text)
        #         for t_str,match in match_list:
        #             pre_text += match
        #             t = datetime.strptime(t_str, r"%H:%M:%S.%f")
        #             sec = (
        #                 t.hour * 3600
        #                 + t.minute * 60
        #                 + t.second
        #                 + t.microsecond / 10 ** len((str(t.microsecond)))
        #             )
        #             if sec - start > 0.1:
        #                 caption_list.append(
        #                     {
        #                         "from": start,
        #                         "to": sec,
        #                         "location": 2,
        #                         "content": pre_text,
        #                     }
        #                 )
        #             start = sec
        #     except:
        #         caption_list.append(
        #             {
        #                 "from": sub.start.ordinal / 1000,
        #                 "to": sub.end.ordinal / 1000,
        #                 "location": 2,
        #                 "content": sub.text,
        #             }
        #         )

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
                    "content": sub.text_without_tags,
                }
                for sub in subs
            ],
        }
        return bcc if subs else {}


from urllib import parse
path = "test.vtt"
bcc = BccParserMixin.vtt2bcc(path)
with open('test.bcc','w') as f:
    json.dump(bcc,f)
    # data = parse.urlencode({"data":json.dumps(bcc)})
    # f.write(data)

# subs = pyvtt.open(path)
# caption_list = []
# for i, sub in enumerate(subs):
#     if i == 0:
#         print(sub)
#         break
#         print("=========================")
#         start = sub.start.ordinal / 1000
#         text = sub.text
#         # print(text)

#         idx = text.index("<")
#         pre_text = text[:idx]
#         regx = re.compile(r"<(.*?)><c>(.*?)</c>")
#         match_list = regx.findall(text)
#         for t_str, match in match_list:
#             pre_text += match
#             t = datetime.strptime(t_str, r"%H:%M:%S.%f")
#             sec = (
#                 t.hour * 3600
#                 + t.minute * 60
#                 + t.second
#                 + t.microsecond / 10 ** len((str(t.microsecond)))
#             )
#             caption_list.append(
#                 {
#                     "from": start,
#                     "to": sec,
#                     "location": 2,
#                     "content": pre_text,
#                 }
#             )
#             start = sec

# print(caption_list)