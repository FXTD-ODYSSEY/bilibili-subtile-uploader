# coding:utf-8
from __future__ import unicode_literals, division, print_function

__author__ = 'timmyliang'
__email__ = '820472580@qq.com'
__date__ = '2020-05-12 11:31:30'

"""

"""
import os
import json
import codecs
import tempfile
import requests

from urllib import parse
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


class BccParser(object):
    def __init__(self):
        pass


def takeParm(kwargs, key, default=None):
    res = kwargs.get(key, default)
    if key in kwargs:
        del kwargs[key]
    return res


class SelectPathWidget(tk.Frame):
    def __init__(self, *args, **kwargs):
        label_text = takeParm(kwargs, "label_text", "")
        path_text = takeParm(kwargs, "path_text", "")
        button_text = takeParm(kwargs, "button_text", "")
        click_event = takeParm(kwargs, "click_event")

        tk.Frame.__init__(self, *args, **kwargs)

        self.grid_columnconfigure(1, weight=1)

        if label_text:
            self.label = tk.Label(self, text=label_text)
            self.label.grid(row=0, column=0, sticky="nsew")

        self.edit = tk.Entry(self, text='', width=25)
        self.edit.insert(0, path_text)
        self.edit.grid(row=0, column=1, sticky="nsew", padx=10)

        callback = click_event if callable(
            click_event) else self.selectDirectory

        self.btn = tk.Button(self, text=button_text,
                             command=callback, width=15)
        self.btn.grid(row=0, column=2, sticky="nsew")

    def selectDirectory(self):
        path = filedialog.askdirectory()
        if path:
            self.edit.delete(0, tk.END)
            self.edit.insert(0, path)

    def get(self):
        return self.edit.get()


class DriveCombobox(tk.Frame):
    def __init__(self, *args, **kwargs):

        label_text = takeParm(kwargs, "label_text", "")
        state = takeParm(kwargs, "state", "readonly")
        self.exists = takeParm(kwargs, "exists", False)

        tk.Frame.__init__(self, *args, **kwargs)

        if label_text:
            self.label = tk.Label(self, text=label_text)
            self.label.pack(side="left", fill="x", padx=(0, 10))

        self.combo = ttk.Combobox(self, state=state)

        self.update()

        self.combo.pack(side="left", fill="x", expand=1)
        self.combo.current(0)
        self.combo.bind("<Button-1>", self.update)

    def update(self, *args):
        dl = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        options = ['%s:' % d for d in dl if os.path.exists('%s:' % d)] if self.exists else [
            '%s:' % d for d in dl if not os.path.exists('%s:' % d)]
        self.combo['values'] = options
        option = self.combo.get()
        if option not in options:
            self.combo.current(0)

    def get(self):
        return self.combo.get()

    def current(self, i):
        return self.combo.current(i)


class LabelSeperator(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

        label_text = kwargs.get("label_text")
        if label_text:
            self.grid_columnconfigure(0, weight=100)
            self.grid_columnconfigure(1, weight=1)
            self.grid_columnconfigure(2, weight=100)
            ttk.Separator(self, orient=tk.HORIZONTAL).grid(
                row=0, column=0, sticky="ew")
            tk.Label(self, text=label_text).grid(
                row=0, column=1, sticky="nsew", padx=10)
            ttk.Separator(self, orient=tk.HORIZONTAL).grid(
                row=0, column=2, sticky="ew")
        else:
            sep = ttk.Separator(self, orient=tk.HORIZONTAL)
            sep.pack(side="top", fill="x", expand=1, padx=5, pady=5)


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.help_win = None

        parent.title("盘符映射工具")
        parent.protocol("WM_DELETE_WINDOW", self.onClosing)

        # NOTE 获取系统临时路径
        temp_dir = tempfile.gettempdir()
        self.json_file = os.path.join(temp_dir, "subst_TK_GUI.json")

        # NOTE 生成菜单
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="使用说明", command=self.helpWin)
        filemenu.add_separator()
        filemenu.add_command(label="退出", command=self.onClosing)
        menubar.add_cascade(label="帮助", menu=filemenu)
        parent.config(menu=menubar)

        UNC_Frame = tk.Frame()

        gen_frame = tk.LabelFrame(UNC_Frame, text="上传 bcc 字幕")
        gen_frame.pack(side="top", fill="x")
        gen_btn = tk.Button(gen_frame, text="批量上传字幕",
                            command=self.submit_subtitle)
        gen_btn.pack(side="top", fill="x", expand=1, padx=5, pady=5)

        self.grid_columnconfigure(0, weight=100)
        # UNC_Frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        UNC_Frame.pack(side="top", fill="x", padx=5, pady=5)
        # test_frame = tk.Button( text="批量上传123字幕")
        # test_frame.pack(side="top", fill="both", expand=1, padx=5, pady=5)
        
        # tk.Frame().grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # self.loadJson()

    def helpWin(self):
        # NOTE 删除重复的窗口
        if self.help_win and self.help_win.winfo_exists():
            self.help_win.destroy()
        self.help_win = tk.Toplevel(self.parent)
        self.help_win.title("使用说明")
        tk.Label(self.help_win, text="选择可映射盘符进行映射").pack(
            side="top", fill="x", padx=5, pady=5)
        # tk.Label(self.help_win, text="如果盘符已经存在需要先删除已有盘符再映射").pack(side="top", fill="x", expand=1, padx=5,pady=5)
        # tk.Label(self.help_win, text="删除盘符为系统分区会提示执行出错，不用担心错误删除系统分区").pack(side="top", fill="x", expand=1, padx=5,pady=5)

    def onClosing(self):
        # self.saveJson()
        self.parent.destroy()

    def loadJson(self, directory=None):
        directory = self.json_file if directory is None else directory
        if not os.path.exists(directory):
            return

        # data = {}
        # try:
        #     with open(directory, "r") as f:
        #         data = json.load(f,encoding="utf-8")
        # except:
        #     import traceback
        #     traceback.print_exc()
        #     return

        # gen_drive = data.get("gen_comboBox")
        # del_drive = data.get("del_comboBox")
        # path = data.get("path")

        # for i,val in enumerate(self.gen_comboBox.combo['values']):
        #     if val == gen_drive:
        #         self.gen_comboBox.current(i)
        #         break

        # for i,val in enumerate(self.del_comboBox.combo['values']):
        #     if val == del_drive:
        #         self.del_comboBox.current(i)
        #         break

        # self.path_widget.edit.delete(0,tk.END)
        # self.path_widget.edit.insert(0,path)

    def saveJson(self, directory=None):
        pass
        # data = {
        #     "gen_comboBox" : self.gen_comboBox.get(),
        #     "del_comboBox" : self.del_comboBox.get(),
        #     "path" : self.path_widget.get(),
        # }
        # directory = self.json_file if directory is None else directory
        # with open(directory, "w") as f:
        #     json.dump(data,f,indent=4)

    def submit_subtitle(self):

        DIR = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(DIR, "config.json"), 'r') as f:
            Cookie = json.load(f)

        csrf = ""
        for line in Cookie.get("Cookie").split(";"):
            line = line.strip()
            if line.startswith("bili_jct="):
                bili_jct = line[len("bili_jct="):]
                break
        else:
            print("缺少 bili_jct 值")
            return

        url = "https://api.bilibili.com/x/v2/dm/subtitle/draft/save"

        subtitle = '''{"font_size":0.4,"font_color":"#FFFFFF","background_alpha":0.5,"background_color":"#9C27B0","Stroke":"none","body":[{"from":4.19,"to":5.93,"location":2,"content":"Hire one."},{"from":6.13,"to":12.43,"location":2,"content":"Annd welcome to the set up section where I'll walk you through the steps in order to get started with"},{"from":12.49,"to":15.57,"location":2,"content":"coding for engine for at this point."},{"from":15.58,"to":19.46,"location":2,"content":"I assume you already have the engine installed and ready to go."},{"from":19.66,"to":26.2,"location":2,"content":"So I'll focus on setting up Visual Studio and highly recommended visual assist plugin which will significantly"},{"from":26.2,"to":30.71,"location":2,"content":"improve your quality of life when coding with C++ throughout the course."},{"from":30.73,"to":37.42,"location":2,"content":"I'll be using visualises for Intellisense and certain navigation Akis if you don't get Ulysses yet you"},{"from":37.42,"to":40.91,"location":2,"content":"can try the trial version for free in case you're wondering."},{"from":40.98,"to":46.79,"location":2,"content":"I will be using Unreal engine for 1:17 for of this course using a later version of the engine is OK"},{"from":46.84,"to":53.68,"location":2,"content":"but keep in mind that the look of the windows may change or that small API changes in C++ moniker to"},{"from":53.68,"to":54.67,"location":2,"content":"be absolutely safe."},{"from":54.67,"to":56.17,"location":2,"content":"Please use Fortran 17."},{"from":56.17,"to":61.36,"location":2,"content":"And please do notify me of any changes or issues you run into by posting in the Q and A board."},{"from":61.39,"to":66.76,"location":2,"content":"I will do my best to keep the videos up to date ones later additions of the engine are released and"},{"from":66.93,"to":70.86,"location":2,"content":"your help in pointing out inconsistencies will be greatly appreciated."}]}'''

        csrf = bili_jct
        bvid = "BV1Cv411k7iN"
        oid = "244626685"
        lan = "en-US"
        payload = f'lan={lan}&submit=true&csrf={csrf}&sign=false&bvid={bvid}&type=1&oid={oid}&{parse.urlencode({"data":subtitle})}'

        headers = {
            'referer': 'https://account.bilibili.com/subtitle/edit/',
            'origin': 'https://account.bilibili.com',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        headers.update(Cookie)

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text.encode('utf8'))


if __name__ == "__main__":
    # submit_subtitle()
    root = tk.Tk()
    MainApplication(root)
    root.mainloop()
