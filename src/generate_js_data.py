"""
生成网页用的JavaScript数据文件
"""
import pandas as pd
import json
import os

# 路径
base_dir = os.path.dirname(__file__)
cleaned_csv = os.path.join(base_dir, "../data/processed/sina_dividend_cleaned.csv")
stats_json = os.path.join(base_dir, "../data/processed/dividend_statistics.json")
output_js = os.path.join(base_dir, "../web/js/data.js")

# 读取清洗后数据
df = pd.read_csv(cleaned_csv, encoding="utf-8-sig")

# 日期格式化为字符串
for col in ["公告日期", "除权除息日", "股权登记日"]:
    df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")
    df[col] = df[col].fillna("--")

# 股票代码补零
df["股票代码"] = df["股票代码"].astype(str).str.zfill(6)

# 转换为记录列表
records = df.to_dict(orient="records")

# 读取统计数据
with open(stats_json, "r", encoding="utf-8") as f:
    stats = json.load(f)

# 修复股票代码格式
for item in stats["by_stock"]:
    item["股票代码"] = str(item["股票代码"]).zfill(6)

# 生成JS内容
js_content = """// 新浪财经分红数据 - 自动生成
// 数据来源：新浪财经个股分红页面
// 生成时间：""" + pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S") + """

const DIVIDEND_DATA = """ + json.dumps(records, ensure_ascii=False, indent=2) + """;

const DIVIDEND_STATS = """ + json.dumps(stats, ensure_ascii=False, indent=2) + """;

// 股票列表
const STOCK_LIST = [...new Set(DIVIDEND_DATA.map(d => d["股票名称"]))];

// 年份列表
const YEAR_LIST = [...new Set(DIVIDEND_DATA.map(d => d["公告日期"].substring(0, 4)))].sort();
"""

with open(output_js, "w", encoding="utf-8") as f:
    f.write(js_content)

stock_list = list(set(df["股票名称"].tolist()))
year_list = sorted(list(set(df["公告日期"].str[:4].tolist())))
print(f"[INFO] 数据文件已生成: {output_js}")
print(f"  - 数据记录: {len(records)} 条")
print(f"  - 股票数量: {len(stock_list)} 只")
print(f"  - 年份范围: {year_list[0]} ~ {year_list[-1]}")
