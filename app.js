let CAR_DATA = [];
let chartInstance = null;
let lastModifiedHeader = null;

const yearFilter = document.getElementById('year-filter');
const monthFilter = document.getElementById('month-filter');
const makerFilter = document.getElementById('maker-filter');
const typeFilter = document.getElementById('type-filter');
const segFilter = document.getElementById('seg-filter');
const carFilter = document.getElementById('car-filter');
const regionFilter = document.getElementById('region-filter');

const totalProdEl = document.getElementById('total-production');
const totalSalesEl = document.getElementById('total-sales');
const tbody = document.getElementById('table-body');
const updateIndicator = document.getElementById('update-indicator');

const carInfoCard = document.getElementById('car-info-card');
const infoName = document.getElementById('info-name');
const infoMaker = document.getElementById('info-maker');
const infoType = document.getElementById('info-type');
const infoSeg = document.getElementById('info-seg');

const FETCH_INTERVAL_MS = 10000;

function sanitizeData(rawCars) {
    const now = new Date();
    const currentY = now.getFullYear();
    const currentM = now.getMonth() + 1; // 1-12

    // 深いコピーを作成して元のデータを破壊しないようにする
    const clonedCars = JSON.parse(JSON.stringify(rawCars));

    return clonedCars.map(car => {
        car.monthlyData = car.monthlyData.filter(d => {
            // 未来の年を非表示
            if (d.year > currentY) return false;
            
            // 今年であっても、現在の月以降（まだ発表されていない未来の月）は非表示
            // ※自動車業界の正式発表は通常1ヶ月遅れなので、当月は非表示
            if (d.year === currentY && d.month >= currentM) return false;
            
            return true;
        });
        return car;
    });
}

async function loadData(isAutoUpdate = false) {
    try {
        const response = await fetch('data.json?t=' + new Date().getTime(), { cache: 'no-store' });

        if (!response.ok) {
            throw new Error('Network error. Status: ' + response.status);
        }

        const currentModified = response.headers.get('Last-Modified') || response.headers.get('ETag') || 'v2';

        if (isAutoUpdate && lastModifiedHeader === currentModified && currentModified !== null) {
            updateIndicator.textContent = "データ最新 (自動同期中)";
            updateIndicator.style.color = "#10B981";
            return;
        }

        const jsonData = await response.json();
        CAR_DATA = sanitizeData(jsonData);
        lastModifiedHeader = currentModified;

        if (!isAutoUpdate) {
            initializeFilters();
        }

        processData();

        const now = new Date();
        updateIndicator.textContent = `更新成功: ${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}`;
        updateIndicator.style.color = "#3B82F6";

        setTimeout(() => {
            updateIndicator.style.color = "#10B981";
            updateIndicator.innerHTML = '<span style="display:inline-block; margin-right:6px; width:8px; height:8px; background-color:#10B981; border-radius:50%;"></span> 自動同期オン';
        }, 3000);

    } catch (error) {
        if (typeof INITIAL_DATA !== 'undefined' && !isAutoUpdate) {
            console.warn("Fetch failed (likely CORS), using local INITIAL_DATA.");
            CAR_DATA = sanitizeData(INITIAL_DATA);
            initializeFilters();
            processData();
            updateIndicator.textContent = "ローカル（バックアップ）動作中";
            updateIndicator.style.color = "#F59E0B";
            if (window.autoSyncInterval) clearInterval(window.autoSyncInterval);
        } else if (!isAutoUpdate && typeof INITIAL_DATA === 'undefined') {
            console.error("Failed to load data:", error);
            updateIndicator.textContent = "CORSエラー / サーバー未起動";
            updateIndicator.style.color = "#EF4444";
        }
    }
}

function initializeFilters() {
    yearFilter.innerHTML = '<option value="all">通年 (All Years)</option>';
    const years = [...new Set(CAR_DATA[0].monthlyData.map(d => d.year))].sort();
    years.forEach(y => {
        const opt = document.createElement('option');
        opt.value = y;
        opt.textContent = y + '年';
        if (y === 2026) opt.selected = true;
        yearFilter.appendChild(opt);
    });

    monthFilter.innerHTML = '<option value="all">通月 (All Months)</option>';
    for (let i = 1; i <= 12; i++) {
        const opt = document.createElement('option');
        opt.value = i;
        opt.textContent = i + '月';
        monthFilter.appendChild(opt);
    }

    makerFilter.innerHTML = '<option value="all">すべて</option>';
    const makers = [...new Set(CAR_DATA.map(c => c.maker))];
    makers.forEach(m => {
        const opt = document.createElement('option');
        opt.value = m;
        opt.textContent = m;
        makerFilter.appendChild(opt);
    });

    typeFilter.innerHTML = '<option value="all">すべて</option>';
    const types = [...new Set(CAR_DATA.map(c => c.type))].sort();
    types.forEach(t => {
        const opt = document.createElement('option');
        opt.value = t;
        opt.textContent = t;
        typeFilter.appendChild(opt);
    });

    segFilter.innerHTML = '<option value="all">すべて</option>';
    const segs = [...new Set(CAR_DATA.map(c => c.segment))].sort();
    segs.forEach(s => {
        const opt = document.createElement('option');
        opt.value = s;
        opt.textContent = s;
        segFilter.appendChild(opt);
    });

    updateCarOptions();
}

function updateCarOptions() {
    const sMaker = makerFilter.value;
    const sType = typeFilter.value;
    const sSeg = segFilter.value;

    carFilter.innerHTML = '<option value="all">すべて</option>';

    let cars = CAR_DATA;
    if (sMaker !== 'all') cars = cars.filter(c => c.maker === sMaker);
    if (sType !== 'all') cars = cars.filter(c => c.type === sType);
    if (sSeg !== 'all') cars = cars.filter(c => c.segment === sSeg);

    cars.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c.name;
        opt.textContent = c.name;
        carFilter.appendChild(opt);
    });
}

function processData() {
    if (!CAR_DATA || CAR_DATA.length === 0) return;

    const sYear = yearFilter.value;
    const sMonth = monthFilter.value;
    const sRegion = regionFilter.value;
    const sMaker = makerFilter.value;
    const sType = typeFilter.value;
    const sSeg = segFilter.value;
    const sCar = carFilter.value;

    let filteredData = [];
    let totProd = 0;
    let totSales = 0;

    let chartLabels = [];
    let prodDataset = [];
    let salesDataset = [];
    let chartType = 'bar';

    if (sCar !== 'all') {
        const car = CAR_DATA.find(c => c.name === sCar);

        carInfoCard.style.display = 'block';
        infoName.textContent = car.name;
        infoMaker.textContent = car.maker;
        infoType.textContent = car.type;
        infoSeg.textContent = car.segment;

        car.monthlyData.forEach(d => {
            const matchYear = (sYear === 'all' || sYear == d.year);
            const matchMonth = (sMonth === 'all' || sMonth == d.month);
            if (matchYear && matchMonth) {
                const p = d.production[sRegion];
                const s = d.sales[sRegion];

                filteredData.push({
                    name: car.name, maker: car.maker, type: car.type, segment: car.segment,
                    year: d.year, month: d.month, production: p, sales: s
                });
                totProd += p;
                totSales += s;

                chartLabels.push(d.year + '年' + d.month + '月');
                prodDataset.push(p);
                salesDataset.push(s);
            }
        });
        chartType = 'line';
    } else {
        carInfoCard.style.display = 'none';

        let targetCars = CAR_DATA;
        if (sMaker !== 'all') targetCars = targetCars.filter(c => c.maker === sMaker);
        if (sType !== 'all') targetCars = targetCars.filter(c => c.type === sType);
        if (sSeg !== 'all') targetCars = targetCars.filter(c => c.segment === sSeg);

        targetCars.forEach(car => {
            let carProd = 0;
            let carSales = 0;
            car.monthlyData.forEach(d => {
                const matchYear = (sYear === 'all' || sYear == d.year);
                const matchMonth = (sMonth === 'all' || sMonth == d.month);
                if (matchYear && matchMonth) {
                    const p = d.production[sRegion];
                    const s = d.sales[sRegion];

                    filteredData.push({
                        name: car.name, maker: car.maker, type: car.type, segment: car.segment,
                        year: d.year, month: d.month, production: p, sales: s
                    });
                    totProd += p;
                    totSales += s;

                    carProd += p;
                    carSales += s;
                }
            });
            chartLabels.push(car.name);
            prodDataset.push(carProd);
            salesDataset.push(carSales);
        });

        const zipped = chartLabels.map((l, i) => ({ l, p: prodDataset[i], s: salesDataset[i] }));
        zipped.sort((a, b) => b.p - a.p);
        const top = zipped.slice(0, 15);
        chartLabels = top.map(x => x.l);
        prodDataset = top.map(x => x.p);
        salesDataset = top.map(x => x.s);
    }

    totalProdEl.textContent = totProd.toLocaleString();
    totalSalesEl.textContent = totSales.toLocaleString();

    updateTable(filteredData);
    let labelPrefix = (sRegion === 'domestic') ? '[国内] ' : (sRegion === 'overseas') ? '[海外] ' : '[全体] ';
    updateChart(chartType, chartLabels, prodDataset, salesDataset, labelPrefix);
}

function updateTable(data) {
    tbody.innerHTML = '';

    data.sort((a, b) => {
        if (a.year !== b.year) return b.year - a.year;
        if (a.month !== b.month) return b.month - a.month;
        return b.production - a.production;
    });

    const frag = document.createDocumentFragment();
    const slice = data.slice(0, 300);
    slice.forEach(d => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${d.name}</td>
            <td>${d.maker}</td>
            <td>${d.type}</td>
            <td>${d.segment}</td>
            <td>${d.year}年</td>
            <td>${d.month}月</td>
            <td>${d.production.toLocaleString()}</td>
            <td>${d.sales.toLocaleString()}</td>
        `;
        frag.appendChild(tr);
    });
    tbody.appendChild(frag);
}

function updateChart(type, labels, prodData, salesData, labelPrefix) {
    const ctx = document.getElementById('mainChart').getContext('2d');

    if (chartInstance) {
        chartInstance.destroy();
    }

    Chart.defaults.color = '#9CA3AF';
    Chart.defaults.font.family = 'Inter';

    chartInstance = new Chart(ctx, {
        type: type,
        data: {
            labels: labels,
            datasets: [
                {
                    label: labelPrefix + '生産数',
                    data: prodData,
                    backgroundColor: 'rgba(59, 130, 246, 0.7)',
                    borderColor: '#3B82F6',
                    borderWidth: 2,
                    tension: 0.3,
                    pointRadius: type === 'line' && labels.length > 50 ? 0 : 3
                },
                {
                    label: labelPrefix + '販売数',
                    data: salesData,
                    backgroundColor: 'rgba(16, 185, 129, 0.7)',
                    borderColor: '#10B981',
                    borderWidth: 2,
                    tension: 0.3,
                    pointRadius: type === 'line' && labels.length > 50 ? 0 : 3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top' }
            },
            scales: {
                y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' } },
                x: { grid: { display: false } }
            }
        }
    });
}

makerFilter.addEventListener('change', () => { updateCarOptions(); processData(); });
typeFilter.addEventListener('change', () => { updateCarOptions(); processData(); });
segFilter.addEventListener('change', () => { updateCarOptions(); processData(); });
yearFilter.addEventListener('change', processData);
monthFilter.addEventListener('change', processData);
carFilter.addEventListener('change', processData);
regionFilter.addEventListener('change', processData);

loadData(false);

window.autoSyncInterval = setInterval(() => {
    loadData(true);
}, FETCH_INTERVAL_MS);
