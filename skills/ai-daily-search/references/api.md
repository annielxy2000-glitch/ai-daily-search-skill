# 搜索接口（直接调用）

基础地址 `https://ai-daily.ihainan.me`，只读、无需登录，返回 JSON。

## GET /api/search

| 参数 | 说明 |
|---|---|
| `q` | 空格分开的词都要出现；`"短语"`；`-排除词`。≤200 字符、≤8 个词 |
| `from` / `to` | `YYYY-MM-DD`，含首尾 |
| `days` | 最近 N 天（含今天，北京时间），不能和 `from` 同用 |
| `tag` | 标签代号或中英文名，可重复（`tag=具身智能&tag=产业`）或逗号分隔，取交集 |
| `kind` | `sig` / `quote` / `mk` / `an` / `pc`（也认 事件 / 观点 / 短讯 / 数据分析 / 播客） |
| `section` | 板块全名，如 `商业与资本动态` |
| `person` | 人物名子串 |
| `sort` | `relevance`（有 q 时默认）/ `date`（默认）/ `date_asc` |
| `limit` / `offset` | 每页 1–50（默认 20）；偏移 ≤1000；`next_offset` 为 null 即最后一页 |
| `detail` | `snippet`（默认）/ `full` |

```bash
curl -sG https://ai-daily.ihainan.me/api/search \
  --data-urlencode 'q=Anthropic 融资' --data-urlencode 'days=30' --data-urlencode 'limit=10'
```

返回：

```json
{"query": {...}, "total": 13, "offset": 0, "limit": 10, "next_offset": 10,
 "items": [{"id": "2026-10-27/s37", "date": "2026-10-27", "kind": "sig", "kind_label": "事件",
            "section": "商业与资本动态", "group": "基础设施", "title": "…", "snippet": "…", "body_chars": 612,
            "tags": [{"key": "d16", "label": "经济金融"}], "people": [], "sources": ["https://…"],
            "url": "https://ai-daily.ihainan.me/2026-10-27.html#s37"}]}
```

## GET /api/search/item/{date}/{key}

`id` 拆成两段，如 `/api/search/item/2026-10-27/s37`，返回同样字段加全文 `body`。

## GET /api/search/meta

覆盖日期、类型、标签表、板块名、检索语法和限额。

## 错误

`{"error": "...", "field": "...", "detail": "..."}`：422 参数不对（看 `field`），404 找不到，429 超频（等 `Retry-After` 秒）。每个地址每分钟约 30 次、每小时约 600 次。
