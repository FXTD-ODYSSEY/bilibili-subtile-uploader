# bilibili-subtile-uploader
auto upload caption


https://github.com/SigureMo/bilili
https://github.com/agermanidis/autosub

TOOD
- [ ] 自动下载链接的视频
- [ ] 使用 autosub 获取字幕
- [ ] 将 srt 字幕转换为 bcc 字幕
- [x] 通过 subtitle 接口上传字幕

# API 链接

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


oid 可以下面的链接获取

## 查询视频分P列表  (avID/bvID转CID)

> http://api.bilibili.com/x/player/pagelist

*请求方式：GET*

**url参数：**

| 参数名 | 类型 | 内容     | 必要性       | 备注               |
| ------ | ---- | -------- | ------------ | ------------------ |
| aid    | num  | 稿件avID | 必要（可选） | avID与bvID任选一个 |
| bvid   | str  | 稿件bvID | 必要（可选） | avID与bvID任选一个 |
