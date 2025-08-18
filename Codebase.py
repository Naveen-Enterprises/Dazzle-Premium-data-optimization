<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sales Dashboard</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Font -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <!-- Chart.js CDN -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f3f4f6;
        }
    </style>
</head>
<body class="p-6 md:p-10">

    <!-- Header Section -->
    <div class="bg-white shadow-xl rounded-2xl p-6 mb-8 text-center">
        <h1 class="text-3xl font-bold text-gray-800 mb-2">📊 Sales Dashboard</h1>
        <p class="text-gray-500">Analyze your sales data directly from Google Sheets.</p>
    </div>

    <!-- URL Input and Load Button -->
    <div class="flex flex-col md:flex-row items-center justify-center space-y-4 md:space-y-0 md:space-x-4 mb-8">
        <input type="text" id="sheetsUrl" placeholder="Paste your Google Sheets URL here..." class="w-full md:w-3/5 p-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
        <button id="loadBtn" class="w-full md:w-auto px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors">Load Data</button>
    </div>

    <!-- Loading Indicator -->
    <div id="loading" class="hidden text-center text-blue-600 font-semibold mb-4">
        Loading data, please wait...
    </div>

    <!-- Message Box -->
    <div id="messageBox" class="hidden p-4 mb-4 text-center rounded-lg font-medium" role="alert"></div>

    <!-- Dashboard Content Container -->
    <div id="dashboard" class="hidden">
        
        <!-- Key Performance Indicators (KPIs) -->
        <h2 class="text-2xl font-semibold text-gray-700 mb-4">📈 Key Metrics</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="bg-white p-6 rounded-2xl shadow-lg border-l-4 border-emerald-500">
                <p class="text-gray-500">Total Revenue</p>
                <h3 id="kpiRevenue" class="text-3xl font-bold text-gray-900 mt-1"></h3>
            </div>
            <div class="bg-white p-6 rounded-2xl shadow-lg border-l-4 border-blue-500">
                <p class="text-gray-500">Total Orders</p>
                <h3 id="kpiOrders" class="text-3xl font-bold text-gray-900 mt-1"></h3>
            </div>
            <div class="bg-white p-6 rounded-2xl shadow-lg border-l-4 border-indigo-500">
                <p class="text-gray-500">Avg. Order Value</p>
                <h3 id="kpiAOV" class="text-3xl font-bold text-gray-900 mt-1"></h3>
            </div>
        </div>

        <!-- Sales Trends Charts -->
        <h2 class="text-2xl font-semibold text-gray-700 mb-4">📊 Sales Trends</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div class="bg-white p-6 rounded-2xl shadow-lg">
                <h3 class="text-lg font-semibold text-gray-800 mb-4">Daily Revenue</h3>
                <canvas id="dailyRevenueChart"></canvas>
            </div>
            <div class="bg-white p-6 rounded-2xl shadow-lg">
                <h3 class="text-lg font-semibold text-gray-800 mb-4">Daily Order Volume</h3>
                <canvas id="dailyOrdersChart"></canvas>
            </div>
        </div>

        <!-- Sales Breakdown Charts -->
        <h2 class="text-2xl font-semibold text-gray-700 mb-4">📉 Sales Breakdown</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div class="bg-white p-6 rounded-2xl shadow-lg">
                <h3 class="text-lg font-semibold text-gray-800 mb-4">Order Status Breakdown</h3>
                <canvas id="statusChart"></canvas>
            </div>
            <div class="bg-white p-6 rounded-2xl shadow-lg">
                <h3 class="text-lg font-semibold text-gray-800 mb-4">Top 10 Customers</h3>
                <canvas id="customersChart"></canvas>
            </div>
        </div>

    </div>

    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const sheetsUrlInput = document.getElementById('sheetsUrl');
            const loadBtn = document.getElementById('loadBtn');
            const loadingIndicator = document.getElementById('loading');
            const messageBox = document.getElementById('messageBox');
            const dashboardContainer = document.getElementById('dashboard');

            let revenueChart, ordersChart, statusChart, customersChart;

            loadBtn.addEventListener('click', () => {
                const url = sheetsUrlInput.value;
                if (url.trim() === '') {
                    showMessage('Please enter a Google Sheets URL.', 'error');
                    return;
                }
                fetchAndProcessData(url);
            });

            function showMessage(message, type) {
                messageBox.textContent = message;
                messageBox.className = `p-4 mb-4 text-center rounded-lg font-medium ${type === 'error' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`;
                messageBox.style.display = 'block';
            }

            // Function to fetch and process data from Google Sheets
            async function fetchAndProcessData(url) {
                loadingIndicator.style.display = 'block';
                dashboardContainer.style.display = 'none';
                messageBox.style.display = 'none';

                try {
                    // Extract the sheet ID and gid from the URL
                    const matches = url.match(/\/d\/(.+?)\/edit(?:#gid=(\d+))?/);
                    if (!matches) {
                        throw new Error("Invalid Google Sheets URL. Please use a valid public link.");
                    }
                    const sheetId = matches[1];
                    const gid = matches[2] || '0'; // default gid is 0 if not specified
                    
                    const csvUrl = `https://docs.google.com/spreadsheets/d/${sheetId}/export?format=csv&gid=${gid}`;

                    const response = await fetch(csvUrl);
                    if (!response.ok) {
                        throw new Error(`Failed to fetch data: HTTP status ${response.status}`);
                    }
                    const csvText = await response.text();
                    
                    const data = parseCSV(csvText);
                    
                    if (data.length === 0) {
                        throw new Error("No data found in the CSV. Please check your sheet.");
                    }

                    // Process the data for the dashboard
                    const processedData = processData(data);
                    
                    renderKPIs(processedData);
                    renderCharts(processedData);

                    dashboardContainer.style.display = 'block';
                    showMessage('Dashboard updated successfully!', 'success');

                } catch (error) {
                    showMessage(`Error: ${error.message}`, 'error');
                    console.error("Dashboard error:", error);
                } finally {
                    loadingIndicator.style.display = 'none';
                }
            }
            
            // Simple CSV parser
            function parseCSV(csv) {
                const lines = csv.split('\n');
                if (lines.length <= 1) return []; // Handle empty or header-only files

                const headers = lines[0].split(',').map(h => h.trim());
                const data = [];

                for (let i = 1; i < lines.length; i++) {
                    const line = lines[i].trim();
                    if (line === '') continue; // Skip empty rows

                    const values = line.split(',');
                    if (values.length !== headers.length) continue; // Skip malformed rows
                    
                    const row = {};
                    for (let j = 0; j < headers.length; j++) {
                        row[headers[j]] = values[j] ? values[j].trim() : '';
                    }
                    data.push(row);
                }
                return data;
            }

            // Data processing logic
            function processData(rawData) {
                const data = rawData.map(row => {
                    const cleanRow = { ...row };
                    
                    // Clean Price
                    cleanRow.Price = parseFloat(row.Price.replace(/[^0-9.-]+/g, "")) || 0;
                    
                    // Clean Date
                    cleanRow.Date = row.Date ? new Date(row.Date) : null;
                    
                    // Clean Status
                    cleanRow.Status = row.Status.trim().toUpperCase();

                    return cleanRow;
                }).filter(row => row.Date && row.Price > 0 && row.Status); // Filter out invalid rows

                const fulfilledOrders = data.filter(d => d.Status === 'FULFILLED');
                const totalRevenue = fulfilledOrders.reduce((sum, row) => sum + row.Price, 0);
                const totalOrders = data.length;
                const avgOrderValue = totalOrders > 0 ? totalRevenue / fulfilledOrders.length : 0;
                
                // Group data for charts
                const dailyRevenue = data.reduce((acc, curr) => {
                    const date = curr.Date.toISOString().split('T')[0];
                    acc[date] = (acc[date] || 0) + curr.Price;
                    return acc;
                }, {});

                const dailyOrders = data.reduce((acc, curr) => {
                    const date = curr.Date.toISOString().split('T')[0];
                    acc[date] = (acc[date] || 0) + 1;
                    return acc;
                }, {});

                const statusCounts = data.reduce((acc, curr) => {
                    acc[curr.Status] = (acc[curr.Status] || 0) + 1;
                    return acc;
                }, {});

                const customerSpending = fulfilledOrders.reduce((acc, curr) => {
                    acc[curr['Customer Name']] = (acc[curr['Customer Name']] || 0) + curr.Price;
                    return acc;
                }, {});

                const topCustomers = Object.entries(customerSpending)
                    .sort(([, a], [, b]) => b - a)
                    .slice(0, 10)
                    .map(([name, price]) => ({ name, price }));
                    
                return {
                    totalRevenue,
                    totalOrders,
                    avgOrderValue,
                    dailyRevenue,
                    dailyOrders,
                    statusCounts,
                    topCustomers
                };
            }

            // Render KPIs
            function renderKPIs(data) {
                document.getElementById('kpiRevenue').textContent = `$${data.totalRevenue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
                document.getElementById('kpiOrders').textContent = data.totalOrders.toLocaleString('en-US');
                document.getElementById('kpiAOV').textContent = `$${data.avgOrderValue.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
            }

            // Render Charts using Chart.js
            function renderCharts(data) {
                // Destroy previous chart instances to prevent duplicates
                if (revenueChart) revenueChart.destroy();
                if (ordersChart) ordersChart.destroy();
                if (statusChart) statusChart.destroy();
                if (customersChart) customersChart.destroy();

                // Daily Revenue Chart
                const dailyRevenueCtx = document.getElementById('dailyRevenueChart').getContext('2d');
                revenueChart = new Chart(dailyRevenueCtx, {
                    type: 'line',
                    data: {
                        labels: Object.keys(data.dailyRevenue),
                        datasets: [{
                            label: 'Daily Revenue ($)',
                            data: Object.values(data.dailyRevenue),
                            backgroundColor: 'rgba(59, 130, 246, 0.2)',
                            borderColor: 'rgba(59, 130, 246, 1)',
                            borderWidth: 2,
                            tension: 0.1
                        }]
                    },
                    options: { responsive: true, maintainAspectRatio: false }
                });

                // Daily Orders Chart
                const dailyOrdersCtx = document.getElementById('dailyOrdersChart').getContext('2d');
                ordersChart = new Chart(dailyOrdersCtx, {
                    type: 'line',
                    data: {
                        labels: Object.keys(data.dailyOrders),
                        datasets: [{
                            label: 'Daily Orders',
                            data: Object.values(data.dailyOrders),
                            backgroundColor: 'rgba(251, 191, 36, 0.2)',
                            borderColor: 'rgba(251, 191, 36, 1)',
                            borderWidth: 2,
                            tension: 0.1
                        }]
                    },
                    options: { responsive: true, maintainAspectRatio: false }
                });

                // Order Status Breakdown Chart (Pie Chart)
                const statusCtx = document.getElementById('statusChart').getContext('2d');
                statusChart = new Chart(statusCtx, {
                    type: 'pie',
                    data: {
                        labels: Object.keys(data.statusCounts),
                        datasets: [{
                            data: Object.values(data.statusCounts),
                            backgroundColor: ['#22c55e', '#ef4444', '#f59e0b', '#3b82f6'],
                            hoverOffset: 4
                        }]
                    },
                    options: { responsive: true, maintainAspectRatio: false }
                });

                // Top 10 Customers Chart (Bar Chart)
                const customersCtx = document.getElementById('customersChart').getContext('2d');
                customersChart = new Chart(customersCtx, {
                    type: 'bar',
                    data: {
                        labels: data.topCustomers.map(c => c.name),
                        datasets: [{
                            label: 'Total Spent ($)',
                            data: data.topCustomers.map(c => c.price),
                            backgroundColor: '#10b981',
                        }]
                    },
                    options: { 
                        responsive: true, 
                        maintainAspectRatio: false,
                        indexAxis: 'y', // Make it a horizontal bar chart
                        scales: { x: { beginAtZero: true } }
                    }
                });
            }
        });
    </script>

</body>
</html>
