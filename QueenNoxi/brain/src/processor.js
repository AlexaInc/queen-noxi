const fs = require('fs');
const path = require('path');

class LanguageProcessor {
    constructor() {
        this.slang = {};
        this.phoneticMap = {}; // Custom word mappings (sinhala script -> singlish)
        this.loadSlang();
        this.loadPhoneticMap();
        this.initTransliteration();
    }

    loadSlang() {
        try {
            const slangPath = path.join(__dirname, '..', 'data', 'slang.json');
            if (fs.existsSync(slangPath)) {
                this.slang = JSON.parse(fs.readFileSync(slangPath, 'utf8'));
            }
        } catch (e) { }
    }

    loadPhoneticMap() {
        try {
            const mapPath = path.join(__dirname, '..', 'data', 'phonetic_map.json');
            if (fs.existsSync(mapPath)) {
                this.phoneticMap = JSON.parse(fs.readFileSync(mapPath, 'utf8'));
            }
        } catch (e) { }
    }

    savePhoneticMap() {
        try {
            const mapPath = path.join(__dirname, '..', 'data', 'phonetic_map.json');
            const dir = path.dirname(mapPath);
            if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
            fs.writeFileSync(mapPath, JSON.stringify(this.phoneticMap, null, 2), 'utf8');
        } catch (e) {
            console.error('Error saving phonetic map:', e);
        }
    }

    initTransliteration() {
        this.vowels = {
            'අ': 'a', 'ආ': 'aa', 'ඇ': 'ae', 'ඈ': 'aee', 'ඉ': 'i', 'ඊ': 'ii',
            'උ': 'u', 'ඌ': 'uu', 'එ': 'e', 'ඒ': 'ee', 'ඔ': 'o', 'ඕ': 'oo',
            'ඓ': 'ai', 'ඖ': 'au'
        };
        this.consonants = {
            'ක': 'k', 'ඛ': 'kh', 'ග': 'g', 'ඝ': 'gh', 'ඞ': 'ng', 'ඟ': 'ng',
            'ච': 'c', 'ඡ': 'ch', 'ජ': 'j', 'ඣ': 'jh', 'ඤ': 'ny', 'ඥ': 'gn',
            'ට': 't', 'ඨ': 'th', 'ඩ': 'd', 'ඪ': 'dh', 'ණ': 'n', 'ඬ': 'nd',
            'ත': 't', 'ථ': 'th', 'ද': 'd', 'ධ': 'dh', 'න': 'n', 'ඳ': 'nd',
            'ප': 'p', 'ඵ': 'ph', 'බ': 'b', 'භ': 'bh', 'ම': 'm', 'ඹ': 'mb',
            'ය': 'y', 'ර': 'r', 'ල': 'l', 'ව': 'v', 'ශ': 'sh', 'ෂ': 'sh',
            'ස': 's', 'හ': 'h', 'ළ': 'l', 'ෆ': 'f'
        };
        this.pilli = {
            '්': '', 'ා': 'aa', 'ැ': 'ae', 'ෑ': 'aee', 'ි': 'i', 'ී': 'ii',
            'ු': 'u', 'ූ': 'uu', 'ෘ': 'ru', 'ෙ': 'e', 'ේ': 'ee', 'ෛ': 'ai',
            'ො': 'o', 'ෝ': 'oo', 'ෞ': 'au', 'ං': 'n'
        };
    }

    sinhalaToSinglish(text) {
        let result = '';
        for (let i = 0; i < text.length; i++) {
            const char = text[i];

            if (this.vowels[char]) {
                result += this.vowels[char];
            } else if (this.consonants[char]) {
                let next = text[i + 1];
                let singlish = this.consonants[char];
                if (next && this.pilli[next] !== undefined) {
                    singlish += this.pilli[next];
                    i++; // skip pilla
                } else {
                    singlish += 'a'; // inherent vowel
                }
                result += singlish;
            } else {
                result += char;
            }
        }
        return result;
    }

    /**
     * Normalizes text for matching.
     * Handles mixed Sinhala/Singlish, slang expansion, and phonetic cleanup.
     */
    process(text) {
        if (!text) return '';

        // 1. Convert Sinhala script to Singlish (using map if available)
        const words = text.split(/\s+/);
        const processedWords = words.map(word => {
            // Handle phonetic map (Sinhala -> Singlish)
            if (this.phoneticMap[word]) return this.phoneticMap[word];

            // Handle rule-based translit
            return this.sinhalaToSinglish(word);
        });

        let processed = processedWords.join(' ').toLowerCase().trim();

        // 2. Expand common slang (Singlish -> Real Concept)
        const finalWords = processed.split(/\s+/);
        processed = finalWords.map(word => this.slang[word] || word).join(' ');

        // 3. Simple phonetic normalization
        processed = this.normalizePhonetics(processed);

        return processed;
    }

    normalizePhonetics(text) {
        return text
            .replace(/sh/g, 's')
            .replace(/th/g, 't')
            .replace(/dh/g, 'd')
            .replace(/aa/g, 'a')
            .replace(/ee/g, 'i')
            .replace(/oo/g, 'u')
            .replace(/y/g, 'i')
            .replace(/w/g, 'v')
            .replace(/([a-z])\1+/g, '$1') // remove double letters
            .replace(/[^a-z0-9\s]/g, ''); // remove non-alphanumeric
    }

    /**
     * Calculates similarity between two strings (Levenshtein Distance)
     */
    calculateSimilarity(s1, s2) {
        if (s1 === s2) return 1.0;

        const len1 = s1.length;
        const len2 = s2.length;
        if (len1 === 0) return 0.0;
        if (len2 === 0) return 0.0;

        const matrix = [];
        for (let i = 0; i <= len1; i++) matrix[i] = [i];
        for (let j = 0; j <= len2; j++) matrix[0][j] = j;

        for (let i = 1; i <= len1; i++) {
            for (let j = 1; j <= len2; j++) {
                const cost = s1[i - 1] === s2[j - 1] ? 0 : 1;
                matrix[i][j] = Math.min(
                    matrix[i - 1][j] + 1,
                    matrix[i][j - 1] + 1,
                    matrix[i - 1][j - 1] + cost
                );
            }
        }

        const distance = matrix[len1][len2];
        return 1.0 - (distance / Math.max(len1, len2));
    }
}

module.exports = new LanguageProcessor();
