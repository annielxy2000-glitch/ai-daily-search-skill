# ai-daily-search

An agent skill for searching **「AI前沿动态追踪」 (AI Frontier Daily)** — a daily digest of AI industry events published by A at <https://ai-daily.ihainan.me>, from 2026-09-11 onward. Your agent can look up what happened with an AI company, lab, person or field (model launches, research, funding and IPOs, policy, named people's views) and answer with dated, sourced, structured output.

让你的 Agent 检索「AI前沿动态追踪」日报知识库：按关键词、日期、标签、类型、人物查 AI 公司、人物和领域的动态，输出带日期和出处的简报、时间线、分类事件清单。

## Install

```bash
npx skills add annielxy2000-glitch/ai-daily-search-skill
```

Works with any agent supported by [skills](https://github.com/vercel-labs/skills) (Claude Code, Codex, Cursor, …). Add `-g` to install for all projects. Requires Python 3.8+ (standard library only); no account or API key.

## Try it

- 最近一个月 Anthropic 有哪些重要动作？给我一份简报
- 整理最近两个月具身智能领域的事件，按技术、商业、政策分类
- 10 月以来有哪些 AI 安全相关的政策？
- What did Physical Intelligence announce in October?

## What's inside

| Path | |
|---|---|
| `skills/ai-daily-search/SKILL.md` | When to use it, search workflow, citation and evidence rules |
| `skills/ai-daily-search/scripts/search.py` | Zero-dependency client: `search`, `item`, `meta` |
| `skills/ai-daily-search/references/api.md` | The public API, for agents without Python |
| `skills/ai-daily-search/references/output-format.md` | Default format for event roundups |

The API is public and read-only (`GET /api/search`, `/api/search/item/{date}/{key}`, `/api/search/meta`), rate-limited to about 30 requests a minute per address.
