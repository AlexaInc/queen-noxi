const brain = require('./src/brain');
const processor = require('./src/processor');
const UserMemory = require('./src/memory');
const GroupSession = require('./src/group');
const nlu = require('./src/nlu');
const ContextWindow = require('./src/context');
const Dictionary = require('./src/dictionary');
const path = require('path');

class SinhalaHumanoid {
    /**
     * @param {Object} options
     * @param {string}  options.style       - Chat style: 'chill' | 'professional' | 'sexy' | 'hot' | 'auto'
     * @param {string}  options.name        - Bot's name (e.g. 'Kasun')
     * @param {string}  options.birthday    - Bot's birthday (e.g. '1998-05-15')
     * @param {string}  options.residence   - Bot's home city (e.g. 'Colombo')
     * @param {string}  options.job         - Bot's job (e.g. 'Web Developer')
     * @param {string}  options.gender      - Bot's gender ('Male'|'Female'|'Other')
     * @param {string}  options.usersDb     - Path to users.json (optional)
     */
    constructor(options = {}) {
        const personaFields = {};
        if (options.name) personaFields.name = options.name;
        if (options.birthday) personaFields.birthday = options.birthday;
        if (options.residence) personaFields.residence = options.residence;
        if (options.job) personaFields.job = options.job;
        if (options.gender) personaFields.gender = options.gender;
        if (options.style) personaFields.style = options.style;
        if (options.persona) Object.assign(personaFields, options.persona);

        if (Object.keys(personaFields).length > 0) brain.setPersona(personaFields);

        this.autoStyle = (options.style === 'auto');

        // Priority: options.mongoUri -> process.env.CHATDB_URL -> options.usersDb -> default
        this.mongoUri = options.mongoUri || process.env.CHATDB_URL || null;
        this.usersDb = options.usersDb || path.join(process.cwd(), 'database');

        const memoryPath = this.mongoUri || this.usersDb;
        this.userMemory = new UserMemory(memoryPath);

        const dictPath = options.dictionaryDb || path.join(__dirname, 'data', 'dictionary.json');
        this.dictionary = new Dictionary(dictPath);

        this.groups = {};
        this.contexts = {};
    }


    async init() {
        await this.userMemory.init();
        return this;
    }

    _getContext(userId) {
        if (!this.contexts[userId]) this.contexts[userId] = new ContextWindow();
        return this.contexts[userId];
    }

    _buildResponse(message, userId, ctx) {
        const user = this.userMemory.getUser(userId);
        const analysis = nlu.analyze(message);
        ctx.addUserTurn(message, analysis);

        const style = this.autoStyle
            ? analysis.detectedStyle
            : ((brain.persona && brain.persona.style) || 'chill');

        const prevStyle = brain.persona.style;
        if (this.autoStyle) brain.setPersona({ style });

        const extracted = this.userMemory.extractFromMessage(userId, message);
        if (extracted.name) {
            const resp = `Suba na ${user.name}! Oyatama ingathin ganna.`;
            ctx.addBotTurn(resp);
            return resp;
        }

        const memQ = this.userMemory.memoryQuery(userId, message);
        if (memQ) { ctx.addBotTurn(memQ); return memQ; }

        const dictWord = this.dictionary.isDictionaryQuery(message);
        if (dictWord) {
            const entry = this.dictionary.lookup(dictWord);
            if (entry) {
                const resp = this.dictionary.formatResponse(dictWord, entry);
                if (resp) { ctx.addBotTurn(resp); return resp; }
            } else {
                const notFound = {
                    chill: `Aiyo sry machan, "${dictWord}" kiyana eka gana mama danne na. Aluth vacanayak da?`,
                    professional: `Sathutu wenawa kiyanna, habai "${dictWord}" kiyana vacanaya mage dictionary eke na.`,
                    sexy: `hmmm "${dictWord}"... eka amuthu vacanayak ne? mama danne na eka gana...`,
                    hot: `"${dictWord}"? eka gana passe kiyannam. dan kiyanna ba.`
                };
                const resp = notFound[style] || notFound['chill'];
                ctx.addBotTurn(resp);
                return resp;
            }
        }

        if (analysis.isGreeting && user.name) {
            const timeSinceSeen = user.lastSeen ? Date.now() - user.lastSeen : Infinity;
            if (timeSinceSeen > 5 * 60 * 1000) {
                const greet = this.userMemory.greet(userId);
                if (greet) { ctx.addBotTurn(greet); return greet; }
            }
        }

        if (analysis.isFarewell) {
            const byes = {
                chill: ['ok yanawa machan, hodatama yanawa', 'bye bye, posuwa enna', 'hodatama yanawa, bye!'],
                professional: ['Bye! Hoda dine ekak waewa.'],
                sexy: ['aww bye baby, miss karannawa', 'bye, jld ohh laa'],
                hot: ['ok bye, jld enna ha', 'missing already']
            };
            const pool = byes[style] || byes['chill'];
            const resp = pool[Math.floor(Math.random() * pool.length)];
            ctx.addBotTurn(resp);
            return resp;
        }

        const tonePrefix = nlu.toneReaction(analysis.tone);
        const parts = [];

        if (analysis.isLong) {
            for (const topic of analysis.topics.slice(0, 2)) {
                const topicResp = nlu.getTopicResponse(topic, style);
                if (topicResp) parts.push(topicResp);
            }
            if (!parts.length) {
                for (const sentence of analysis.sentences.slice(0, 2)) {
                    const r = brain.respond(sentence, { user });
                    if (r) parts.push(brain.fillTemplate(r, { user }));
                }
            }
        }

        if (!parts.length) {
            for (const sentence of analysis.sentences) {
                // 1. Brain match (most specific knowledge)
                const r = brain.respond(sentence, { user });
                if (r) {
                    parts.push(brain.fillTemplate(r, { user }));
                    break;
                }

                // 2. Fallback to general topics
                const topicHit = analysis.topics.find(t => nlu.getTopicResponse(t, style));
                if (topicHit) {
                    parts.push(nlu.getTopicResponse(topicHit, style));
                    break;
                }
            }
        }

        if (ctx.isAnsweringBotQuestion() && !analysis.isQuestion && parts.length) {
            const acks = ['ahh ok ok', 'oo arageina', 'ah supa', 'ok ok gotcha'];
            parts.unshift(acks[Math.floor(Math.random() * acks.length)]);
        }

        let finalParts = parts.filter(Boolean);
        if (tonePrefix && finalParts.length) {
            finalParts = [tonePrefix, ...finalParts];
        }

        if (!finalParts.length) {
            finalParts = [brain.getFallback()];
        }

        if (Math.random() < 0.4 && !analysis.isQuestion) {
            const followUps = {
                chill: ['ekath?', 'oya kohomada?', 'moko kiyanne?', 'oya thiyenawada?'],
                professional: ['Oba kohomada?', 'Meken help one da?'],
                sexy: ['oya mokada karanne tawa?', 'oya miss una neda?'],
                hot: ['oya kiyanne?', 'enna enna']
            };
            const pool = followUps[style] || followUps['chill'];
            finalParts.push(pool[Math.floor(Math.random() * pool.length)]);
        }

        const response = finalParts.join(' ');
        ctx.addBotTurn(response);
        if (this.autoStyle) brain.setPersona({ style: prevStyle });
        return response;
    }

    getResponse(message, userId = 'anon') {
        this.userMemory.addHistory(userId, message, 'user');
        const ctx = this._getContext(userId);
        const response = this._buildResponse(message, userId, ctx);
        this.userMemory.addHistory(userId, response, 'bot');
        return response;
    }

    async getGroupResponse(message, userId, groupId = 'default') {
        if (!this.groups[groupId]) {
            this.groups[groupId] = new GroupSession({
                groupId,
                memory: this.userMemory,
                mongoUri: this.mongoUri,
                usersDb: this.usersDb
            });
            await this.groups[groupId].init();
        }

        const group = this.groups[groupId];
        await group.addMessage(userId, message, userId);

        const memQuery = this.userMemory.memoryQuery(userId, message);
        if (memQuery) {
            await group.addMessage('bot', memQuery, 'bot');
            return memQuery;
        }

        this.userMemory.extractFromMessage(userId, message);

        const botName = (brain.persona && brain.persona.name) || 'Kasun';
        const analysis = nlu.analyze(message);
        const addressed = message.toLowerCase().includes(botName.toLowerCase())
            || message.toLowerCase().includes('bot')
            || analysis.isGreeting;
        const randomReply = Math.random() < 0.3;

        if (!addressed && !randomReply) return null;

        const ctx = this._getContext(`${groupId}:${userId}`);
        const user = this.userMemory.getUser(userId);
        const response = this._buildResponse(message, userId, ctx);

        await group.addMessage('bot', response, 'bot');
        return response;
    }

    /**
     * Permanent Learning: Add a new pattern to the brain and save to disk.
     */
    async learn(input, response, style = 'chill') {
        const prevStyle = (brain.persona && brain.persona.style) || 'chill';
        brain.setPersona({ style });
        brain.learn(input, response, true);
        brain.setPersona({ style: prevStyle });
        return true;
    }

    trainFromGroup(groupId) {
        const group = this.groups[groupId];
        if (group) group.autoTrainFromGroup(brain);
    }

    trainData(data, style) {
        const Trainer = require('./src/trainer');
        return Trainer.trainData(data, style);
    }

    autoTrain(history) {
        for (let i = 0; i < history.length - 1; i++) {
            const curr = history[i], next = history[i + 1];
            if (curr.sender !== next.sender) brain.learn(curr.text, next.text);
        }
    }

    setStyle(style) { brain.setPersona({ style }); }
    setPersona(details) { brain.setPersona(details); }
    getUser(userId) { return this.userMemory.getUser(userId); }
    setUserData(u, f, v) { this.userMemory.setUserData(u, f, v); }
    setUserFact(u, k, v) { this.userMemory.setFact(u, k, v); }
    getUserFact(u, k) { return this.userMemory.getFact(u, k); }
    resetContext(userId) { if (this.contexts[userId]) this.contexts[userId].reset(); }
    analyze(message) { return nlu.analyze(message); }
    detectLanguage(text) {
        return /[\u0D80-\u0DFF]/.test(text) ? 'sinhala' : 'singlish';
    }
}

const createBot = (options) => new SinhalaHumanoid(options);

module.exports = {
    SinhalaHumanoid,
    createBot
};
