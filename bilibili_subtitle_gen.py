# -*- coding: utf-8 -*-
"""

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

__author__ = "timmyliang"
__email__ = "820472580@qq.com"
__date__ = "2020-10-17 22:13:40"


import os
import re
import sys
import json
import tempfile
import requests
import contextlib
import subprocess

from urllib import parse

import pysrt
import pyvtt

# NOTE Python 3 & 2 兼容
try:
    import tkinter as tk
    from tkinter import ttk
    from tkinter import filedialog, messagebox
except:
    import ttk
    import Tkinter as tk
    import tkFileDialog as filedialog
    import tkMessageBox as messagebox

LANG_LIST = [
    "en-US",
    "zh-CN",
]

VIDEO_QUALITY_LIST = [
    "360P(推荐)",
    "480P",
    "720P",
    "720P60",
    "1080P",
    "1080P+",
    "1080P60",
    "4K",
]
VIDEO_QUALITY_DICT = {
    "360P(推荐)": 16,
    "480P": 32,
    "720P": 64,
    "720P60": 74,
    "1080P": 80,
    "1080P+": 112,
    "1080P60": 116,
    "4K": 120,
}
#   -q {120,116,112,80,74,64,32,16}, --quality {120,116,112,80,74,64,32,16}
#                         视频清晰度 120:4K, 116:1080P60, 112:1080P+, 80:1080P, 74:720P60, 64:720P, 32:480P, 16:360P
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


class ConfigDumperMixin(object):
    """ConfigDumperMixin
    自动记录 Tkinter Variable 配置
    """

    @staticmethod
    def load_deco(func):
        def wrapper(self, *args, **kwargs):
            res = func(self, *args, **kwargs)
            self.load_config()
            return res

        return wrapper

    @property
    def config_path(self):
        # return os.path.join(tempfile.gettempdir(), f"{self.__class__.__name__}.json")
        return os.path.join(__file__, "..", "config.json")

    def get_tkinter_varaible(self):
        return [var for var in dir(self) if isinstance(getattr(self, var), tk.Variable)]

    def load_config(self, *args, **kwargs):
        path = kwargs.get("path", "")
        path = path if path else self.config_path
        if not os.path.exists(path):
            return

        with open(path, "r") as f:
            config = json.load(f, encoding="utf-8")
            [getattr(self, var).set(val) for var, val in config.items()]

    def dump_config(self, *args, **kwargs):
        path = kwargs.get("path", "")
        path = path if path else self.config_path
        data = {var: getattr(self, var).get() for var in self.get_tkinter_varaible()}
        with open(path, "w") as f:
            # f.write(json.dumps(data))
            json.dump(data, f, indent=4, ensure_ascii=False)


class ListVar(tk.Variable):
    """ListVar
    自动将 ListVar 数据映射为对应序号
    """

    @property
    def list_data(self):
        return self._list_data

    @list_data.setter
    def list_data(self, data):
        self._list_data = data if isinstance(data, list) else []

    def set(self, val):
        val = next(iter(self._list_data[val:]), "")
        return super(ListVar, self).set(val)

    def get(self):
        val = super(ListVar, self).get()
        return self._list_data.index(val)


@contextlib.contextmanager
def TKFrame(*args, **kwargs):
    Frame = tk.Frame(*args)
    yield Frame
    Frame.pack(**kwargs)


@contextlib.contextmanager
def TKLabelFrame(*args, **kwargs):
    frame = kwargs.get("frame", {})
    pack = kwargs.get("pack", {})
    args = frame.pop("__args__", [])
    args.extend(args)
    Frame = tk.LabelFrame(*args, **frame)
    yield Frame
    Frame.pack(**pack)


class BiliBili_SubtitleGenerator(tk.Frame, ConfigDumperMixin, BccParserMixin):
    @ConfigDumperMixin.load_deco
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.help_win = None

        parent.title("BiliBili 字幕上传工具")
        parent.protocol("WM_DELETE_WINDOW", self.onClosing)

        # NOTE 生成菜单
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="使用说明", command=self.show_help_win)
        filemenu.add_separator()
        filemenu.add_command(label="退出", command=self.onClosing)
        menubar.add_cascade(label="帮助", menu=filemenu)
        parent.config(menu=menubar)

        self.bilibili_cookie = tk.StringVar()
        self.bilibili_cookie.trace("w", self.dump_config)

        self.youtube_cookie = tk.StringVar()
        self.youtube_cookie.trace("w", self.dump_config)
        self.youtube_cn = tk.IntVar()

        self.lang_index = ListVar()
        self.lang_index.list_data = LANG_LIST
        self.lang_index.set(0)

        self.video_quality_index = ListVar()
        self.video_quality_index.list_data = VIDEO_QUALITY_LIST
        self.video_quality_index.set(0)

        self.bv = tk.StringVar()
        self.bv.trace("w", self.dump_config)

        self.proxy = tk.StringVar()
        self.proxy.trace("w", self.dump_config)

        pack_config = {"side": "top", "fill": "x", "padx": 5, "pady": 5}

        with TKFrame(**pack_config) as Cookie_Frame:
            text = "Bilibili 登陆 Cookie"
            tk.Label(Cookie_Frame, text=text).grid(row=0, column=0, sticky="nsew")
            entry = tk.Entry(Cookie_Frame, textvariable=self.bilibili_cookie)
            entry.grid(row=0, column=1, sticky="nsew")
            Cookie_Frame.grid_columnconfigure(1, weight=1)

        with TKFrame(**pack_config) as BV_Frame:
            tk.Label(BV_Frame, text="BV 号").grid(row=0, column=0, sticky="nsew")
            entry = tk.Entry(BV_Frame, textvariable=self.bv)
            entry.grid(row=0, column=1, sticky="nsew")
            BV_Frame.grid_columnconfigure(1, weight=1)

        # NOTE 视频质量下载
        with TKFrame(**pack_config) as Quality_Frame:
            label = tk.Label(Quality_Frame, text="视频质量")
            label.grid(row=0, column=0, sticky="nsew")

            lang_combo = ttk.Combobox(
                Quality_Frame,
                textvariable=self.video_quality_index,
                values=self.video_quality_index.list_data,
                state="readonly",
            )
            lang_combo.grid(row=0, column=1, sticky="nsew")
            lang_combo.bind("<<ComboboxSelected>>", self.dump_config)
            Quality_Frame.grid_columnconfigure(1, weight=1)

        with TKFrame(**pack_config) as Proxy_Frame:
            text = "代理地址(空值则不代理)"
            tk.Label(Proxy_Frame, text=text).grid(row=0, column=0, sticky="nsew")
            entry = tk.Entry(Proxy_Frame, textvariable=self.proxy)
            entry.grid(row=0, column=1, sticky="nsew")
            Proxy_Frame.grid_columnconfigure(1, weight=1)

        with TKLabelFrame(
            frame={"text": "AutoSub 生成机翻字幕"},
            pack={"side": "top", "fill": "x", "padx": 5, "pady": 5},
        ) as Trans_Frame:
            pack_config = {"side": "top", "fill": "x", "padx": 15, "pady": 5}

            gen_btn = tk.Button(Trans_Frame, text="自动生成并上传字幕", command=self.autoSub_run)
            gen_btn.pack(side="top", fill="x", padx=5, pady=5)

        with TKLabelFrame(
            frame={"text": "Youtube 上传视频获取机翻字幕"},
            pack={"side": "top", "fill": "x", "padx": 5, "pady": 5},
        ) as Youtube_Frame:

            # NOTE 双语字幕上传 Checkbox 确认
            c1 = tk.Checkbutton(
                Youtube_Frame,
                text="中文字幕下载并上传",
                variable=self.youtube_cn,
                onvalue=1,
                offvalue=0,
                command=self.dump_config,
            )
            c1.pack(side="top", fill="x", padx=5, pady=5)
            with TKFrame(Youtube_Frame, **pack_config) as Cookie_Frame:
                text = "Youtube 登陆 Cookie"
                tk.Label(Cookie_Frame, text=text).grid(row=0, column=0, sticky="nsew")
                entry = tk.Entry(Cookie_Frame, textvariable=self.youtube_cookie)
                entry.grid(row=0, column=1, sticky="nsew")
                Cookie_Frame.grid_columnconfigure(1, weight=1)

            gen_btn = tk.Button(
                Youtube_Frame, text="自动生成并上传字幕", command=self.youtube_run
            )
            gen_btn.pack(side="top", fill="x", padx=5, pady=5)

        with TKLabelFrame(
            frame={"text": "批量上传现有字幕"},
            pack={"side": "top", "fill": "x", "padx": 5, "pady": 5},
        ) as Upload_Frame:

            with TKFrame(Upload_Frame, **pack_config) as Lang_Frame:
                label = tk.Label(Lang_Frame, text="选择语言")
                label.grid(row=0, column=0, sticky="nsew")

                lang_combo = ttk.Combobox(
                    Lang_Frame,
                    textvariable=self.lang_index,
                    values=self.lang_index.list_data,
                    state="readonly",
                )
                lang_combo.grid(row=0, column=1, sticky="nsew")
                lang_combo["values"] = LANG_LIST
                lang_combo.bind("<<ComboboxSelected>>", self.dump_config)
                Lang_Frame.grid_columnconfigure(1, weight=1)

            gen_btn = tk.Button(
                Upload_Frame, text="选择字幕文件进行上传", command=self.upload_subtile
            )
            gen_btn.pack(side="top", fill="x", padx=5, pady=5)

    def show_help_win(self):
        # NOTE 删除重复的窗口
        if self.help_win and self.help_win.winfo_exists():
            self.help_win.destroy()
        self.help_win = tk.Toplevel(self.parent)
        self.help_win.title("使用说明")
        text = "Cookie 通过登陆在浏览器控制台中获取"
        tk.Label(self.help_win, text=text).pack(side="top", fill="x", padx=5, pady=5)
        text = "自动将 srt 字幕转换为 bcc 字幕上传到 B 站"
        tk.Label(self.help_win, text=text).pack(side="top", fill="x", padx=5, pady=5)

    def onClosing(self):
        self.parent.destroy()

    @staticmethod
    def check_variable(func):
        def _check(self):
            # Note 检查输入是否合法
            bv = self.bv.get()
            cookie = self.bilibili_cookie.get()

            if not bv or not cookie:
                msg = "缺少输入参数"
                print(msg)
                tk.messagebox.showwarning("警告", msg)
                return False

            for line in cookie.split(";"):
                line = line.strip()
                if line.startswith("bili_jct="):
                    self.bili_jct = line[len("bili_jct=") :]
                    break
            else:
                msg = "缺少 bili_jct 值"
                print(msg)
                tk.messagebox.showwarning("警告", msg)
                return False
            return True

        def wrapper(self, *args, **kwargs):
            if not _check(self):
                return
            return func(self, *args, **kwargs)

        return wrapper

    @check_variable.__func__
    def autoSub_run(self):

        autosub = os.path.join(__file__, "..", "autosub", "autosub.exe")
        if not os.path.isfile(autosub):
            msg = f"{autosub} 路径不存在\n请到 https://github.com/BingLingGroup/autosub/releases 页面下载最新版本的 autosub.exe 程序"
            print(msg)
            tk.messagebox.showwarning("警告", msg)
            return

        proxy = self.proxy.get()
        for bvid in self.bvid_list:
            self.bvid = bvid

            # NOTE 查询下载的视频对应的 oid
            info = self.get_video_info(bvid)

            # NOTE 下载视频
            self.download_video()

            # NOTE 修改视频名称为 oid
            title = info.get("title").replace("&amp;", "&")
            pages = info.get("pages")

            video = os.path.join(
                __file__, "..", "video", f"{title} - bilibili", "Videos"
            )

            for p, oid in pages.items():
                src = os.path.join(video, f"{p}.mp4")
                if not os.path.isfile(src):
                    continue

                # NOTE 调用 autosub 进行视频字幕生成
                args = [autosub, "-i", f'"{src}"', "-S", self.lang]
                args.extend(["-hsp", proxy]) if proxy.startswith("http") else None

                command = " ".join(args)

                src = os.path.join(video, f"{p}.{self.lang.lower()}.srt")
                os.remove(src) if os.path.isfile(src) else None

                subprocess.call(command)

                srt_path = os.path.join(video, f"{oid}.srt")
                os.remove(srt_path) if os.path.isfile(srt_path) else None

                os.rename(src, srt_path)

                subtitle = self.srt2bcc(srt_path)
                self.submit_subtitle(subtitle, oid, self.lang)

        tk.messagebox.showinfo("恭喜你", f"{self.bvid} 字幕上传成功")

    @check_variable.__func__
    def youtube_run(self):
        youtube = os.path.join(__file__, "..", "youtube")
        youtubeuploader = os.path.join(youtube, "youtubeuploader.exe")
        secrets = os.path.join(youtube, "client_secrets.json")
        token = os.path.join(youtube, "request.token")

        if not os.path.exists(youtubeuploader):
            msg = f"{youtubeuploader} 路径不存在"
            print(msg)
            tk.messagebox.showwarning("警告", msg)
            return
        elif not os.path.exists(token):
            msg = f"{token} 路径不存在"
            print(msg)
            tk.messagebox.showwarning("警告", msg)
            return
        elif not os.path.exists(secrets):
            msg = f"{secrets} 路径不存在"
            print(msg)
            tk.messagebox.showwarning("警告", msg)
            return

        for bvid in self.bvid_list:
            self.bvid = bvid
            info = self.get_video_info(bvid)

            # NOTE 下载视频
            self.download_video()

            # NOTE 修改视频名称为 oid
            title = info.get("title").replace("&amp;", "&")
            pages = info.get("pages")

            video = os.path.join(
                __file__, "..", "video", f"{title} - bilibili", "Videos"
            )

            for p, oid in pages.items():
                src = os.path.join(video, f"{p}.mp4")
                if not os.path.isfile(src):
                    continue
                    
                # TODO 上传到 youtube
                res = subprocess.check_output(
                    [
                        youtubeuploader,
                        "-filename",
                        src,
                        "-secrets",
                        secrets,
                        "-cache",
                        token,
                    ]
                )

                # TODO 下载 youtube 字幕

    @check_variable.__func__
    def upload_subtile(self):
        directory = filedialog.askdirectory()
        if not directory:
            return

        info = self.get_video_info()
        pages = info.get("pages")
        for root, _, files in os.walk(directory):
            for f in files:
                name = f[: -len(".srt")]
                oid = pages.get(name)
                if oid:
                    continue

                path = os.path.join(root, f)
                if f.endswith(".srt"):
                    subtitle = self.srt2bcc(path)
                elif f.endswith(".vtt"):
                    subtitle = self.vtt2bcc(path)
                else:
                    continue

                self.submit_subtitle(subtitle, oid, self.lang)

    @property
    def bvid_list(self):
        bv = self.bv.get()
        return [
            v
            for v in re.split(r"/|\\|\?| ", bv)
            if v.lower().startswith("bv") or v.lower().startswith("av")
        ]

    @property
    def lang(self):
        return self.lang_index.list_data[self.lang_index.get()]

    @property
    def quality(self):
        return self.video_quality_index.list_data[self.video_quality_index.get()]

    def get_video_info(self, bvid=""):
        bvid = bvid if bvid else self.bvid
        url = f"http://api.bilibili.com/x/web-interface/view?bvid={bvid}"

        response = requests.request("GET", url)

        data = json.loads(response.text.encode("utf8")).get("data", {})

        return {
            "title": data.get("title"),
            "pages": {p.get("part"): p.get("cid") for p in data.get("pages", {})},
        }

    def download_video(self):

        output_path = os.path.join(__file__, "..", "video")
        if not os.path.exists(output_path):
            os.mkdir(output_path)
        subprocess.call(
            [
                "bilili",
                f"https://www.bilibili.com/video/{self.bvid}",
                "-d",
                f"{output_path}",
                "-y",
                "--danmaku",
                "no",
                "--playlist-type",
                "no",
                "-q",
                f"{VIDEO_QUALITY_DICT.get(self.quality,16)}",
                "--audio-quality",
                "30280",
            ]
        )

    def submit_subtitle(self, subtitle, oid, lang="en-US"):
        subtitle = subtitle if isinstance(subtitle, dict) else {}
        if not subtitle or not oid:
            print(f"{oid} 文件为空 - 跳过")
            return
        subtitle = json.dumps(subtitle)

        csrf = self.bili_jct
        # oid = "244626685"
        payload = f'lan={lang}&submit=true&csrf={csrf}&sign=false&bvid={self.bvid}&type=1&oid={oid}&{parse.urlencode({"data":subtitle})}'

        headers = {
            # "referer": "https://account.bilibili.com/subtitle/edit/",
            # "origin": "https://account.bilibili.com",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        headers.update({"Cookie": self.bilibili_cookie.get()})

        url = "https://api.bilibili.com/x/v2/dm/subtitle/draft/save"
        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text.encode("utf8"))


if __name__ == "__main__":
    root = tk.Tk()
    BiliBili_SubtitleGenerator(root)
    root.mainloop()
