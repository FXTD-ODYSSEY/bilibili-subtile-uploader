from selenium import webdriver
import os
import json

# 创建 WebDriver 对象，指明使用chrome浏览器驱动
# browser = webdriver.Chrome(r'C:\Windows\System32\chromedriver.exe')

from selenium import webdriver
from time import sleep
import time
from pathlib import Path

class Google:

    def __init__(self, username, password):

        self.browser = webdriver.Chrome(r'C:\Windows\System32\chromedriver.exe')
        self.browser.get('https://stackoverflow.com/users/signup?ssrc=head&returnurl=%2fusers%2fstory%2fcurrent%27')
        sleep(Constant.USER_WAITING_TIME)
        self.browser.find_element_by_xpath('//*[@id="openid-buttons"]/button[1]').click()
        self.browser.find_element_by_xpath('//input[@type="email"]').send_keys(username)
        self.browser.find_element_by_xpath('//*[@id="identifierNext"]').click()
        sleep(Constant.USER_WAITING_TIME)
        self.browser.find_element_by_xpath('//input[@type="password"]').send_keys(password)
        self.browser.find_element_by_xpath('//*[@id="passwordNext"]').click()
        sleep(Constant.USER_WAITING_TIME)
        

username = ''
password = ''
Google(username, password)


# # 调用WebDriver 对象的get方法 可以让浏览器打开指定网址
# browser.get('https://www.youtube.com/')

# # NOTE 添加登陆 cookie
# config = os.path.join(__file__,'..','..','config.json')
# with open(config,'r') as f:
#     config = json.load(f)
# cookie = config.get("youtube_cookie")
# for line in cookie.split(";"):
#     line = line.strip()
#     k,v = line.split('=',1)
#     browser.add_cookie({
#         "name":k,
#         "value":v,
#     })


# browser.get('https://www.youtube.com/upload')
