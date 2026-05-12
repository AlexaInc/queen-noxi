const fs = require('fs');
const path = require('path');

/**
 * StorageAdapter provides a unified interface for local JSON and MongoDB.
 * For local 'users' context, it saves individual files per user.
 */
class StorageAdapter {
    /**
     * @param {string} connectionStr - Local path (file or dir) or MongoDB URI
     * @param {string} context - 'users' | 'brain' | 'common'
     */
    constructor(connectionStr, context = 'common') {
        this.connectionStr = connectionStr;
        this.context = context;
        this.isMongo = connectionStr.startsWith('mongodb');
        this.client = null;
        this.db = null;
    }

    async init() {
        if (this.isMongo) {
            try {
                const { MongoClient } = require('mongodb');
                this.client = new MongoClient(this.connectionStr);
                await this.client.connect();
                this.db = this.client.db();
                console.log(`📡 Storage: Connected to MongoDB [${this.context}]`);
            } catch (e) {
                console.error(`❌ Storage: Failed to connect to MongoDB. Falling back to local storage.`);
                this.isMongo = false;
            }
        } else if (this.context === 'users') {
            // Local Users should use a directory
            if (!fs.existsSync(this.connectionStr)) {
                fs.mkdirSync(this.connectionStr, { recursive: true });
            }
        }
        return this;
    }

    /**
     * Load all data for this context
     */
    async loadAll() {
        if (this.isMongo && this.db) {
            const collection = this.db.collection(this.context);
            if (this.context === 'users') {
                const results = await collection.find({}).toArray();
                const out = {};
                results.forEach(r => {
                    const { _id, ...data } = r;
                    out[_id] = data;
                });
                return out;
            } else {
                const doc = await collection.findOne({ _id: 'master' });
                return doc ? doc.data : {};
            }
        } else {
            // Local FS
            if (this.context === 'users') {
                const dir = this.connectionStr;
                if (!fs.existsSync(dir)) return {};
                const files = fs.readdirSync(dir).filter(f => f.endsWith('.json'));
                const out = {};
                files.forEach(f => {
                    try {
                        const content = fs.readFileSync(path.join(dir, f), 'utf8');
                        out[f.replace('.json', '')] = JSON.parse(content);
                    } catch (e) { }
                });
                return out;
            } else {
                try {
                    if (fs.existsSync(this.connectionStr)) {
                        return JSON.parse(fs.readFileSync(this.connectionStr, 'utf8'));
                    }
                } catch (e) { }
                return {};
            }
        }
    }

    /**
     * Save all data (Bulk)
     */
    async saveAll(data) {
        if (this.isMongo && this.db) {
            const collection = this.db.collection(this.context);
            if (this.context === 'users') {
                for (const userId in data) {
                    await collection.updateOne({ _id: userId }, { $set: data[userId] }, { upsert: true });
                }
            } else {
                await collection.updateOne({ _id: 'master' }, { $set: { data, updatedAt: Date.now() } }, { upsert: true });
            }
        } else {
            if (this.context === 'users') {
                const dir = this.connectionStr;
                if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
                for (const userId in data) {
                    const filePath = path.join(dir, `${userId}.json`);
                    fs.writeFileSync(filePath, JSON.stringify(data[userId], null, 2), 'utf8');
                }
            } else {
                const dir = path.dirname(this.connectionStr);
                if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
                fs.writeFileSync(this.connectionStr, JSON.stringify(data, null, 2), 'utf8');
            }
        }
    }

    /**
     * Save a single item (highly optimized for users context)
     */
    async saveItem(id, itemData) {
        if (this.isMongo && this.db) {
            const collection = this.db.collection(this.context);
            await collection.updateOne({ _id: id }, { $set: itemData }, { upsert: true });
        } else {
            if (this.context === 'users') {
                const dir = this.connectionStr;
                const filePath = path.join(dir, `${id}.json`);
                fs.writeFileSync(filePath, JSON.stringify(itemData, null, 2), 'utf8');
            } else {
                const all = await this.loadAll();
                all[id] = itemData;
                await this.saveAll(all);
            }
        }
    }
}

module.exports = StorageAdapter;
