/**
 * API Module
 * Handles data loading and communication with backend
 * Version: 1.1.0
 */

const API = {
    // Configuration
    baseUrl: '', // Relative path for production
    demoMode: false, // Will auto-switch to demo if backend unreachable
    
    // Check if backend is available
    async checkBackend() {
        try {
            const response = await fetch(`${this.baseUrl}/api/health`, { 
                method: 'GET',
                mode: 'cors'
            });
            return response.ok;
        } catch (e) {
            return false;
        }
    },
    
    // Load data from backend or fallback to demo
    async loadData() {
        const backendAvailable = await this.checkBackend();
        
        if (backendAvailable) {
            this.demoMode = false;
            try {
                const response = await fetch(`${this.baseUrl}/api/data`);
                const data = await response.json();
                console.log('✅ Loaded real data from backend');
                return data;
            } catch (e) {
                console.warn('Backend error, falling back to demo:', e);
            }
        }
        
        // Fallback to demo data
        this.demoMode = true;
        console.log('📊 Using demo data (backend not available)');
        return {
            toto: this.generateDemoTotoDraws(150),
            fourD: this.generateDemo4DDraws(150),
        };
    },
    
    // Load Toto analysis from backend
    async loadTotoAnalysis() {
        if (this.demoMode) return null;
        
        try {
            const response = await fetch(`${this.baseUrl}/api/analysis/toto`);
            return await response.json();
        } catch (e) {
            console.error('Failed to load Toto analysis:', e);
            return null;
        }
    },
    
    // Load 4D analysis from backend
    async load4DAnalysis() {
        if (this.demoMode) return null;
        
        try {
            const response = await fetch(`${this.baseUrl}/api/analysis/4d`);
            return await response.json();
        } catch (e) {
            console.error('Failed to load 4D analysis:', e);
            return null;
        }
    },
    
    // Generate demo Toto data
    generateDemoTotoDraws(count = 100) {
        const draws = [];
        const startDate = new Date(); // Current date
        
        for (let i = 0; i < count; i++) {
            const date = new Date(startDate);
            date.setDate(date.getDate() - (i * 3)); // Draws every 3 days backwards
            
            // Generate 6 random numbers (1-49)
            const numbers = [];
            while (numbers.length < 6) {
                const num = Math.floor(Math.random() * 49) + 1;
                if (!numbers.includes(num)) {
                    numbers.push(num);
                }
            }
            numbers.sort((a, b) => a - b);
            
            // Additional number
            let additional;
            do {
                additional = Math.floor(Math.random() * 49) + 1;
            } while (numbers.includes(additional));
            
            draws.push({
                draw_number: String(4200 + count - i),
                draw_date: date.toISOString().split('T')[0],
                winning_numbers: numbers,
                additional_number: additional,
                is_demo: true, // Flag for demo data
            });
        }
        
        return draws;
    },
    
    // Generate demo 4D data
    generateDemo4DDraws(count = 100) {
        const draws = [];
        const startDate = new Date(); // Current date
        
        for (let i = 0; i < count; i++) {
            const date = new Date(startDate);
            date.setDate(date.getDate() - (i * 3));
            
            const generate4D = () => String(Math.floor(Math.random() * 10000)).padStart(4, '0');
            
            draws.push({
                draw_number: String(3700 + count - i),
                draw_date: date.toISOString().split('T')[0],
                first_prize: generate4D(),
                second_prize: generate4D(),
                third_prize: generate4D(),
                starters: Array(10).fill(0).map(() => generate4D()),
                consolation: Array(10).fill(0).map(() => generate4D()),
                is_demo: true,
            });
        }
        
        return draws;
    },
    
    
    // Load data (demo mode or from backend)
    async loadData() {
        if (this.demoMode) {
            return {
                toto: this.generateDemoTotoDraws(150),
                fourD: this.generateDemo4DDraws(150),
            };
        }
        
        // Real backend call would go here
        try {
            const response = await fetch('/api/data');
            return await response.json();
        } catch (error) {
            console.error('Failed to load data:', error);
            return null;
        }
    },
    
    // Analyze frequency
    analyzeFrequency(draws, gameType = 'toto') {
        if (gameType === 'toto') {
            return this.analyzeTotoFrequency(draws);
        }
        return this.analyze4DFrequency(draws);
    },
    
    analyzeTotoFrequency(draws) {
        const frequency = {};
        for (let i = 1; i <= 49; i++) {
            frequency[i] = 0;
        }
        
        draws.forEach(draw => {
            draw.winning_numbers.forEach(num => {
                frequency[num]++;
            });
        });
        
        const totalDrawn = draws.length * 6;
        const expected = totalDrawn / 49;
        
        // Calculate raw deviations and find max for normalization
        const rawDeviations = {};
        let maxAbsDeviation = 0;
        Object.entries(frequency).forEach(([num, count]) => {
            const deviation = (count - expected) / expected;
            rawDeviations[num] = deviation;
            maxAbsDeviation = Math.max(maxAbsDeviation, Math.abs(deviation));
        });
        
        // Normalize deviations to -1 to 1 range and classify
        const classification = {};
        const deviations = {};
        Object.entries(rawDeviations).forEach(([num, rawDev]) => {
            // Normalize to -1 to 1 (cold to hot)
            deviations[num] = maxAbsDeviation > 0 ? rawDev / maxAbsDeviation : 0;
            
            // Keep classification for backwards compatibility
            if (rawDev > 0.2) classification[num] = 'hot';
            else if (rawDev < -0.2) classification[num] = 'cold';
            else classification[num] = 'normal';
        });
        
        return {
            frequency,
            classification,
            deviations, // Normalized -1 to 1 for gradient heatmap
            expected,
            hotNumbers: Object.entries(classification)
                .filter(([_, cls]) => cls === 'hot')
                .map(([num]) => parseInt(num)),
            coldNumbers: Object.entries(classification)
                .filter(([_, cls]) => cls === 'cold')
                .map(([num]) => parseInt(num)),
        };
    },
    
    analyze4DFrequency(draws) {
        const positionFreq = {
            thousands: {},
            hundreds: {},
            tens: {},
            units: {},
        };
        
        for (let d = 0; d <= 9; d++) {
            Object.keys(positionFreq).forEach(pos => {
                positionFreq[pos][d] = 0;
            });
        }
        
        draws.forEach(draw => {
            ['first_prize', 'second_prize', 'third_prize'].forEach(prize => {
                const num = draw[prize];
                if (num && num.length === 4) {
                    positionFreq.thousands[num[0]]++;
                    positionFreq.hundreds[num[1]]++;
                    positionFreq.tens[num[2]]++;
                    positionFreq.units[num[3]]++;
                }
            });
        });
        
        return { positionFreq };
    },
    
    // Analyze gaps
    analyzeGaps(draws) {
        const lastSeen = {};
        
        draws.forEach((draw, i) => {
            draw.winning_numbers.forEach(num => {
                if (!(num in lastSeen)) {
                    lastSeen[num] = i;
                }
            });
        });
        
        const gaps = {};
        for (let i = 1; i <= 49; i++) {
            gaps[i] = i in lastSeen ? lastSeen[i] : draws.length;
        }
        
        const sorted = Object.entries(gaps)
            .sort((a, b) => b[1] - a[1])
            .map(([num, gap]) => ({ number: parseInt(num), gap }));
        
        return {
            gaps,
            mostOverdue: sorted.slice(0, 10),
            expectedGap: 49 / 6,
        };
    },
};

// Export for use in other modules
window.API = API;
