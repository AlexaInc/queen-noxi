# 🤖 QueenNoxi — Complete Setup Guide

> Get every API key and config value needed to run the bot.

---

## 1. Telegram API Credentials (`API_ID` & `API_HASH`)

1. Go to **[my.telegram.org](https://my.telegram.org)**
2. Log in with your phone number
3. Click **"API development tools"**
4. Create an app (any name/platform is fine)
5. Copy **App api_id** → `API_ID`
6. Copy **App api_hash** → `API_HASH`

---

## 2. Bot Token (`TOKEN`)

1. Open Telegram → message **[@BotFather](https://t.me/BotFather)**
2. Send `/newbot`
3. Choose a **name** (display name, e.g. `Queen Noxi`)
4. Choose a **username** (must end in `bot`, e.g. `QueenNoxiGroupBot`)
5. BotFather replies with your token:
   ```
   123456789:AABBccDDeeFFggHHiiJJ...
   ```
   → `TOKEN`
6. Also set `BOT_NAME` = the display name you chose
7. Also set `BOT_USERNAME` = the username **without @**

> **Tip:** Also send `/setprivacy` → `Disable` to let the bot read all group messages.

---

## 3. Your Owner ID (`OWNER_IDS`)

Message **[@userinfobot](https://t.me/userinfobot)** on Telegram.
It replies with your numeric user ID, e.g. `123456789`.

To add **multiple owners**, separate with spaces:
```
OWNER_IDS=123456789 987654321
```

---

## 4. MongoDB (`MONGO_DB_URI`)

> You already have MongoDB Atlas — reuse the same cluster or create a new database in it.

**To add a new database in your existing Atlas cluster:**
1. Go to **[cloud.mongodb.com](https://cloud.mongodb.com)**
2. Open your cluster → **Browse Collections** → **Add My Own Data**
3. Create a database named `QueenNoxi`
4. Your existing connection URI works — just change the DB name at the end:
   ```
   mongodb+srv://user:pass@cluster.xxxxx.mongodb.net/QueenNoxi?retryWrites=true&w=majority
   ```
   → `MONGO_DB_URI`

---

## 5. PostgreSQL Database (`DATABASE_URL`)

### 🆓 Recommended: [Neon.tech](https://neon.tech)
*(Free forever — serverless, no credit card, never sleeps)*

1. Sign up at **[neon.tech](https://neon.tech)** (GitHub login works)
2. Click **"New Project"** → choose a region closest to you
3. Wait ~10 seconds for provisioning
4. Go to **Dashboard → Connection Details**
5. Select **"Pooled connection"** and copy the string:
   ```
   postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
   → `DATABASE_URL`

| Alternative | Free Tier | Notes |
|---|---|---|
| [Supabase](https://supabase.com) | 500 MB | Pauses after 1 week inactive |
| [Railway](https://railway.app) | $5 credit/mo | Easiest UI |
| [Aiven](https://aiven.io) | 1 free service | Good uptime |

---

## 6. Support Chat (`SUPPORT_CHAT`)

You can provide either a public username or a full invite link.

- **Public Group:** Set `SUPPORT_CHAT=yourgroupusername` (without `@`)
- **Private Group:** Set `SUPPORT_CHAT=https://t.me/+xyz123...` (full invite link)

The bot will automatically handle either format for the support buttons in the menu.

---

## 7. Start Image (`START_IMG`)

Any **direct image URL** (must end in `.jpg`, `.png`, `.webp`).

Quick options:
- Upload to [imgbb.com](https://imgbb.com) → get direct link
- Use any public Telegram CDN URL
- Use a raw GitHub image URL

---

## 8. Log Channel (`EVENT_LOGS`)

1. Create a private Telegram channel
2. Add your bot as **admin**
3. Forward any message from the channel to **[@getidsbot](https://t.me/getidsbot)**
4. Copy the **channel ID** (looks like `-100xxxxxxxxxx`)
   → `EVENT_LOGS`

---

## 9. Optional API Keys

| Variable | Service | Cost | Link |
|---|---|---|---|
| `CASH_API_KEY` | Currency conversion | Free | [api.freecurrencyapi.com](https://freecurrencyapi.com) |
| `TIME_API_KEY` | Timezone lookup | Free | [timezonedb.com](https://timezonedb.com/api) |

---

## 10. Deploying on HuggingFace Spaces

1. Push this repo to **[Hugging Face](https://huggingface.co/new-space)**
   - Space SDK: **Docker**
   - Visibility: Public or Private
2. After creating, go to **Settings → Variables and secrets**
3. Add each key below as a **Secret** (sensitive) or Variable:

| Type | Variables |
|---|---|
| 🔐 Secret | `API_ID`, `API_HASH`, `TOKEN`, `MONGO_DB_URI`, `DATABASE_URL`, `OWNER_IDS` |
| 📝 Variable | `BOT_NAME`, `BOT_USERNAME`, `SUPPORT_CHAT`, `START_IMG`, `EVENT_LOGS`, `WORKERS` |

4. The Space auto-builds and starts — watch **Logs** for any errors.
5. Your bot should come online within 2–3 minutes.

> **Health check:** HuggingFace pings `https://your-space.hf.space/health`
> The bot responds with `✅ QueenNoxi is running!`

---

## 11. Minimum Required `.env` for Local Testing

```env
API_ID=12345678
API_HASH=your_api_hash_here
TOKEN=bot:token_here
OWNER_IDS=123456789
MONGO_DB_URI=mongodb+srv://user:pass@cluster.mongodb.net/QueenNoxi
BOT_NAME=QueenNoxi
BOT_USERNAME=yourbotusername
```

Run locally with:
```powershell
# Load .env vars and start the bot
Get-Content .env | ForEach-Object { if ($_ -match '^([^#=]+)=(.*)$') { [System.Environment]::SetEnvironmentVariable($Matches[1].Trim(), $Matches[2].Trim()) } }
python app.py
```
