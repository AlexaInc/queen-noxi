import json
import requests
from PyDictionary import PyDictionary
from pyrogram import filters
from QueenNoxi import pbot as app

API_KEY = "6ae0c3a0-afdc-4532-a810-82ded0054236"
URL = "http://services.gingersoftware.com/Ginger/correct/json/GingerTheText"

@app.on_message(filters.command("spell"))
async def _(_, message):
    if not message.reply_to_message:
        return
    msg = message.reply_to_message.text
    if not msg:
        return
    params = dict(lang="US", clientVersion="2.0", apiKey=API_KEY, text=msg)
    res = requests.get(URL, params=params)
    changes = json.loads(res.text).get("LightGingerTheTextResult")
    curr_string = ""
    prev_end = 0
    for change in changes:
        start = change.get("From")
        end = change.get("To") + 1
        suggestions = change.get("Suggestions")
        if suggestions:
            sugg_str = suggestions[0].get("Text")
            curr_string += msg[prev_end:start] + sugg_str
            prev_end = end
    curr_string += msg[prev_end:]
    await message.reply(curr_string)


dictionary = PyDictionary()

@app.on_message(filters.command("define"))
async def _(_, message):
    if len(message.command) < 2:
        return
    word = message.text.split(None, 1)[1]
    let = dictionary.meaning(word)
    set_word = str(let)
    jet = set_word.replace("{", "")
    net = jet.replace("}", "")
    got = net.replace("'", "")
    await message.reply(got)


@app.on_message(filters.command("synonyms"))
async def _(_, message):
    if len(message.command) < 2:
        return
    word = message.text.split(None, 1)[1]
    let = dictionary.synonym(word)
    set_word = str(let)
    jet = set_word.replace("{", "")
    net = jet.replace("}", "")
    got = net.replace("'", "")
    await message.reply(got)


@app.on_message(filters.command("antonyms"))
async def _(_, message):
    if len(message.command) < 2:
        return
    word = message.text.split(None, 1)[1]
    let = dictionary.antonym(word)
    set_word = str(let)
    jet = set_word.replace("{", "")
    net = jet.replace("}", "")
    got = net.replace("'", "")
    await message.reply(got)


__help__ = """
 ❍ /define  <ᴛᴇxᴛ>*:* ᴛʏᴘᴇ ᴛʜᴇ ᴡᴏʀᴅ ᴏʀ ᴇxᴘʀᴇssɪᴏɴ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ sᴇᴀʀᴄʜ
ғᴏʀ ᴇxᴀᴍᴘʟᴇ /ᴅᴇғɪɴᴇ ᴋɪʟʟ
 ❍ /spell *:* ᴡʜɪʟᴇ ʀᴇᴘʟʏɪɴɢ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ, ᴡɪʟʟ ʀᴇᴘʟʏ ᴡɪᴛʜ ᴀ ɢʀᴀᴍᴍᴀʀ ᴄᴏʀʀᴇᴄᴛᴇᴅ ᴠᴇʀsɪᴏɴ
 ❍ /synonyms  <ᴡᴏʀᴅ>*:* ғɪɴᴅ ᴛʜᴇ sʏɴᴏɴʏᴍs ᴏғ ᴀ ᴡᴏʀᴅ
 ❍ /antonyms  <ᴡᴏʀᴅ>*:* ғɪɴᴅ ᴛʜᴇ ᴀɴᴛᴏɴʏᴍs ᴏғ ᴀ ᴡᴏʀᴅ
"""

__mod_name__ = "Eɴɢʟɪsʜ"
