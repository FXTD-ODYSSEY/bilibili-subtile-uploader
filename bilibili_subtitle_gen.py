import os
import json
import requests

from urllib import parse


def submit_subtitle():
    
    DIR = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(DIR,"config.json"),'r') as f:
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

    response = requests.request("POST", url, headers=headers, data = payload)

    print(response.text.encode('utf8'))

if __name__ == "__main__":
    submit_subtitle()
