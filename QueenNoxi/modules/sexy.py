import random

from telethon import Button, events

from .. import telethn as asst, SUPPORT_CHAT_URL as c

BUTTON = [[Button.url("🍒 ꜱᴜᴘᴘᴏʀᴛ 🍒", c)]]
HOT = "https://telegra.ph/file/daad931db960ea40c0fca.gif"
SMEXY = "https://telegra.ph/file/a23e9fd851fb6bc771686.gif"
LEZBIAN = "https://telegra.ph/file/5609b87f0bd461fc36acb.gif"
BIGBALL = "https://i.gifer.com/8ZUg.gif"
LANG = "https://telegra.ph/file/423414459345bf18310f5.gif"
CUTIE = "https://64.media.tumblr.com/d701f53eb5681e87a957a547980371d2/tumblr_nbjmdrQyje1qa94xto1_500.gif"
PUSSY = "https://nekos.best/api/v2/poke/773e1d53-bb7c-410c-8dfd-e16da3fc7344.gif"
SEX = "https://c.tenor.com/7u92I92oPwgAAAAC/tenor.gif"
LUST = "https://c.tenor.com/54MQB5tN6kwAAAAd/tenor.gif"
VIRGIN = "https://c.tenor.com/L5okNZ6GO40AAAAC/tenor.gif"
ASS = "https://c.tenor.com/qMnrmSdE_IYAAAAC/tenor.gif"
THIGHS = "https://c.tenor.com/8RNv7Ip6GlAAAAAd/tenor.gif"
WAIFU = "https://i.giphy.com/0xwUkYOI3D60r9bz2o.webp"


@asst.on(events.NewMessage(pattern="/horny ?(.*)"))
async def horny(e):
    user_id = e.sender.id
    user_name = e.sender.first_name
    mention = f"[{user_name}](tg://user?id={str(user_id)})"
    mm = random.randint(1, 100)
    HORNY = f"**🔥** {mention} **ɪꜱ** {mm}**% ʜᴏʀɴʏ!**"
    await e.reply(HORNY, buttons=BUTTON, file=HOT)


@asst.on(events.NewMessage(pattern="/gay ?(.*)"))
async def gay(e):
    user_id = e.sender.id
    user_name = e.sender.first_name
    mention = f"[{user_name}](tg://user?id={str(user_id)})"
    mm = random.randint(1, 100)
    GAY = f"**🍷** {mention} **ɪꜱ** {mm}**% ɢᴀʏ!**"
    await e.reply(GAY, buttons=BUTTON, file=SMEXY)


@asst.on(events.NewMessage(pattern="/lezbian ?(.*)"))
async def lezbian(e):
    user_id = e.sender.id
    user_name = e.sender.first_name
    mention = f"[{user_name}](tg://user?id={str(user_id)})"
    mm = random.randint(1, 100)
    FEK = f"**💜** {mention} **ɪꜱ** {mm}**% ʟᴇᴢʙɪᴀɴ!**"
    await e.reply(FEK, buttons=BUTTON, file=LEZBIAN)


@asst.on(events.NewMessage(pattern="/boob ?(.*)"))
async def boob(e):
    user_id = e.sender.id
    user_name = e.sender.first_name
    mention = f"[{user_name}](tg://user?id={str(user_id)})"
    mm = random.randint(1, 100)
    BOOBS = f"**🍒** {mention}**'ꜱ ʙᴏᴏʙꜱ ꜱɪᴢᴇ ɪᴢ** {mm}**!**"
    await e.reply(BOOBS, buttons=BUTTON, file=BIGBALL)


@asst.on(events.NewMessage(pattern="/cock ?(.*)"))
async def cock(e):
    user_id = e.sender.id
    user_name = e.sender.first_name
    mention = f"[{user_name}](tg://user?id={str(user_id)})"
    mm = random.randint(1, 100)
    COCK = f"**🍆** {mention}**'ꜱ ᴄᴏᴄᴋ ꜱɪᴢᴇ ɪᴢ** {mm}**ᴄᴍ**"
    await e.reply(COCK, buttons=BUTTON, file=LANG)


@asst.on(events.NewMessage(pattern="/cute ?(.*)"))
async def cute(e):
    user_id = e.sender.id
    user_name = e.sender.first_name
    mention = f"[{user_name}](tg://user?id={str(user_id)})"
    mm = random.randint(1, 100)
    CUTE = f"**🍑** {mention} {mm}**% ᴄᴜᴛᴇ**"
    await e.reply(CUTE, buttons=BUTTON, file=CUTIE)


@asst.on(events.NewMessage(pattern="/pussy ?(.*)"))
async def pussy(e):
    user_id = e.sender.id
    user_name = e.sender.first_name
    mention = f"[{user_name}](tg://user?id={str(user_id)})"
    mm = random.randint(1, 100)
    PUSSY_TEXT = f"**😻** {mention}**'ꜱ ᴘᴜꜱꜱʏ ᴛɪɢʜᴛɴᴇꜱꜱ ɪᴢ** {mm}**%**"
    await e.reply(PUSSY_TEXT, buttons=BUTTON, file=PUSSY)


@asst.on(events.NewMessage(pattern="/sex ?(.*)"))
async def sex(e):
    user_id = e.sender.id
    user_name = e.sender.first_name
    mention = f"[{user_name}](tg://user?id={str(user_id)})"
    mm = random.randint(1, 100)
    SEX_TEXT = f"**👑** {mention} **ʜᴀꜱ** {mm}**% sᴇx ᴀᴘᴘᴇᴀʟ!**"
    await e.reply(SEX_TEXT, buttons=BUTTON, file=SEX)


@asst.on(events.NewMessage(pattern="/lust ?(.*)"))
async def lust(e):
    user_id = e.sender.id
    user_name = e.sender.first_name
    mention = f"[{user_name}](tg://user?id={str(user_id)})"
    mm = random.randint(1, 100)
    LUST_TEXT = f"**🥵** {mention} **ɪꜱ** {mm}**% ʟᴜꜱᴛꜰᴜʟ!**"
    await e.reply(LUST_TEXT, buttons=BUTTON, file=LUST)


@asst.on(events.NewMessage(pattern="/virgin ?(.*)"))
async def virgin(e):
    user_id = e.sender.id
    user_name = e.sender.first_name
    mention = f"[{user_name}](tg://user?id={str(user_id)})"
    mm = random.randint(1, 100)
    VIRGIN_TEXT = f"**😇** {mention} **ɪꜱ** {mm}**% ᴠɪʀɢɪɴ!**"
    await e.reply(VIRGIN_TEXT, buttons=BUTTON, file=VIRGIN)


@asst.on(events.NewMessage(pattern="/ass ?(.*)"))
async def ass(e):
    user_id = e.sender.id
    user_name = e.sender.first_name
    mention = f"[{user_name}](tg://user?id={str(user_id)})"
    mm = random.randint(1, 100)
    ASS_TEXT = f"**🍑** {mention}**'ꜱ ᴀꜱꜱ sɪᴢᴇ ɪᴢ** {mm}**%**"
    await e.reply(ASS_TEXT, buttons=BUTTON, file=ASS)


@asst.on(events.NewMessage(pattern="/thighs ?(.*)"))
async def thighs(e):
    user_id = e.sender.id
    user_name = e.sender.first_name
    mention = f"[{user_name}](tg://user?id={str(user_id)})"
    mm = random.randint(1, 100)
    THIGHS_TEXT = f"**🍗** {mention}**'ꜱ ᴛʜɪɢʜs ǫᴜᴀʟɪᴛʏ ɪᴢ** {mm}**/100**"
    await e.reply(THIGHS_TEXT, buttons=BUTTON, file=THIGHS)


@asst.on(events.NewMessage(pattern="/waifurate ?(.*)"))
async def waifurate(e):
    user_id = e.sender.id
    user_name = e.sender.first_name
    mention = f"[{user_name}](tg://user?id={str(user_id)})"
    mm = random.randint(1, 100)
    WAIFU_TEXT = f"**💃** {mention} **ɪꜱ ʀᴀᴛᴇᴅ** {mm}**/100 ᴀs ᴀ ᴡᴀɪꜰᴜ!**"
    await e.reply(WAIFU_TEXT, buttons=BUTTON, file=WAIFU)


__help__ = """
➻ /horny - ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ʜᴏʀɴʏᴇꜱꜱ

➻ /gay - ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ɢᴜʏɴᴇꜱꜱ

➻ /lezbian - ᴄʜᴇᴄᴋ ᴜʀ ᴄᴜʀʀᴇɴᴛ ʟᴀᴢʙɪᴀɴ

➻ /boob - ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ʙᴏᴏʙꜱ ꜱɪᴢᴇ

➻ /cute - ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴄᴜᴛᴇɴᴇꜱꜱ

➻ /pussy - ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴘᴜꜱꜱʏ ᴛɪɢʜᴛɴᴇꜱꜱ

➻ /sex - ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ sᴇx ᴀᴘᴘᴇᴀʟ

➻ /lust - ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ʟᴜꜱᴛꜰᴜʟɴᴇꜱꜱ

➻ /virgin - ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴠɪʀɢɪɴɪᴛʏ

➻ /ass - ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴀꜱꜱ sɪᴢᴇ

➻ /thighs - ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ᴛʜɪɢʜs ǫᴜᴀʟɪᴛʏ

➻ /waifurate - ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴡᴀɪꜰᴜ ʀᴀᴛɪɴɢ
"""

__mod_name__ = "Sᴇᴍxʏ"
