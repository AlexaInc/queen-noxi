const fs = require('fs');
const path = require('path');
const readline = require('readline');
const Brain = require('./brain');

/**
 * Universal training tool for Sinhala dataset ingestion.
 * Supports JSON, TSV, CSV, Parallel Text, and Large-Scale Streaming.
 */
class Trainer {
    /**
     * Train from an array of objects
     */
    static trainData(data, defaultStyle = 'chill') {
        if (!Array.isArray(data)) return 0;
        const oldStyle = (Brain.persona && Brain.persona.style) || 'chill';
        let count = 0;
        
        console.log(`🧠 Processing ${data.length} patterns...`);
        
        for (const item of data) {
            const input = item.input || item.q || item.question || item.text || item.Phrase;
            const response = item.response || item.a || item.answer || item.reply || item.Response;
            const style = item.style || defaultStyle;
            
            if (input && response) {
                const s = ['chill', 'professional', 'sexy', 'hot'].includes(style) ? style : defaultStyle;
                Brain.setPersona({ style: s });
                // Bulk training: disable auto-save
                Brain.learn(input.toString(), response.toString(), false);
                count++;
            }
            
            if (count > 0 && count % 10000 === 0) {
                console.log(`...ingested ${count} patterns`);
            }
        }
        
        // Final Save for bulk data
        console.log('💾 Saving brain to disk (this may take a moment)...');
        Brain.saveData();
        
        Brain.setPersona({ style: oldStyle });
        return count;
    }

    /**
     * Train from a raw string
     */
    static trainString(content, format = 'json', defaultStyle = 'chill') {
        const fmt = format.toLowerCase().replace('.', '');
        if (fmt === 'json') {
            try { return this.trainData(JSON.parse(content), defaultStyle); }
            catch (e) { return 0; }
        } else if (fmt === 'tsv' || fmt === 'csv' || fmt === 'txt') {
            const lines = content.split(/\r?\n/);
            let count = 0;
            const delimiter = (fmt === 'tsv' || fmt === 'txt') ? /\t+/ : ',';
            const data = [];

            for (const line of lines) {
                if (!line.trim()) continue;
                const columns = line.split(delimiter);
                if (columns.length >= 2) {
                    const col1 = columns[0].trim().replace(/^"|"$/g, '');
                    const col2 = columns[1].trim().replace(/^"|"$/g, '');
                    if (col1.toLowerCase() === 'question' || col1.toLowerCase() === 'phrase' || col1.toLowerCase() === 'singlish') continue;
                    data.push({ q: col1, a: col2, style: defaultStyle });
                }
            }
            return this.trainData(data, defaultStyle);
        }
        return 0;
    }

    /**
     * Streaming Trainer for LARGE files (100MB+)
     * Supports Tab, Comma, and custom WSD format.
     */
    static async trainLarge(filePath, defaultStyle = 'chill') {
        const absPath = path.isAbsolute(filePath) ? filePath : path.join(process.cwd(), filePath);
        if (!fs.existsSync(absPath)) return 0;

        // Detect encoding
        const buffer = fs.readFileSync(absPath, { length: 500 });
        let encoding = 'utf8';
        if (buffer[0] === 0xFF && buffer[1] === 0xFE) encoding = 'utf16le';
        else if (buffer[0] === 0xFE && buffer[1] === 0xFF) encoding = 'utf16be';
        else if (buffer.some(b => b === 0)) encoding = 'utf16le';

        const processor = require('./processor');
        const fileStream = fs.createReadStream(absPath, { encoding });

        const rl = readline.createInterface({
            input: fileStream,
            crlfDelay: Infinity
        });

        console.log(`🚀 Streaming training from ${path.basename(filePath)} (${encoding})...`);
        let count = 0;

        for await (const line of rl) {
            if (!line.trim()) continue;

            let sinhala, singlish;

            // Pattern 1: WSD Format
            const wsdMatch = line.match(/^Word:\s*([^,]+),\s*Sinhala\s*Words:\s*\[(.*)\]/i);
            if (wsdMatch) {
                singlish = wsdMatch[1].trim();
                const variants = wsdMatch[2].split(',').map(v => v.trim().replace(/['"\[\]]/g, ''));
                variants.forEach(v => {
                    if (v && /[\u0D80-\u0DFF]/.test(v)) {
                        processor.phoneticMap[v] = singlish;
                        count++;
                    }
                });
                continue;
            }

            // Pattern 2: Swa Bhasha / test1
            const parts = line.split(/[\t,/]/);
            if (parts.length >= 2) {
                const p1 = parts[0].trim().replace(/^"|"$/g, '');
                const p2 = parts[1].trim().replace(/^"|"$/g, '');

                const isP1S = /[\u0D80-\u0DFF]/.test(p1);
                const isP2S = /[\u0D80-\u0DFF]/.test(p2);

                if (isP1S && !isP2S) { sinhala = p1; singlish = p2; }
                else if (!isP1S && isP2S) { sinhala = p2; singlish = p1; }
                else if (!isP1S && !isP2S) { Brain.learn(p1, p2, false); count++; }

                if (sinhala && singlish) {
                    processor.phoneticMap[sinhala] = singlish;
                    count++;
                }
            }

            if (count > 0 && count % 50000 === 0) {
                console.log(`...memorized ${count} phonetic patterns`);
            }
        }

        processor.savePhoneticMap();
        Brain.saveData(); // Save brain after large stream as well
        return count;
    }

    /**
     * Legacy File Trainer
     */
    static trainFile(filePath, defaultStyle = 'chill') {
        const absPath = path.isAbsolute(filePath) ? filePath : path.join(process.cwd(), filePath);
        if (!fs.existsSync(absPath)) return 0;
        const buffer = fs.readFileSync(absPath);
        let content;
        if (buffer[0] === 0xFF && buffer[1] === 0xFE) content = buffer.toString('utf16le');
        else if (buffer[0] === 0xFE && buffer[1] === 0xFF) content = buffer.toString('utf16be');
        else {
            const isUtf16 = buffer.slice(0, 500).some(b => b === 0);
            content = isUtf16 ? buffer.toString('utf16le') : buffer.toString('utf8');
        }
        return this.trainString(content, path.extname(absPath).replace('.', ''), defaultStyle);
    }
}

module.exports = Trainer;
