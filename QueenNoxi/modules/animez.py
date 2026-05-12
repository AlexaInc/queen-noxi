import datetime
import html
import textwrap
import aiohttp
import bs4
from jikanpy import AioJikan
from pyrogram import filters, Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from QueenNoxi import pbot
from QueenNoxi.modules.disable import DisableAbleCommandHandler

info_btn = "More Information"
close_btn = "Close ❌"

def shorten(description, info="anilist.co"):
    msg = ""
    if len(description) > 700:
        description = description[0:500] + "...."
        msg += f"\n**Description**: _{description}_[Read More]({info})"
    else:
        msg += f"\n**Description**:_{description}_"
    return msg

def t(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        ((str(days) + " Days, ") if days else "")
        + ((str(hours) + " Hours, ") if hours else "")
        + ((str(minutes) + " Minutes, ") if minutes else "")
        + ((str(seconds) + " Seconds, ") if seconds else "")
        + ((str(milliseconds) + " ms, ") if milliseconds else "")
    )
    return tmp[:-2]

airing_query = """
query ($id: Int,$search: String) { 
    Media (id: $id, type: ANIME,search: $search) {
        id
        episodes
        title {
            romaji
            english
            native
        }
        nextAiringEpisode {
            airingAt
            timeUntilAiring
            episode
        } 
    }
}
"""

anime_query = """
query ($id: Int,$search: String) {
    Media (id: $id, type: ANIME,search: $search) {
        id
        title {
            romaji
            english
            native
        }
        description (asHtml: false)
        startDate{
            year
        }
        episodes
        season
        type
        format
        status
        duration
        siteUrl
        studios{
            nodes{
                name
            }
        }
        trailer{
            id
            site
            thumbnail
        }
        averageScore
        genres
        bannerImage
    }
}
"""

character_query = """
query ($query: String) {
    Character (search: $query) {
        id
        name {
            first
            last
            full
        }
        siteUrl
        image {
            large
        }
        description
    }
}
"""

manga_query = """
query ($id: Int,$search: String) { 
    Media (id: $id, type: MANGA,search: $search) { 
        id
        title {
            romaji
            english
            native
        }
        description (asHtml: false)
        startDate{
            year
        }
        type
        format
        status
        siteUrl
        averageScore
        genres
        bannerImage
    }
}
"""

url = "https://graphql.anilist.co"

async def get_response(query, variables):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"query": query, "variables": variables}) as resp:
            return await resp.json()

@pbot.on_message(filters.command("airing"))
@DisableAbleCommandHandler("airing")
async def airing(client: Client, message: Message):
    search_str = message.text.split(None, 1)[1] if len(message.command) > 1 else None
    if not search_str and message.reply_to_message:
        search_str = message.reply_to_message.text
    
    if not search_str:
        await message.reply_text("Tell Anime Name :) ( /airing <anime name>)")
        return

    data = await get_response(airing_query, {"search": search_str})
    if not data or "data" not in data or not data["data"]["Media"]:
        await message.reply_text("Anime not found")
        return

    response = data["data"]["Media"]
    msg = f"**Name**: **{response['title']['romaji']}**(`{response['title']['native']}`)\n**ID**: `{response['id']}`"
    if response["nextAiringEpisode"]:
        time_val = response["nextAiringEpisode"]["timeUntilAiring"] * 1000
        time_str = t(time_val)
        msg += f"\n**Episode**: `{response['nextAiringEpisode']['episode']}`\n**Airing In**: `{time_str}`"
    else:
        msg += f"\n**Episode**:{response['episodes']}\n**Status**: `N/A`"
    await message.reply_text(msg)

@pbot.on_message(filters.command("anime"))
@DisableAbleCommandHandler("anime")
async def anime(client: Client, message: Message):
    search = message.text.split(None, 1)[1] if len(message.command) > 1 else None
    if not search and message.reply_to_message:
        search = message.reply_to_message.text

    if not search:
        await message.reply_text("Format : /anime < anime name >")
        return

    data = await get_response(anime_query, {"search": search})
    if not data or "data" not in data or not data["data"]["Media"]:
        await message.reply_text("Anime not found")
        return

    json_data = data["data"]["Media"]
    msg = f"**{json_data['title']['romaji']}**(`{json_data['title']['native']}`)\n**Type**: {json_data['format']}\n**Status**: {json_data['status']}\n**Episodes**: {json_data.get('episodes', 'N/A')}\n**Duration**: {json_data.get('duration', 'N/A')} Per Ep.\n**Score**: {json_data['averageScore']}\n**Genres**: `"
    msg += ", ".join(json_data["genres"]) + "`\n"
    msg += "**Studios**: `"
    msg += ", ".join([x['name'] for x in json_data["studios"]["nodes"]]) + "`\n"
    
    info = json_data.get("siteUrl")
    trailer = json_data.get("trailer", None)
    if trailer:
        trailer_id = trailer.get("id", None)
        site = trailer.get("site", None)
        if site == "youtube":
            trailer = "https://youtu.be/" + trailer_id
    
    description = json_data.get("description", "N/A").replace("<i>", "").replace("</i>", "").replace("<br>", "")
    msg += train_shorten(description, info)
    image = json_data.get("bannerImage", None)
    
    buttons = [
        [
            InlineKeyboardButton("ᴍᴏʀᴇ ɪɴғᴏ", url=info),
        ]
    ]
    if trailer:
        buttons[0].append(InlineKeyboardButton("ᴛʀᴀɪʟᴇʀ", url=str(trailer)))
        
    if image:
        try:
            await message.reply_photo(photo=image, caption=msg,保护_markup=InlineKeyboardMarkup(buttons))
        except Exception:
            msg += f" [〽️]({image})"
            await message.reply_text(msg, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply_text(msg, reply_markup=InlineKeyboardMarkup(buttons))

def train_shorten(description, info):
    if len(description) > 700:
        return f"\n**Description**: _{description[:500]}...._[Read More]({info})"
    return f"\n**Description**: _{description}_"

@pbot.on_message(filters.command("character"))
@DisableAbleCommandHandler("character")
async def character(client: Client, message: Message):
    search = message.text.split(None, 1)[1] if len(message.command) > 1 else None
    if not search and message.reply_to_message:
        search = message.reply_to_message.text

    if not search:
        await message.reply_text("Format : /character < character name >")
        return

    data = await get_response(character_query, {"query": search})
    if not data or "data" not in data or not data["data"]["Character"]:
        await message.reply_text("Character not found")
        return

    json_data = data["data"]["Character"]
    msg = f"**{json_data.get('name').get('full')}**(`{json_data.get('name').get('native')}`)\n"
    description = f"{json_data['description']}"
    site_url = json_data.get("siteUrl")
    msg += train_shorten(description, site_url)
    image = json_data.get("image", None)
    
    if image:
        await message.reply_photo(photo=image["large"], caption=msg.replace("<b>", "").replace("</b>", ""))
    else:
        await message.reply_text(msg.replace("<b>", "").replace("</b>", ""))

@pbot.on_message(filters.command("manga"))
@DisableAbleCommandHandler("manga")
async def manga(client: Client, message: Message):
    search = message.text.split(None, 1)[1] if len(message.command) > 1 else None
    if not search and message.reply_to_message:
        search = message.reply_to_message.text

    if not search:
        await message.reply_text("Format : /manga < manga name >")
        return

    data = await get_response(manga_query, {"search": search})
    if not data or "data" not in data or not data["data"]["Media"]:
        await message.reply_text("Manga not found")
        return

    json_data = data["data"]["Media"]
    msg = f"**{json_data['title']['romaji']}**(`{json_data['title']['native']}`)\n"
    if json_data["startDate"].get("year"):
        msg += f"**Start Date**: `{json_data['startDate']['year']}`\n"
    if json_data.get("status"):
        msg += f"**Status**: `{json_data['status']}`\n"
    if json_data.get("averageScore"):
        msg += f"**Score**: `{json_data['averageScore']}`\n"
    
    msg += "**Genres**: " + ", ".join(json_data.get("genres", [])) + "\n"
    
    info = json_data["siteUrl"]
    description = json_data.get('description', 'N/A')
    msg += train_shorten(description, info)
    
    image = json_data.get("bannerImage")
    buttons = [[InlineKeyboardButton("More Info", url=info)]]
    
    if image:
        try:
            await message.reply_photo(photo=image, caption=msg, reply_markup=InlineKeyboardMarkup(buttons))
        except Exception:
            msg += f" [〽️]({image})"
            await message.reply_text(msg, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply_text(msg, reply_markup=InlineKeyboardMarkup(buttons))

@pbot.on_message(filters.command("user"))
@DisableAbleCommandHandler("user")
async def user_info(client: Client, message: Message):
    search_query = message.text.split(None, 1)[1] if len(message.command) > 1 else None
    if not search_query:
        await message.reply_text("Format : /user <username>")
        return

    async with AioJikan() as jikan:
        try:
            us = await jikan.user(search_query)
        except Exception:
            await message.reply_text("Username not found.")
            return

    img = us.get("images", {}).get("jpg", {}).get("image_url", "https://cdn.myanimelist.net/images/questionmark_50.gif")
    
    birthday = us.get("birthday")
    joined = us.get("joined")
    
    caption = f"**ᴜsᴇʀɴᴀᴍᴇ**: [{us['username']}]({us['url']})\n\n"
    caption += f"**ɢᴇɴᴅᴇʀ**: `{us.get('gender', 'Unknown')}`\n"
    caption += f"**ʙɪʀᴛʜᴅᴀʏ**: `{birthday[:10] if birthday else 'Unknown'}`\n"
    caption += f"**ᴊᴏɪɴᴇᴅ**: `{joined[:10] if joined else 'Unknown'}`\n"
    
    anime_stats = us.get("statistics", {}).get("anime", {})
    manga_stats = us.get("statistics", {}).get("manga", {})
    
    caption += f"**ᴅᴀʏs ᴡᴀsᴛᴇᴅ ᴡᴀᴛᴄʜɪɴɢ ᴀɴɪᴍᴇ**: `{anime_stats.get('days_watched', 0)}`\n"
    caption += f"**ᴅᴀʏs ᴡᴀsᴛᴇᴅ ʀᴇᴀᴅɪɴɢ ᴍᴀɴɢᴀ**: `{manga_stats.get('days_read', 0)}`\n\n"
    
    about = us.get("about", "N/A")
    if len(about) > 300:
        about = about[:300] + "..."
    caption += f"**ᴀʙᴏᴜᴛ**: {about}"

    buttons = [
        [InlineKeyboardButton(info_btn, url=us["url"])],
        [InlineKeyboardButton(close_btn, callback_data=f"anime_close,{message.from_user.id}")]
    ]

    await message.reply_photo(photo=img, caption=caption, reply_markup=InlineKeyboardMarkup(buttons))

@pbot.on_message(filters.command("upcoming"))
@DisableAbleCommandHandler("upcoming")
async def upcoming_anime(client: Client, message: Message):
    async with AioJikan() as jikan:
        upcomin = await jikan.top(type="anime", filter="upcoming")
        
    upcoming_message = "Upcoming Anime:\n"
    for i, entry in enumerate(upcomin["data"][:10]):
        upcoming_message += f"{i + 1}. {entry['title']}\n"

    await message.reply_text(upcoming_message)

async def search_site(message, query, site):
    search_url = f"https://{site}.com/?s={query}"
    async with aiohttp.ClientSession() as session:
        async with session.get(search_url) as resp:
            html_text = await resp.text()
            
    soup = bs4.BeautifulSoup(html_text, "html.parser")
    if site == "animekaizoku":
        search_result = soup.find_all("h2", {"class": "post-title"})
    else:
        search_result = soup.find_all("h2", {"class": "title"})

    if not search_result:
        await message.reply_text(f"**No result found for** `{query}`")
        return

    result = f"**Search results for** `{query}`\n"
    for entry in search_result:
        if entry.text.strip() == "Nothing Found":
            await message.reply_text(f"**No result found for** `{query}`")
            return
        
        link = entry.a["href"]
        if site == "animekaizoku" and not link.startswith("http"):
            link = "https://animekaizoku.com/" + link
        
        name = html.escape(entry.text.strip())
        result += f"• [{name}]({link})\n"

    buttons = [[InlineKeyboardButton("See all results", url=search_url)]]
    await message.reply_text(result, reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)

@pbot.on_message(filters.command("kaizoku"))
@DisableAbleCommandHandler("kaizoku")
async def kaizoku_cmd(client: Client, message: Message):
    query = message.text.split(None, 1)[1] if len(message.command) > 1 else None
    if not query:
        await message.reply_text("Give something to search")
        return
    await search_site(message, query, "animekaizoku")

@pbot.on_message(filters.command("kayo"))
@DisableAbleCommandHandler("kayo")
async def kayo_cmd(client: Client, message: Message):
    query = message.text.split(None, 1)[1] if len(message.command) > 1 else None
    if not query:
        await message.reply_text("Give something to search")
        return
    await search_site(message, query, "animekayo")

__mod_name__ = "Aɴɪᴍᴇ"
__help__ = """
ɢᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴀɴɪᴍᴇ, ᴍᴀɴɢᴀ ᴏʀ ᴄʜᴀʀᴀᴄᴛᴇʀs ғʀᴏᴍ [ᴀɴɪʟɪsᴛ](ᴀɴɪʟɪsᴛ.ᴄᴏ).

**ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs:**
• `/anime <anime>`: ʀᴇᴛᴜʀɴs ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴛʜᴇ ᴀɴɪᴍᴇ.
• `/character <ᴄʜᴀʀᴀᴄᴛᴇʀ>`: ʀᴇᴛᴜʀɴs ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴛʜᴇ ᴄʜᴀʀᴀᴄᴛᴇʀ.
• `/manga <ᴍᴀɴɢᴀ>`: ʀᴇᴛᴜʀɴs ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴛʜᴇ ᴍᴀɴɢᴀ.
• `/user <ᴜsᴇʀ>`: ʀᴇᴛᴜʀɴs ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴀ ᴍʏᴀɴɪᴍᴇʟɪsᴛ ᴜsᴇʀ.
• `/upcoming`: ʀᴇᴛᴜʀɴs ᴀ ʟɪsᴛ ᴏғ ɴᴇᴡ ᴀɴɪᴍᴇ ɪɴ ᴛʜᴇ ᴜᴘᴄᴏᴍɪɴɢ sᴇᴀsᴏɴs.
• `/kaizoku <ᴀɴɪᴍᴇ>`: sᴇᴀʀᴄʜ ᴀɴ ᴀɴɪᴍᴇ ᴏɴ ᴀɴɪᴍᴇᴋᴀɪᴢᴏᴋᴜ.ᴄᴏᴍ
• `/kayo <ᴀɴɪᴍᴇ>`: sᴇᴀʀᴄʜ ᴀɴ ᴀɴɪᴍᴇ ᴏɴ ᴀɴɪᴍᴇᴋᴀʏᴏ.ᴄᴏᴍ
• `/airing <ᴀɴɪᴍᴇ>`: ʀᴇᴛᴜʀɴs ᴀɴɪᴍᴇ ᴀɪɪɴɢ ɪɴғᴏ.
"""
