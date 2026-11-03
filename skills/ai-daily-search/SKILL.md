---
name: ai-daily-search
description: Search the 「AI前沿动态追踪」 (AI Frontier Daily, by ZGCA AI战略研究所) knowledge base of daily AI industry events since 2026-09-11 — model and product launches, research, funding/IPO/M&A, policy, and named people's views — by keyword, date range, tag (大模型, 智能体, 具身智能, AI安全与对齐, 生命科学…), type and person, and turn the results into sourced, structured answers. Use when the user asks what happened with an AI company, lab, person or field over a period, wants a briefing, timeline, roundup or list of events, or mentions AI日报 / AI前沿动态 / ai-daily.ihainan.me. 中文：查 AI 公司、人物、领域在一段时间内的动态，做简报、时间线、事件盘点。Read-only, no account needed.
---

# AI前沿动态追踪 · 搜索

知识库是「AI前沿动态追踪」日报（<https://ai-daily.ihainan.me>）的全部已发布条目，每天一期，从 2026-09-11 开始。每条有日期、标题、正文、类型、板块、分组、标签、人物、**原始来源链接**和**日报页面链接**。

| 类型 `kind` | 内容 |
|---|---|
| `sig` 事件 | 编号事件卡片，最主要的内容 |
| `an` 数据分析 | 高价值数据与图表 |
| `quote` 观点 | 具名人物的实质观点（标题是发言人） |
| `mk` 短讯 | 较短的产业、资本消息（早期日报） |
| `pc` 播客 | 播客、访谈摘要 |

## 命令

脚本只用 Python 3.8+ 标准库，路径相对本 skill 目录：

```bash
python3 scripts/search.py meta                                   # 覆盖日期、标签、类型、板块、限额
python3 scripts/search.py search "Anthropic 融资" --days 30       # 关键词检索
python3 scripts/search.py search --tag 具身智能 --kind 事件 --from 2026-10-01 --to 2026-10-31 --all --brief
python3 scripts/search.py item 2026-10-31/s01 2026-10-30/s05      # 按 id 取全文
```

- **关键词 `q`**：空格分开的词**都要**出现（标题、正文、人物里的子串，不分大小写）；`"Physical Intelligence"` 加引号当短语；`-词` 排除。
- **过滤**：`--days N`（最近 N 天，含今天）或 `--from/--to`；`--tag`（标签全名、英文名或代号，如 `AI安全与对齐` / `Safety` / `d3`，以 `meta` 列出的为准；可重复，取交集）；`--kind`；`--section`（板块全名）；`--person`。
- **结果**：默认按相关度（有关键词时）或日期倒序，每页 ≤50；`--all` 自动翻页（默认最多 200 条，`--max` 调整）；默认只给摘要，`--brief` 每条一行（日期、id、标题），`--full` 或 `item` 取全文；`--json` 给结构化数据。
- 没有 Python 时直接请求接口，见 [references/api.md](references/api.md)。
- **限额**：每个地址每分钟约 30 次。脚本遇到 429 会按 `Retry-After` 等一次。不要并发狂刷，能用一次 `--all` 就别拆成几十次请求。

## 工作流程

1. **拆问题**：主体（公司/人/领域）、时间范围、关心的事件类型、要什么输出格式。没说时间就用最近 30 天，并在答案里写出实际起止日期。
2. **扩检索词**：检索是字面匹配，不懂同义词。中文名、英文名、产品名、核心人物分别查，例如 Anthropic 再查 `Claude`；DeepSeek 再查 `深度求索`；融资再查 `募资`、`估值`、`轮`。多个词放在同一个 `q` 里是“都要出现”，想要“任一出现”就分开查、按 `id` 去重。
3. **领域问题先用标签**：`--tag 具身智能` 比关键词全；再用关键词补查没打这个标签的条目。先跑 `meta` 看有哪些标签。
4. **先宽后窄**：看 `total`。太多就缩时间、加标签/类型/更多关键词；太少就换词、放宽时间。短词会误命中（`AI` 几乎全中，`-API` 会排除含 “Capital” 的条目），逐条看标题确认相关。
5. **先列标题，再读全文**：命中多时先 `--all --brief` 看全部标题、剔除不相关的、找出同一事件的几条，再对要写进答案的条目用 `item <id>`（可一次给多个 id）或 `--full` 读全文，不要只凭摘要下结论。
   命中很多（如 50 个事件以上）时，先告诉用户总数，默认全部列出但每条压到一句；用户只要重点时，按影响面挑（格局变化 > 能力信号 > 研究与应用 > 跟进与讨论），并说明挑选标准。
6. **合并同一事件**：同一件事常在几天里重复出现（首发、后续、跟进评论），按时间合成一条，写清每一步的日期。正文写了事件发生日（如“10-27 宣布”）就用发生日，否则用日报日期。检索窗口按日报日期算；窗口内日报补报的更早事件可以收，按发生日排并照写日期。
7. **按格式输出**：用户给了格式就照用；要“整理/盘点/列出事件”时默认用 [references/output-format.md](references/output-format.md) 的分类事件清单。一级分类固定，没有条目的不写；小类按领域调整（如 AI 安全可设“对齐与评测”“模型越界事件”“网络攻防与滥用”）。具名人物的独立论点放“观点与讨论”，对某个事件的跟进评论留在该事件那一条里。

## 硬规则

- **只用检索到的内容**，不补充库外知识，不推算或换算数字（例如不要用投前估值加融资额算投后估值）。确需背景时单独标「库外补充」。
- **每条事实都要能追溯**：答案里给日报链接（`url`），并尽量给一个原始来源（`sources`，优先官方或监管文件，其次一线媒体）。
- **保留原文的证据标注**：【仅见媒体报道】、“据报道”、“称”、“预计”等照写，不把报道写成事实、把计划写成已完成。
- **结论不超出证据**：单个案例只算“信号”，不写成“趋势”；“全面”“普遍”这类词不能超出条目本身。
- **观点归属准确**：`quote` 和正文里的跟进评论属于具名发言人，写明是谁、什么身份说的。
- **说明检索范围**：结尾一行写时间区间、用过的检索词和过滤条件、命中多少、用了多少。知识库从 2026-09-11 开始，更早的查不到要直说；查不到就说查不到，不拿相近的事凑数。
