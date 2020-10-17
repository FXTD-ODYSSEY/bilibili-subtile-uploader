# -*- coding: utf-8 -*-
"""

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

__author__ = 'timmyliang'
__email__ = '820472580@qq.com'
__date__ = '2020-10-17 22:13:40'


import os
import json
import codecs
import tempfile
import requests
import contextlib

from urllib import parse

import pysrt

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


class ConfigDumperMixin(object):
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
            json.dump(data, f,indent=4, ensure_ascii=False)


class ListVar(tk.Variable):
    @property
    def dict_data(self):
        return self._dict_data

    @dict_data.setter
    def dict_data(self, data):
        self._dict_data = data if isinstance(data, list) else []

    def set(self, val):
        val = next(iter(self._dict_data[val:]), "")
        return super(ListVar, self).set(val)

    def get(self):
        val = super(ListVar, self).get()
        return self._dict_data.index(val)


@contextlib.contextmanager
def TKFrame(*args, **kwargs):
    Frame = tk.Frame()
    yield Frame
    Frame.pack(**kwargs)


class BiliBili_SubtitleGenerator(tk.Frame, ConfigDumperMixin):

    LANG_LIST = [
        "en-US",
        "zh-CN",
    ]

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
        filemenu.add_command(label="使用说明", command=self.helpWin)
        filemenu.add_separator()
        filemenu.add_command(label="退出", command=self.onClosing)
        menubar.add_cascade(label="帮助", menu=filemenu)
        parent.config(menu=menubar)

        with TKFrame(side="top", fill="x", padx=5, pady=5) as Main_Frame:
            with TKFrame(side="top", fill="x", padx=15, pady=5) as Cookie_Frame:
                tk.Label(Cookie_Frame, text="登陆 Cookie").grid(row=0, column=0, sticky="nsew")
                self.Cookie = tk.StringVar()
                self.Cookie.trace('w', self.dump_config)
                entry = tk.Entry(Cookie_Frame, textvariable=self.Cookie)
                entry.grid(row=0, column=1, sticky="nsew")
                Cookie_Frame.grid_columnconfigure(1, weight=1)

            with TKFrame(side="top", fill="x", padx=15) as Lang_Frame:
                label = tk.Label(Lang_Frame, text="选择语言")
                label.grid(row=0, column=0, sticky="nsew")
                self.combo_index = ListVar()
                self.combo_index.dict_data = self.LANG_LIST
                self.combo_index.set(0)
                lang_combo = ttk.Combobox(
                    Lang_Frame, textvariable=self.combo_index, state="readonly"
                )
                lang_combo.grid(row=0, column=1, sticky="nsew")
                lang_combo["values"] = self.LANG_LIST
                lang_combo.bind("<<ComboboxSelected>>", self.dump_config)
                Lang_Frame.grid_columnconfigure(1, weight=1)

            with TKFrame(side="top", fill="x", padx=15, pady=5) as BV_Frame:
                tk.Label(BV_Frame, text="BV 号").grid(row=0, column=0, sticky="nsew")
                self.bv = tk.StringVar()
                self.bv.trace('w', self.dump_config)
                entry = tk.Entry(BV_Frame, textvariable=self.bv)
                entry.grid(row=0, column=1, sticky="nsew")
                BV_Frame.grid_columnconfigure(1, weight=1)

            gen_btn = tk.Button(Main_Frame, text="自动生成并上传字幕", command=self.run)
            gen_btn.pack(side="top", fill="x", padx=5)

    @staticmethod
    def time_to_seconds(t):
        return t.hours * 3600 + t.minutes * 60 + t.seconds + t.milliseconds / 1000

    @classmethod
    def parse_srt(cls, srt_path):
        bcc = {
            "font_size": 0.4,
            "font_color": "#FFFFFF",
            "background_alpha": 0.5,
            "background_color": "#9C27B0",
            "Stroke": "none",
            "body": [
                {
                    "from": cls.time_to_seconds(sub.start),
                    "to": cls.time_to_seconds(sub.end),
                    "location": 2,
                    "content": sub.text,
                }
                for sub in pysrt.open(srt_path)
            ],
        }
        return json.dumps(bcc)

    def helpWin(self):
        # NOTE 删除重复的窗口
        if self.help_win and self.help_win.winfo_exists():
            self.help_win.destroy()
        self.help_win = tk.Toplevel(self.parent)
        self.help_win.title("使用说明")
        text = "自动将 srt 字幕转换为 bcc 字幕上传到 B 站"
        tk.Label(self.help_win, text=text).pack(side="top", fill="x", padx=5, pady=5)

    def onClosing(self):
        self.parent.destroy()

    def run(self):
        pass

    def submit_subtitle(self):

        DIR = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(DIR, "config.json"), "r") as f:
            Cookie = json.load(f)

        csrf = ""
        for line in Cookie.get("Cookie").split(";"):
            line = line.strip()
            if line.startswith("bili_jct="):
                bili_jct = line[len("bili_jct=") :]
                break
        else:
            print("缺少 bili_jct 值")
            return

        url = "https://api.bilibili.com/x/v2/dm/subtitle/draft/save"

        subtitle = """{"font_size":0.4,"font_color":"#FFFFFF","background_alpha":0.5,"background_color":"#9C27B0","Stroke":"none","body":[{"from":4.19,"to":5.93,"location":2,"content":"Hire one."},{"from":6.13,"to":12.43,"location":2,"content":"Annd welcome to the set up section where I'll walk you through the steps in order to get started with"},{"from":12.49,"to":15.57,"location":2,"content":"coding for engine for at this point."},{"from":15.58,"to":19.46,"location":2,"content":"I assume you already have the engine installed and ready to go."},{"from":19.66,"to":26.2,"location":2,"content":"So I'll focus on setting up Visual Studio and highly recommended visual assist plugin which will significantly"},{"from":26.2,"to":30.71,"location":2,"content":"improve your quality of life when coding with C++ throughout the course."},{"from":30.73,"to":37.42,"location":2,"content":"I'll be using visualises for Intellisense and certain navigation Akis if you don't get Ulysses yet you"},{"from":37.42,"to":40.91,"location":2,"content":"can try the trial version for free in case you're wondering."},{"from":40.98,"to":46.79,"location":2,"content":"I will be using Unreal engine for 1:17 for of this course using a later version of the engine is OK"},{"from":46.84,"to":53.68,"location":2,"content":"but keep in mind that the look of the windows may change or that small API changes in C++ moniker to"},{"from":53.68,"to":54.67,"location":2,"content":"be absolutely safe."},{"from":54.67,"to":56.17,"location":2,"content":"Please use Fortran 17."},{"from":56.17,"to":61.36,"location":2,"content":"And please do notify me of any changes or issues you run into by posting in the Q and A board."},{"from":61.39,"to":66.76,"location":2,"content":"I will do my best to keep the videos up to date ones later additions of the engine are released and"},{"from":66.93,"to":70.86,"location":2,"content":"your help in pointing out inconsistencies will be greatly appreciated."}]}"""

        csrf = bili_jct
        bvid = "BV1Cv411k7iN"
        oid = "244626685"
        lan = "en-US"
        payload = f'lan={lan}&submit=true&csrf={csrf}&sign=false&bvid={bvid}&type=1&oid={oid}&{parse.urlencode({"data":subtitle})}'

        headers = {
            # "referer": "https://account.bilibili.com/subtitle/edit/",
            # "origin": "https://account.bilibili.com",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        headers.update(Cookie)

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text.encode("utf8"))


if __name__ == "__main__":
    # submit_subtitle()
    root = tk.Tk()
    BiliBili_SubtitleGenerator(root)
    root.mainloop()
