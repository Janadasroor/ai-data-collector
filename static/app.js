// WebSocket connection
let ws = null;
let reconnectInterval = null;
let charts = {};
let dataHistory = {
    pages: [],
    speed: [],
    labels: []
};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    connectWebSocket();
    loadRecentData();
    loadLogs();
    
    // Auto-refresh every 30 seconds
    setInterval(() => {
        loadRecentData();
        loadLogs();
    }, 30000);
});

// WebSocket connection
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        console.log('WebSocket connected');
        updateStatus(true);
        if (reconnectInterval) {
            clearInterval(reconnectInterval);
            reconnectInterval = null;
        }
    };
    
    ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        if (message.type === 'stats') {
            updateStats(message.data);
        }
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        updateStatus(false);
    };
    
    ws.onclose = () => {
        console.log('WebSocket disconnected');
        updateStatus(false);
        
        // Attempt to reconnect
        if (!reconnectInterval) {
            reconnectInterval = setInterval(() => {
                console.log('Attempting to reconnect...');
                connectWebSocket();
            }, 5000);
        }
    };
}

// Update connection status
function updateStatus(connected) {
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');
    
    if (connected) {
        statusDot.classList.remove('disconnected');
        statusText.textContent = 'Connected';
    } else {
        statusDot.classList.add('disconnected');
        statusText.textContent = 'Disconnected';
    }
}

// Update statistics
function updateStats(data) {
    const stats = data.stats;
    
    // Update stat cards
    document.getElementById('pagesCrawled').textContent = stats.pages_crawled.toLocaleString();
    document.getElementById('codeFiles').textContent = stats.code_files_collected.toLocaleString();
    document.getElementById('dataCollected').textContent = `${stats.total_mb} MB`;
    document.getElementById('speed').textContent = `${stats.pages_per_minute} p/min`;
    document.getElementById('totalItems').textContent = data.total_items.toLocaleString();
    document.getElementById('queueSize').textContent = data.queue_size.toLocaleString();
    document.getElementById('runtime').textContent = `${stats.elapsed_hours}h`;
    document.getElementById('failed').textContent = stats.pages_failed.toLocaleString();
    
    // Update charts
    updateCharts(stats);
}

// Initialize charts
function initCharts() {
    // Progress Chart
    const progressCtx = document.getElementById('progressChart').getContext('2d');
    charts.progress = new Chart(progressCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Pages Crawled',
                data: [],
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#e2e8f0'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#94a3b8'
                    },
                    grid: {
                        color: 'rgba(148, 163, 184, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: '#94a3b8'
                    },
                    grid: {
                        color: 'rgba(148, 163, 184, 0.1)'
                    }
                }
            }
        }
    });
    
    // Distribution Chart
    const distributionCtx = document.getElementById('distributionChart').getContext('2d');
    charts.distribution = new Chart(distributionCtx, {
        type: 'doughnut',
        data: {
            labels: ['Webpages', 'Code Files', 'Failed'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: [
                    'rgba(99, 102, 241, 0.8)',
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(239, 68, 68, 0.8)'
                ],
                borderColor: [
                    '#6366f1',
                    '#10b981',
                    '#ef4444'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#e2e8f0',
                        padding: 15
                    }
                }
            }
        }
    });
}

// Update charts with new data
function updateCharts(stats) {
    const now = new Date().toLocaleTimeString();
    
    // Keep last 20 data points
    if (dataHistory.labels.length >= 20) {
        dataHistory.labels.shift();
        dataHistory.pages.shift();
    }
    
    dataHistory.labels.push(now);
    dataHistory.pages.push(stats.pages_crawled);
    
    // Update progress chart
    charts.progress.data.labels = dataHistory.labels;
    charts.progress.data.datasets[0].data = dataHistory.pages;
    charts.progress.update('none');
    
    // Update distribution chart
    const webpages = stats.pages_crawled - stats.code_files_collected;
    charts.distribution.data.datasets[0].data = [
        webpages,
        stats.code_files_collected,
        stats.pages_failed
    ];
    charts.distribution.update('none');
}

// Load recent data
async function loadRecentData() {
    try {
        const response = await fetch('/api/recent-data');
        const result = await response.json();
        
        const tbody = document.getElementById('recentDataBody');
        tbody.innerHTML = '';
        
        if (result.data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="loading">No data collected yet</td></tr>';
            return;
        }
        
        result.data.forEach(item => {
            const row = document.createElement('tr');
            
            const typeClass = item.type === 'code' ? 'type-code' : 'type-webpage';
            const title = item.type === 'code' ? item.file_extension : (item.title || 'Untitled');
            const size = formatBytes(item.size_bytes);
            const time = new Date(item.timestamp).toLocaleTimeString();
            
            row.innerHTML = `
                <td><span class="type-badge ${typeClass}">${item.type}</span></td>
                <td class="url-cell" title="${item.url}">${item.url}</td>
                <td>${title}</td>
                <td>${size}</td>
                <td>${item.source_domain}</td>
                <td>${time}</td>
            `;
            
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading recent data:', error);
    }
}

// Load logs
async function loadLogs() {
    try {
        const response = await fetch('/api/logs');
        const result = await response.json();
        
        const container = document.getElementById('logsContainer');
        container.innerHTML = '';
        
        if (result.logs.length === 0) {
            container.innerHTML = '<div class="loading">No logs available</div>';
            return;
        }
        
        result.logs.forEach(log => {
            const div = document.createElement('div');
            div.className = 'log-line';
            
            // Colorize based on log level
            if (log.includes('INFO')) {
                div.classList.add('info');
            } else if (log.includes('WARNING')) {
                div.classList.add('warning');
            } else if (log.includes('ERROR')) {
                div.classList.add('error');
            } else if (log.includes('✅')) {
                div.classList.add('success');
            }
            
            div.textContent = log;
            container.appendChild(div);
        });
        
        // Auto-scroll to bottom
        container.scrollTop = container.scrollHeight;
    } catch (error) {
        console.error('Error loading logs:', error);
    }
}

// Format bytes
function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}
