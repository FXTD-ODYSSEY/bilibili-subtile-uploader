# bilibili-subtile-uploader
auto upload caption


[bilili 视频下载](https://github.com/SigureMo/bilili) 
[autosub 字幕生成](https://github.com/BingLingGroup/autosub) 
[autosub 使用教程](https://binglinggroup.github.io/archives/autosub_057a_quick_guide.html)

[selenium 上传 yotuube 视频](https://github.com/linouk23/youtube_uploader_selenium) 

> youtube 上传视频用浏览器自动化可以上传更多视频
> 这里借助的 selenium_firefox 进行控制
> 必须安装 火狐浏览器 并且下载 geckodriver.exe 驱动器环境变量路径来通过 selenium 控制浏览器

TOOD
- [x] 通过 bilili  自动下载链接的视频
- [x] ~~使用 autosub 获取字幕~~
- [x] 使用国人维护的 autosub 进行下载
- [x] 将 srt 字幕转换为 bcc 字幕
- [x] 构建界面
- [x] 通过 subtitle 接口上传字幕
- [x] 批量上传现有字幕
- [ ] ~~多线程调用 autosub 提高字幕生成效率~~
- [x] youtube Private 视频字幕下载测试
- [x] youtube vtt 字幕转 bcc (保留逐字出现效果)
- [x] youtube selenium 上传
- [x] bilibili selenium 上传 （然而 B 站有上传大小限制 (逐字出现很容易超出限制) | 和使用接口的效果差不多）
- [ ] 自动获取账户下的 bvid 进行上传
- [ ] youtube 字幕上传失败用 fail 进行记录
- [ ] 定时自动执行


> 工具启动界面如下↓↓↓
![alt](https://cdn.jsdelivr.net/gh/FXTD-odyssey/FXTD-odyssey.github.io@master/post_img/55790015/01.png)

# API 链接 

API 索引参考 [bilibili-API-collect](https://github.com/SocialSisterYi/bilibili-API-collect)    
字幕上传 API 尚未收录

> https://api.bilibili.com/x/v2/dm/subtitle/draft/save

*请求方式：POST*

**正文参数（ application/x-www-form-urlencoded ）：**

| 参数名 | 类型   | 内容                    | 必要性 | 备注              |
| ------ | ----  | ----------------------- | ------ | ----------------- |
| aid     | num  | 视频av号                 | 必要   |                   |
| type   | num   | 操作方式                 | 必要   | 一般为 1          |
| csrf   | str   | CSRF Token（位于cookie） | 必要   |                   |
| data   | str   | bcc 字幕数据             | 必要   |                   |
| bvid   | num   | 视频bv号                 | 必要   |                   |
| sign   | bool  | 签名                     | 必要   |   一般为 false    |
| submit | bool  | 提交                     | 必要   |   一般为 true     |
| oid    | num   | 分P编号                  | 必要   |                   |


oid 可以通过 http://api.bilibili.com/x/web-interface/view 获取

---

> https://api.bilibili.com/x/space/arc/search?mid=12895307&ps=30&tid=0&pn=1&keyword=&order=pubdate&jsonp=jsonp

获取空间的视频信息
