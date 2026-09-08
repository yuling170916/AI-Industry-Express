#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI 行业速递 · 静态站点构建脚本

读取 data/prices.json 与 reports/ 目录，渲染单页站点到 dist/index.html。
零第三方依赖。GitHub Actions 每日运行后由 actions-gh-pages 发布。

用法：
    python scripts/build_site.py
"""

from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "prices.json"
REPORTS_DIR = ROOT / "reports"
DIST = ROOT.parent / "dist"  # 仓库根目录下的 dist/，供 Pages 发布
CST = timezone(timedelta(hours=8))

PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI 行业速递 · 每日模型价格看板</title>
<style>
  :root {{ --text:#1a1a1a; --muted:#666; --border:#e5e5e5; --accent:#2563eb; --bg:#fafafa; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --text:#eaeaea; --muted:#999; --border:#333; --accent:#60a5fa; --bg:#111; }}
  }}
  * {{ box-sizing:border-box; }}
  body {{ font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif; margin:0;
         background:var(--bg); color:var(--text); line-height:1.6; }}
  .wrap {{ max-width:1000px; margin:0 auto; padding:32px 20px 64px; }}
  h1 {{ font-size:24px; margin:0 0 4px; }}
  .sub {{ color:var(--muted); font-size:14px; margin-bottom:8px; }}
  .note {{ color:var(--muted); font-size:13px; margin-bottom:24px; }}
  h2 {{ font-size:17px; margin:32px 0 12px; }}
  .card {{ border:1px solid var(--border); border-radius:10px; padding:14px 20px; margin-bottom:10px;
          display:flex; justify-content:space-between; align-items:center; gap:16px; flex-wrap:wrap; }}
  .card a {{ color:var(--accent); text-decoration:none; font-weight:500; }}
  .card a:hover {{ text-decoration:underline; }}
  .date {{ color:var(--muted); font-size:13px; white-space:nowrap; }}
  table {{ width:100%; border-collapse:collapse; font-size:14px; border:1px solid var(--border);
          border-radius:10px; overflow:hidden; }}
  th, td {{ text-align:left; padding:9px 12px; border-bottom:1px solid var(--border); }}
  th {{ color:var(--muted); font-weight:400; font-size:13px; }}
  td.num, th.num {{ text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }}
  .badge {{ font-size:12px; padding:2px 8px; border-radius:999px; white-space:nowrap; }}
  .ok {{ color:#16a34a; background:rgba(22,163,42,.12); }}
  .warn {{ color:#d97706; background:rgba(217,119,6,.12); }}
  .foot {{ color:var(--muted); font-size:13px; margin-top:24px; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>AI 行业速递</h1>
  <div class="sub">每日 AI 行业日报 + 国内外大模型 API 价格看板 · 数据更新于 {updated}</div>
  <div class="note">价格为官方公告 / 官方定价页口径，单位：每百万 tokens；标注「未核实」的为二手信源，仅供参考。</div>

  <h2>📰 日报归档</h2>
  {reports}

  <h2>🔄 近期价格变动</h2>
  {changes}

  <h2>💰 国内模型价格（人民币）</h2>
  <table><thead><tr><th>厂商</th><th>模型</th><th class="num">输入价</th><th class="num">输出价</th><th class="num">缓存命中</th><th>生效日期</th><th>信源</th></tr></thead>
  <tbody>{domestic}</tbody></table>

  <h2>🌍 国外模型价格（美元）</h2>
  <table><thead><tr><th>厂商</th><th>模型</th><th class="num">输入价</th><th class="num">输出价</th><th class="num">缓存命中</th><th>生效日期</th><th>信源</th></tr></thead>
  <tbody>{international}</tbody></table>

  <div class="foot">本页由 GitHub Actions 每日自动构建（fetch_prices.py → build_site.py）。项目开源，欢迎 fork 自用。</div>
</div>
</body>
</html>
"""


def esc(s) -> str:
    return (str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def rows(items: list[dict]) -> str:
    out = []
    for r in items:
        badge = '<span class="badge ok">官方</span>' if r.get("verified") else '<span class="badge warn">未核实</span>'
        out.append(
            "<tr><td>{v}</td><td>{m}</td><td class=\"num\">{i}</td><td class=\"num\">{o}</td>"
            "<td class=\"num\">{c}</td><td>{d}</td><td>{b} <span style=\"color:var(--muted);font-size:12px\">{s}</span></td></tr>".format(
                v=esc(r.get("vendor")), m=esc(r.get("model")), i=esc(r.get("input")), o=esc(r.get("output")),
                c=esc(r.get("cache") or "—"), d=esc(r.get("effectiveDate")), b=badge, s=esc(r.get("source")),
            )
        )
    return "".join(out)


def reports_html() -> str:
    if not REPORTS_DIR.exists():
        return '<div class="card"><span class="date">暂无归档</span></div>'
    md_files = sorted(REPORTS_DIR.glob("*.md"), reverse=True)
    if not md_files:
        return '<div class="card"><span class="date">暂无归档</span></div>'
    return "".join(
        '<div class="card"><a href="reports/{name}">{title}</a><span class="date">{date}</span></div>'.format(
            name=f.name, title=f.stem + " 日报", date=f.stem)
        for f in md_files
    )


def changes_html(items: list[dict]) -> str:
    if not items:
        return '<div class="card"><span class="date">近期无记录的价格变动</span></div>'
    return "".join(
        '<div class="card"><div><b>{v}</b> · {c} <span class="date">{d}</span><br>'
        '<span style="font-size:14px">{detail}</span><br>'
        '<span class="date">来源：{s}</span></div></div>'.format(
            v=esc(c.get("vendor")), c=esc(c.get("change")), d=esc(c.get("date")),
            detail=esc(c.get("detail")), s=esc(c.get("source")),
        )
        for c in items
    )


def main() -> None:
    data = json.loads(DATA_FILE.read_text(encoding="utf-8")) if DATA_FILE.exists() else {}
    DIST.mkdir(parents=True, exist_ok=True)
    html = PAGE.format(
        updated=esc(data.get("updatedAt") or datetime.now(CST).strftime("%Y-%m-%d %H:%M CST")),
        reports=reports_html(),
        changes=changes_html(data.get("changes", [])),
        domestic=rows(data.get("domestic", [])),
        international=rows(data.get("international", [])),
    )
    (DIST / "index.html").write_text(html, encoding="utf-8")
    # 日报归档随站点一起发布，保证链接可用
    dist_reports = DIST / "reports"
    dist_reports.mkdir(exist_ok=True)
    if REPORTS_DIR.exists():
        for f in REPORTS_DIR.glob("*.md"):
            (dist_reports / f.name).write_text(f.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"[build_site] dist/index.html written ({len(html)} bytes)")


if __name__ == "__main__":
    main()
