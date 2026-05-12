const fs = require('fs');
const path = require('path');
const processor = require('./processor');

class Brain {
    constructor() {
        this.memory = {};
        this.persona = {};
        this.loadData();
    }

    loadData() {
        try {
            const brainPath = path.join(__dirname, '..', 'data', 'brain.json');
            if (fs.existsSync(brainPath)) this.memory = JSON.parse(fs.readFileSync(brainPath, 'utf8'));

            const personaPath = path.join(__dirname, '..', 'data', 'persona.json');
            if (fs.existsSync(personaPath)) this.persona = JSON.parse(fs.readFileSync(personaPath, 'utf8'));
        } catch (e) { console.error('Error loading brain data:', e); }
    }

    saveData() {
        try {
            const brainPath = path.join(__dirname, '..', 'data', 'brain.json');
            fs.writeFileSync(brainPath, JSON.stringify(this.memory, null, 2));
        } catch (e) { console.error('Error saving brain data:', e); }
    }

    setPersona(data) {
        this.persona = { ...this.persona, ...data };
    }

    /**
     * Core respond logic. Accepts optional context (userId, userMemory, groupSession)
     */
    respond(inputText, context = {}) {
        const processedInput = processor.process(inputText);
        if (!processedInput) return this.getFallback();

        // 1. Direct match
        if (this.memory[processedInput]) {
            return this.fillTemplate(this.pickResponse(this.memory[processedInput]), context);
        }

        // 2. Persona questions (Identity should take precedence over fuzzy chat)
        const personaResp = this.checkPersonaQuestions(processedInput, inputText);
        if (personaResp) return this.fillTemplate(personaResp, context);

        // 3. Fuzzy match
        let bestMatch = null;
        let highestScore = 0;
        for (const [pattern, data] of Object.entries(this.memory)) {
            const score = processor.calculateSimilarity(processedInput, pattern);
            if (score > highestScore && score > 0.65) {
                highestScore = score;
                bestMatch = data;
            }
        }
        if (bestMatch) {
            return this.fillTemplate(this.pickResponse(bestMatch), context);
        }

        return this.getFallback();
    }

    pickResponse(data) {
        const style = this.persona.style || 'chill';
        const pool = data[style] || data['chill'] || data['default'] || data;
        if (Array.isArray(pool)) return pool[Math.floor(Math.random() * pool.length)];
        return String(pool);
    }

    /**
     * Fill {name}, {job}, {birthday}, {age}, {residence}, {user_name} etc.
     */
    fillTemplate(text, context = {}) {
        if (!text) return this.getFallback();
        const p = this.persona;
        const u = context.user || {};
        const now = new Date();
        const birthYear = p.birthday ? new Date(p.birthday).getFullYear() : null;

        return text
            .replace(/\{name\}/g, p.name || 'Kasun')
            .replace(/\{birthday\}/g, p.birthday || '?')
            .replace(/\{job\}/g, p.job || 'web dev')
            .replace(/\{residence\}/g, p.residence || 'Colombo')
            .replace(/\{age\}/g, birthYear ? (now.getFullYear() - birthYear) : '?')
            .replace(/\{user_name\}/g, u.name || 'machan')
            .replace(/\{user_location\}/g, u.location || 'koheda?')
            .replace(/\{user_job\}/g, u.job || '?');
    }

    checkPersonaQuestions(processedInput, rawInput = '') {
        const text = processedInput.toLowerCase();
        const raw = rawInput.toLowerCase();

        // Helper: check either raw or processed text
        const has = (...kws) => kws.some(k => text.includes(k) || raw.includes(k));

        // Priority order matters — check most specific first
        if (has('oyage gana', 'about you', 'introduce yourself', 'tell me about'))
            return 'mama {name}. {job} kenek. {residence} wala inne.';

        // Name — must have name-specific trigger word
        if (has('nama', 'name', 'kauda oya', 'oyage kauda', 'oyage nam', 'oyage name'))
            return 'mage nama {name} machan.';

        // Age / Birthday
        if (has('bday', 'birthday', 'ipaduna', 'wayasa', 'age'))
            return 'mama {age} wiye inne. bday eka {birthday}.';

        // Residence — must be explicit about location
        if (has('koheda inne', 'live in', 'koheda', 'residence', 'wasi'))
            return 'mama {residence} wala inne machan.';

        // Job — only if there's a clear job-asking keyword, NOT general "karanne"
        if (has('oyage job', 'what is your job', 'weda karanne mokakda', 'job eka', 'profession', 'oyage weda'))
            return 'mama {job} kenek machan.';

        return null;
    }

    getFallback() {
        const style = this.persona.style || 'chill';
        const fallbacks = (this.persona.fallbacks && this.persona.fallbacks[style])
            || (this.persona.fallbacks && this.persona.fallbacks['chill'])
            || ['moko kiyanne?', 'poddak hitapan', 'kiyanna aney'];
        return fallbacks[Math.floor(Math.random() * fallbacks.length)];
    }

    learn(input, response, shouldSave = true) {
        const processedInput = processor.process(input);
        if (!processedInput || !response) return;

        const style = this.persona.style || 'chill';
        if (!this.memory[processedInput]) {
            this.memory[processedInput] = {};
        }
        if (!this.memory[processedInput][style]) {
            this.memory[processedInput][style] = [];
        }
        if (!this.memory[processedInput][style].includes(response)) {
            this.memory[processedInput][style].push(response);
        }
        if (shouldSave) this.saveData();
    }
}

module.exports = new Brain();
