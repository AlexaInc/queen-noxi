/**
 * nlu.js — Natural Language Understanding Engine
 *
 * Makes the bot understand:
 *   1. Long paragraphs (segmented into individual thoughts)
 *   2. Intent detection (question, greeting, complaint, story, tease, etc.)
 *   3. Keyword/topic extraction (what is the user REALLY talking about?)
 *   4. Emotional tone detection (happy, sad, angry, excited)
 *   5. Context window (what was just talked about?)
 */

// ────────────────────────────────────────────────────────────────────────────
// KNOWLEDGE MAPS
// ────────────────────────────────────────────────────────────────────────────

const INTENT_PATTERNS = {
    greeting: [/^(hi|hello|hai|hey|ata ne|kohomada|ayye|subha udesanak|good morning|gm)\b/i],
    farewell: [/\b(bye|goodnight|subha rathriyak|gn|yanawa|later|ttyl|cya)\b/i],
    question: [/\b(mokakda|kohomada|kauda|kawda|monada|koheda|kiia|when|why|how|what|who|where|when|da\?|neda\?|da$)\b/i, /\?/],
    complaint: [/\b(dukei|duk|problem|issue|kapuna|asathutak|baya|adura|roga|hondatama na|hodatma na|barei)\b/i],
    happy: [/\b(supa|ela|elatama|maru|hodai|santhosai|love|like|enjoy|ado hehe|haha|lol|:d|😂|😍|❤️|🔥)\b/i],
    sad: [/\b(duk|sad|cry|neth|balanna bari|tani|ekai|adare na|alone|miss|😢|💔|😞)\b/i],
    angry: [/\b(eka nan|apahu|nonsense|baena|bae|budukarapu|waeda na|kelawera|okama|angry|mad|😠|🤬)\b/i],
    excited: [/\b(!{2,}|omg|aiyoo|wait|seriously|ow ow|neda|😱|🤩|elaaaaaa|supaaa)\b/i],
    love: [/\b(love|adare|miss|baby|bae|heart|❤️|😘|💕|💖|xoxo)\b/i],
    story: [/^(ada|kalin|ekl|eka dawas|meka une|eeka giia|eka thamath|api giia|api gaththee|api hitiye)\b/i],
    thanks: [/\b(thanks|thank you|sthuthi|stuthi|awlak na|np|🙏)\b/i],
    request: [/\b(karanna puluwan|help|support|explain|kiyanna|denna|ganna|hadanna)\b/i],
    selfIntro: [/\b(my name is|mama|mage nama|i am|i'm|iam)\b/i],
    teasing: [/\b(hehe|hihi|🤭|😜|😏|;|patta|wela|joke|haha)\b/i]
};

const TOPIC_KEYWORDS = {
    relationship: ['love', 'adare', 'gf', 'bf', 'girlfriend', 'boyfriend', 'miss', 'marry', 'nikaya', 'prema', 'date', 'kiss'],
    food: ['kema', 'rice', 'food', 'eat', 'restaurant', 'kanne', 'bathi', 'curry', 'pizza', 'kottu', 'hoppers', 'string hoppers'],
    work: ['job', 'weda', 'office', 'project', 'deadline', 'meeting', 'boss', 'salary', 'work', 'weda karanne', 'interview'],
    school: ['school', 'university', 'exam', 'pariksha', 'class', 'lecture', 'teacher', 'student', 'ol', 'al', 'degree'],
    games: ['game', 'play', 'pubg', 'fifa', 'cricket', 'sport', 'win', 'lose', 'match'],
    weather: ['rain', 'vasse', 'hot', 'climate', 'weather', 'udawa', 'ginithapu', 'thawath vasse'],
    transport: ['bus', 'train', 'uber', 'taxi', 'bike', 'car', 'traffic', 'jam', 'yanna', 'enna'],
    money: ['money', 'salary', 'loan', 'borrow', 'spend', 'expensive', 'cheap', 'hari ganan', 'pisa', 'rata'],
    health: ['sick', 'roga', 'hospital', 'doctor', 'medicine', 'adura', 'pain', 'headache', 'fever', 'gedara inne'],
    tech: ['phone', 'laptop', 'computer', 'internet', 'data', 'app', 'code', 'website', 'software', 'hack'],
    family: ['amma', 'thaththa', 'mom', 'dad', 'akka', 'malli', 'nangi', 'brother', 'sister', 'family', 'gedara'],
    social: ['party', 'meet', 'hangout', 'friend', 'machan', 'api', 'mall', 'trip', 'outing', 'picnic'],
    srilanka: ['sl', 'srilanka', 'colombo', 'kandy', 'galle', 'jaffna', 'ratnapura', 'lanka'],
    feelings: ['hithenne', 'feel', 'think', 'baya', 'happy', 'sad', 'cry', 'emotion'],
};

const TOPIC_RESPONSES = {
    relationship: {
        chill: ['ada relationship gana dan hodatama katha karanna epa machan hehe', 'adare gana kiyannako, mokada?', 'ow ow, gf/bf gana da?'],
        sexy: ['ooh relationship gana da? oya kauda lucky one?', 'adare gana oya hithanawa da?'],
        hot: ['adare gana da? oyata special kenek innawada?', 'ooh oya kiyanne relationship gana da?']
    },
    food: {
        chill: ['ada kema supa da?!', 'mama dan godak kapannawa, kottu gana kiyanne?', 'ae machan, mama godak hungry', 'abaa kema kiyannako!'],
        professional: ['Hoda keme irunawada?']
    },
    work: {
        chill: ['aiyo weda wada, poddak relax karaganna machan', 'deadline gana stress wena epa', 'weda wenawata kalin api katha kaapuwa na?'],
        professional: ['Project eka kohomada giya? Help ona nam kiyanna.']
    },
    school: {
        chill: ['exam gana stress wena epa machan, blew ekak gamu', 'hondatama study karaganna, ekath mama help karanna puluwan', 'ow pariksha gana da? kalin kiyanna thibathe'],
        professional: ['Study karala hodatama exams passweida?']
    },
    games: {
        chill: ['ado PUBG da?! mama oka ban khelannawa', 'game gana kiyannako, api multiplayer kaamu', 'cricket match baluwada? maru giia na?'],
        hot: ['game karala jadi wunasama prize karannako chat eka']
    },
    weather: {
        chill: ['ada vasse da koheda?', 'aiyo ginithapu, AC eka dala inne', 'ae machan vasse aiye gedara hitapu', 'Colombo wala ginithapu, koheda oya?'],
    },
    transport: {
        chill: ['bus eke traffic jam da? ae ae normal', 'Uber gahanna, bus pain wena epaa machan'],
    },
    money: {
        chill: ['aiyo machan pisa gana duku', 'salary eka waidi wenna one', 'mae ithin savings poddak', 'hari ganan aney life'],
    },
    health: {
        chill: ['aiyo machan! hondatama hoddaganna', 'roga nathnam santhosai', 'hospital giiewda? kohomada?', 'adura na?! gedara hitapan'],
    },
    tech: {
        chill: ['tech gana naththam mama kiyannawa machan', 'code gahala trouble da? kiyanna', 'phone da laptop da?'],
        professional: ['Tech stack eka mokakda use karanne?']
    },
    family: {
        chill: ['family gana hari supa machan', 'amma thaththa kohomada?', 'gedara gihilla aawada?'],
    },
    social: {
        chill: ['outing gamu! koheda?', 'party ekak?! enna enna', 'machan ahala hitiye api meet weida'],
        hot: ['outing gamu, just ape dokomath']
    },
    srilanka: {
        chill: ['mama SL eke podi balla', 'SL game elatama', 'koheda inne SL wala?'],
    },
    feelings: {
        chill: ['mokakda hithenne? kiyanna machan', 'awl na ado, mama innawa ne?', 'mama thiyanawa obage kotaswa'],
        sexy: ['kiyanna aney, mama ahannawa', 'oya feel wenne mama danne na ne?'],
    }
};

// ────────────────────────────────────────────────────────────────────────────
// AUTO-STYLE SIGNAL MAPS
// ────────────────────────────────────────────────────────────────────────────

// Each style has signal words/patterns. Weighted scoring picks the winner.
const STYLE_SIGNALS = {
    professional: {
        weight: 1,
        patterns: [
            /\b(project|meeting|deadline|report|client|sir|madam|please|thank you|regards|schedule|proposal|discuss|email|call|agenda|budget|salary|office|manager|team)\b/i
        ]
    },
    sexy: {
        weight: 1,
        patterns: [
            /\b(baby|babe|honey|cutie|beautiful|gorgeous|hot|sexy|miss you|come over|alone|cuddle|kiss|hug|adore|😍|😘|💋|🥵|😏|😉|flirt|date|special|crush)\b/i
        ]
    },
    hot: {
        weight: 1,
        patterns: [
            /\b(!!|come|enna|langata|tonight|now|asap|jld|fast|quick|urgent|secret|naughty|dark|🔥|😈|🥵|💦|need you|want you|right now)\b/i,
            /!{2,}/
        ]
    },
    chill: {
        weight: 0.5,  // default — lower weight so it loses to specific signals
        patterns: [
            /\b(machan|ado|ayye|poddak|nikang|hehe|lol|supa|ela|maru|chilling|relax|nothing|nothing much|nikan)\b/i
        ]
    }
};

// ────────────────────────────────────────────────────────────────────────────
// NLU CLASS
// ────────────────────────────────────────────────────────────────────────────

class NLU {

    /**
     * Segment a long paragraph into individual thought-sentences
     * Splits on: . ! ? newlines, and Sinhala sentence enders
     */
    segment(text) {
        // Split on sentence terminators
        const raw = text.split(/[.!?\n\r।ෙ]+/).map(s => s.trim()).filter(s => s.length > 1);
        // Also split on conjunctions that indicate a change of subject
        const sentences = [];
        for (const s of raw) {
            // If sentence has comma + subject change indicator, further split
            const subParts = s.split(/\s*,\s*(?=(?:mama|oya|api|ekka|eka|dan|kalin|ekath|ado|machan)\b)/i);
            for (const p of subParts) {
                if (p.trim().length > 1) sentences.push(p.trim());
            }
        }
        return sentences.length ? sentences : [text.trim()];
    }

    /**
     * Detect intents from a sentence
     * @returns {string[]} list of matched intents
     */
    detectIntents(text) {
        const found = [];
        for (const [intent, patterns] of Object.entries(INTENT_PATTERNS)) {
            for (const pat of patterns) {
                if (pat.test(text)) { found.push(intent); break; }
            }
        }
        return found.length ? found : ['unknown'];
    }

    /**
     * Extract topics from text
     * @returns {string[]} matched topic names
     */
    extractTopics(text) {
        const lower = text.toLowerCase();
        const found = [];
        for (const [topic, keywords] of Object.entries(TOPIC_KEYWORDS)) {
            if (keywords.some(kw => lower.includes(kw))) found.push(topic);
        }
        return found;
    }

    /**
     * Get a topic-based response
     */
    getTopicResponse(topic, style = 'chill') {
        const bank = TOPIC_RESPONSES[topic];
        if (!bank) return null;
        const pool = bank[style] || bank['chill'] || null;
        if (!pool || !pool.length) return null;
        return pool[Math.floor(Math.random() * pool.length)];
    }

    /**
     * Detect the emotional tone of a message
     */
    detectTone(text) {
        if (INTENT_PATTERNS.happy.some(p => p.test(text))) return 'happy';
        if (INTENT_PATTERNS.sad.some(p => p.test(text))) return 'sad';
        if (INTENT_PATTERNS.angry.some(p => p.test(text))) return 'angry';
        if (INTENT_PATTERNS.excited.some(p => p.test(text))) return 'excited';
        if (INTENT_PATTERNS.love.some(p => p.test(text))) return 'love';
        return 'neutral';
    }

    /**
     * Generate a tone-aware reaction prefix
     */
    toneReaction(tone) {
        const reactions = {
            happy: ['supa aney!', 'elatama!', 'maru!', 'hodai!'],
            sad: ['aiyo duka aney...', 'awl na machan...', 'duk gannaka eppa ne?'],
            angry: ['ok ok, chill down machan', 'relax ado...', 'aiyo mokada wune?'],
            excited: ['ado!', 'wait wait!', 'seriously?!'],
            love: ['aww hehe', 'ooh ooh', '😊'],
            neutral: []
        };
        const pool = reactions[tone] || [];
        return pool.length ? pool[Math.floor(Math.random() * pool.length)] : '';
    }

    /**
     * Auto-detect the best response style based on message content.
     * Scores each style by how many signals match, returns the top scorer.
     * @param {string} text
     * @returns {string} style name
     */
    detectAutoStyle(text) {
        const scores = {};
        for (const [style, config] of Object.entries(STYLE_SIGNALS)) {
            let score = 0;
            for (const pat of config.patterns) {
                const matches = text.match(pat);
                if (matches) score += matches.length * config.weight;
            }
            scores[style] = score;
        }
        // Return style with highest score; default to chill
        const best = Object.entries(scores).sort((a, b) => b[1] - a[1])[0];
        return (best && best[1] > 0) ? best[0] : 'chill';
    }

    /**
     * Full analysis of any message (short or long paragraph)
     * Returns a structured analysis object
     */
    analyze(text) {
        const sentences = this.segment(text);
        const intents = new Set();
        const topics = new Set();
        const tone = this.detectTone(text);

        for (const s of sentences) {
            this.detectIntents(s).forEach(i => intents.add(i));
            this.extractTopics(s).forEach(t => topics.add(t));
        }

        return {
            original: text,
            sentences,
            intents: [...intents],
            topics: [...topics],
            tone,
            detectedStyle: this.detectAutoStyle(text),
            isLong: sentences.length > 1,
            isQuestion: intents.has('question'),
            isGreeting: intents.has('greeting'),
            isFarewell: intents.has('farewell')
        };
    }
}

module.exports = new NLU();
