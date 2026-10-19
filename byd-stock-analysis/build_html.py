# -*- coding: utf-8 -*-
"""生成内嵌数据的 index.html"""
import json
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(base_dir, 'data.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)

data_json = json.dumps(data, ensure_ascii=False)

html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>比亚迪股票走势分析</title>
<!-- TDesign Mobile CSS -->
<link rel="stylesheet" href="https://unpkg.com/tdesign-mobile-vue@1.5.0/dist/reset.css">
<!-- ECharts -->
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
  body {
    background: #0d1117;
    color: #e6edf3;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    max-width: 480px;
    margin: 0 auto;
    padding-bottom: 30px;
  }
  /* 顶部导航 */
  .nav-bar {
    position: sticky; top: 0; z-index: 100;
    background: #161b22;
    padding: 12px 16px;
    display: flex; align-items: center; justify-content: space-between;
    border-bottom: 1px solid #21262d;
  }
  .nav-title { font-size: 17px; font-weight: 600; }
  .nav-sub { font-size: 12px; color: #8b949e; }
  .tag {
    background: #1f6feb22; color: #58a6ff;
    padding: 3px 8px; border-radius: 4px; font-size: 11px;
  }
  /* 概览卡片 */
  .overview {
    background: #161b22;
    margin: 12px; padding: 16px;
    border-radius: 12px;
    border: 1px solid #21262d;
  }
  .price-row { display: flex; align-items: baseline; gap: 10px; margin-bottom: 12px; }
  .price { font-size: 36px; font-weight: 700; }
  .price.down { color: #22c55e; }
  .change-badge {
    font-size: 14px; padding: 3px 8px; border-radius: 6px; font-weight: 600;
  }
  .change-badge.down { background: #22c55e22; color: #22c55e; }
  .grid-4 {
    display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
  }
  .stat-item { background: #0d1117; padding: 10px; border-radius: 8px; }
  .stat-label { font-size: 11px; color: #8b949e; margin-bottom: 4px; }
  .stat-value { font-size: 15px; font-weight: 600; }
  .stat-value.up { color: #ef4444; }
  .stat-value.down { color: #22c55e; }
  /* 图表卡片 */
  .chart-card {
    background: #161b22;
    margin: 12px; padding: 12px;
    border-radius: 12px;
    border: 1px solid #21262d;
  }
  .chart-title {
    font-size: 15px; font-weight: 600; margin-bottom: 8px;
    padding-left: 4px; display: flex; align-items: center; gap: 6px;
  }
  .chart-title::before {
    content: ''; width: 3px; height: 14px; background: #1f6feb; border-radius: 2px;
  }
  .chart-sub { font-size: 11px; color: #8b949e; margin-bottom: 6px; padding-left: 7px; }
  #klineChart { width: 100%; height: 320px; }
  #volumeChart { width: 100%; height: 160px; }
  #monthlyChart { width: 100%; height: 220px; }
  /* 统计面板 */
  .stats-panel {
    background: #161b22; margin: 12px; padding: 14px;
    border-radius: 12px; border: 1px solid #21262d;
  }
  .stats-row {
    display: flex; justify-content: space-between; padding: 8px 0;
    border-bottom: 1px solid #21262d; font-size: 13px;
  }
  .stats-row:last-child { border-bottom: none; }
  .stats-label { color: #8b949e; }
  .stats-value { font-weight: 500; }
  /* 底部 */
  .footer {
    text-align: center; padding: 20px 16px; font-size: 11px; color: #6e7681; line-height: 1.6;
  }
  /* 涨跌标签 */
  .up-text { color: #ef4444; }
  .down-text { color: #22c55e; }
</style>
</head>
<body>

<!-- 顶部导航 -->
<div class="nav-bar">
  <div>
    <div class="nav-title">比亚迪</div>
    <div class="nav-sub">002594.SZ · 后复权</div>
  </div>
  <span class="tag">2023 年度</span>
</div>

<!-- 行情概览 -->
<div class="overview">
  <div class="price-row">
    <span class="price down" id="finalPrice">--</span>
    <span class="change-badge down" id="finalChange">--</span>
  </div>
  <div class="grid-4">
    <div class="stat-item">
      <div class="stat-label">年度开盘</div>
      <div class="stat-value" id="yearOpen">--</div>
    </div>
    <div class="stat-item">
      <div class="stat-label">年度最高</div>
      <div class="stat-value up" id="yearHigh">--</div>
    </div>
    <div class="stat-item">
      <div class="stat-label">年度最低</div>
      <div class="stat-value down" id="yearLow">--</div>
    </div>
    <div class="stat-item">
      <div class="stat-label">总成交额(亿)</div>
      <div class="stat-value" id="totalAmount">--</div>
    </div>
  </div>
</div>

<!-- K线图 -->
<div class="chart-card">
  <div class="chart-title">日 K 线走势</div>
  <div class="chart-sub">后复权收盘价 · MA5/10/20/60 均线叠加</div>
  <div id="klineChart"></div>
</div>

<!-- 成交量 -->
<div class="chart-card">
  <div class="chart-title">成交量</div>
  <div class="chart-sub">单位：手 · 红涨绿跌</div>
  <div id="volumeChart"></div>
</div>

<!-- 月度涨跌 -->
<div class="chart-card">
  <div class="chart-title">月度涨跌幅</div>
  <div class="chart-sub">各月涨跌幅（%）</div>
  <div id="monthlyChart"></div>
</div>

<!-- 统计面板 -->
<div class="stats-panel">
  <div class="chart-title" style="margin-bottom:10px;">年度统计</div>
  <div class="stats-row">
    <span class="stats-label">交易天数</span>
    <span class="stats-value" id="tradingDays">--</span>
  </div>
  <div class="stats-row">
    <span class="stats-label">上涨 / 下跌天数</span>
    <span class="stats-value"><span class="up-text" id="upDays">--</span> / <span class="down-text" id="downDays">--</span></span>
  </div>
  <div class="stats-row">
    <span class="stats-label">日均成交量(手)</span>
    <span class="stats-value" id="avgVolume">--</span>
  </div>
  <div class="stats-row">
    <span class="stats-label">日均成交额(亿)</span>
    <span class="stats-value" id="avgAmount">--</span>
  </div>
  <div class="stats-row">
    <span class="stats-label">最大单日涨幅</span>
    <span class="stats-value up-text" id="maxUp">--</span>
  </div>
  <div class="stats-row">
    <span class="stats-label">最大单日跌幅</span>
    <span class="stats-value down-text" id="maxDown">--</span>
  </div>
</div>

<div class="footer">
  数据来源：比亚迪后复权历史行情（2023-01-03 至 2023-12-29）<br>
  本页面仅用于课程作业展示，不构成任何投资建议
</div>

<script>
const DATA = ''' + data_json + ''';

// 填充概览数据
(function fillOverview() {
  const s = DATA.summary;
  document.getElementById('finalPrice').textContent = s.yearClose.toFixed(2);
  const changeEl = document.getElementById('finalChange');
  const pct = s.yearChangePct;
  changeEl.textContent = (pct >= 0 ? '+' : '') + s.yearChange.toFixed(2) + ' (' + (pct >= 0 ? '+' : '') + pct.toFixed(2) + '%)';
  document.getElementById('yearOpen').textContent = s.yearOpen.toFixed(2);
  document.getElementById('yearHigh').textContent = s.yearHigh.toFixed(2);
  document.getElementById('yearLow').textContent = s.yearLow.toFixed(2);
  document.getElementById('totalAmount').textContent = s.totalAmount.toFixed(2);
  document.getElementById('tradingDays').textContent = s.tradingDays + ' 天';
  document.getElementById('upDays').textContent = s.upDays + ' 天';
  document.getElementById('downDays').textContent = s.downDays + ' 天';
  document.getElementById('avgVolume').textContent = s.avgVolume.toLocaleString();
  document.getElementById('avgAmount').textContent = s.avgAmount.toFixed(2);
  document.getElementById('maxUp').textContent = '+' + s.maxDailyUp.toFixed(2) + '% (' + s.maxUpDate + ')';
  document.getElementById('maxDown').textContent = s.maxDailyDown.toFixed(2) + '% (' + s.maxDownDate + ')';
})();

// 通用深色主题
const darkTheme = {
  backgroundColor: 'transparent',
  textStyle: { color: '#8b949e' },
  categoryAxis: {
    axisLine: { lineStyle: { color: '#30363d' } },
    axisLabel: { color: '#8b949e', fontSize: 10 },
    splitLine: { show: false }
  },
  valueAxis: {
    axisLine: { show: false },
    axisLabel: { color: '#8b949e', fontSize: 10 },
    splitLine: { lineStyle: { color: '#21262d' } }
  }
};

// K线图
const klineChart = echarts.init(document.getElementById('klineChart'));
const dates = DATA.dates;
const ohlc = DATA.kline.map(d => [d[1], d[2], d[3], d[4]]);

klineChart.setOption({
  ...darkTheme,
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'cross' },
    backgroundColor: '#161b22',
    borderColor: '#30363d',
    textStyle: { color: '#e6edf3', fontSize: 12 }
  },
  legend: {
    data: ['MA5', 'MA10', 'MA20', 'MA60'],
    textStyle: { color: '#8b949e', fontSize: 10 },
    top: 0, right: 0, itemWidth: 12, itemHeight: 8
  },
  grid: { left: 50, right: 12, top: 30, bottom: 24 },
  xAxis: {
    type: 'category',
    data: dates,
    ...darkTheme.categoryAxis
  },
  yAxis: {
    scale: true,
    ...darkTheme.valueAxis
  },
  dataZoom: [
    { type: 'inside', start: 0, end: 100 },
    { type: 'slider', show: false }
  ],
  series: [
    {
      name: 'K线',
      type: 'candlestick',
      data: ohlc,
      itemStyle: {
        color: '#ef4444',
        color0: '#22c55e',
        borderColor: '#ef4444',
        borderColor0: '#22c55e'
      }
    },
    { name: 'MA5', type: 'line', data: DATA.ma5, smooth: true, lineStyle: { width: 1, color: '#f0b429' }, symbol: 'none' },
    { name: 'MA10', type: 'line', data: DATA.ma10, smooth: true, lineStyle: { width: 1, color: '#58a6ff' }, symbol: 'none' },
    { name: 'MA20', type: 'line', data: DATA.ma20, smooth: true, lineStyle: { width: 1, color: '#bc8cff' }, symbol: 'none' },
    { name: 'MA60', type: 'line', data: DATA.ma60, smooth: true, lineStyle: { width: 1, color: '#ff7b72' }, symbol: 'none' }
  ]
});

// 成交量图
const volumeChart = echarts.init(document.getElementById('volumeChart'));
volumeChart.setOption({
  ...darkTheme,
  tooltip: { trigger: 'axis', backgroundColor: '#161b22', borderColor: '#30363d', textStyle: { color: '#e6edf3', fontSize: 12 } },
  grid: { left: 50, right: 12, top: 10, bottom: 24 },
  xAxis: { type: 'category', data: dates, ...darkTheme.categoryAxis },
  yAxis: { type: 'value', ...darkTheme.valueAxis },
  series: [{
    type: 'bar',
    data: DATA.volume.map(v => ({
      value: v[1],
      itemStyle: { color: v[2] >= 0 ? '#ef4444' : '#22c55e' }
    }))
  }]
});

// 月度涨跌图
const monthlyChart = echarts.init(document.getElementById('monthlyChart'));
monthlyChart.setOption({
  ...darkTheme,
  tooltip: { trigger: 'axis', backgroundColor: '#161b22', borderColor: '#30363d', textStyle: { color: '#e6edf3', fontSize: 12 },
    formatter: function(p) { return p[0].name + '<br/>涨跌幅: ' + p[0].value + '%'; }
  },
  grid: { left: 40, right: 12, top: 20, bottom: 24 },
  xAxis: { type: 'category', data: DATA.monthlyLabels, ...darkTheme.categoryAxis,
    axisLabel: { color: '#8b949e', fontSize: 10, rotate: 30 }
  },
  yAxis: { type: 'value', ...darkTheme.valueAxis,
    axisLabel: { color: '#8b949e', fontSize: 10, formatter: '{value}%' }
  },
  series: [{
    type: 'bar',
    data: DATA.monthlyChange.map(v => ({
      value: v,
      itemStyle: { color: v >= 0 ? '#ef4444' : '#22c55e', borderRadius: [3, 3, 0, 0] }
    })),
    barWidth: '50%'
  }]
});

// 响应式
window.addEventListener('resize', () => {
  klineChart.resize();
  volumeChart.resize();
  monthlyChart.resize();
});
</script>
</body>
</html>
'''

out_path = os.path.join(base_dir, 'index.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'index.html generated: {out_path}')
print(f'Size: {os.path.getsize(out_path)} bytes')
