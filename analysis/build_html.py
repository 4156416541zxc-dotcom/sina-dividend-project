"""
生成自包含可视化页面 web/index.html
CDN: Vue3 + TDesign Vue Next + ECharts5
数据内嵌自 src/data.js
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_JS = ROOT / "web" / "src" / "data.js"
OUT_HTML = ROOT / "web" / "index.html"

raw = DATA_JS.read_text(encoding="utf-8")
# 提取 JSON 对象
m = re.search(r"export const BYD_DATA = (\{.*\});", raw, re.S)
data_json = m.group(1)

html = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>比亚迪(002594) 后复权股价走势分析</title>
<link rel="stylesheet" href="https://unpkg.com/tdesign-vue-next@latest/dist/tdesign.min.css" />
<style>
  body { margin:0; background:#f3f3f3; font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif; }
  .app-header { background:#fff; padding:16px 24px; border-bottom:1px solid #e7e7e7; display:flex; align-items:center; justify-content:space-between; }
  .app-header h1 { margin:0; font-size:20px; color:#333; }
  .app-header .sub { color:#888; font-size:13px; margin-top:4px; }
  .container { padding:16px 24px; max-width:1400px; margin:0 auto; }
  .stat-row { display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:12px; margin-bottom:16px; }
  .stat-card { background:#fff; border-radius:6px; padding:14px 16px; }
  .stat-card .label { font-size:12px; color:#999; }
  .stat-card .value { font-size:22px; font-weight:600; margin-top:6px; font-variant-numeric:tabular-nums; }
  .up { color:#d54941; }
  .down { color:#2ba471; }
  .chart-card { background:#fff; border-radius:6px; padding:16px; margin-bottom:16px; }
  .chart-card h3 { margin:0 0 12px; font-size:15px; color:#333; }
  #kchart { width:100%; height:480px; }
  #yrchart { width:100%; height:280px; }
  #mmchart { width:100%; height:260px; }
  .two-col { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
  @media (max-width: 900px){ .two-col{ grid-template-columns:1fr; } }
</style>
</head>
<body>
<div id="app">
  <div class="app-header">
    <div>
      <h1>比亚迪 (002594.SZ) · 后复权行情分析</h1>
      <div class="sub">数据区间 {{ BYD.meta.range[0] }} ~ {{ BYD.meta.range[1] }} · 共 {{ BYD.meta.tradingDays }} 个交易日</div>
    </div>
    <t-tag theme="primary" size="large">{{ BYD.meta.adjust }}</t-tag>
  </div>

  <div class="container">
    <div class="stat-row">
      <div class="stat-card">
        <div class="label">最新收盘 ({{ BYD.latest.date }})</div>
        <div class="value" :class="BYD.latest.pctChange >= 0 ? 'up' : 'down'">{{ BYD.latest.close.toFixed(2) }}</div>
      </div>
      <div class="stat-card">
        <div class="label">当日涨跌幅</div>
        <div class="value" :class="BYD.latest.pctChange >= 0 ? 'up' : 'down'">{{ BYD.latest.pctChange >= 0 ? '+' : '' }}{{ BYD.latest.pctChange.toFixed(2) }}%</div>
      </div>
      <div class="stat-card">
        <div class="label">当日最高 / 最低</div>
        <div class="value" style="font-size:16px;line-height:1.6">{{ BYD.latest.high.toFixed(2) }} / {{ BYD.latest.low.toFixed(2) }}</div>
      </div>
      <div class="stat-card">
        <div class="label">当日成交量 (手)</div>
        <div class="value" style="font-size:18px">{{ BYD.latest.volume.toLocaleString() }}</div>
      </div>
      <div class="stat-card">
        <div class="label">区间最大回撤</div>
        <div class="value down">{{ BYD.maxDrawdown['最大回撤%'] }}%</div>
        <div style="font-size:11px;color:#aaa;margin-top:4px">{{ BYD.maxDrawdown['峰值日期'] }} → {{ BYD.maxDrawdown['谷值日期'] }}</div>
      </div>
    </div>

    <div class="chart-card">
      <h3>K 线走势 · MA5/MA20/MA60/MA120 · 成交量</h3>
      <div id="kchart"></div>
    </div>

    <div class="two-col">
      <div class="chart-card">
        <h3>年度收益率对比</h3>
        <div id="yrchart"></div>
      </div>
      <div class="chart-card">
        <h3>月度涨跌幅 (%)</h3>
        <div id="mmchart"></div>
      </div>
    </div>
  </div>
</div>

<script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>
<script src="https://unpkg.com/tdesign-vue-next@latest/dist/tdesign.min.js"></script>
<script src="https://unpkg.com/echarts@5/dist/echarts.min.js"></script>
<script>
const BYD_DATA = __DATA_JSON__;

const { createApp, ref, onMounted } = Vue;
createApp({
  setup(){
    const BYD = BYD_DATA;
    onMounted(() => {
      // K 线 + 均线 + 成交量
      const kchart = echarts.init(document.getElementById('kchart'));
      const dates = BYD.dates;
      const upColor = '#d54941', downColor = '#2ba471';
      kchart.setOption({
        tooltip: { trigger:'axis', axisPointer:{ type:'cross' } },
        legend: { data:['K线','MA5','MA20','MA60','MA120','成交量'], top:0 },
        grid: [
          { left:60, right:30, top:40, height:'58%' },
          { left:60, right:30, top:'72%', height:'18%' }
        ],
        xAxis: [
          { type:'category', data:dates, gridIndex:0, boundaryGap:true, axisLine:{lineStyle:{color:'#ccc'}} },
          { type:'category', data:dates, gridIndex:1, boundaryGap:true, axisLabel:{show:false} }
        ],
        yAxis: [
          { scale:true, gridIndex:0, splitLine:{lineStyle:{color:'#f0f0f0'}} },
          { scale:true, gridIndex:1, splitNumber:2, splitLine:{show:false} }
        ],
        dataZoom: [
          { type:'inside', xAxisIndex:[0,1], start:0, end:100 },
          { type:'slider', xAxisIndex:[0,1], bottom:5, height:18, start:0, end:100 }
        ],
        series: [
          { name:'K线', type:'candlestick', data:BYD.kline, itemStyle:{ color:upColor, color0:downColor, borderColor:upColor, borderColor0:downColor } },
          { name:'MA5', type:'line', data:BYD.ma.MA5, smooth:true, showSymbol:false, lineStyle:{width:1, color:'#faad14'} },
          { name:'MA20', type:'line', data:BYD.ma.MA20, smooth:true, showSymbol:false, lineStyle:{width:1, color:'#1890ff'} },
          { name:'MA60', type:'line', data:BYD.ma.MA60, smooth:true, showSymbol:false, lineStyle:{width:1, color:'#722ed1'} },
          { name:'MA120', type:'line', data:BYD.ma.MA120, smooth:true, showSymbol:false, lineStyle:{width:1, color:'#fa541c'} },
          { name:'成交量', type:'bar', xAxisIndex:1, yAxisIndex:1, data:BYD.volume,
            itemStyle:{ color: p => {
              const k = BYD.kline[p.dataIndex];
              return k[1] <= k[2] ? upColor : downColor;
            }}
          }
        ]
      });

      // 年度收益率
      const yrs = Object.entries(BYD.yearlyReturns);
      const yrchart = echarts.init(document.getElementById('yrchart'));
      yrchart.setOption({
        tooltip:{ trigger:'axis', formatter: p => {
          const i = p[0].dataIndex;
          const d = yrs[i][1];
          return `${yrs[i][0]}年<br/>收益率: ${d['年度收益率%']}%<br/>年初: ${d['年初收盘']} → 年末: ${d['年末收盘']}<br/>最高: ${d['年内最高']} / 最低: ${d['年内最低']}`;
        }},
        xAxis:{ type:'category', data: yrs.map(x=>x[0]+'年') },
        yAxis:{ type:'value', axisLabel:{ formatter:'{value}%' } },
        series:[{
          type:'bar',
          data: yrs.map(x => ({
            value: x[1]['年度收益率%'],
            itemStyle:{ color: x[1]['年度收益率%'] >= 0 ? upColor : downColor }
          })),
          label:{ show:true, position:'top', formatter:'{c}%' }
        }]
      });

      // 月度涨跌幅
      const mm = BYD.monthlyReturns;
      const mmchart = echarts.init(document.getElementById('mmchart'));
      mmchart.setOption({
        tooltip:{ trigger:'axis', formatter: p => `${p[0].name}<br/>${p[0].value}%` },
        grid:{ left:50, right:20, top:20, bottom:60 },
        xAxis:{ type:'category', data: mm.map(x=>x.month), axisLabel:{ rotate:45, fontSize:10 } },
        yAxis:{ type:'value', axisLabel:{ formatter:'{value}%' } },
        series:[{
          type:'bar',
          data: mm.map(x => ({ value:x.ret, itemStyle:{ color: x.ret >= 0 ? upColor : downColor } }))
        }]
      });

      window.addEventListener('resize', () => { kchart.resize(); yrchart.resize(); mmchart.resize(); });
    });
    return { BYD };
  }
}).use(TDesign).mount('#app');
</script>
</body>
</html>
"""

html = html.replace("__DATA_JSON__", data_json)
OUT_HTML.write_text(html, encoding="utf-8")
print(f"Generated {OUT_HTML} ({round(OUT_HTML.stat().st_size/1024,1)} KB)")
