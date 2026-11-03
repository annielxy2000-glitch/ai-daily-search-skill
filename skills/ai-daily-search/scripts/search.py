#!/usr/bin/env python3
"""Search the "AI前沿动态追踪" (AI Frontier Daily) knowledge base. Read-only, no account, Python 3.8+ stdlib only.

  python3 search.py search "Anthropic 融资" --days 30
  python3 search.py search --tag 具身智能 --kind 事件 --from 2026-10-01 --all
  python3 search.py item 2026-10-31/s01
  python3 search.py meta

API: https://ai-daily.ihainan.me/api/search (override with env AI_DAILY_API). Rate limit: about 30 requests a minute
per address; on 429 this script waits Retry-After once and tries again.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = os.environ.get("AI_DAILY_API", "https://ai-daily.ihainan.me").rstrip("/")
UA = "ai-daily-search-skill/1.0"
PAGE = 50


def call(path, params=None):
    url = API + path + ("?" + urllib.parse.urlencode(params, doseq=True) if params else "")
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    for attempt in range(2):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            try:
                body = json.load(e)
            except ValueError:
                body = {"error": "http_error", "detail": str(e)}
            if e.code == 429 and attempt == 0:
                wait = min(int(e.headers.get("Retry-After") or body.get("retry_after") or 10), 90)
                print(f"[rate limited, waiting {wait}s]", file=sys.stderr)
                time.sleep(wait)
                continue
            msg = body.get("detail") or body.get("error")
            field = f" ({body['field']})" if body.get("field") else ""
            sys.exit(f"error {e.code}{field}: {msg}")
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt == 0:
                time.sleep(2)
                continue
            sys.exit(f"cannot reach {API}: {e}")
    sys.exit("gave up after rate limiting")


def do_search(a):
    params = {"limit": min(a.limit, PAGE), "offset": a.offset, "detail": "full" if a.full else "snippet"}
    for k in ("q", "to", "days", "kind", "section", "person", "sort"):
        v = getattr(a, k)
        if v not in (None, ""):
            params[k] = v
    if a.date_from:
        params["from"] = a.date_from
    if a.tag:
        params["tag"] = a.tag
    want = a.max if a.all else a.limit
    items, page = [], None
    while True:
        page = call("/api/search", params)
        items += page["items"]
        if not a.all or page["next_offset"] is None or len(items) >= want:
            break
        params["offset"] = page["next_offset"]
    items = items[:want]
    if a.json:
        print(json.dumps({"query": page["query"], "total": page["total"], "returned": len(items),
                          "next_offset": None if len(items) >= page["total"] else a.offset + len(items),
                          "items": items}, ensure_ascii=False, indent=1))
        return
    qd = page["query"]
    desc = "  ".join(f"{k}={v}" for k, v in qd.items() if v not in (None, [], "") and k not in ("detail",))
    print(f"# {page['total']} matches  ({desc})")
    if len(items) < page["total"]:
        nxt = a.offset + len(items)
        print(f"# showing {len(items)}; more with --offset {nxt}" + ("" if a.all else " or --all"))
    print()
    for it in items:
        print_item(it)


def print_item(it):
    tags = "、".join(t["label"] for t in it["tags"])
    meta = [it["kind_label"], it["section"] + (f" / {it['group']}" if it.get("group") else ""), tags]
    if it["people"]:
        meta.append("人物 " + "、".join(it["people"]))
    print(f"## [{it['date']}] {it['title']}")
    print(f"id {it['id']} | " + " | ".join(m for m in meta if m))
    print(f"日报: {it['url']}")
    print("来源: " + (" ".join(it["sources"]) if it["sources"] else "(无)"))
    text = it.get("body") if "body" in it else it.get("snippet", "")
    if "snippet" in it and it.get("body_chars", 0) > len(it["snippet"]):
        text += f"  [摘要；全文 {it['body_chars']} 字: item {it['id']}]"
    print(text)
    print()


def do_item(a):
    ids = []
    for raw in a.ids:
        date, _, key = raw.strip().partition("/")
        if not key:
            sys.exit(f"bad id {raw!r}: use DATE/KEY, e.g. 2026-10-31/s01")
        ids.append((date, key))
    out = [call(f"/api/search/item/{urllib.parse.quote(d)}/{urllib.parse.quote(k)}") for d, k in ids]
    if a.json:
        print(json.dumps(out if len(out) > 1 else out[0], ensure_ascii=False, indent=1))
        return
    for it in out:
        print_item(it)


def do_meta(a):
    m = call("/api/search/meta")
    if a.json:
        print(json.dumps(m, ensure_ascii=False, indent=1))
        return
    c = m["coverage"]
    print(f"覆盖 {c['first_date']} → {c['last_date']}，共 {c['issues']} 期")
    print("类型 kind: " + "、".join(f"{k['key']}={k['label']}" for k in m["kinds"]))
    print("学部标签 tag: " + "、".join(f"{t['key']}={t['label']}" for t in m["tags"]["departments"]))
    print("性质标签 tag: " + "、".join(f"{t['key']}={t['label']}" for t in m["tags"]["natures"]))
    print("板块 section: " + "、".join(m["sections"]))
    print("检索语法: " + m["query_syntax"])
    lim = m["limits"]
    print(f"限额: 每页≤{lim['max_limit']}，偏移≤{lim['max_offset']}，每分钟约 {lim['requests_per_minute']} 次")


def main():
    p = argparse.ArgumentParser(description="Search AI Frontier Daily (ai-daily.ihainan.me)")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="keyword search")
    s.add_argument("q", nargs="?", help='words (all must match), "exact phrase", -exclude')
    s.add_argument("--from", dest="date_from", help="YYYY-MM-DD")
    s.add_argument("--to", help="YYYY-MM-DD")
    s.add_argument("--days", type=int, help="last N days, today included")
    s.add_argument("--tag", action="append", help="tag key or name, e.g. 具身智能 / d4 / Robotics; repeat = AND")
    s.add_argument("--kind", help="sig/quote/mk/an/pc or 事件/观点/短讯/数据分析/播客")
    s.add_argument("--section", help="exact section name, e.g. 商业与资本动态")
    s.add_argument("--person", help="person name (substring)")
    s.add_argument("--sort", choices=["relevance", "date", "date_asc"])
    s.add_argument("--limit", type=int, default=20, help="results to show (≤50 per page)")
    s.add_argument("--offset", type=int, default=0)
    s.add_argument("--all", action="store_true", help="follow pages up to --max results")
    s.add_argument("--max", type=int, default=200)
    s.add_argument("--full", action="store_true", help="full bodies instead of snippets")
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=do_search)
    i = sub.add_parser("item", help="full text of items by id (DATE/KEY)")
    i.add_argument("ids", nargs="+")
    i.add_argument("--json", action="store_true")
    i.set_defaults(fn=do_item)
    m = sub.add_parser("meta", help="coverage, tags, kinds, sections, limits")
    m.add_argument("--json", action="store_true")
    m.set_defaults(fn=do_meta)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
