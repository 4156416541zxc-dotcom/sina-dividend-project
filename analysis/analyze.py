"""
比亚迪后复权行情指标计算 + 教材 P92 实战任务
输出:
  - data/byd_indicators.csv   每日 MA/回撤
  - data/descriptive_stats.csv 定量变量描述性统计
  - data/corr_matrix.csv      相关系数矩阵
  - web/src/data.js           前端聚合数据
"""
import json
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_IN = ROOT / "data" / "byd_post_adjusted.csv"
CSV_OUT = ROOT / "data" / "byd_indicators.csv"
DESC_OUT = ROOT / "data" / "descriptive_stats.csv"
CORR_OUT = ROOT / "data" / "corr_matrix.csv"
JS_OUT = ROOT / "web" / "src" / "data.js"

QUANT_COLS = ["开盘", "收盘", "最高", "最低", "成交量", "成交额",
              "振幅", "涨跌幅", "涨跌额", "换手率"]


def load() -> pd.DataFrame:
    df = pd.read_csv(CSV_IN, parse_dates=["日期"])
    return df.sort_values("日期").reset_index(drop=True)


def add_ma(df: pd.DataFrame) -> pd.DataFrame:
    for n in (5, 20, 60, 120):
        df[f"MA{n}"] = df["收盘"].rolling(n).mean().round(2)
    return df


def add_drawdown(df: pd.DataFrame) -> pd.DataFrame:
    cummax = df["收盘"].cummax()
    df["回撤"] = (df["收盘"] / cummax - 1 * 100).round(2)
    return df


def yearly_returns(df: pd.DataFrame) -> dict:
    out = {}
    for year, g in df.groupby(df["日期"].dt.year):
        first_close = g.iloc[0]["收盘"]
        last_close = g.iloc[-1]["收盘"]
        ret = (last_close / first_close - 1) * 100
        out[str(year)] = {
            "年初收盘": round(first_close, 2),
            "年末收盘": round(last_close, 2),
            "年度收益率%": round(ret, 2),
            "年内最高": round(g["最高"].max(), 2),
            "年内最低": round(g["最低"].min(), 2),
            "交易日数": int(len(g)),
        }
    return out


def monthly_returns(df: pd.DataFrame) -> list:
    g = df.groupby(df["日期"].dt.to_period("M"))["收盘"].agg(["first", "last"])
    g["ret%"] = ((g["last"] / g["first"] - 1) * 100).round(2)
    return [{"month": str(idx), "ret": float(row["ret%"])} for idx, row in g.iterrows()]


def max_drawdown(df: pd.DataFrame) -> dict:
    cummax = df["收盘"].cummax()
    dd = df["收盘"] / cummax - 1
    i = dd.idxmin()
    peak_i = df.loc[:i, "收盘"].idxmax()
    return {
        "最大回撤%": round(float(dd.min() * 100), 2),
        "峰值日期": str(df.loc[peak_i, "日期"].date()),
        "谷值日期": str(df.loc[i, "日期"].date()),
        "峰值价": round(float(df.loc[peak_i, "收盘"]), 2),
        "谷值价": round(float(df.loc[i, "收盘"]), 2),
    }


def main():
    df = load()
    df = add_ma(df)
    df = add_drawdown(df)
    df.to_csv(CSV_OUT, index=False, encoding="utf-8-sig")
    print(f"[indicators] {len(df)} rows -> {CSV_OUT}")

    # 教材任务1: 描述性统计
    desc = df[QUANT_COLS].describe().round(2)
    desc.to_csv(DESC_OUT, encoding="utf-8-sig")
    print(f"[descriptive] -> {DESC_OUT}")
    print(desc.to_string())

    # 教材任务2: 相关系数矩阵
    corr = df[QUANT_COLS].corr().round(3)
    corr.to_csv(CORR_OUT, encoding="utf-8-sig")
    print(f"\n[correlation] -> {CORR_OUT}")

    yr = yearly_returns(df)
    mr = monthly_returns(df)
    mdd = max_drawdown(df)

    # 教材任务4: 2023年4-6月 K 线聚焦
    mask_23q2 = (df["日期"] >= "2023-04-01") & (df["日期"] <= "2023-06-30")
    df_23q2 = df[mask_23q2]
    kline_23q2 = [
        [str(r["日期"].date()), round(float(r["开盘"]), 2), round(float(r["收盘"]), 2),
         round(float(r["最低"]), 2), round(float(r["最高"]), 2)]
        for _, r in df_23q2.iterrows()
    ]
    dates_23q2 = [str(d.date()) for d in df_23q2["日期"]]
    vol_23q2 = [int(v) for v in df_23q2["成交量"]]

    payload = {
        "meta": {
            "code": "002594", "name": "比亚迪", "adjust": "后复权",
            "range": [str(df["日期"].iloc[0].date()), str(df["日期"].iloc[-1].date())],
            "tradingDays": int(len(df)),
        },
        "latest": {
            "date": str(df["日期"].iloc[-1].date()),
            "close": float(df["收盘"].iloc[-1]),
            "high": float(df["最高"].iloc[-1]),
            "low": float(df["最低"].iloc[-1]),
            "pctChange": float(df["涨跌幅"].iloc[-1]),
            "volume": int(df["成交量"].iloc[-1]),
        },
        "head5": df.head(5)[["日期"] + QUANT_COLS].assign(
            日期=lambda x: x["日期"].dt.strftime("%Y-%m-%d")
        ).to_dict(orient="records"),
        "descriptiveStats": json.loads(desc.to_json(orient="index")),
        "corrMatrix": {
            "labels": QUANT_COLS,
            "values": corr.values.tolist(),
        },
        "kline": [
            [str(r["日期"].date()), round(float(r["开盘"]), 2), round(float(r["收盘"]), 2),
             round(float(r["最低"]), 2), round(float(r["最高"]), 2)]
            for _, r in df.iterrows()
        ],
        "kline23Q2": kline_23q2,
        "dates23Q2": dates_23q2,
        "volume23Q2": vol_23q2,
        "closeSeries": [round(float(v), 2) for v in df["收盘"]],
        "ma": {
            "MA5": [None if pd.isna(v) else round(float(v), 2) for v in df["MA5"]],
            "MA20": [None if pd.isna(v) else round(float(v), 2) for v in df["MA20"]],
            "MA60": [None if pd.isna(v) else round(float(v), 2) for v in df["MA60"]],
            "MA120": [None if pd.isna(v) else round(float(v), 2) for v in df["MA120"]],
        },
        "volume": [int(v) for v in df["成交量"]],
        "dates": [str(d.date()) for d in df["日期"]],
        "yearlyReturns": yr,
        "monthlyReturns": mr,
        "maxDrawdown": mdd,
    }

    JS_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(JS_OUT, "w", encoding="utf-8") as f:
        f.write("// AUTO GENERATED by analysis/analyze.py\n")
        f.write("export const BYD_DATA = ")
        f.write(json.dumps(payload, ensure_ascii=False, indent=2))
        f.write(";\n")
    print(f"\n[frontend] -> {JS_OUT}")

    print("\n=== 年度收益率 ===")
    for y, v in yr.items():
        print(f"  {y}: {v['年度收益率%']:+.2f}%  ({v['年初收盘']} -> {v['年末收盘']})")
    print(f"\n=== 最大回撤: {mdd['最大回撤%']}% ===")


if __name__ == "__main__":
    main()
