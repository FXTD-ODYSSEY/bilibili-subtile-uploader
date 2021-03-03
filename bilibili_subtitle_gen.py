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
import copy
import random
import tempfile
import requests
import contextlib
import subprocess
from datetime import datetime
from urllib import parse

import pysrt
import pyvtt

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox

from selenium_firefox import YouTubeUploader

import selenium_firefox




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
    def vtt2bcc(path, threshold=0.1, word=True):
        path = path if path else ""
        if os.path.exists(path):
            subs = pyvtt.open(path)
        else:
            subs = pyvtt.from_string(path)

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
            # NOTE 按照 vtt 的断词模式分隔 bcc
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

        # print(len(caption_list))
        # NOTE 避免超出视频长度
        last = caption_list[-1]
        last["to"] = last.get("from") + 0.1
        bcc = {
            "font_size": 0.4,
            "font_color": "#FFFFFF",
            "background_alpha": 0.5,
            "background_color": "#9C27B0",
            "Stroke": "none",
            "body": caption_list,
        }

        return bcc if subs else {}


class ConfigDumperMixin(object):
    """ConfigDumperMixin
    自动记录 Tkinter Variable 配置
    """

    @staticmethod
    def auto_load(func):
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
    @ConfigDumperMixin.auto_load
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.help_win = None
        self.youtube_folder = os.path.join(__file__, "..", "oid2youtube")
        if not os.path.isdir(self.youtube_folder):
            os.mkdir(self.youtube_folder)
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
        self.youtube_username = tk.StringVar()
        self.youtube_username.trace("w", self.dump_config)
        self.youtube_password = tk.StringVar()
        self.youtube_password.trace("w", self.dump_config)
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

            with TKFrame(Youtube_Frame, **pack_config) as Username_Frame:
                text = "Yotube 用户名"
                tk.Label(Username_Frame, text=text).grid(row=0, column=0, sticky="nsew")
                entry = tk.Entry(Username_Frame, textvariable=self.youtube_username)
                entry.grid(row=0, column=1, sticky="nsew")
                Username_Frame.grid_columnconfigure(1, weight=1)

            with TKFrame(Youtube_Frame, **pack_config) as Password_Frame:
                text = "Yotube 登陆密码"
                tk.Label(Password_Frame, text=text).grid(row=0, column=0, sticky="nsew")
                entry = tk.Entry(
                    Password_Frame, show="*", textvariable=self.youtube_password
                )
                entry.grid(row=0, column=1, sticky="nsew")
                Password_Frame.grid_columnconfigure(1, weight=1)

            gen_btn = tk.Button(
                Youtube_Frame, text="上传 youtube 视频", command=self.youtube_selenium_run
            )

            gen_btn.pack(side="top", fill="x", padx=5, pady=5)

            gen_btn = tk.Button(
                Youtube_Frame,
                text="下载字幕 | 上传B站",
                command=self.submit_youtube_subtitle_run,
            )
            gen_btn.pack(side="top", fill="x", padx=5, pady=5)

        with TKLabelFrame(
            frame={"text": "AutoSub 生成机翻字幕"},
            pack={"side": "top", "fill": "x", "padx": 5, "pady": 5},
        ) as Trans_Frame:
            pack_config = {"side": "top", "fill": "x", "padx": 15, "pady": 5}
            gen_btn = tk.Button(Trans_Frame, text="自动生成并上传字幕", command=self.autoSub_run)
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
        text = "网站的 Cookie 信息可以通过安装 EditThisCookie 浏览器插件获取"
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
            res = func(self, *args, **kwargs)
            msg = "处理完成"
            print(msg)
            tk.messagebox.showinfo("恭喜你", msg)
            return res

        return wrapper

    @staticmethod
    def repair_filename(filename):
        """ Ref : bilili utils/base.py """

        def to_full_width_chr(matchobj):
            char = matchobj.group(0)
            full_width_char = chr(ord(char) + ord("？") - ord("?"))
            return full_width_char

        # 路径非法字符，转全角
        regex_path = re.compile(r'[\\/:*?"<>|]')
        # 空格类字符，转空格
        regex_spaces = re.compile(r"\s+")
        # 不可打印字符，移除
        regex_non_printable = re.compile(
            r"[\001\002\003\004\005\006\007\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f"
            r"\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a]"
        )

        filename = regex_path.sub(to_full_width_chr, filename)
        filename = regex_spaces.sub(" ", filename)
        filename = regex_non_printable.sub("", filename)
        filename = filename.strip()
        filename = (
            filename if filename else "file_{:04}".format(random.randint(0, 9999))
        )
        return filename.replace("&", "&amp;").replace('  ',' ')

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
            self.download_video(bvid)

            # NOTE 修改视频名称为 oid
            title = info.get("title")
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
                self.submit_subtitle(subtitle, oid, bvid, lang=self.lang)

        tk.messagebox.showinfo("恭喜你", "字幕上传成功")

    # @check_variable.__func__
    # def youtube_run(self):
    #     youtube = os.path.join(__file__, "..", "youtube")
    #     youtubeuploader = os.path.join(youtube, "youtubeuploader.exe")
    #     secrets = os.path.join(youtube, "client_secrets.json")
    #     token = os.path.join(youtube, "request.token")

    #     if not os.path.exists(youtubeuploader):
    #         msg = f"{youtubeuploader} 路径不存在"
    #         print(msg)
    #         tk.messagebox.showwarning("警告", msg)
    #         return
    #     elif not os.path.exists(token):
    #         msg = f"{token} 路径不存在"
    #         print(msg)
    #         tk.messagebox.showwarning("警告", msg)
    #         return
    #     elif not os.path.exists(secrets):
    #         msg = f"{secrets} 路径不存在"
    #         print(msg)
    #         tk.messagebox.showwarning("警告", msg)
    #         return

    #     for bvid in self.bvid_list:
    #         self.bvid = bvid
    #         info = self.get_video_info(bvid)

    #         # NOTE 下载视频
    #         self.download_video(bvid)

    #         # NOTE 修改视频名称为 oid
    #         title = info.get("title")
    #         pages = info.get("pages")

    #         video = os.path.join(
    #             __file__, "..", "video", f"{title} - bilibili", "Videos"
    #         )

    #         oid2youtube = {}
    #         for p, oid in pages.items():
    #             src = os.path.join(video, f"{p}.mp4")
    #             if not os.path.isfile(src):
    #                 continue
    #             command = " ".join(
    #                 [
    #                     os.path.abspath(youtubeuploader),
    #                     "-filename",
    #                     f'"{os.path.abspath(src)}"',
    #                     "-secrets",
    #                     os.path.abspath(secrets),
    #                     "-cache",
    #                     os.path.abspath(token),
    #                 ]
    #             )

    #             # NOTE 上传到 youtube
    #             res = subprocess.check_output(command)

    #             # NOTE 获取上传的 id
    #             res = res.decode("utf-8")
    #             regx = re.compile(r"Video ID: (.*)")
    #             grp = regx.search(res)
    #             if grp:
    #                 youtube_id = grp.group(1)
    #                 oid2youtube[oid] = youtube_id
    #                 print(f"{youtube_id} 上传成功")

    #         output = os.path.join(self.youtube_folder, f"{bvid}.json")
    #         with open(output, "w") as f:
    #             json.dump(oid2youtube, f, indent=4)

    @staticmethod
    def check_bvid_json(output):
        data = {}
        if os.path.exists(output):
            with open(output, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            directory,name = os.path.split(output)
            output = os.path.join(directory,"upload",name)
            if os.path.exists(output):
                with open(output, "r", encoding="utf-8") as f:
                    data = json.load(f)
        return data

    @check_variable.__func__
    def youtube_selenium_run(self):

        uploader = YouTubeUploader("")
        uploader.username = self.youtube_username.get()
        uploader.password = self.youtube_password.get()
        uploader.youtube_login()
    
        for bvid in self.bvid_list:
            self.bvid = bvid
            output = os.path.join(self.youtube_folder, f"{bvid}.json")
            data = self.check_bvid_json(output)
            if data.get("upload"):
                print("uploaded ",self.bvid)
                continue
            # if not data:
            #     print("ignore ",self.bvid)
            #     continue
                # _output = os.path.join(self.youtube_folder, "upload", f"{bvid}.json")
                # data = self.check_bvid_json(_output)
            
            info = self.get_video_info(bvid)
            # NOTE 修改视频名称为 oid
            title = info.get("title")
            pages = info.get("pages")
            
            video = os.path.join(
                __file__, "..", "video", f"{title} - bilibili", "Videos"
            )
            
            oid2youtube = data.get("oid2youtube",{})
            # NOTE json 获取的 字符串 oid 是数字需要转换
            page_dict = {p:oid for p, oid in pages.items() if not oid2youtube.get(str(oid))}
            # NOTE 如果为空说明 已经上传过了
            if not page_dict:
                continue
            
            
            for p, oid in page_dict.items():
                src = os.path.join(video, f"{p}.mp4")
                if not os.path.isfile(src):
                    # NOTE 下载视频
                    self.download_video(bvid)
                    break

            info["oid2youtube"] = oid2youtube
            for p, oid in page_dict.items():
                p = p.replace("&amp;","&")
                src = os.path.join(video, f"{p}.mp4")
                if not os.path.isfile(src):
                    print(f"{src} 视频源找不到 - 跳过")
                    continue
                
                uploader.video_path = src
                was_video_uploaded, youtube_id = uploader.youtube_upload()
                if was_video_uploaded and youtube_id:
                    oid2youtube[oid] = youtube_id
                    print(f"{youtube_id} 上传成功")
                    self.dump_dict(info, path=output, indent=4)

        uploader.quit()

    @check_variable.__func__
    def submit_youtube_subtitle_run(self):
        
        upload = os.path.join(self.youtube_folder, "upload")
        if not os.path.exists(upload):
            os.mkdir(upload)
            
        for j in os.listdir(self.youtube_folder):
            if not j.endswith(".json"):
                continue
            
            output = os.path.join(self.youtube_folder, j)
            location = os.path.join(upload, os.path.basename(output))

            self.bvid = j[:-5]
            with open(output, "r", encoding="utf-8") as f:
                info = json.load(f)
            
            # NOTE 检查是不是视频都上传完成了
            for p,oid in info.get("pages").items():
                if not info.get("oid2youtube").get(oid):
                    break
            else:
                print(f"跳过 {j}")
                # NOTE 如果上传完了判断是已经上传到B站了
                if info.get("upload"):
                    os.rename(output, location)
                continue

            print(f"上传 {j}")
            oid2youtube = info.get("oid2youtube")

            for oid, youtube_id in oid2youtube.items():
                if not self.upload_bilibili_subtitle(youtube_id, oid):
                    if not info.get("fail"):
                        info["fail"] = {}
                    if not info["fail"].get(oid):
                        info["fail"][oid] = [youtube_id]
                    info["fail"][oid].append("en_US")
                # if not self.youtube_cn.get():
                #     continue
                elif not self.upload_bilibili_subtitle(youtube_id, oid, zh=True):
                    if not info.get("fail"):
                        info["fail"] = {}
                    if not info["fail"].get(oid):
                        info["fail"][oid] = [youtube_id]
                    info["fail "][oid].append("zh_CN")
                
            info["upload"] = True
            self.dump_dict(info, path=output, indent=4)
            if os.path.exists(location):
                os.remove(location)
            os.rename(output, location)

    def upload_bilibili_subtitle(self, youtube_id, oid, zh=False):
        cookie = self.youtube_cookie.get()
        vtt = self.get_youtube_vtt(youtube_id, cookie, zh=zh)
        if not vtt:
            return False
        subtitle = self.vtt2bcc(vtt)
        lang = "zh-CN" if zh else "en-US"
        text = self.submit_subtitle(subtitle, oid, lang=lang)
        if text != '{"code":0,"message":"0","ttl":1,"data":null}':
            subtitle = self.vtt2bcc(vtt, word=False)
            text = self.submit_subtitle(subtitle, oid, lang=lang)
        print(f"{'【中文】' if zh else '【英文】'} {self.bvid} {oid} -> {text}")
        return True

    # @check_variable.__func__
    def submit_youtube_subtitle_selenium_run(self):
        uploader = YouTubeUploader("")
        uploader.bilibili_login()
        for j in os.listdir(self.youtube_folder):
            if not j.endswith(".json"):
                continue

            output = os.path.join(self.youtube_folder, j)
            self.bvid = j[:-5]
            with open(output, "r") as f:
                info = json.load(f)
            if info.get("upload"):
                continue

            print(f"上传 {j}")
            oid2youtube = info.get("oid2youtube")
            cookie = self.youtube_cookie.get()
            flag = True
            for oid, youtube_id in oid2youtube.items():
                vtt = self.get_youtube_vtt(youtube_id, cookie)
                if not vtt:
                    flag = False
                    break
                subtitle = self.vtt2bcc(vtt)
                path = self.dump_dict(subtitle)
                uploader.bilibili_upload(self.bvid, oid, path)
                if self.youtube_cn.get():
                    vtt = self.get_youtube_vtt(youtube_id, cookie, zh=True)
                    if not vtt:
                        flag = False
                        break
                    subtitle = self.vtt2bcc(vtt)
                    path = self.dump_dict(subtitle)
                    uploader.bilibili_upload(self.bvid, oid, path, zh=True)

            if flag:
                info["upload"] = flag
                self.dump_dict(info, path=output, indent=4)

        uploader.quit()

    @staticmethod
    def dump_dict(subtitle, path="", indent=None):
        path = path if path else os.path.join(os.getcwd(), "temp.bcc")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(subtitle, f, ensure_ascii=False, indent=indent)
        return path

    def get_youtube_vtt(
        self, youtube_id, youtube_cookie="", zh=False, count=0, max_count=4
    ):

        if count > max_count:
            print(f"Skip {youtube_id} ...")
            return ""

        youtube_cookie = youtube_cookie if youtube_cookie else self.youtube_cookie.get()
        url = f"https://www.youtube.com/watch?v={youtube_id}"

        headers = {
            "authority": "www.youtube.com",
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3775.400 QQBrowser/10.6.4209.400",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            # 'accept-encoding': 'gzip, deflate',
            "accept-language": "zh-CN,zh;q=0.9",
            "cookie": youtube_cookie,
        }

        response = requests.request("GET", url, headers=headers)

        html = response.text
        
        # with open("test.txt",'w') as f:
        #     f.write(html)
        # raise RuntimeError
        
        pattern = re.escape(r'"captionTracks":[{"baseUrl":')
        regx = re.search(f'{pattern}"(.*?)"', html)

        if not regx:
            count += 1
            print(f"fail to find {youtube_id} subtitle , Retry Count {count} ...")
            # time.sleep(3)
            return ""

        url = regx.group(1).replace(r"\u0026", "&")
        url += "&fmt=vtt"
        url += "&tlang=zh-Hans" if zh else ""
        res = requests.request("GET", url)
        text = res.text
        if zh:
            # NOTE 中文自动翻译字幕 清除 最后一行字幕
            lines = [line for i, line in enumerate(text.splitlines()[:-5])]
            text = "\n".join(lines)
        else:
            # NOTE 英语字幕 清除 youtube vtt 第5行 空行
            lines = [line for i, line in enumerate(text.splitlines()) if i != 5]
            text = "\n".join(lines)

        return text

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

                self.submit_subtitle(subtitle, oid, lang=self.lang)

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

        data = response.json().get("data", {})
        # data = json.loads(response.text).get("data", {})

        return {
            "title": self.repair_filename(data.get("title", "")),
            "pages": {self.repair_filename(p.get("part")): p.get("cid") for p in data.get("pages", {})},
        }

    def download_video(self, bvid):
        bvid = bvid if bvid else self.bvid

        output_path = os.path.join(__file__, "..", "video")
        if not os.path.exists(output_path):
            os.mkdir(output_path)
        subprocess.call(
            [
                "bilili",
                f"https://www.bilibili.com/video/{bvid}",
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

    def submit_subtitle(self, subtitle, oid, bvid=None, lang="en-US"):
        bvid = bvid if bvid else self.bvid

        subtitle = subtitle if isinstance(subtitle, dict) else {}
        if not subtitle or not oid:
            print(f"{oid} 文件为空 - 跳过")
            return
        subtitle = json.dumps(subtitle)

        csrf = self.bili_jct
        payload = f'lan={lang}&submit=true&csrf={csrf}&sign=false&bvid={bvid}&type=1&oid={oid}&{parse.urlencode({"data":subtitle})}'

        headers = {
            # "referer": "https://account.bilibili.com/subtitle/edit/",
            # "origin": "https://account.bilibili.com",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        headers.update({"Cookie": self.bilibili_cookie.get()})

        url = "https://api.bilibili.com/x/v2/dm/subtitle/draft/save"
        response = requests.request("POST", url, headers=headers, data=payload)

        return response.text

if __name__ == "__main__":
    root = tk.Tk()
    uploader = BiliBili_SubtitleGenerator(root)
    root.mainloop()
