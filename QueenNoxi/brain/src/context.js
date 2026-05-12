/**
 * context.js — Conversation Context Window
 *
 * Tracks:
 *  - Recent turns (last N messages from user + bot)
 *  - Active topics (what is being discussed)
 *  - Active intents
 *  - Emotional trend
 */

class ContextWindow {
    constructor(maxTurns = 10) {
        this.maxTurns = maxTurns;
        this.turns = [];           // { role: 'user'|'bot', text, analysis?, ts }
        this.activeTopics = [];    // most recent topics discussed
        this.activeIntents = [];   // most recent intents
        this.tone = 'neutral';
        this.waitingForAnswer = null; // if bot asked a question, track what it asked
    }

    /**
     * Add a user turn (with NLU analysis attached)
     */
    addUserTurn(text, analysis) {
        this.turns.push({ role: 'user', text, analysis, ts: Date.now() });
        if (this.turns.length > this.maxTurns * 2) this.turns.shift();

        if (analysis) {
            // Update active topics (prepend newest, keep last 3)
            this.activeTopics = [...new Set([...analysis.topics, ...this.activeTopics])].slice(0, 3);
            this.activeIntents = analysis.intents;
            this.tone = analysis.tone;
        }
    }

    /**
     * Add a bot turn
     */
    addBotTurn(text) {
        this.turns.push({ role: 'bot', text, ts: Date.now() });
        if (this.turns.length > this.maxTurns * 2) this.turns.shift();

        // Track if bot asked a question (ends in ?)
        if (text && text.includes('?')) {
            this.waitingForAnswer = text;
        } else {
            this.waitingForAnswer = null;
        }
    }

    /**
     * Get recent user messages (last N)
     */
    getRecentUserMessages(n = 3) {
        return this.turns.filter(t => t.role === 'user').slice(-n).map(t => t.text);
    }

    /**
     * Get last bot message
     */
    getLastBotMessage() {
        const botTurns = this.turns.filter(t => t.role === 'bot');
        return botTurns.length ? botTurns[botTurns.length - 1].text : null;
    }

    /**
     * Check if current message is likely a follow-up to an active topic
     */
    isFollowUp(analysis) {
        if (!analysis || !this.activeTopics.length) return false;
        return analysis.topics.some(t => this.activeTopics.includes(t));
    }

    /**
     * Check if the bot recently asked a question and is waiting for an answer
     */
    isAnsweringBotQuestion() {
        return !!this.waitingForAnswer;
    }

    /**
     * Wipe context (for fresh conversation)
     */
    reset() {
        this.turns = [];
        this.activeTopics = [];
        this.activeIntents = [];
        this.tone = 'neutral';
        this.waitingForAnswer = null;
    }
}

module.exports = ContextWindow;
