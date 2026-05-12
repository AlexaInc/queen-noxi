const { createBot } = require('./index.js');
const path = require('path');
const fs = require('fs');

async function main() {
    const args = process.argv.slice(2);
    const command = args[0] || 'query';

    try {
        const databasePath = path.join(__dirname, 'database');
        if (!fs.existsSync(databasePath)) {
            fs.mkdirSync(databasePath, { recursive: true });
        }

        const bot = createBot({
            name: 'Queen Noxi',
            style: 'auto',
            birthday: '2004-01-21',
            gender: 'Female',
            residence: 'Sri Lanka',
            job: 'Student',
            mongoUri: process.env.CHATDB_URL || null,
            usersDb: databasePath,
            dictionaryDb: path.join(__dirname, 'data', 'dictionary.json')
        });

        await bot.init();

        if (command === 'learn') {
            const input = args[1];
            const response = args[2];
            if (!input || !response) {
                process.stderr.write('Usage: learn <input> <response>');
                process.exit(1);
            }
            await bot.learn(input, response);
            process.stdout.write('LEARNED');
        } else {
            // query command
            const text = args[1];
            const userId = args[2] || 'anon';
            const groupId = args[3] || null;

            if (!text) {
                process.exit(1);
            }

            let response;
            if (groupId) {
                response = await bot.getGroupResponse(text, userId, groupId);
            } else {
                response = bot.getResponse(text, userId);
            }
            process.stdout.write(response || '');
        }
    } catch (err) {
        process.stderr.write(err.message || String(err));
        process.exit(1);
    }
}

main();
