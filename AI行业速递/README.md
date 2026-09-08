# AI 行业速递 · 项目目录

项目主体的详细说明见仓库根目录的 [README.md](../README.md)（含看板截图与使用指南）。

本目录内容：

- `data/prices.json` — 国内外模型 API 价格数据（`verified: true` 为官方口径，其余为「未核实」）
- `prompts/daily-report.md` — 日报生成提示词，粘贴到任意 AI 助手即可生成当日日报
- `reports/` — 日报归档（`YYYY-MM-DD.md`），存入后次日 8:00 自动出现在站点
- `scripts/fetch_prices.py` — 每日抓取 9 家官方定价页状态（零依赖）
- `scripts/build_site.py` — 渲染静态站点（零依赖）
