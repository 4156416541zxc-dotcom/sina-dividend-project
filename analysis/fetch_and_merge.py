"""
比亚迪(002594)后复权历史行情数据合并
- 2023 年数据来自原始 Excel
- 2024-01-02 至 2026-10-27 数据来自 data/raw_2024_2026.json (东方财富后复权)
输出: data/byd_post_adjusted.csv
"""
import json
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_XLSX = r"D:\360极速浏览器X下载\比亚迪后复权历史行情数据 (1).xlsx"
RAW_JSON = ROOT / "data" / "raw_2024_2026.json"
OUT_CSV = ROOT / "data" / "byd_post_adjusted.csv"


def load_api_json() -> pd.DataFrame:
    with open(RAW_JSON, encoding="utf-8") as f:
        raw = json.load(f)
    rows = [r.split(",") for r in raw["data"]["klines"]]
    cols = ["日期", "开盘", "收盘", "最高", "最低", "成交量", "成交额",
            "振幅", "涨跌幅", "涨跌额", "换手率"]
    df = pd.DataFrame(rows, columns=cols)
    df["日期"] = pd.to_datetime(df["日期"])
    for c in cols[1:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def main():
    df_2023 = pd.read_excel(SRC_XLSX)
    df_2023["日期"] = pd.to_datetime(df_2023["日期"])
    print(f"[2023 Excel] {len(df_2023)} rows, {df_2023['日期'].min().date()} ~ {df_2023['日期'].max().date()}")

    df_new = load_api_json()
    print(f"[2024+ JSON]  {len(df_new)} rows, {df_new['日期'].min().date()} ~ {df_new['日期'].max().date()}")

    merged = pd.concat([df_2023, df_new], ignore_index=True)
    merged = merged.drop_duplicates(subset=["日期"]).sort_values("日期").reset_index(drop=True)

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
    print(f"[Merged]     {len(merged)} rows -> {OUT_CSV}")
    print(f"  Range: {merged['日期'].min().date()} ~ {merged['日期'].max().date()}")
    print("\nHead:")
    print(merged.head(3).to_string(index=False))
    print("\nTail:")
    print(merged.tail(3).to_string(index=False))


if __name__ == "__main__":
    main()
