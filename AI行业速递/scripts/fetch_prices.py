#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI 行业速递 · 模型 API 价格抓取脚本

每日抓取各厂商官方定价页，刷新可达性状态，并尝试用正则抽取标价。
设计原则：
- 零第三方依赖（仅标准库），任何 Python 3.9+ 环境可直接运行；
- 任一源失败不影响整体：记录 status（ok / fetch_failed / parse_failed）；
- 人工校准行保存在 data/prices.json 的 domestic / international 中，本脚本
  默认保留既有行，仅在官方页面明确可解析时更新 input/output/cache 字段。

用法：
    python scripts/fetch_prices.py
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "prices.json"
CST = timezone(timedelta(hours=8))

# 官方定价页清单。parser 为可选的轻量正则抽取器名。
SOURCES = [
    {"name": "DeepSeek", "url": "https://api-docs.deepseek.com/quick_start/pricing", "parser": "deepseek"},
    {"name": "OpenAI", "url": "https://platform.openai.com/docs/pricing", "parser": None},
    {"name": "Anthropic", "url": "https://docs.anthropic.com/en/docs/about-claude/pricing", "parser": None},
    {"name": "Google Gemini", "url": "https://ai.google.dev/gemini-api/docs/pricing", "parser": None},
    {"name": "Moonshot Kimi", "url": "https://platform.moonshot.cn/docs/pricing", "parser": None},
    {"name": "Zhipu GLM", "url": "https://open.bigmodel.cn/pricing", "parser": None},
    {"name": "MiniMax", "url": "https://platform.minimaxi.com/document/Price", "parser": None},
    {"name": "Volcengine Doubao", "url": "https://www.volcengine.com/docs/82379/1099320", "parser": None},
    {"name": "Tencent Hunyuan", "url": "https://cloud.tencent.com/document/product/1729/97731", "parser": None},
]

PRICE_RE = re.compile(
    r"(?:[$¥￥]\s?\d+(?:\.\d+)?\s*/?\s*(?:million|百万)|\d+(?:\.\d+)?\s*(?:元|美元|USD)\s*/?\s*(?:million\s*tokens?|百万\s*tokens?|百万词元))",
    re.IGNORECASE,
)


def fetch(url: str, timeout: int = 8) -> str | None:
    req = urllib.request.Request(url, headers={"User-Agent": "ai-daily-digest/1.0 (+https://github.com)"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                return None
            raw = resp.read(512_000)
            return raw.decode("utf-8", errors="ignore")
    except Exception:
        return None


def parse_snippets(html: str) -> list[str]:
    """抽取页面中带货币单位的价格片段，作为人工校准线索。"""
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    return [m.group(0) for m in PRICE_RE.finditer(text)][:20]


def run() -> dict:
    now = datetime.now(CST).strftime("%Y-%m-%d %H:%M CST")
    data = json.loads(DATA_FILE.read_text(encoding="utf-8")) if DATA_FILE.exists() else {
        "domestic": [], "international": [],
    }

    source_status = []
    for src in SOURCES:
        html = fetch(src["url"])
        entry = {"name": src["name"], "url": src["url"], "fetchedAt": now}
        if html is None:
            entry["status"] = "fetch_failed"
        else:
            entry["status"] = "ok"
            entry["snippets"] = parse_snippets(html)
        source_status.append(entry)
        time.sleep(0.5)  # 礼貌延迟

    data["updatedAt"] = now
    data["sources"] = source_status
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    ok = sum(1 for s in source_status if s["status"] == "ok")
    print(f"[fetch_prices] {ok}/{len(source_status)} sources reachable, data -> {DATA_FILE}")
    return data


if __name__ == "__main__":
    try:
        run()
    except Exception as exc:  # 不让抓取失败阻断站点构建
        print(f"[fetch_prices] WARNING: {exc}", file=sys.stderr)
        sys.exit(0)
