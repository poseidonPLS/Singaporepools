/**
 * Charts Module
 * Handles Chart.js visualizations
 * Version: 1.0.0
 */

const Charts = {
    frequencyChart: null,
    
    // Chart.js default configuration for dark theme
    defaultConfig: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false,
            },
            tooltip: {
                backgroundColor: '#222230',
                titleColor: '#f0f0f5',
                bodyColor: '#8888a0',
                borderColor: 'rgba(0, 255, 240, 0.2)',
                borderWidth: 1,
                padding: 12,
                cornerRadius: 8,
            },
        },
        scales: {
            x: {
                grid: {
                    color: 'rgba(255, 255, 255, 0.05)',
                },
                ticks: {
                    color: '#8888a0',
                    font: {
                        family: 'JetBrains Mono',
                        size: 10,
                    },
                },
            },
            y: {
                grid: {
                    color: 'rgba(255, 255, 255, 0.05)',
                },
                ticks: {
                    color: '#8888a0',
                    font: {
                        family: 'JetBrains Mono',
                        size: 10,
                    },
                },
            },
        },
    },
    
    // Initialize frequency chart
    initFrequencyChart(canvasId = 'frequencyChart') {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;
        
        // Destroy existing chart
        if (this.frequencyChart) {
            this.frequencyChart.destroy();
        }
        
        // Create gradient
        const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'rgba(0, 255, 240, 0.8)');
        gradient.addColorStop(1, 'rgba(255, 0, 255, 0.2)');
        
        this.frequencyChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Array.from({ length: 49 }, (_, i) => i + 1),
                datasets: [{
                    label: 'Frequency',
                    data: Array(49).fill(0),
                    backgroundColor: gradient,
                    borderColor: 'rgba(0, 255, 240, 0.8)',
                    borderWidth: 1,
                    borderRadius: 4,
                }],
            },
            options: {
                ...this.defaultConfig,
                plugins: {
                    ...this.defaultConfig.plugins,
                    tooltip: {
                        ...this.defaultConfig.plugins.tooltip,
                        callbacks: {
                            title: (items) => `Number ${items[0].label}`,
                            label: (item) => `Appearances: ${item.raw}`,
                        },
                    },
                },
            },
        });
    },
    
    // Update frequency chart with new data
    updateFrequencyChart(frequencyData) {
        if (!this.frequencyChart) {
            this.initFrequencyChart();
        }
        
        const data = [];
        for (let i = 1; i <= 49; i++) {
            data.push(frequencyData[i] || 0);
        }
        
        this.frequencyChart.data.datasets[0].data = data;
        
        // Color based on frequency
        const max = Math.max(...data);
        const min = Math.min(...data);
        const colors = data.map(val => {
            const ratio = (val - min) / (max - min || 1);
            if (ratio > 0.7) return 'rgba(255, 107, 53, 0.8)'; // Hot
            if (ratio < 0.3) return 'rgba(74, 144, 217, 0.6)'; // Cold
            return 'rgba(0, 255, 240, 0.6)'; // Normal
        });
        
        this.frequencyChart.data.datasets[0].backgroundColor = colors;
        this.frequencyChart.update('none');
    },
    
    // Create distribution chart
    createDistributionChart(canvasId, labels, datasets) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;
        
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: datasets.map((ds, i) => ({
                    ...ds,
                    borderColor: ['#00fff0', '#ff00ff', '#ffd700'][i % 3],
                    backgroundColor: 'transparent',
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                })),
            },
            options: this.defaultConfig,
        });
    },
};

window.Charts = Charts;
