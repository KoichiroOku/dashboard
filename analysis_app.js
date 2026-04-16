// Globals
let charts = {};
const chartInstances = {};

// Colors based on categories to mimic the matplotlib Set1/Set2
const colorPalette = [
    '#ef4444', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6',
    '#ec4899', '#14b8a6', '#f97316', '#6366f1', '#84cc16'
];
let categoryColors = {};

document.addEventListener('DOMContentLoaded', () => {
    if (typeof ANALYSIS_DATA === 'undefined') {
        alert("分析データ(analysis_data.js)がロードされていません");
        return;
    }

    // Register DataLabels plugin
    Chart.register(ChartDataLabels);
    Chart.defaults.color = '#94a3b8';
    Chart.defaults.font.family = 'Hiragino Sans, sans-serif';
    Chart.defaults.plugins.datalabels.color = '#cbd5e1';
    Chart.defaults.plugins.datalabels.font = { size: 10 };

    initFilters();
    initCharts();
    setupEventListeners();
    updateDashboard(); // Initial draw
});

function initFilters() {
    const segments = [...new Set(ANALYSIS_DATA.CARS.map(c => c.segment))].sort();
    const clusters = [...new Set(ANALYSIS_DATA.CARS.map(c => c.cluster))].sort();
    
    // Assign colors to categories for consistency across charts
    const categories = [...new Set(ANALYSIS_DATA.CARS.map(c => c.category))].sort();
    categories.forEach((cat, i) => {
        categoryColors[cat] = colorPalette[i % colorPalette.length];
    });

    renderCheckboxes('filter-segment', segments, 'segment');
    renderCheckboxes('filter-category', categories, 'category');
    renderCheckboxes('filter-cluster', clusters, 'cluster');
}

function renderCheckboxes(containerId, items, filterType) {
    const container = document.getElementById(containerId);
    items.forEach(item => {
        if (!item || item === 'undefined' || item === 'nan') return;
        const btn = document.createElement('button');
        btn.className = 'filter-btn active';
        btn.dataset.val = item;
        btn.dataset.type = filterType;
        btn.textContent = item;
        container.appendChild(btn);
    });
}

function setupEventListeners() {
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.target.classList.toggle('active');
            updateDashboard();
        });
    });

    document.getElementById('btn-reset').addEventListener('click', () => {
        document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.add('active'));
        updateDashboard();
    });
}

function getActiveFilters() {
    const activeSegs = Array.from(document.querySelectorAll('#filter-segment .active')).map(b => b.dataset.val);
    const activeCats = Array.from(document.querySelectorAll('#filter-category .active')).map(b => b.dataset.val);
    const activeClusters = Array.from(document.querySelectorAll('#filter-cluster .active')).map(b => b.dataset.val);
    return { segments: activeSegs, categories: activeCats, clusters: activeClusters };
}

function updateDashboard() {
    const filters = getActiveFilters();
    console.log("Filters:", filters);

    // Filter Cars Data
    const filteredCars = ANALYSIS_DATA.CARS.filter(c => {
        const segMatch = filters.segments.includes(c.segment);
        const catMatch = filters.categories.includes(c.category);
        const clusterMatch = filters.clusters.includes(c.cluster);
        return segMatch && catMatch && clusterMatch;
    });

    // Update Table
    renderTable(filteredCars);

    // Update charts that depend on CARS filtering
    drawScatterCar('chart-cs-cars', filteredCars, 'score_t', 'cp_t', '車種CSポートフォリオ', '総合評価 (偏差値)', 'コストパフォーマンス (偏差値)', 50, 50);
    drawScatterCar('chart-pca-cars', filteredCars, 'pc1', 'pc2', 'PCA 車種マップ', '第1主成分 (PC1)', '第2主成分 (PC2)', 0, 0);
    drawScatterMap('chart-ca', filteredCars, ANALYSIS_DATA.CATEGORIES, 'ca_x', 'ca_y', 'コレスポンデンス分析', '関連性次元1 (Dim 1)', '関連性次元2 (Dim 2)');
    drawScatterMap('chart-q3', filteredCars, ANALYSIS_DATA.SEGMENTS, 'q3_x', 'q3_y', '数量化理論III類', '関連性次元1 (Dim 1)', '関連性次元2 (Dim 2)');
}

// ================= TABLE DRAWING LOGIC =================
function renderTable(cars) {
    const tbody = document.getElementById('cars-table-body');
    tbody.innerHTML = ''; // clear

    const frag = document.createDocumentFragment();
    cars.forEach(c => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-700/50 transition-colors cursor-default';
        tr.innerHTML = `
            <td class="px-6 py-3 font-semibold text-white">${c.name}</td>
            <td class="px-6 py-3">${c.maker}</td>
            <td class="px-6 py-3"><span style="color:${categoryColors[c.category] || '#fff'}">${c.category}</span></td>
            <td class="px-6 py-3">${c.segment}</td>
            <td class="px-6 py-3 font-bold text-blue-400">${c.cluster}</td>
        `;
        frag.appendChild(tr);
    });
    tbody.appendChild(frag);

    document.getElementById('table-count').textContent = `表示件数: ${cars.length} 台`;
}

// ================= CHART DRAWING LOGIC =================
function initCharts() {
    // Static charts don't need re-drawing on filter
    drawScatterItems('chart-cs-items', ANALYSIS_DATA.VARIABLES, 'imp_t', 'ach_t', '重要度', '達成度', 50, 50);
    drawScatterItems('chart-pca-vars', ANALYSIS_DATA.VARIABLES, 'pc1', 'pc2', 'PC1', 'PC2', 0, 0, true);

    drawBarChart('chart-reg-score', ANALYSIS_DATA.VARIABLES, 'reg_score', '#fbbf24');
    drawBarChart('chart-reg-price', ANALYSIS_DATA.VARIABLES, 'reg_price', '#f59e0b');

    drawBarObj('chart-q1-score', ANALYSIS_DATA.Q1_SCORE, '#2dd4bf');
    drawBarObj('chart-q1-price', ANALYSIS_DATA.Q1_PRICE, '#0d9488');
}

// Draw Car-based Dynamic Scatter
function drawScatterCar(canvasId, cars, xKey, yKey, title, xLabel, yLabel, xCenter = null, yCenter = null) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    if (chartInstances[canvasId]) chartInstances[canvasId].destroy();

    // Group by category to apply colors cleanly
    const datasets = [];
    const grouped = {};
    cars.forEach(c => {
        if (!grouped[c.category]) grouped[c.category] = [];
        grouped[c.category].push({ x: c[xKey], y: c[yKey], car: c });
    });

    Object.keys(grouped).forEach(cat => {
        datasets.push({
            label: cat,
            data: grouped[cat],
            backgroundColor: categoryColors[cat] || '#888',
            borderColor: '#fff',
            borderWidth: 1,
            pointRadius: 6,
            pointHoverRadius: 8
        });
    });

    chartInstances[canvasId] = new Chart(ctx, {
        type: 'scatter',
        data: { datasets },
        options: {
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function (ctx) {
                            const d = ctx.raw.car;
                            return `${d.name} (${d.maker}/${d.body_type})`;
                        }
                    }
                },
                datalabels: {
                    align: 'top',
                    offset: 4,
                    display: function (context) { // Only show label if filtered down or if few points
                        return cars.length < 50 ? true : 'auto';
                    },
                    formatter: function (value) {
                        return value.car.name;
                    }
                }
            },
            scales: {
                x: { title: { display: true, text: xLabel }, grid: { color: '#334155' } },
                y: { title: { display: true, text: yLabel }, grid: { color: '#334155' } }
            }
        },
        plugins: [getQuadrantPlugin(xCenter, yCenter)]
    });
}

function drawScatterItems(canvasId, vars, xKey, yKey, xLabel, yLabel, xCenter = null, yCenter = null, isArrow = false) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const dataPts = vars.map(v => ({ x: v[xKey], y: v[yKey], item: v }));

    new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: '評価項目',
                data: dataPts,
                backgroundColor: '#cbd5e1',
                pointRadius: 5
            }]
        },
        options: {
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                datalabels: {
                    align: 'right',
                    offset: 5,
                    formatter: v => v.item.name,
                    color: '#e2e8f0'
                },
                tooltip: {
                    callbacks: { label: ctx => ctx.raw.item.name }
                }
            },
            scales: {
                x: { title: { display: true, text: xLabel }, grid: { color: '#334155' } },
                y: { title: { display: true, text: yLabel }, grid: { color: '#334155' } }
            }
        },
        plugins: [getQuadrantPlugin(xCenter, yCenter)]
    });
}

function drawScatterMap(canvasId, cars, categories, xKey, yKey, title, xLabel, yLabel) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    if (chartInstances[canvasId]) chartInstances[canvasId].destroy();

    const carPts = cars.map(c => ({ x: c[xKey], y: c[yKey], car: c }));
    const catPts = categories.map(c => ({ x: c[xKey], y: c[yKey], isCat: true, name: c.name }));

    chartInstances[canvasId] = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [
                {
                    label: 'Cars',
                    data: carPts,
                    backgroundColor: 'rgba(56, 189, 248, 0.4)',
                    pointRadius: 4
                },
                {
                    label: 'Categories/Segments',
                    data: catPts,
                    backgroundColor: '#ef4444',
                    pointStyle: 'rectRot',
                    pointRadius: 8
                }
            ]
        },
        options: {
            maintainAspectRatio: false,
            plugins: {
                datalabels: {
                    align: 'top',
                    offset: 4,
                    display: function (ctx) {
                        return ctx.datasetIndex === 1 || cars.length <= 40;
                    },
                    formatter: function (value, ctx) {
                        return ctx.datasetIndex === 1 ? value.name : value.car.name;
                    },
                    color: ctx => ctx.datasetIndex === 1 ? '#fca5a5' : '#94a3b8',
                    font: ctx => ({ weight: ctx.datasetIndex === 1 ? 'bold' : 'normal', size: ctx.datasetIndex === 1 ? 14 : 10 })
                },
                tooltip: {
                    callbacks: {
                        label: ctx => ctx.raw.isCat ? ctx.raw.name : ctx.raw.car.name
                    }
                }
            },
            scales: {
                x: { title: { display: true, text: xLabel }, grid: { color: '#334155' } },
                y: { title: { display: true, text: yLabel }, grid: { color: '#334155' } }
            }
        },
        plugins: [getQuadrantPlugin(0, 0)]
    });
}

function drawBarChart(canvasId, items, valKey, color) {
    const ctx = document.getElementById(canvasId).getContext('2d');

    // Sort array
    const sorted = [...items].sort((a, b) => b[valKey] - a[valKey]);
    const labels = sorted.map(i => i.name);
    const data = sorted.map(i => i[valKey]);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Coefficient',
                data,
                backgroundColor: color,
            }]
        },
        options: {
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: { legend: { display: false }, datalabels: { display: false } },
            scales: { x: { title: { display: true, text: '偏回帰係数' }, grid: { color: '#334155' } }, y: { grid: { display: false } } }
        }
    });
}

function drawBarObj(canvasId, objData, color) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const sortedKeys = Object.keys(objData).sort((a, b) => objData[b] - objData[a]);
    const labels = sortedKeys;
    const data = sortedKeys.map(k => objData[k]);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Coefficient',
                data,
                backgroundColor: color,
            }]
        },
        options: {
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: { legend: { display: false }, datalabels: { display: false } },
            scales: { x: { title: { display: true, text: '回帰係数 (加点・減点)' }, grid: { color: '#334155' } }, y: { grid: { display: false } } }
        }
    });
}

function getQuadrantPlugin(xCenter, yCenter) {
    return {
        id: 'quadrants',
        beforeDraw(chart, args, options) {
            if (xCenter === null || yCenter === null) return;
            const { ctx, chartArea: { top, bottom, left, right }, scales: { x, y } } = chart;
            const xPos = x.getPixelForValue(xCenter);
            const yPos = y.getPixelForValue(yCenter);

            ctx.save();
            ctx.strokeStyle = '#475569';
            ctx.setLineDash([5, 5]);
            ctx.lineWidth = 1;

            if (xPos >= left && xPos <= right) {
                ctx.beginPath();
                ctx.moveTo(xPos, top);
                ctx.lineTo(xPos, bottom);
                ctx.stroke();
            }
            if (yPos >= top && yPos <= bottom) {
                ctx.beginPath();
                ctx.moveTo(left, yPos);
                ctx.lineTo(right, yPos);
                ctx.stroke();
            }
            ctx.restore();
        }
    };
}
