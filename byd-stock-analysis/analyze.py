# -*- coding: utf-8 -*-
"""比亚迪后复权历史行情数据分析脚本"""
import pandas as pd
import json
import os

# 读取数据
df = pd.read_excel(r'D:\360极速浏览器X下载\比亚迪后复权历史行情数据.xlsx')
df = df.sort_values('日期').reset_index(drop=True)

# 基础统计
first_row = df.iloc[0]
last_row = df.iloc[-1]
year_open = first_row['开盘']
year_close = last_row['收盘']
year_high = df['最高'].max()
year_low = df['最低'].min()
year_high_date = df.loc[df['最高'].idxmax(), '日期'].strftime('%Y-%m-%d')
year_low_date = df.loc[df['最低'].idxmin(), '日期'].strftime('%Y-%m-%d')
year_change = year_close - year_open
year_change_pct = (year_close / year_open - 1) * 100
avg_volume = int(df['成交量'].mean())
avg_amount = df['成交额'].mean()
total_amount = df['成交额'].sum()
up_days = len(df[df['涨跌幅'] > 0])
down_days = len(df[df['涨跌幅'] < 0])
flat_days = len(df[df['涨跌幅'] == 0])
max_daily_up = df['涨跌幅'].max()
max_daily_down = df['涨跌幅'].min()
max_up_date = df.loc[df['涨跌幅'].idxmax(), '日期'].strftime('%Y-%m-%d')
max_down_date = df.loc[df['涨跌幅'].idxmin(), '日期'].strftime('%Y-%m-%d')

# 计算均线
df['MA5'] = df['收盘'].rolling(window=5).mean().round(2)
df['MA10'] = df['收盘'].rolling(window=10).mean().round(2)
df['MA20'] = df['收盘'].rolling(window=20).mean().round(2)
df['MA60'] = df['收盘'].rolling(window=60).mean().round(2)

# 月度统计
df['月份'] = df['日期'].dt.to_period('M')
monthly = df.groupby('月份').agg({
    '开盘': 'first',
    '收盘': 'last',
    '最高': 'max',
    '最低': 'min',
    '成交量': 'sum'
}).reset_index()
monthly['月涨跌幅'] = ((monthly['收盘'] / monthly['开盘'] - 1) * 100).round(2)

# 导出K线数据（ECharts格式：[日期, 开盘, 收盘, 最低, 最高]）
kline_data = []
for _, row in df.iterrows():
    kline_data.append([
        row['日期'].strftime('%Y-%m-%d'),
        round(row['开盘'], 2),
        round(row['收盘'], 2),
        round(row['最低'], 2),
        round(row['最高'], 2)
    ])

# 成交量数据
volume_data = []
for _, row in df.iterrows():
    volume_data.append([
        row['日期'].strftime('%Y-%m-%d'),
        int(row['成交量']),
        row['涨跌幅']
    ])

# 均线数据
ma5_data = [round(v, 2) if pd.notna(v) else None for v in df['MA5']]
ma10_data = [round(v, 2) if pd.notna(v) else None for v in df['MA10']]
ma20_data = [round(v, 2) if pd.notna(v) else None for v in df['MA20']]
ma60_data = [round(v, 2) if pd.notna(v) else None for v in df['MA60']]

# 日期数组
dates = [d.strftime('%Y-%m-%d') for d in df['日期']]

# 月度统计导出
monthly_labels = [str(m) for m in monthly['月份']]
monthly_change = monthly['月涨跌幅'].tolist()

# 汇总指标
summary = {
    'stockName': '比亚迪',
    'stockCode': '002594.SZ',
    'period': '2023-01-03 至 2023-12-29',
    'tradingDays': len(df),
    'yearOpen': round(year_open, 2),
    'yearClose': round(year_close, 2),
    'yearHigh': round(year_high, 2),
    'yearHighDate': year_high_date,
    'yearLow': round(year_low, 2),
    'yearLowDate': year_low_date,
    'yearChange': round(year_change, 2),
    'yearChangePct': round(year_change_pct, 2),
    'avgVolume': avg_volume,
    'avgAmount': round(avg_amount / 1e8, 2),
    'totalAmount': round(total_amount / 1e8, 2),
    'upDays': up_days,
    'downDays': down_days,
    'flatDays': flat_days,
    'maxDailyUp': round(max_daily_up, 2),
    'maxUpDate': max_up_date,
    'maxDailyDown': round(max_daily_down, 2),
    'maxDownDate': max_down_date
}

# 输出JSON
output = {
    'summary': summary,
    'dates': dates,
    'kline': kline_data,
    'volume': volume_data,
    'ma5': ma5_data,
    'ma10': ma10_data,
    'ma20': ma20_data,
    'ma60': ma60_data,
    'monthlyLabels': monthly_labels,
    'monthlyChange': monthly_change
}

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"数据已导出到: {out_path}")
print(f"K线条目: {len(kline_data)}")
print(f"年度涨跌幅: {year_change_pct:.2f}%")
print(f"年度最高: {year_high:.2f} ({year_high_date})")
print(f"年度最低: {year_low:.2f} ({year_low_date})")
print(f"上涨天数: {up_days}, 下跌天数: {down_days}")
