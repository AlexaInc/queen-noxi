const UserMemory = require('./memory');
const StorageAdapter = require('./storage');
const path = require('path');

class GroupSession {
    constructor(options = {}) {
        this.groupId = options.groupId || 'default_group';
        this.memory = options.memory; // global UserMemory instance for user lookup
        this.members = new Set();
        this.recentMessages = [];
        this.maxHistory = options.maxHistory || 50;

        const storagePath = options.mongoUri || (options.usersDb ? path.join(options.usersDb, `${this.groupId}.json`) : path.join(process.cwd(), 'database', `${this.groupId}.json`));
        this.storage = new StorageAdapter(storagePath, 'groups');
    }

    async init() {
        await this.storage.init();
        const data = await this.storage.loadAll();
        this.recentMessages = data.history || [];
        if (data.members) this.members = new Set(data.members);
    }

    async save() {
        await this.storage.saveAll({
            groupId: this.groupId,
            members: [...this.members],
            history: this.recentMessages,
            lastUpdate: Date.now()
        });
    }

    /**
     * Register a member in this group
     */
    addMember(userId) {
        this.members.add(userId);
    }

    /**
     * Record a message in group context
     */
    async addMessage(userId, text, from = null) {
        this.addMember(userId);
        const sender = from || userId;
        const msg = { from: sender, text, ts: Date.now() };
        this.recentMessages.push(msg);
        if (this.recentMessages.length > this.maxHistory) {
            this.recentMessages.shift();
        }

        // Also update the global user memory if they are in this group
        if (this.memory && sender !== 'bot') {
            await this.memory.addHistory(sender, text, 'user');
        }

        await this.save();
        return msg;
    }

    /**
     * Get recent group conversation (last N messages)
     */
    getContext(n = 10) {
        return this.recentMessages.slice(-n);
    }

    /**
     * Check if a user was recently active in this group
     */
    isRecentlyActive(userId, withinMs = 300000) { // 5 min
        const now = Date.now();
        for (let i = this.recentMessages.length - 1; i >= 0; i--) {
            const m = this.recentMessages[i];
            if (m.userId === userId && now - m.ts < withinMs) return true;
        }
        return false;
    }

    /**
     * Get all members the bot has seen in this group
     */
    getMembers() {
        return [...this.members];
    }

    /**
     * Get the last message from a specific user
     */
    getLastMessageFrom(userId) {
        for (let i = this.recentMessages.length - 1; i >= 0; i--) {
            if (this.recentMessages[i].userId === userId) {
                return this.recentMessages[i];
            }
        }
        return null;
    }

    /**
     * Auto-train the brain from recent group messages
     * (pass in a brain instance)
     */
    autoTrainFromGroup(brain) {
        const msgs = this.recentMessages;
        for (let i = 0; i < msgs.length - 1; i++) {
            const curr = msgs[i];
            const next = msgs[i + 1];
            if (curr.userId !== next.userId) {
                brain.learn(curr.text, next.text);
            }
        }
    }
}

module.exports = GroupSession;
