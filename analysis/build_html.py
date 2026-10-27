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
  body { margin:0; background:#f3f3f3; font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif; color:#333; }
  .app-header { background:#fff; padding:16px 24px; border-bottom:1px solid #e7e7e7; }
  .app-header h1 { margin:0; font-size:20px; }
  .app-header .sub { color:#888; font-size:13px; margin-top:4px; }
  .container { padding:16px 24px; max-width:1400px; margin:0 auto; }
  .stat-row { display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:12px; margin-bottom:16px; }
  .stat-card { background:#fff; border-radius:6px; padding:14px 16px; }
  .stat-card .label { font-size:12px; color:#999; }
  .stat-card .value { font-size:22px; font-weight:600; margin-top:6px; font-variant-numeric:tabular-nums; }
  .up { color:#d54941; } .down { color:#2ba471; }
  .chart-card { background:#fff; border-radius:6px; padding:16px; margin-bottom:16px; }
  .chart-card h3 { margin:0 0 12px; font-size:15px; }
  .chart { width:100%; }
  #kchart { height:480px; } #closeChart { height:300px; }
  #yrchart { height:280px; } #mmchart { height:260px; }
  #corrChart { height:420px; } #k23q2 { height:420px; }
  .two-col { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
  table { width:100%; border-collapse:collapse; font-size:12px; font-variant-numeric:tabular-nums; }
  th,td { border:1px solid #eee; padding:5px 8px; text-align:right; }
  th { background:#fafafa; } th:first-child,td:first-child { text-align:left; }
  .note { background:#fff7e6; border-left:3px solid #faad14; padding:10px 14px; margin:10px 0; font-size:13px; line-height:1.7; border-radius:0 4px 4px 0; }
</style>
</head>
<body>
<div id="app">
  <div class="app-header">
    <h1>比亚迪 (002594.SZ) · 后复权行情分析与可视化</h1>
    <div class="sub">数据区间 {{ BYD.meta.range[0] }} ~ {{ BYD.meta.range[1] }} · 共 {{ BYD.meta.tradingDays }} 个交易日 · 数据源：原始Excel + 东方财富API</div>
  </div>

  <div class="container">
    <!-- 指标卡片 -->
    <div class="stat-row">
      <div class="stat-card"><div class="label">最新收盘 ({{ BYD.latest.date }})</div>
        <div class="value" :class="BYD.latest.pctChange>=0?'up':'down'">{{ BYD.latest.close.toFixed(2) }}</div></div>
      <div class="stat-card"><div class="label">当日涨跌幅</div>
        <div class="value" :class="BYD.latest.pctChange>=0?'up':'down'">{{ BYD.latest.pctChange>=0?'+':'' }}{{ BYD.latest.pctChange.toFixed(2) }}%</div></div>
      <div class="stat-card"><div class="label">当日最高/最低</div>
        <div class="value" style="font-size:16px;line-height:1.6">{{ BYD.latest.high.toFixed(2) }} / {{ BYD.latest.low.toFixed(2) }}</div></div>
      <div class="stat-card"><div class="label">当日成交量(手)</div>
        <div class="value" style="font-size:18px">{{ BYD.latest.volume.toLocaleString() }}</div></div>
      <div class="stat-card"><div class="label">区间最大回撤</div>
        <div class="value down">{{ BYD.maxDrawdown['最大回撤%'] }}%</div>
        <div style="font-size:11px;color:#aaa">{{ BYD.maxDrawdown['峰值日期'] }} → {{ BYD.maxDrawdown['谷值日期'] }}</div></div>
    </div>

    <!-- 任务1: 前5行 + 描述性统计 -->
    <div class="chart-card">
      <h3>任务1 · 数据前5行</h3>
      <table>
        <thead><tr><th>日期</th><th v-for="c in headCols">{{ c }}</th></tr></thead>
        <tbody><tr v-for="(row,i) in BYD.head5" :key="i">
          <td>{{ row['日期'] }}</td>
          <td v-for="c in headCols">{{ row[c] }}</td>
        </tr></tbody>
      </table>
    </div>

    <div class="chart-card">
      <h3>任务1 · 定量变量描述性统计</h3>
      <table>
        <thead><tr><th>统计量</th><th v-for="c in descCols">{{ c }}</th></tr></thead>
        <tbody><tr v-for="stat in descStatsRows" :key="stat">
          <td>{{ stat }}</td>
          <td v-for="c in descCols">{{ BYD.descriptiveStats[stat][c] }}</td>
        </tr></tbody>
      </table>
    </div>

    <!-- 任务2: 相关系数热力图 -->
    <div class="chart-card">
      <h3>任务2 · 变量相关系数热力图</h3>
      <div id="corrChart" class="chart"></div>
      <div class="note">价格四要素（开盘/收盘/最高/最低）之间相关系数接近 1，呈高度共线性；成交量与成交额高度相关（r≈1）；涨跌幅与涨跌额高度相关（r≈1）。</div>
    </div>

    <!-- 任务3: 收盘价时序图 -->
    <div class="chart-card">
      <h3>任务3 · 2023-2026 全年收盘价时序图</h3>
      <div id="closeChart" class="chart"></div>
    </div>

    <!-- 主K线图 -->
    <div class="chart-card">
      <h3>2023-2026 K 线走势 · MA5/20/60/120 · 成交量</h3>
      <div id="kchart" class="chart"></div>
    </div>

    <!-- 任务4: 2023年4-6月 K 线 -->
    <div class="chart-card">
      <h3>任务4 · 2023年4月-6月 K 线图分析</h3>
      <div id="k23q2" class="chart"></div>
      <div class="note">
        <b>K线解读：</b>2023年4-6月比亚迪后复权股价处于 4月反弹后的高位震荡回落阶段。4月初从约200元附近反弹至4月中旬250元上方，随后在5-6月震荡走低至220元附近，成交量随价格回落逐步萎缩，显示多头动能减弱、抛压释放后进入整理。
      </div>
    </div>

    <!-- 年度/月度收益 -->
    <div class="two-col">
      <div class="chart-card"><h3>年度收益率对比</h3><div id="yrchart" class="chart"></div></div>
      <div class="chart-card"><h3>月度涨跌幅 (%)</h3><div id="mmchart" class="chart"></div></div>
    </div>
  </div>
</div>

<script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>
<script src="https://unpkg.com/tdesign-vue-next@latest/dist/tdesign.min.js"></script>
<script src="https://unpkg.com/echarts@5/dist/echarts.min.js"></script>
<script>
const BYD = __DATA_JSON__;
const { createApp, ref, onMounted } = Vue;

createApp({
  setup(){
    const headCols = ["开盘","收盘","最高","最低","成交量","成交额","振幅","涨跌幅","涨跌额","换手率"];
    const descCols = headCols;
    const descStatsRows = ["count","mean","std","min","25%","50%","75%","max"];

    onMounted(() => {
      const upC='#d54941', dnC='#2ba471';

      // 相关系数热力图
      const corrChart = echarts.init(document.getElementById('corrChart'));
      const labels = BYD.corrMatrix.labels;
      const data = [];
      for(let i=0;i<labels.length;i++) for(let j=0;j<labels.length;j++){
        data.push([j,i,BYD.corrMatrix.values[i][j]]);
      }
      corrChart.setOption({
        tooltip:{ position:'top', formatter: p => `${labels[p.value[1]]} × ${labels[p.value[0]]}<br/>r = ${p.value[2]}` },
        grid:{ height:'70%', top:'10%' },
        xAxis:{ type:'category', data:labels, splitArea:{show:true}, axisLabel:{rotate:45,fontSize:10} },
        yAxis:{ type:'category', data:labels, splitArea:{show:true}, axisLabel:{fontSize:10} },
        visualMap:{ min:-1, max:1, calculable:true, orient:'horizontal', left:'center', bottom:'5%',
          inRange:{ color:['#2ba471','#fff','#d54941'] } },
        series:[{ type:'heatmap', data, label:{ show:true, fontSize:9 }, emphasis:{ itemStyle:{ shadowBlur:10 } } }]
      });

      // 收盘价时序图
      const closeChart = echarts.init(document.getElementById('closeChart'));
      closeChart.setOption({
        tooltip:{ trigger:'axis' },
        grid:{ left:60, right:30, top:20, bottom:50 },
        xAxis:{ type:'category', data:BYD.dates },
        yAxis:{ scale:true, splitLine:{lineStyle:{color:'#f0f0f0'}} },
        dataZoom:[{type:'inside',start:0,end:100},{type:'slider',bottom:10,height:18,start:0,end:100}],
        series:[{ name:'收盘价', type:'line', data:BYD.closeSeries, showSymbol:false,
          lineStyle:{ color:'#0052D9', width:1.5 }, areaStyle:{ color:'rgba(0,82,217,0.08)' } }]
      });

      // 主K线
      const kchart = echarts.init(document.getElementById('kchart'));
      kchart.setOption({
        tooltip:{ trigger:'axis', axisPointer:{type:'cross'} },
        legend:{ data:['K线','MA5','MA20','MA60','MA120','成交量'], top:0 },
        grid:[{left:60,right:30,top:40,height:'55%'},{left:60,right:30,top:'72%',height:'18%'}],
        xAxis:[
          {type:'category',data:BYD.dates,gridIndex:0},
          {type:'category',data:BYD.dates,gridIndex:1,axisLabel:{show:false}}],
        yAxis:[{scale:true,gridIndex:0,splitLine:{lineStyle:{color:'#f0f0f0'}}},
               {scale:true,gridIndex:1,splitNumber:2,splitLine:{show:false}}],
        dataZoom:[{type:'inside',xAxisIndex:[0,1],start:0,end:100},
                  {type:'slider',xAxisIndex:[0,1],bottom:5,height:18,start:0,end:100}],
        series:[
          {name:'K线',type:'candlestick',data:BYD.kline,itemStyle:{color:upC,color0:dnC,borderColor:upC,borderColor0:dnC}},
          {name:'MA5',type:'line',data:BYD.ma.MA5,smooth:true,showSymbol:false,lineStyle:{width:1,color:'#faad14'}},
          {name:'MA20',type:'line',data:BYD.ma.MA20,smooth:true,showSymbol:false,lineStyle:{width:1,color:'#1890ff'}},
          {name:'MA60',type:'line',data:BYD.ma.MA60,smooth:true,showSymbol:false,lineStyle:{width:1,color:'#722ed1'}},
          {name:'MA120',type:'line',data:BYD.ma.MA120,smooth:true,showSymbol:false,lineStyle:{width:1,color:'#fa541c'}},
          {name:'成交量',type:'bar',xAxisIndex:1,yAxisIndex:1,data:BYD.volume,
            itemStyle:{color:p=>{const k=BYD.kline[p.dataIndex];return k[1]<=k[2]?upC:dnC;}}}
        ]
      });

      // 2023年4-6月K线
      const k23q2 = echarts.init(document.getElementById('k23q2'));
      k23q2.setOption({
        tooltip:{trigger:'axis',axisPointer:{type:'cross'}},
        legend:{data:['K线','成交量'],top:0},
        grid:[{left:60,right:30,top:40,height:'55%'},{left:60,right:30,top:'72%',height:'18%'}],
        xAxis:[{type:'category',data:BYD.dates23Q2,gridIndex:0},
               {type:'category',data:BYD.dates23Q2,gridIndex:1,axisLabel:{show:false}}],
        yAxis:[{scale:true,gridIndex:0,splitLine:{lineStyle:{color:'#f0f0f0'}}},
               {scale:true,gridIndex:1,splitNumber:2,splitLine:{show:false}}],
        series:[
          {name:'K线',type:'candlestick',data:BYD.kline23Q2,itemStyle:{color:upC,color0:dnC,borderColor:upC,borderColor0:dnC}},
          {name:'成交量',type:'bar',xAxisIndex:1,yAxisIndex:1,data:BYD.volume23Q2,
            itemStyle:{color:p=>{const k=BYD.kline23Q2[p.dataIndex];return k[1]<=k[2]?upC:dnC;}}}
        ]
      });

      // 年度收益
      const yrs = Object.entries(BYD.yearlyReturns);
      const yrchart = echarts.init(document.getElementById('yrchart'));
      yrchart.setOption({
        tooltip:{trigger:'axis',formatter:p=>{const i=p[0].dataIndex,d=yrs[i][1];
          return `${yrs[i][0]}年<br/>收益率: ${d['年度收益率%']}%<br/>${d['年初收盘']} → ${d['年末收盘']}<br/>高:${d['年内最高']} 低:${d['年内最低']}`;}},
        xAxis:{type:'category',data:yrs.map(x=>x[0]+'年')},
        yAxis:{type:'value',axisLabel:{formatter:'{value}%'}},
        series:[{type:'bar',data:yrs.map(x=>({value:x[1]['年度收益率%'],
          itemStyle:{color:x[1]['年度收益率%']>=0?upC:dnC}})),
          label:{show:true,position:'top',formatter:'{c}%'}}]
      });

      // 月度
      const mm = BYD.monthlyReturns;
      const mmchart = echarts.init(document.getElementById('mmchart'));
      mmchart.setOption({
        tooltip:{trigger:'axis',formatter:p=>`${p[0].name}<br/>${p[0].value}%`},
        grid:{left:50,right:20,top:20,bottom:60},
        xAxis:{type:'category',data:mm.map(x=>x.month),axisLabel:{rotate:45,fontSize:10}},
        yAxis:{type:'value',axisLabel:{formatter:'{value}%'}},
        series:[{type:'bar',data:mm.map(x=>({value:x.ret,itemStyle:{color:x.ret>=0?upC:dnC}}))}]
      });

      window.addEventListener('resize',()=>{corrChart.resize();closeChart.resize();kchart.resize();k23q2.resize();yrchart.resize();mmchart.resize();});
    });

    return { BYD, headCols, descCols, descStatsRows };
  }
}).use(TDesign).mount('#app');
</script>
</body>
</html>
"""

html = html.replace("__DATA_JSON__", data_json)
OUT_HTML.write_text(html, encoding="utf-8")
print(f"Generated {OUT_HTML} ({round(OUT_HTML.stat().st_size/1024,1)} KB)")
