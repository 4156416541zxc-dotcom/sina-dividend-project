/**
 * 新浪财经分红数据可视化应用
 * 主逻辑文件
 */

// 全局状态
const state = {
    currentPage: 1,
    pageSize: 15,
    filteredData: [...DIVIDEND_DATA],
    stockFilter: 'all',
    yearFilter: 'all',
    searchText: '',
};

// 颜色配置
const COLORS = {
    primary: '#1a73e8',
    secondary: '#34a853',
    accent: '#fbbc04',
    danger: '#ea4335',
    purple: '#9c27b0',
    orange: '#ff9800',
};

const STOCK_COLORS = {
    '贵州茅台': '#1a73e8',
    '工商银行': '#34a853',
    '中国平安': '#9c27b0',
    '格力电器': '#fbbc04',
    '招商银行': '#ea4335',
};

// ========== 初始化 ==========
document.addEventListener('DOMContentLoaded', function() {
    initNavigation();
    initStockCards();
    initFilters();
    initCharts();
    renderTable();
    renderStatsTable();
    initScrollEffects();
});

// ========== 导航栏 ==========
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    const sections = document.querySelectorAll('section[id], header[id]');

    // 滚动监听
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }

        // 更新活跃导航
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 100;
            if (window.scrollY >= sectionTop) {
                current = section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + current) {
                link.classList.add('active');
            }
        });
    });

    // 平滑滚动
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const target = document.querySelector(targetId);
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
}

// ========== 样本股票卡片 ==========
function initStockCards() {
    const grid = document.getElementById('stock-grid');
    const stockStats = DIVIDEND_STATS.by_stock;

    stockStats.forEach(stock => {
        const card = document.createElement('div');
        card.className = 'stock-card';
        card.innerHTML = `
            <div class="stock-code">${stock['股票代码']}</div>
            <div class="stock-name">${stock['股票名称']}</div>
            <div class="stock-meta">分红 ${stock['分红次数']} 次 | 累计派息 ${stock['累计每股派息(元)']} 元/股</div>
        `;
        card.addEventListener('click', function() {
            document.getElementById('stock-filter').value = stock['股票名称'];
            state.stockFilter = stock['股票名称'];
            applyFilters();
            document.getElementById('datatable').scrollIntoView({ behavior: 'smooth' });
        });
        grid.appendChild(card);
    });
}

// ========== 筛选器 ==========
function initFilters() {
    const stockFilter = document.getElementById('stock-filter');
    const yearFilter = document.getElementById('year-filter');
    const searchInput = document.getElementById('search-input');

    // 填充股票选项
    STOCK_LIST.forEach(stock => {
        const option = document.createElement('option');
        option.value = stock;
        option.textContent = stock;
        stockFilter.appendChild(option);
    });

    // 填充年份选项
    YEAR_LIST.forEach(year => {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year + '年';
        yearFilter.appendChild(option);
    });

    // 事件监听
    stockFilter.addEventListener('change', function() {
        state.stockFilter = this.value;
        state.currentPage = 1;
        applyFilters();
    });

    yearFilter.addEventListener('change', function() {
        state.yearFilter = this.value;
        state.currentPage = 1;
        applyFilters();
    });

    searchInput.addEventListener('input', function() {
        state.searchText = this.value.toLowerCase();
        state.currentPage = 1;
        applyFilters();
    });

    // 分页按钮
    document.getElementById('prev-page').addEventListener('click', function() {
        if (state.currentPage > 1) {
            state.currentPage--;
            renderTable();
        }
    });

    document.getElementById('next-page').addEventListener('click', function() {
        const totalPages = Math.ceil(state.filteredData.length / state.pageSize);
        if (state.currentPage < totalPages) {
            state.currentPage++;
            renderTable();
        }
    });
}

function applyFilters() {
    state.filteredData = DIVIDEND_DATA.filter(item => {
        // 股票筛选
        if (state.stockFilter !== 'all' && item['股票名称'] !== state.stockFilter) {
            return false;
        }
        // 年份筛选
        if (state.yearFilter !== 'all') {
            const itemYear = item['公告日期'].substring(0, 4);
            if (itemYear !== state.yearFilter) {
                return false;
            }
        }
        // 搜索
        if (state.searchText) {
            const searchStr = Object.values(item).join(' ').toLowerCase();
            if (!searchStr.includes(state.searchText)) {
                return false;
            }
        }
        return true;
    });
    renderTable();
}

// ========== 图表初始化 ==========
function initCharts() {
    renderTrendChart();
    renderCompareChart();
    renderPieChart();
    renderHeatmap();
    renderYearlyChart();
    renderRadarChart();

    // 窗口resize时重绘
    window.addEventListener('resize', function() {
        setTimeout(() => {
            Object.values(charts).forEach(chart => chart && chart.resize());
        }, 100);
    });
}

const charts = {};

// 历年分红趋势图
function renderTrendChart() {
    const chart = echarts.init(document.getElementById('chart-trend'));
    charts.trend = chart;

    const years = DIVIDEND_STATS.by_year.map(y => y['年份']);
    const avgDividend = DIVIDEND_STATS.by_year.map(y => y['平均每股派息(元)']);
    const eventCount = DIVIDEND_STATS.by_year.map(y => y['分红事件数']);

    const option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'cross' }
        },
        legend: {
            data: ['平均每股派息(元)', '分红事件数'],
            top: 0
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            top: '15%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: years,
            axisLabel: { rotate: 45 }
        },
        yAxis: [
            {
                type: 'value',
                name: '派息(元/股)',
                position: 'left'
            },
            {
                type: 'value',
                name: '事件数',
                position: 'right'
            }
        ],
        series: [
            {
                name: '平均每股派息(元)',
                type: 'line',
                data: avgDividend,
                smooth: true,
                itemStyle: { color: COLORS.primary },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(26, 115, 232, 0.3)' },
                        { offset: 1, color: 'rgba(26, 115, 232, 0.05)' }
                    ])
                }
            },
            {
                name: '分红事件数',
                type: 'bar',
                yAxisIndex: 1,
                data: eventCount,
                itemStyle: { color: COLORS.secondary, opacity: 0.6 }
            }
        ]
    };

    chart.setOption(option);
}

// 各股票累计派息对比
function renderCompareChart() {
    const chart = echarts.init(document.getElementById('chart-compare'));
    charts.compare = chart;

    const stocks = DIVIDEND_STATS.by_stock.map(s => s['股票名称']);
    const totalDividend = DIVIDEND_STATS.by_stock.map(s => s['累计每股派息(元)']);

    const option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'value',
            name: '累计每股派息(元)'
        },
        yAxis: {
            type: 'category',
            data: stocks
        },
        series: [{
            type: 'bar',
            data: totalDividend.map((value, index) => ({
                value,
                itemStyle: { color: STOCK_COLORS[stocks[index]] || COLORS.primary }
            })),
            label: {
                show: true,
                position: 'right',
                formatter: '{c} 元'
            }
        }]
    };

    chart.setOption(option);
}

// 分红类型分布饼图
function renderPieChart() {
    const chart = echarts.init(document.getElementById('chart-pie'));
    charts.pie = chart;

    const cashOnly = DIVIDEND_DATA.filter(d => d['是否现金分红'] && !d['是否送转股']).length;
    const stockOnly = DIVIDEND_DATA.filter(d => !d['是否现金分红'] && d['是否送转股']).length;
    const both = DIVIDEND_DATA.filter(d => d['是否现金分红'] && d['是否送转股']).length;
    const none = DIVIDEND_DATA.filter(d => !d['是否现金分红'] && !d['是否送转股']).length;

    const option = {
        tooltip: {
            trigger: 'item',
            formatter: '{b}: {c} 次 ({d}%)'
        },
        legend: {
            orient: 'vertical',
            left: 'left'
        },
        series: [{
            type: 'pie',
            radius: ['40%', '70%'],
            avoidLabelOverlap: false,
            itemStyle: {
                borderRadius: 8,
                borderColor: '#fff',
                borderWidth: 2
            },
            label: {
                show: true,
                formatter: '{b}\n{d}%'
            },
            data: [
                { value: cashOnly, name: '仅现金分红', itemStyle: { color: COLORS.primary } },
                { value: both, name: '现金+送转', itemStyle: { color: COLORS.secondary } },
                { value: stockOnly, name: '仅送转股', itemStyle: { color: COLORS.accent } },
                { value: none, name: '无分红', itemStyle: { color: COLORS.danger } }
            ]
        }]
    };

    chart.setOption(option);
}

// 热力图
function renderHeatmap() {
    const chart = echarts.init(document.getElementById('chart-heatmap'));
    charts.heatmap = chart;

    const pivotData = DIVIDEND_STATS.pivot_dividend;
    const stocks = pivotData.map(d => d['股票名称']);
    const years = Object.keys(pivotData[0]).filter(k => k !== '股票名称').map(Number).sort((a, b) => a - b);

    const data = [];
    let maxValue = 0;
    pivotData.forEach((row, stockIndex) => {
        years.forEach((year, yearIndex) => {
            const value = row[year] || 0;
            data.push([yearIndex, stockIndex, value]);
            if (value > maxValue) maxValue = value;
        });
    });

    const option = {
        tooltip: {
            position: 'top',
            formatter: function(params) {
                return `${stocks[params.value[1]]} ${years[params.value[0]]}年<br/>每股派息: ${params.value[2]} 元`;
            }
        },
        grid: {
            left: '10%',
            right: '5%',
            bottom: '15%',
            top: '5%'
        },
        xAxis: {
            type: 'category',
            data: years,
            splitArea: { show: true },
            axisLabel: { rotate: 45, fontSize: 10 }
        },
        yAxis: {
            type: 'category',
            data: stocks,
            splitArea: { show: true }
        },
        visualMap: {
            min: 0,
            max: maxValue,
            calculable: true,
            orient: 'horizontal',
            left: 'center',
            bottom: '0%',
            inRange: {
                color: ['#e8f0fe', '#1a73e8', '#0d47a1']
            }
        },
        series: [{
            type: 'heatmap',
            data: data,
            label: {
                show: true,
                fontSize: 9,
                formatter: function(params) {
                    return params.value[2] > 0 ? params.value[2] : '';
                }
            },
            emphasis: {
                itemStyle: {
                    shadowBlur: 10,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
            }
        }]
    };

    chart.setOption(option);
}

// 年度分红事件数
function renderYearlyChart() {
    const chart = echarts.init(document.getElementById('chart-yearly'));
    charts.yearly = chart;

    const years = DIVIDEND_STATS.by_year.map(y => y['年份']);
    const eventCount = DIVIDEND_STATS.by_year.map(y => y['分红事件数']);
    const stockCount = DIVIDEND_STATS.by_year.map(y => y['涉及股票数']);

    const option = {
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            data: ['分红事件数', '涉及股票数'],
            top: 0
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            top: '15%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: years,
            axisLabel: { rotate: 45, fontSize: 10 }
        },
        yAxis: {
            type: 'value'
        },
        series: [
            {
                name: '分红事件数',
                type: 'bar',
                data: eventCount,
                itemStyle: { color: COLORS.primary }
            },
            {
                name: '涉及股票数',
                type: 'line',
                data: stockCount,
                smooth: true,
                itemStyle: { color: COLORS.accent },
                lineStyle: { width: 3 }
            }
        ]
    };

    chart.setOption(option);
}

// 雷达图
function renderRadarChart() {
    const chart = echarts.init(document.getElementById('chart-radar'));
    charts.radar = chart;

    const stocks = DIVIDEND_STATS.by_stock.map(s => s['股票名称']);
    const indicators = [
        { name: '分红次数', max: 45 },
        { name: '现金分红次数', max: 45 },
        { name: '送转股次数', max: 10 },
        { name: '累计派息', max: 350 },
        { name: '平均派息', max: 12 },
        { name: '最大派息', max: 35 }
    ];

    const seriesData = DIVIDEND_STATS.by_stock.map(stock => ({
        name: stock['股票名称'],
        value: [
            stock['分红次数'],
            stock['现金分红次数'],
            stock['送转股次数'],
            stock['累计每股派息(元)'],
            stock['平均每股派息(元)'],
            stock['最大每股派息(元)']
        ],
        itemStyle: { color: STOCK_COLORS[stock['股票名称']] },
        areaStyle: { opacity: 0.1 }
    }));

    const option = {
        tooltip: {},
        legend: {
            data: stocks,
            bottom: 0,
            textStyle: { fontSize: 11 }
        },
        radar: {
            indicator: indicators,
            radius: '60%',
            center: ['50%', '45%']
        },
        series: [{
            type: 'radar',
            data: seriesData
        }]
    };

    chart.setOption(option);
}

// ========== 数据表格 ==========
function renderTable() {
    const tbody = document.getElementById('table-body');
    const tableInfo = document.getElementById('table-info');
    const pageNumber = document.getElementById('page-number');
    const prevBtn = document.getElementById('prev-page');
    const nextBtn = document.getElementById('next-page');

    const start = (state.currentPage - 1) * state.pageSize;
    const end = start + state.pageSize;
    const pageData = state.filteredData.slice(start, end);

    tbody.innerHTML = '';
    pageData.forEach(item => {
        const tr = document.createElement('tr');
        const dividendClass = item['每股派息(元)'] > 0 ? 'positive' : '';
        tr.innerHTML = `
            <td>${item['股票代码']}</td>
            <td>${item['股票名称']}</td>
            <td>${item['公告日期']}</td>
            <td>${item['送股(每10股)']}</td>
            <td>${item['转增(每10股)']}</td>
            <td class="${dividendClass}">${item['派息税前(每10股/元)']}</td>
            <td class="${dividendClass}">${item['每股派息(元)'].toFixed(4)}</td>
            <td>${item['进度']}</td>
            <td>${item['除权除息日']}</td>
            <td>${item['股权登记日']}</td>
        `;
        tbody.appendChild(tr);
    });

    const totalPages = Math.ceil(state.filteredData.length / state.pageSize) || 1;
    tableInfo.textContent = `显示 ${state.filteredData.length} 条记录`;
    pageNumber.textContent = `第 ${state.currentPage} / ${totalPages} 页`;
    prevBtn.disabled = state.currentPage <= 1;
    nextBtn.disabled = state.currentPage >= totalPages;
}

// ========== 统计表格 ==========
function renderStatsTable() {
    const tbody = document.getElementById('stats-body');
    const stockStats = DIVIDEND_STATS.by_stock;

    tbody.innerHTML = '';
    stockStats.forEach(stock => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${stock['股票代码']}</td>
            <td><strong>${stock['股票名称']}</strong></td>
            <td class="highlight-value">${stock['分红次数']}</td>
            <td>${stock['现金分红次数']}</td>
            <td>${stock['送转股次数']}</td>
            <td class="highlight-value">${stock['累计每股派息(元)']}</td>
            <td>${stock['平均每股派息(元)']}</td>
            <td>${stock['最大每股派息(元)']}</td>
            <td>${stock['累计每股送转(股)']}</td>
            <td>${stock['首次分红年份']}</td>
            <td>${stock['最近分红年份']}</td>
        `;
        tbody.appendChild(tr);
    });
}

// ========== 滚动动画 ==========
function initScrollEffects() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.chart-card, .pipeline-step, .stock-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}
