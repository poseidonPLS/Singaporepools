/**
 * Main Application Controller
 * Initializes dashboard and handles user interactions
 * Version: 1.0.0
 */

// Application State
const App = {
    currentGame: 'toto',
    data: {
        toto: [],
        fourD: [],
    },
    // Pagination State
    pagination: {
        currentPage: 1,
        itemsPerPage: 10
    },
    analysis: {},
    lang: 'en', // Default language

    // Toggle Donation Modal
    toggleDonationModal() {
        const modal = document.getElementById('donationModal');
        if (modal) {
            modal.style.display = modal.style.display === 'none' ? 'flex' : 'none';
        }
    },

    // Set Language
    setLanguage(lang) {
        if (!TRANSLATIONS[lang]) return;
        
        this.lang = lang;
        localStorage.setItem('pool_lang', lang);
        
        // Update Buttons
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.classList.toggle('active', btn.textContent.toLowerCase() === lang || 
                (lang === 'zh' && btn.textContent === '中') ||
                (lang === 'ms' && btn.textContent === 'MS') ||
                (lang === 'ta' && btn.textContent === 'TA'));
        });

        // Update Text
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            const text = TRANSLATIONS[lang][key];
            if (text) {
                // If it contains HTML tag (like span), use innerHTML, else textContent
                if (text.includes('<')) el.innerHTML = text;
                else el.textContent = text;
            }
        });
        
        // Update Dynamic Placeholders
        this.updateDynamicText();
    },

    updateDynamicText() {
        // Status message if loaded
        if (this.data.toto.length > 0) {
            const tmpl = TRANSLATIONS[this.lang]["status.success"];
            const msg = tmpl.replace('{toto}', this.data.toto.length).replace('{fourd}', this.data.fourD.length);
            this.updateScrapeStatus('success', msg);
        } else {
             this.updateScrapeStatus(document.querySelector('.scrape-status').className.includes('success') ? 'success' : 'warning', 
                TRANSLATIONS[this.lang][this.data.toto.length > 0 ? "status.success" : "status.notLoaded"]);
        }
    },

    // Initialize application
    async init() {
        console.log('🎲 Initializing SG Pools Predictor...');
        
        // Load Language
        const savedLang = localStorage.getItem('pool_lang');
        if (savedLang && TRANSLATIONS[savedLang]) {
            this.setLanguage(savedLang);
        } else {
            this.setLanguage('en');
        }
        
        // Set up event listeners
        this.setupStrategyButtons();
        this.setupNavigation();
        
        // Initialize charts
        Charts.initFrequencyChart();
        
        // Generate heatmap
        this.renderHeatmap();
        
        // Load demo data on start
        await this.loadData();
        
        console.log('✅ Application initialized');
    },

    // --- Navigation Logic ---
    setupNavigation() {
        const links = document.querySelectorAll('.nav__link');
        const views = document.querySelectorAll('.view-content');

        links.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                
                // Active Link
                links.forEach(l => l.classList.remove('nav__link--active'));
                link.classList.add('nav__link--active');

                // Show View
                const targetId = link.getAttribute('href').substring(1); // 'dashboard'
                
                views.forEach(view => {
                    view.style.display = view.id === `view-${targetId}` ? 'block' : 'none';
                });
                
                // If switching to analysis, refresh charts to ensure width is correct
                if (targetId === 'analysis') {
                    setTimeout(() => Charts.updateFrequencyChart(this.analysis.frequency?.frequency), 100);
                }
            });
        });
    },

    // --- Pagination Logic ---
    nextPage() {
        const draws = this.currentGame === 'toto' ? this.data.toto : this.data.fourD;
        const maxPage = Math.ceil(draws.length / this.pagination.itemsPerPage);
        
        if (this.pagination.currentPage < maxPage) {
            this.pagination.currentPage++;
            this.renderHistoryTable();
            this.scrollToTop();
        }
    },

    prevPage() {
        if (this.pagination.currentPage > 1) {
            this.pagination.currentPage--;
            this.renderHistoryTable();
            this.scrollToTop();
        }
    },

    scrollToTop() {
        const table = document.getElementById('view-history');
        if (table) {
            const headerOffset = 100;
            const elementPosition = table.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });
        }
    },
    
    // Load data from API
    async loadData() {
        try {
            this.updateScrapeStatus('loading', 'Loading data...');
            
            const data = await API.loadData();
            
            if (data) {
                this.data.toto = data.toto || [];
                this.data.fourD = data.fourD || [];
                
                // Update stats
                document.getElementById('stat4dDraws').textContent = this.data.fourD.length;
                document.getElementById('statTotoDraws').textContent = this.data.toto.length;
                
                // Analyze data
                this.analyzeData();
                
                // Update UI
                this.updateDashboard();
                
                this.updateScrapeStatus('success', `Loaded ${this.data.toto.length} Toto + ${this.data.fourD.length} 4D draws`);
            } else {
                this.updateScrapeStatus('error', 'Failed to load data');
            }
        } catch (error) {
            console.error('Load error:', error);
            this.updateScrapeStatus('error', 'Error loading data');
        }
    },
    
    // Analyze loaded data
    analyzeData() {
        if (this.currentGame === 'toto' && this.data.toto.length > 0) {
            this.analysis.frequency = API.analyzeFrequency(this.data.toto, 'toto');
            this.analysis.gaps = API.analyzeGaps(this.data.toto);
            
            // Pass to Predictions module
            Predictions.setData(this.analysis.frequency, this.analysis.gaps);
            
            // Update stats
            if (this.analysis.frequency?.hotNumbers?.length > 0) {
                document.getElementById('statHotNumber').textContent = this.analysis.frequency.hotNumbers[0];
            }
            if (this.analysis.gaps?.mostOverdue?.length > 0) {
                document.getElementById('statOverdue').textContent = this.analysis.gaps.mostOverdue[0].number;
            }
        } else if (this.currentGame === '4d' && this.data.fourD.length > 0) {
            this.analysis.fourDFrequency = API.analyze4DFrequency(this.data.fourD);
        }
    },
    
    // Update dashboard UI
    updateDashboard() {
        // Update frequency chart
        if (this.analysis.frequency?.frequency) {
            Charts.updateFrequencyChart(this.analysis.frequency.frequency);
        }
        
        // Update heatmap
        this.renderHeatmap();
        
        // Update overdue list
        this.renderOverdueList();
        
        // Update history table
        this.renderHistoryTable();
    },
    
    // Render frequency heatmap with gradient colors
    renderHeatmap() {
        const container = document.getElementById('heatmap');
        if (!container) return;
        
        container.innerHTML = '';
        
        // Clean color palette
        const coldColor = { r: 59, g: 130, b: 246 };   // #3b82f6 - Vibrant blue
        const neutralColor = { r: 35, g: 35, b: 45 };  // #23232d - Dark gray
        const hotColor = { r: 239, g: 68, b: 68 };     // #ef4444 - Vibrant red
        
        const lerp = (a, b, t) => Math.round(a + (b - a) * t);
        const lerpColor = (c1, c2, t) => ({
            r: lerp(c1.r, c2.r, t),
            g: lerp(c1.g, c2.g, t),
            b: lerp(c1.b, c2.b, t)
        });
        
        // Helper to style a cell based on deviation
        const styleCell = (cell, deviation, freq, label) => {
            let color, textColor, boxShadow = 'none';
            
            if (deviation > 0.05) {
                const t = Math.min(deviation / 0.8, 1);
                color = lerpColor(neutralColor, hotColor, t);
                textColor = `rgba(255, 255, 255, ${0.6 + t * 0.4})`;
                if (t > 0.6) boxShadow = `0 0 ${Math.round(8 + t * 8)}px rgba(239, 68, 68, ${t * 0.4})`;
            } else if (deviation < -0.05) {
                const t = Math.min(Math.abs(deviation) / 0.8, 1);
                color = lerpColor(neutralColor, coldColor, t);
                textColor = `rgba(255, 255, 255, ${0.6 + t * 0.4})`;
                if (t > 0.6) boxShadow = `0 0 ${Math.round(8 + t * 8)}px rgba(59, 130, 246, ${t * 0.4})`;
            } else {
                color = neutralColor;
                textColor = 'rgba(255, 255, 255, 0.5)';
            }
            
            cell.style.background = `rgb(${color.r}, ${color.g}, ${color.b})`;
            cell.style.color = textColor;
            cell.style.boxShadow = boxShadow;
            
            const deviationPct = Math.round(deviation * 100);
            const sign = deviationPct >= 0 ? '+' : '';
            cell.setAttribute('data-tooltip', `${label}: ${freq}× (${sign}${deviationPct}%)`);
        };
        
        if (this.currentGame === '4d') {
            // 4D: Show 4-column (positions) × 10-row (digits) grid
            container.style.gridTemplateColumns = 'repeat(4, 1fr)';
            container.style.maxWidth = '320px';
            
            const positionData = this.analysis.fourDFrequency?.positionFreq;
            const positions = ['thousands', 'hundreds', 'tens', 'units'];
            const positionLabels = ['1st', '2nd', '3rd', '4th'];
            
            // Add header row
            positions.forEach((_, i) => {
                const header = document.createElement('div');
                header.className = 'heatmap__header';
                header.textContent = positionLabels[i];
                header.style.textAlign = 'center';
                header.style.fontWeight = '600';
                header.style.color = 'var(--accent-cyan)';
                header.style.padding = '0.5rem';
                header.style.fontSize = '0.75rem';
                container.appendChild(header);
            });
            
            // Calculate deviations for 4D
            const totalPerPosition = this.data.fourD.length * 3; // 3 prizes per draw
            const expected = totalPerPosition / 10; // 10 digits
            
            // Find max deviation for normalization
            let maxAbsDev = 0;
            positions.forEach(pos => {
                for (let d = 0; d <= 9; d++) {
                    const count = positionData?.[pos]?.[d] || 0;
                    const dev = Math.abs((count - expected) / expected);
                    if (dev > maxAbsDev) maxAbsDev = dev;
                }
            });
            
            // Render digit rows (0-9)
            for (let digit = 0; digit <= 9; digit++) {
                positions.forEach(pos => {
                    const cell = document.createElement('div');
                    cell.className = 'heatmap__cell';
                    cell.textContent = digit;
                    
                    const count = positionData?.[pos]?.[digit] || 0;
                    const rawDev = (count - expected) / expected;
                    const deviation = maxAbsDev > 0 ? rawDev / maxAbsDev : 0;
                    
                    styleCell(cell, deviation, count, `Digit ${digit}`);
                    container.appendChild(cell);
                });
            }
        } else {
            // TOTO: Standard 1-49 grid (7 columns)
            container.style.gridTemplateColumns = 'repeat(7, 1fr)';
            container.style.maxWidth = '500px';
            
            for (let i = 1; i <= 49; i++) {
                const cell = document.createElement('div');
                cell.className = 'heatmap__cell';
                cell.textContent = i;
                
                const deviation = this.analysis.frequency?.deviations?.[i] || 0;
                const freq = this.analysis.frequency?.frequency?.[i] || 0;
                
                styleCell(cell, deviation, freq, `#${i}`);
                container.appendChild(cell);
            }
        }
    },
    
    // Render overdue numbers list
    renderOverdueList() {
        const container = document.getElementById('overdueList');
        if (!container || !this.analysis.gaps?.mostOverdue) return;
        
        const items = this.analysis.gaps.mostOverdue.slice(0, 8);
        
        container.innerHTML = items.map((item, i) => `
            <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                <span style="color: ${i < 3 ? 'var(--accent-orange)' : 'var(--text-secondary)'};">
                    #${item.number}
                </span>
                <span style="color: var(--text-muted);">
                    ${item.gap} draws ago
                </span>
            </div>
        `).join('');
    },
    
    // Render history table
    renderHistoryTable() {
        const tbody = document.getElementById('historyBody');
        const countBadge = document.getElementById('historyCount');
        const prevBtn = document.getElementById('prevPageBtn');
        const nextBtn = document.getElementById('nextPageBtn');
        const pageNum = document.getElementById('currentPageNum');
        
        if (!tbody) return;
        
        const draws = this.currentGame === 'toto' ? this.data.toto : this.data.fourD;
        
        // Pagination Calculation
        const startIndex = (this.pagination.currentPage - 1) * this.pagination.itemsPerPage;
        const endIndex = startIndex + this.pagination.itemsPerPage;
        const recent = draws.slice(startIndex, endIndex);
        const totalPages = Math.ceil(draws.length / this.pagination.itemsPerPage);
        
        // Update Controls
        if (countBadge) countBadge.textContent = `${draws.length} draws`;
        if (pageNum) pageNum.textContent = `${this.pagination.currentPage} / ${totalPages}`;
        if (prevBtn) prevBtn.disabled = this.pagination.currentPage === 1;
        if (nextBtn) nextBtn.disabled = this.pagination.currentPage >= totalPages;
        
        if (recent.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="4" style="text-align: center; color: var(--text-muted);">
                        No data loaded. Run the scrapers first.
                    </td>
                </tr>
            `;
            return;
        }
        
        if (this.currentGame === 'toto') {
            tbody.innerHTML = recent.map(draw => `
                <tr>
                    <td>${draw.draw_number}</td>
                    <td>${draw.draw_date}</td>
                    <td>
                        ${draw.winning_numbers.map(n => 
                            `<span style="display: inline-block; width: 28px; height: 28px; line-height: 28px; text-align: center; background: var(--gradient-primary); color: var(--bg-primary); border-radius: 50%; font-size: 0.75rem; font-weight: bold; margin: 2px;">${n}</span>`
                        ).join('')}
                    </td>
                    <td>
                        <span style="display: inline-block; width: 28px; height: 28px; line-height: 28px; text-align: center; background: var(--gradient-gold); color: var(--bg-primary); border-radius: 50%; font-size: 0.75rem; font-weight: bold;">+${draw.additional_number}</span>
                    </td>
                </tr>
            `).join('');
        } else {
            // 4D table format
            const headers = document.querySelector('#historyTable thead tr');
            if (headers) {
                headers.innerHTML = `
                    <th>Draw #</th>
                    <th>Date</th>
                    <th>1st Prize</th>
                    <th>2nd Prize</th>
                    <th>3rd Prize</th>
                `;
            }
            
            tbody.innerHTML = recent.map(draw => `
                <tr>
                    <td>${draw.draw_number}</td>
                    <td>${draw.draw_date}</td>
                    <td style="color: var(--accent-gold); font-weight: bold;">${draw.first_prize}</td>
                    <td>${draw.second_prize}</td>
                    <td>${draw.third_prize}</td>
                </tr>
            `).join('');
        }
    },
    
    // Setup strategy button listeners
    setupStrategyButtons() {
        const generateBtn = document.querySelector('.generate-btn');
        
        document.querySelectorAll('.strategy-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.strategy-btn').forEach(b => b.classList.remove('strategy-btn--active'));
                btn.classList.add('strategy-btn--active');
                
                // Disable generate button for AI strategy (predictions are pre-cached)
                if (btn.dataset.strategy === 'ai') {
                    generateBtn.disabled = true;
                    generateBtn.style.opacity = '0.5';
                    generateBtn.style.cursor = 'not-allowed';
                    generateBtn.textContent = '🤖 AI Predictions are pre-generated';
                } else {
                    generateBtn.disabled = false;
                    generateBtn.style.opacity = '1';
                    generateBtn.style.cursor = 'pointer';
                    generateBtn.textContent = '🎯 Generate Numbers';
                    // Reset explanation when switching away from AI
                    document.getElementById('strategyExplanation').textContent = 'Select a strategy and generate your lucky numbers';
                }
            });
        });
    },
    
    // Update scrape status indicator
    updateScrapeStatus(status, message) {
        const container = document.getElementById('scrapeStatus');
        if (!container) return;
        
        const indicator = container.querySelector('.scrape-status__indicator');
        const text = container.querySelector('.scrape-status__text');
        
        indicator.className = 'scrape-status__indicator';
        if (status === 'error') indicator.classList.add('scrape-status__indicator--error');
        else if (status === 'loading') indicator.classList.add('scrape-status__indicator--warning');
        // Success is default green
        
        if (text) text.textContent = message;
    },
};

// Global functions for HTML onclick handlers
function switchGame(game) {
    App.currentGame = game;
    
    // Update tabs
    document.querySelectorAll('.game-tab').forEach(tab => {
        tab.classList.toggle('game-tab--active', tab.dataset.game === game);
    });
    
    // Update label
    document.getElementById('gameTypeLabel').textContent = game === 'toto' ? 'TOTO' : '4D';
    
    // Update ball display for 4D
    const additionalBall = document.getElementById('additionalBall');
    if (game === '4d') {
        // Show 4 balls for 4D
        const balls = document.querySelectorAll('#predictedNumbers .lottery-ball');
        balls.forEach((ball, i) => {
            if (i < 4) {
                ball.style.display = 'flex';
                ball.classList.add('lottery-ball--4d');
            } else {
                ball.style.display = 'none';
            }
        });
        if (additionalBall) additionalBall.style.display = 'none';
    } else {
        // Show 6 balls for Toto
        const balls = document.querySelectorAll('#predictedNumbers .lottery-ball');
        balls.forEach((ball, i) => {
            ball.style.display = 'flex';
            ball.classList.remove('lottery-ball--4d');
        });
        if (additionalBall) additionalBall.style.display = 'inline-flex';
    }
    
    // Reset pagination
    App.pagination.currentPage = 1;
    
    // Re-analyze data for the new game
    App.analyzeData();
    App.updateDashboard();
    
    // Reset prediction display
    resetPredictionDisplay();
}

function generateNumbers() {
    const activeBtn = document.querySelector('.strategy-btn.strategy-btn--active');
    const strategy = activeBtn?.dataset.strategy || 'weighted';
    
    if (App.currentGame === 'toto') {
        const result = Predictions.generateToto(strategy);
        displayTotoNumbers(result.numbers, result.explanation);
    } else {
        const result = Predictions.generate4D(strategy);
        display4DNumber(result.number, result.explanation);
    }
}

function displayTotoNumbers(numbers, explanation) {
    const container = document.getElementById('predictedNumbers');
    const balls = container.querySelectorAll('.lottery-ball:not(.lottery-ball--additional)');
    
    // Animate balls
    balls.forEach((ball, i) => {
        if (i < numbers.length) {
            ball.style.transform = 'scale(0)';
            setTimeout(() => {
                ball.textContent = numbers[i];
                ball.style.transform = 'scale(1)';
            }, i * 100);
        }
    });
    
    // Generate additional number
    setTimeout(() => {
        const additional = document.getElementById('additionalBall');
        if (additional) {
            let addNum;
            do {
                addNum = Math.floor(Math.random() * 49) + 1;
            } while (numbers.includes(addNum));
            additional.textContent = `+${addNum}`;
            additional.style.display = 'inline-flex';
        }
    }, 600);
    
    // Update explanation
    document.getElementById('strategyExplanation').textContent = explanation;
}

function display4DNumber(number, explanation) {
    const container = document.getElementById('predictedNumbers');
    const balls = container.querySelectorAll('.lottery-ball:not(.lottery-ball--additional)');
    
    balls.forEach((ball, i) => {
        if (i < 4) {
            ball.style.transform = 'scale(0)';
            setTimeout(() => {
                ball.textContent = number[i];
                ball.style.transform = 'scale(1)';
            }, i * 100);
        }
    });
    
    document.getElementById('strategyExplanation').textContent = explanation;
}

function resetPredictionDisplay() {
    const balls = document.querySelectorAll('#predictedNumbers .lottery-ball');
    balls.forEach(ball => {
        ball.textContent = '?';
    });
    document.getElementById('strategyExplanation').textContent = 'Select a strategy and generate your lucky numbers';
}

function loadData() {
    App.loadData();
}

// AI Prediction handler (uses cached predictions only - generated after each scrape)
async function generateAINumbers() {
    const strategyExplanation = document.getElementById('strategyExplanation');
    strategyExplanation.textContent = '🤖 Loading AI prediction...';
    
    try {
        // Fetch cached AI predictions (generated automatically after scrapes)
        const predictions = await Predictions.getAIPrediction();
        
        if (predictions.error) {
            // No cached prediction available
            strategyExplanation.innerHTML = 
                `<span style="color: var(--accent-orange);">⚠️ No AI prediction available yet</span><br>` +
                `<span style="font-size: 0.8em; color: var(--text-muted);">AI predictions are generated automatically after each draw scrape to conserve API tokens.</span>`;
            return;
        }
        
        // Display cached prediction
        if (App.currentGame === 'toto' && predictions.toto) {
            displayAIPrediction(predictions.toto);
        } else if (App.currentGame === '4d' && predictions['4d']) {
            displayAI4DPrediction(predictions['4d']);
        } else {
            strategyExplanation.innerHTML = 
                `<span style="color: var(--accent-orange);">⚠️ No ${App.currentGame.toUpperCase()} prediction available</span><br>` +
                `<span style="font-size: 0.8em; color: var(--text-muted);">Predictions are generated after each new draw is scraped.</span>`;
        }
    } catch (error) {
        console.error('AI Prediction error:', error);
        strategyExplanation.textContent = '⚠️ Failed to load AI prediction';
    }
}

function displayAIPrediction(prediction) {
    // Handle new multi-set format
    const predictions = prediction.predictions || [];
    const analysisSummary = prediction.analysis_summary || 'AI-powered pattern analysis';
    const generatedAt = prediction.generated_at ? new Date(prediction.generated_at).toLocaleString() : '';
    
    // If old single-prediction format, convert to array
    if (predictions.length === 0 && prediction.main_numbers) {
        predictions.push({
            main_numbers: prediction.main_numbers,
            additional_number: prediction.additional_number,
            confidence: prediction.confidence || 'medium',
            reasoning: prediction.reasoning
        });
    }
    
    if (predictions.length === 0) {
        document.getElementById('strategyExplanation').innerHTML = 
            `<span style="color: var(--accent-orange);">⚠️ No TOTO prediction available</span>`;
        return;
    }
    
    // Display first (highest confidence) set in the balls
    const firstSet = predictions[0];
    const container = document.getElementById('predictedNumbers');
    const balls = container.querySelectorAll('.lottery-ball:not(.lottery-ball--additional)');
    
    balls.forEach((ball, i) => {
        if (i < firstSet.main_numbers.length) {
            ball.style.transform = 'scale(0)';
            setTimeout(() => {
                ball.textContent = firstSet.main_numbers[i];
                ball.style.transform = 'scale(1)';
            }, i * 100);
        }
    });
    
    // Show additional number
    setTimeout(() => {
        const additionalBall = document.getElementById('additionalBall');
        if (additionalBall && firstSet.additional_number) {
            additionalBall.textContent = `+${firstSet.additional_number}`;
            additionalBall.style.display = 'inline-flex';
        }
    }, 600);
    
    // Build all 4 predictions display
    const confidenceColors = {
        'high': '#10b981',
        'medium': '#f59e0b', 
        'low': '#ef4444',
        'speculative': '#8b5cf6'
    };
    
    const confidenceEmoji = {
        'high': '🟢',
        'medium': '🟡',
        'low': '🔴',
        'speculative': '🔮'
    };
    
    let allSetsHtml = `<div style="margin-top: 1rem;">
        <strong style="color: #8b5cf6;">🤖 AI TOTO Predictions</strong>
        <span style="font-size: 0.75rem; color: var(--text-muted); margin-left: 0.5rem;">Generated: ${generatedAt}</span>
    </div>`;
    
    predictions.forEach((set, i) => {
        const conf = set.confidence || 'medium';
        const nums = set.main_numbers.join(', ');
        const add = set.additional_number;
        
        allSetsHtml += `
        <div style="margin-top: 0.75rem; padding: 0.75rem; background: var(--surface-glass); border-radius: 8px; border-left: 3px solid ${confidenceColors[conf]};">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
                <span>${confidenceEmoji[conf]}</span>
                <strong style="color: ${confidenceColors[conf]}; text-transform: uppercase; font-size: 0.75rem;">${conf}</strong>
            </div>
            <div style="font-family: var(--font-mono); font-size: 0.9rem; color: var(--text-primary);">
                ${nums} <span style="color: var(--accent-gold);">+${add}</span>
            </div>
            <div style="font-size: 0.7rem; color: var(--text-muted); margin-top: 0.25rem;">${set.reasoning || ''}</div>
        </div>`;
    });
    
    allSetsHtml += `<div style="margin-top: 0.75rem; font-size: 0.75rem; color: var(--text-muted); font-style: italic;">${analysisSummary}</div>`;
    
    document.getElementById('strategyExplanation').innerHTML = allSetsHtml;
}

function displayAI4DPrediction(prediction) {
    const predictions = prediction.predictions || [];
    const analysisSummary = prediction.analysis_summary || 'AI-powered pattern analysis';
    const generatedAt = prediction.generated_at ? new Date(prediction.generated_at).toLocaleString() : '';
    
    if (predictions.length === 0) {
        document.getElementById('strategyExplanation').textContent = '⚠️ No 4D predictions available';
        return;
    }
    
    // Display first (highest confidence) prediction in the balls
    const firstPrediction = predictions[0];
    const number = firstPrediction.number || '????';
    
    const container = document.getElementById('predictedNumbers');
    const balls = container.querySelectorAll('.lottery-ball:not(.lottery-ball--additional)');
    
    balls.forEach((ball, i) => {
        if (i < 4) {
            ball.style.transform = 'scale(0)';
            setTimeout(() => {
                ball.textContent = number[i] || '?';
                ball.style.transform = 'scale(1)';
            }, i * 100);
        }
    });
    
    // Build all 4 predictions display
    const confidenceColors = {
        'high': '#10b981',
        'medium': '#f59e0b', 
        'low': '#ef4444',
        'speculative': '#8b5cf6'
    };
    
    const confidenceEmoji = {
        'high': '🟢',
        'medium': '🟡',
        'low': '🔴',
        'speculative': '🔮'
    };
    
    let allSetsHtml = `<div style="margin-top: 1rem;">
        <strong style="color: #8b5cf6;">🤖 AI 4D Predictions</strong>
        <span style="font-size: 0.75rem; color: var(--text-muted); margin-left: 0.5rem;">Generated: ${generatedAt}</span>
    </div>`;
    
    predictions.forEach((pred, i) => {
        const conf = pred.confidence || 'medium';
        const num = pred.number;
        
        allSetsHtml += `
        <div style="margin-top: 0.75rem; padding: 0.75rem; background: var(--surface-glass); border-radius: 8px; border-left: 3px solid ${confidenceColors[conf]};">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
                <span>${confidenceEmoji[conf]}</span>
                <strong style="color: ${confidenceColors[conf]}; text-transform: uppercase; font-size: 0.75rem;">${conf}</strong>
            </div>
            <div style="font-family: var(--font-mono); font-size: 1.25rem; color: var(--accent-gold); font-weight: bold;">
                ${num}
            </div>
            <div style="font-size: 0.7rem; color: var(--text-muted); margin-top: 0.25rem;">${pred.reasoning || ''}</div>
        </div>`;
    });
    
    allSetsHtml += `<div style="margin-top: 0.75rem; font-size: 0.75rem; color: var(--text-muted); font-style: italic;">${analysisSummary}</div>`;
    
    document.getElementById('strategyExplanation').innerHTML = allSetsHtml;
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});

// Export
window.App = App;
