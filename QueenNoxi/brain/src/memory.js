const StorageAdapter = require('./storage');

class UserMemory {
    constructor(dbPath) {
        this.storage = new StorageAdapter(dbPath, 'users');
        this.users = {};
    }

    async init() {
        await this.storage.init();
        this.users = await this.storage.loadAll();
    }

    async save() {
        await this.storage.saveAll(this.users);
    }

    /**
     * Get a user's memory object. Creates one if it doesn't exist.
     * @param {string} userId 
     */
    getUser(userId) {
        if (!this.users[userId]) {
            this.users[userId] = {
                id: userId,
                name: null,
                age: null,
                location: null,
                job: null,
                gender: null,
                nickname: null,
                facts: {},         // Free-form key-value facts
                history: [],       // Last N messages
                lastSeen: null,
                seenCount: 0
            };
        } else {
            // Safety check for legacy or malformed files
            if (!this.users[userId].facts) this.users[userId].facts = {};
            if (!this.users[userId].history) this.users[userId].history = [];
        }
        return this.users[userId];
    }

    /**
     * Set a specific field on a user
     */
    async setUserData(userId, field, value) {
        const user = this.getUser(userId);
        user[field] = value;
        await this.save();
    }

    /**
     * Set a free-form fact about a user
     */
    async setFact(userId, key, value) {
        const user = this.getUser(userId);
        user.facts[key] = value;
        await this.save();
    }

    /**
     * Get a fact about a user
     */
    getFact(userId, key) {
        const user = this.getUser(userId);
        return user.facts[key] || null;
    }

    /**
     * Record a message in the user's history (keep last 30)
     */
    async addHistory(userId, text, from = 'user') {
        const user = this.getUser(userId);
        user.history.push({ text, from, ts: Date.now() });
        if (user.history.length > 30) user.history.shift();
        user.lastSeen = Date.now();
        user.seenCount = (user.seenCount || 0) + 1;
        await this.save();
    }

    /**
     * Auto-extract user info from message text (name, location, job, age)
     * Returns any fields that were updated
     */
    extractFromMessage(userId, text) {
        const lower = text.toLowerCase().trim();
        const extracted = {};

        // BLACKLIST: common Singlish words that look like a "match" but are NOT names/locations
        const blacklistNames = new Set(['mama', 'machan', 'godak', 'poddak', 'hodai', 'supa', 'maru', 'ada',
            'kalin', 'dan', 'eka', 'api', 'ado', 'ayye', 'aiyo', 'ekath', 'kohomada', 'tani', 'ganna',
            'karanna', 'kiyanna', 'ne', 'da', 'ba', 'ok', 'lol', 'haha', 'bye', 'hi', 'hai', 'hello',
            'sorry', 'thanks', 'library', 'school', 'office', 'bus', 'train', 'gedara', 'weda', 'giia',
            'apahu', 'pass', 'fail', 'suba', 'subha', 'aiya', 'akka', 'nangi', 'malli', 'amma', 'thaththa']);

        // Name: ONLY on explicit "my name is X" or "mage nama X" (not bare "mama X")
        const nameMatch = lower.match(/(?:my name is|mage nama|namayi)\s+([a-z]{2,20})(?:\s|$|,|\.)/i);
        if (nameMatch && !blacklistNames.has(nameMatch[1].toLowerCase())) {
            const name = this._capitalize(nameMatch[1]);
            this.setUserData(userId, 'name', name); // Note: this is async but we don't await here to keep it non-blocking in NLU
            extracted.name = name;
        }

        // Age: "mage wayasa 22", "age 22", "i am 22 years"
        const ageMatch = lower.match(/(?:mage wayasa|wayasa|age)\s+(\d{1,3})/i)
            || lower.match(/i(?:'| a)m (\d{1,3})\s*y/i);
        if (ageMatch) {
            const age = parseInt(ageMatch[1]);
            if (age > 5 && age < 100) {
                this.setUserData(userId, 'age', age); // Background save
                extracted.age = age;
            }
        }

        // Location: explicit "i live in X", "stay in X" — NOT bare "inne"
        const locMatch = lower.match(/(?:i live in|stay in|wasi)\s+([a-z]{3,20})(?:\s|$|,)/i);
        if (locMatch && !blacklistNames.has(locMatch[1].toLowerCase())) {
            const loc = this._capitalize(locMatch[1].trim());
            this.setUserData(userId, 'location', loc); // Background save
            extracted.location = loc;
        }

        // Job: "i work as X", "weda karanne X", "i am a X"
        const jobMatch = lower.match(/(?:i work as|weda karanne|i'm a|i am a)\s+([a-z\s]{3,30})(?:\s|$|,|\.)/i);
        if (jobMatch) {
            const job = this._capitalize(jobMatch[1].trim());
            this.setUserData(userId, 'job', job); // Background save
            extracted.job = job;
        }

        // Favorites: "my favorite X is Y", "mama kemati X walata"
        // Improved regex with non-greedy match for the 'thing'
        const favMatch = lower.match(/(?:my favorite|mama kamati|mama kemati)\s+([a-z\s]{2,20}?)\s+(?:is|kata|walata)\s+([a-z\s]{2,20})/i);
        if (favMatch) {
            const thing = favMatch[1].trim().replace(/\s+/g, '_');
            const value = favMatch[2].trim();
            this.setFact(userId, `favorite_${thing}`, value);
            extracted[`favorite_${thing}`] = value;
        }

        // Likes: "I like X", "mama X walata kamati"
        const likeMatch = lower.match(/(?:i like|mama)\s+([a-z\s]{2,20})\s+(?:kamathi|kemati|like)/i)
            || lower.match(/(?:i like)\s+([a-z\s]{2,20})/i);
        if (likeMatch && !blacklistNames.has(likeMatch[1].trim())) {
            const like = likeMatch[1].trim();
            this.setFact(userId, `likes_${like.replace(/\s+/g, '_')}`, true);
            extracted.likes = like;
        }

        return extracted;
    }

    _capitalize(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    /**
     * Compose a greeting using remembered data
     */
    greet(userId) {
        const user = this.getUser(userId);
        if (user.name) {
            const greetings = [
                `${user.name} machan, kohomada?`,
                `Aiyo ${user.name}, ata ne?`,
                `${user.name}! Oya thiyanawada?`,
                `Oya ${user.name} ne! Kohomada?`
            ];
            return greetings[Math.floor(Math.random() * greetings.length)];
        }
        return null;
    }

    /**
     * Check if the user is asking the bot about what it knows of them
     */
    memoryQuery(userId, text) {
        const lower = text.toLowerCase();
        const user = this.getUser(userId);
        if (!user) return null;

        if (lower.match(/mage nama|my name|oya thiyanawd|do you know me|oyata mata danne|mama gana|about me/)) {
            const parts = [];
            if (user.name) parts.push(`Oba ${user.name}.`);
            if (user.age) parts.push(`Wayasa ${user.age}.`);
            if (user.location) parts.push(`${user.location} wala inne.`);
            if (user.job) parts.push(`${user.job} kenek.`);

            // Add facts/favorites
            const favs = Object.keys(user.facts).filter(k => k.startsWith('favorite_'));
            if (favs.length) {
                const f = favs[0];
                parts.push(`${f.replace('favorite_', '').replace('_', ' ')} eka ${user.facts[f]}.`);
            }

            if (parts.length) return parts.join(' ');
        }
        return null;
    }
}

module.exports = UserMemory;
