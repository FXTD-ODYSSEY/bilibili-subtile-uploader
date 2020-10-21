## 操作教程

youtube 命令行上传工具 [Github 链接](https://github.com/porjo/youtubeuploader)

> 下载 release 的 windows 版本 [链接](https://github.com/porjo/youtubeuploader/releases)
> 改名为 youtubeuploader.exe 


> 前往 [google 控制台](https://console.developers.google.com/apis/credentials) 创建 OAuth 2.0 Client IDs
> 在 Create OAuth client ID 选择 Desktop app
> 将生成的验证信息下载到 Youtube下载器 目录
> 添加 `"redirect_uris": ["http://localhost:8080/oauth2callback"]` 信息

> 任意上传一个视频

```shell
./youtubeuploader -filename blob.mp4
```

> 没有授权会自动打开 Google 的授权窗口，授权完成之后会获取一个授权码
> 然后上传的时候补上 -headlessAuth 可以输入获取的授权码
> 然后需要开启 Youtube 服务 [链接](https://console.developers.google.com/apis/api/youtube.googleapis.com/overview?project=909030560387)

## token.zip 解压密码

数字+字母+特殊符号+"_youtube"

