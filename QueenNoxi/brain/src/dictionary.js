const fs = require('fs');
const path = require('path');
const processor = require('./processor');

class Dictionary {
    constructor(dbPath) {
        this.dbPath = dbPath || path.join(__dirname, '..', 'data', 'dictionary.json');
        this.data = {};
        this.load();
    }

    load() {
        try {
            if (fs.existsSync(this.dbPath)) {
                this.data = JSON.parse(fs.readFileSync(this.dbPath, 'utf8'));
                // Create a separate index for normalized keys
                this.normalizedIndex = {};
                for (const key of Object.keys(this.data)) {
                    this.normalizedIndex[processor.process(key)] = key;
                }
            }
        } catch (e) {
            console.error('Dictionary load error:', e);
            this.data = {};
        }
    }

    /**
     * Look up a word in the dictionary.
     * Supports Sinhala script and Singlish (via internal normalization).
     */
    lookup(word) {
        if (!word) return null;

        const lower = word.toLowerCase().trim();
        const normalized = processor.process(word);

        // 1. Direct match (exact)
        if (this.data[lower]) return this.data[lower];
        if (this.data[normalized]) return this.data[normalized];

        // 2. Normalized index match (e.g. කොම්පියුටර් -> kompiutar -> computer)
        if (this.normalizedIndex[normalized]) {
            return this.data[this.normalizedIndex[normalized]];
        }

        // 3. Fuzzy search for similar words
        let bestMatch = null;
        let highestScore = 0;

        for (const [key, value] of Object.entries(this.data)) {
            const score = processor.calculateSimilarity(normalized, processor.process(key));
            if (score > highestScore && score > 0.8) {
                highestScore = score;
                bestMatch = value;
            }
        }

        return bestMatch;
    }

    /**
     * Check if the message is a "what is X" type question
     */
    isDictionaryQuery(text) {
        const lower = text.toLowerCase();
        // Common dictionary query patterns
        const patterns = [
            /mokakda (.*) kiyanne/i,
            /what is (.*)/i,
            /meaning of (.*)/i,
            /arthaya (.*)/i,
            /(.*) kiyanne mokakda/i,
            /(.*) meaning/i
        ];

        for (const pat of patterns) {
            const match = lower.match(pat);
            if (match) {
                // Clean punctuation from the extracted word
                return match[1].trim().replace(/[?!,.]$/, '');
            }
        }
        return null;
    }

    /**
     * Format a dictionary entry into a human-like response
     */
    formatResponse(word, entry) {
        if (!entry) return null;

        if (typeof entry === 'string') {
            return `"${word}" kiyanne: ${entry}`;
        }

        let resp = `"${word}" gana mama hoyala beluva... `;

        if (entry.sin) resp += `Sinhala: ${entry.sin}. `;
        if (entry.en) resp += `English: ${entry.en}. `;
        if (entry.def) resp += `Definition: ${entry.def}. `;
        if (entry.synonyms && entry.synonyms.length) {
            resp += `Synonyms: ${entry.synonyms.slice(0, 3).join(', ')}.`;
        }

        return resp;
    }
}

module.exports = Dictionary;
