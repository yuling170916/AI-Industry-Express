# AI 行业速递（ai-daily-digest）

每日 AI 行业中文日报 + 国内外大模型 API 价格看板。仓库通过 GitHub Actions 每天北京时间 8:00 自动刷新官方定价页状态并重建站点，GitHub Pages 地址即「每天打开刷新就能看」的网页链接。

## 功能

- 💰 **价格看板**：国内（DeepSeek / 豆包 / 混元 / 智谱 / Kimi / MiniMax / 通义）与国外（OpenAI / Anthropic / Google）主流模型 API 输入价、输出价、缓存命中价对比，标注「官方 / 未核实」信源。
- 📰 **日报归档**：`reports/` 目录按日期存放日报（Markdown）。
- 🔁 **每日自动更新**：Actions 定时任务抓取各官方定价页，刷新可达性并重建页面。

## 目录结构

```
AI行业速递/
├── README.md              ← 本文件
├── data/
│   └── prices.json        ← 价格数据（脚本每日刷新 sources 状态；行数据人工校准）
├── prompts/
│   └── daily-report.md    ← 日报生成提示词（配合任意 LLM 使用）
├── reports/               ← 日报归档（YYYY-MM-DD.md）
└── scripts/
    ├── fetch_prices.py    ← 抓取官方定价页状态（零依赖，Python 3.9+）
    └── build_site.py      ← 渲染 dist/index.html（零依赖）
.github/workflows/
└── daily.yml              ← 每日 8:00（北京时间）自动构建并发布 Pages
```

## 快速开始（fork 后自用）

1. Fork 本仓库；
2. 在 Settings → Pages 中选择 **gh-pages 分支 / (root)**（首次 Actions 运行后自动生成该分支）；
3. 次日 8:00 后即可通过 `https://<你的用户名>.github.io/<你的仓库名>/` 访问；
4. 手动校准价格：直接编辑 `data/prices.json`（推送后 Actions 会自动重建页面）；
5. 生成日报：把 `prompts/daily-report.md` 粘贴到你常用的 AI 助手（Kimi / ChatGPT / Claude 等），产出后存入 `reports/` 即可自动出现在站点归档中。

## 设计原则

- **零第三方依赖**：脚本只用 Python 标准库，Actions 环境开箱即用；
- **优雅降级**：任一官方页面抓取失败不影响整体，状态记录在 `prices.json` 的 `sources` 字段；
- **信源分级**：`verified: true` 表示官方公告/定价页口径，其余标注「未核实」，不混同。

## 许可

MIT（欢迎随意 fork、改造、二次分发）。
