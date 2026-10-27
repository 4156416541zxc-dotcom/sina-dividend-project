# AGENTS.md — Agent 协作规范

> 本文件为 AI Agent 进入本仓库时的第一必读文档，用于快速对齐项目目标、技术栈、目录结构与交互规范。

## 项目概述

**比亚迪(002594.SZ)后复权股价走势分析与可视化**

- 数据源：2023 年历史行情(Excel) + 2024-01 至 2026-10 东方财富公开 API(后复权)
- 分析目标：基于完整后复权日线数据，完成价格趋势、均线、成交量、涨跌幅分布、年度收益等指标分析，并输出交互式可视化页面
- 交付物：分析脚本 + TDesign 可视化页面 + git 仓库

## 技术栈

| 层 | 选型 | 说明 |
|---|---|---|
| 数据处理 | Python 3.13 + pandas | 数据清洗、指标计算 |
| 可视化图表 | ECharts 5 | K线、均线、成交量、收益分布 |
| UI 组件库 | TDesign Vue Next | 页面布局、卡片、标签页、筛选器 |
| 前端工程 | Vite + Vue 3 | 本地 dev / build |
| 版本管理 | Git | 提交规范见下 |

## 目录结构

```
byd-stock-analysis/
├── AGENTS.md                  # 本文件
├── README.md                  # 项目说明
├── data/
│   ├── byd_post_adjusted.csv  # 合并后完整数据(2023-01 ~ 2026-10)
│   └── raw_2024_2026.json     # API 原始返回(缓存)
├── analysis/
│   ├── fetch_and_merge.py     # 数据采集与合并脚本
│   └── analyze.py             # 指标计算与统计输出
└── web/
    ├── index.html             # Vite 入口
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── main.js
        ├── App.vue
        └── components/        # TDesign + ECharts 组件
```

## 设计规范（ui-ux-pro 产出）

### 设计基调
- **风格**：金融数据仪表盘，深色系为主、数据高亮色点缀
- **主色**：TDesign Brand Blue `#0052D9`（主操作/正向）
- **涨跌色**：红涨 `#D54941` / 绿跌 `#2BA471`（A 股习惯）
- **背景**：`#F3F3F3` 浅灰底 + 白色卡片
- **字体**：系统无衬线，数字用等宽字体便于对齐

### 页面布局
1. 顶部：标题栏 + 股票代码/名称 + 当前价/涨跌幅大数字卡片
2. 核心区：K 线主图(含 MA5/MA20/MA60/MA120) + 成交量副图
3. 侧栏/下方：年度收益对比柱状图、月涨跌幅热力、关键指标卡片
4. 筛选器：日期范围选择器、均线开关

## 交互规范

- Agent 必须先读本文件再动手
- 数据口径以 `data/byd_post_adjusted.csv` 为准，不得在代码里硬编码行情数值
- 图表指标必须可复算：所有衍生指标在 `analysis/analyze.py` 中由原始 OHLCV 计算
- 提交信息格式：`<type>: <summary>`，type ∈ feat/fix/docs/refactor/chore
