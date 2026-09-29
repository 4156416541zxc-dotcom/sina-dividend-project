"""
新浪财经历史分红数据爬虫
功能：从新浪财经获取指定股票的历史分红数据
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import json


class SinaDividendScraper:
    """新浪财经分红数据爬虫"""

    BASE_URL = "https://vip.stock.finance.sina.com.cn/corp/go.php/vISSUE_ShareBonus/stockid/{stock_code}.phtml"

    def __init__(self, output_dir="../data/raw"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }

    def fetch_page(self, stock_code):
        """获取股票分红页面HTML"""
        url = self.BASE_URL.format(stock_code=stock_code)
        try:
            response = requests.get(url, headers=self.headers, timeout=20)
            response.encoding = "gb2312"
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"[ERROR] 获取 {stock_code} 页面失败: {e}")
            return None

    def parse_dividend_table(self, html, stock_code, stock_name=""):
        """解析分红数据表格"""
        if not html:
            return pd.DataFrame()

        soup = BeautifulSoup(html, "lxml")
        tables = soup.find_all("table")

        dividend_table = None
        for table in tables:
            rows = table.find_all("tr")
            if len(rows) > 10:
                first_row_text = rows[0].get_text(strip=True)
                if "分红" in first_row_text or "公告" in first_row_text:
                    dividend_table = table
                    break

        if dividend_table is None and len(tables) > 12:
            dividend_table = tables[12]

        if dividend_table is None:
            print(f"[WARN] {stock_code} 未找到分红数据表")
            return pd.DataFrame()

        rows = dividend_table.find_all("tr")
        data = []

        for row in rows[3:]:
            cells = row.find_all(["td", "th"])
            if len(cells) < 7:
                continue

            cell_texts = [c.get_text(strip=True) for c in cells]

            if not cell_texts[0] or cell_texts[0] == "--":
                continue

            try:
                record = {
                    "股票代码": stock_code,
                    "股票名称": stock_name,
                    "公告日期": cell_texts[0],
                    "送股(每10股)": self._safe_float(cell_texts[1]),
                    "转增(每10股)": self._safe_float(cell_texts[2]),
                    "派息税前(每10股/元)": self._safe_float(cell_texts[3]),
                    "进度": cell_texts[4] if len(cell_texts) > 4 else "",
                    "除权除息日": cell_texts[5] if len(cell_texts) > 5 else "",
                    "股权登记日": cell_texts[6] if len(cell_texts) > 6 else "",
                }
                data.append(record)
            except (IndexError, ValueError) as e:
                print(f"[WARN] 解析行失败: {cell_texts}, 错误: {e}")
                continue

        df = pd.DataFrame(data)
        return df

    def _safe_float(self, value):
        """安全转换为浮点数"""
        try:
            if value in ("--", "", "-"):
                return 0.0
            return float(value)
        except (ValueError, TypeError):
            return 0.0

    def scrape_stock(self, stock_code, stock_name=""):
        """爬取单只股票的分红数据"""
        print(f"[INFO] 正在爬取 {stock_name}({stock_code}) 的分红数据...")
        html = self.fetch_page(stock_code)
        if html is None:
            return pd.DataFrame()

        df = self.parse_dividend_table(html, stock_code, stock_name)
        print(f"[INFO] {stock_name}({stock_code}) 获取到 {len(df)} 条分红记录")
        return df

    def scrape_multiple(self, stock_list):
        """批量爬取多只股票"""
        all_data = []
        for stock_code, stock_name in stock_list:
            df = self.scrape_stock(stock_code, stock_name)
            if not df.empty:
                all_data.append(df)
            time.sleep(1)

        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            return combined_df
        return pd.DataFrame()

    def save_data(self, df, filename="dividend_data.csv"):
        """保存数据到CSV"""
        filepath = os.path.join(self.output_dir, filename)
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        print(f"[INFO] 数据已保存到 {filepath}, 共 {len(df)} 条记录")
        return filepath

    def save_json(self, df, filename="dividend_data.json"):
        """保存数据到JSON"""
        filepath = os.path.join(self.output_dir, filename)
        records = df.to_dict(orient="records")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        print(f"[INFO] JSON数据已保存到 {filepath}")
        return filepath


def main():
    """主函数：爬取示例股票的分红数据"""
    stock_list = [
        ("600519", "贵州茅台"),
        ("601398", "工商银行"),
        ("601318", "中国平安"),
        ("000651", "格力电器"),
        ("600036", "招商银行"),
    ]

    scraper = SinaDividendScraper(
        output_dir=os.path.join(os.path.dirname(__file__), "../data/raw")
    )

    df = scraper.scrape_multiple(stock_list)

    if not df.empty:
        scraper.save_data(df, "sina_dividend_raw.csv")
        scraper.save_json(df, "sina_dividend_raw.json")

        print("\n" + "=" * 60)
        print("数据爬取完成统计")
        print("=" * 60)
        print(f"总记录数: {len(df)}")
        print(f"涉及股票数: {df['股票代码'].nunique()}")
        print(f"日期范围: {df['公告日期'].min()} ~ {df['公告日期'].max()}")
        print("\n各股票记录数:")
        print(df.groupby(["股票代码", "股票名称"]).size().to_string())
    else:
        print("[ERROR] 未获取到任何数据")


if __name__ == "__main__":
    main()
