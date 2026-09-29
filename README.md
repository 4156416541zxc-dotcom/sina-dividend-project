# 新浪财经历史分红数据获取与预处理实战作业

## 项目概述

本项目是一个完整的数据工程实战项目，涵盖从新浪财经网站爬取股票历史分红数据，到数据清洗、统计分析、可视化展示和自动化测试的全流程。

## 技术栈

- **数据采集**: Python + Requests + BeautifulSoup4
- **数据处理**: Pandas + NumPy
- **数据存储**: CSV / JSON / Excel
- **前端展示**: HTML5 + CSS3 + JavaScript + ECharts
- **自动化测试**: Playwright
- **版本控制**: Git

## 项目结构

```
sina-dividend-project/
├── src/                          # 源代码目录
│   ├── scraper.py               # 新浪财经数据爬虫
│   ├── preprocess.py            # 数据预处理脚本
│   └── generate_js_data.py      # 生成前端数据文件
├── data/                         # 数据目录
│   ├── raw/                     # 原始数据
│   │   ├── sina_dividend_raw.csv
│   │   └── sina_dividend_raw.json
│   └── processed/               # 处理后数据
│       ├── sina_dividend_cleaned.csv
│       ├── dividend_statistics.json
│       └── sina_dividend_analysis.xlsx
├── web/                          # 前端网页
│   ├── index.html               # 主页面
│   ├── css/
│   │   └── style.css            # 样式文件
│   └── js/
│       ├── data.js              # 数据文件（自动生成）
│       └── app.js               # 应用逻辑
├── tests/                        # 测试目录
│   └── test_web.py              # Playwright网页测试
├── screenshots/                  # 截图目录
│   ├── *.png                    # 网页截图
│   └── test_report.json         # 测试报告
├── docs/                         # 文档目录
│   └── conversation.md          # Agent交互对话记录（脱敏）
└── README.md                     # 项目说明
```

## 样本股票

| 股票代码 | 股票名称 | 行业 |
|---------|---------|------|
| 600519 | 贵州茅台 | 白酒 |
| 601398 | 工商银行 | 银行 |
| 601318 | 中国平安 | 保险 |
| 000651 | 格力电器 | 家电 |
| 600036 | 招商银行 | 银行 |

## 数据概览

- **总记录数**: 161 条分红记录
- **涉及股票**: 5 只
- **时间范围**: 1996年 - 2026年
- **现金分红次数**: 154 次
- **送转股次数**: 21 次

## 快速开始

### 1. 安装依赖

```bash
pip install requests pandas beautifulsoup4 lxml openpyxl playwright
python -m playwright install chromium
```

### 2. 运行数据爬虫

```bash
cd src
python scraper.py
```

### 3. 运行数据预处理

```bash
python preprocess.py
```

### 4. 生成前端数据

```bash
python generate_js_data.py
```

### 5. 查看网页

直接在浏览器中打开 `web/index.html`

### 6. 运行自动化测试

```bash
cd tests
python test_web.py
```

## 功能特性

### 数据采集
- 支持批量爬取多只股票分红数据
- 自动解析HTML表格结构
- 礼貌延时，避免对服务器造成压力
- 支持CSV和JSON双格式输出

### 数据预处理
- 自动去重
- 日期格式标准化
- 数值类型转换
- 衍生指标计算（每股派息、每股送转等）
- 多维度统计分析（按股票、按年份）
- 透视表生成
- Excel多Sheet导出

### 可视化展示
- 历年分红趋势图（双Y轴）
- 各股票累计派息对比图
- 分红类型分布饼图
- 股票×年份派息热力图
- 年度分红事件统计图
- 多维度雷达图
- 可筛选、可搜索的数据表格
- 响应式布局设计

### 自动化测试
- 页面加载测试
- 导航栏功能测试
- 图表渲染测试
- 数据表格测试
- 筛选功能测试
- 分页功能测试
- 响应式布局测试
- 自动截图和测试报告生成

## 考核点对应

| 考核点 | 实现方式 |
|--------|---------|
| plan模式确认需求 | 项目开始前进行需求分析和任务规划 |
| ui-ux-pro-max-skill设计ui | 现代化UI设计，包含渐变、动画、响应式布局 |
| playwright做网页测试 | 完整的Playwright自动化测试套件 |

## 数据来源

数据来源于新浪财经个股分红页面：
`https://vip.stock.finance.sina.com.cn/corp/go.php/vISSUE_ShareBonus/stockid/{股票代码}.phtml`

**免责声明**: 本项目数据仅供学习研究使用，不构成任何投资建议。

## 许可证

MIT License
