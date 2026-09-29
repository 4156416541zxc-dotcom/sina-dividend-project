"""
新浪财经分红数据预处理脚本
功能：清洗、转换、统计分析原始分红数据
"""

import pandas as pd
import os
import json
from datetime import datetime


class DividendPreprocessor:
    """分红数据预处理器"""

    def __init__(self, input_path="../data/raw/sina_dividend_raw.csv",
                 output_dir="../data/processed"):
        self.input_path = input_path
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def load_data(self):
        """加载原始数据"""
        if not os.path.exists(self.input_path):
            raise FileNotFoundError(f"原始数据文件不存在: {self.input_path}")
        df = pd.read_csv(self.input_path, encoding="utf-8-sig")
        print(f"[INFO] 加载原始数据: {len(df)} 条记录")
        return df

    def clean_data(self, df):
        """数据清洗"""
        print("[INFO] 开始数据清洗...")

        # 1. 去除完全重复的记录
        initial_count = len(df)
        df = df.drop_duplicates()
        print(f"  - 去除重复记录: {initial_count - len(df)} 条")

        # 2. 日期格式标准化
        df["公告日期"] = pd.to_datetime(df["公告日期"], errors="coerce")
        df["除权除息日"] = pd.to_datetime(df["除权除息日"], errors="coerce")
        df["股权登记日"] = pd.to_datetime(df["股权登记日"], errors="coerce")

        # 3. 提取年份
        df["年份"] = df["公告日期"].dt.year

        # 4. 数值列确保为float
        numeric_cols = ["送股(每10股)", "转增(每10股)", "派息税前(每10股/元)"]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

        # 5. 计算每股派息（元/股）
        df["每股派息(元)"] = df["派息税前(每10股/元)"] / 10.0

        # 6. 计算每股送转股数
        df["每股送转(股)"] = (df["送股(每10股)"] + df["转增(每10股)"]) / 10.0

        # 7. 标记是否有现金分红
        df["是否现金分红"] = df["派息税前(每10股/元)"] > 0

        # 8. 标记是否有送转股
        df["是否送转股"] = (df["送股(每10股)"] + df["转增(每10股)"]) > 0

        print(f"  - 清洗后数据量: {len(df)} 条")
        return df

    def generate_statistics(self, df):
        """生成统计分析数据"""
        print("[INFO] 生成统计分析...")

        stats = {}

        # 1. 总体统计
        stats["overview"] = {
            "total_records": int(len(df)),
            "total_stocks": int(df["股票代码"].nunique()),
            "date_range": {
                "start": str(df["公告日期"].min().date()),
                "end": str(df["公告日期"].max().date()),
            },
            "cash_dividend_count": int(df["是否现金分红"].sum()),
            "stock_dividend_count": int(df["是否送转股"].sum()),
        }

        # 2. 按股票统计
        stock_stats = []
        for (code, name), group in df.groupby(["股票代码", "股票名称"]):
            stock_stat = {
                "股票代码": code,
                "股票名称": name,
                "分红次数": int(len(group)),
                "现金分红次数": int(group["是否现金分红"].sum()),
                "送转股次数": int(group["是否送转股"].sum()),
                "累计每股派息(元)": round(float(group["每股派息(元)"].sum()), 4),
                "平均每股派息(元)": round(float(group["每股派息(元)"].mean()), 4),
                "最大每股派息(元)": round(float(group["每股派息(元)"].max()), 4),
                "累计每股送转(股)": round(float(group["每股送转(股)"].sum()), 4),
                "首次分红年份": int(group["年份"].min()),
                "最近分红年份": int(group["年份"].max()),
            }
            stock_stats.append(stock_stat)
        stats["by_stock"] = stock_stats

        # 3. 按年份统计
        year_stats = []
        for year, group in df.groupby("年份"):
            year_stat = {
                "年份": int(year),
                "分红事件数": int(len(group)),
                "涉及股票数": int(group["股票代码"].nunique()),
                "平均每股派息(元)": round(float(group["每股派息(元)"].mean()), 4),
                "总派息(每10股/元)": round(float(group["派息税前(每10股/元)"].sum()), 2),
            }
            year_stats.append(year_stat)
        stats["by_year"] = sorted(year_stats, key=lambda x: x["年份"])

        # 4. 按股票-年份透视（派息）
        pivot_dividend = df.pivot_table(
            index="股票名称",
            columns="年份",
            values="每股派息(元)",
            aggfunc="sum",
            fill_value=0
        ).round(4)
        stats["pivot_dividend"] = pivot_dividend.reset_index().to_dict(orient="records")

        return stats

    def save_processed_data(self, df, stats):
        """保存处理后的数据"""
        # 保存清洗后的CSV
        csv_path = os.path.join(self.output_dir, "sina_dividend_cleaned.csv")
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        print(f"[INFO] 清洗后数据已保存: {csv_path}")

        # 保存统计JSON
        json_path = os.path.join(self.output_dir, "dividend_statistics.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2, default=str)
        print(f"[INFO] 统计数据已保存: {json_path}")

        # 保存Excel（多sheet）
        excel_path = os.path.join(self.output_dir, "sina_dividend_analysis.xlsx")
        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="清洗后数据", index=False)
            pd.DataFrame(stats["by_stock"]).to_excel(writer, sheet_name="按股票统计", index=False)
            pd.DataFrame(stats["by_year"]).to_excel(writer, sheet_name="按年份统计", index=False)
        print(f"[INFO] Excel分析报告已保存: {excel_path}")

        return csv_path, json_path, excel_path

    def run(self):
        """执行完整预处理流程"""
        print("=" * 60)
        print("新浪财经分红数据预处理")
        print("=" * 60)

        # 加载数据
        df = self.load_data()

        # 数据清洗
        df = self.clean_data(df)

        # 生成统计
        stats = self.generate_statistics(df)

        # 保存结果
        csv_path, json_path, excel_path = self.save_processed_data(df, stats)

        # 打印摘要
        print("\n" + "=" * 60)
        print("预处理完成摘要")
        print("=" * 60)
        print(f"总记录数: {stats['overview']['total_records']}")
        print(f"涉及股票: {stats['overview']['total_stocks']} 只")
        print(f"日期范围: {stats['overview']['date_range']['start']} ~ {stats['overview']['date_range']['end']}")
        print(f"现金分红次数: {stats['overview']['cash_dividend_count']}")
        print(f"送转股次数: {stats['overview']['stock_dividend_count']}")

        return df, stats


if __name__ == "__main__":
    preprocessor = DividendPreprocessor()
    preprocessor.run()
