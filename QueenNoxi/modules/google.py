import glob
import io
import os
import re
import urllib
import urllib.request
import bs4
import requests
from bing_image_downloader import downloader
from bs4 import BeautifulSoup
from PIL import Image
from search_engine_parser import GoogleSearch

from pyrogram import filters
from pyrogram.types import InputMediaPhoto
from QueenNoxi import pbot as app

opener = urllib.request.build_opener()
useragent = "Mozilla/5.0 (Linux; Android 11; SM-M017F Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.157 Mobile Safari/537.36"
opener.addheaders = [("User-agent", useragent)]

@app.on_message(filters.command("google"))
async def _(_, message):
    if getattr(message, "forward_from", None):
        return

    webevent = await message.reply("Searching...")
    match = message.text.split(None, 1)[1] if len(message.command) > 1 else ""
    if not match:
        return await webevent.edit("Please provide a query.")
        
    page = re.findall(r"page=\d+", match)
    try:
        page_num = int(page[0].replace("page=", ""))
        match = match.replace("page=" + page[0], "")
    except (IndexError, ValueError):
        page_num = 1
        
    search_args = (str(match), page_num)
    gsearch = GoogleSearch()
    gresults = await gsearch.async_search(*search_args)
    msg = ""
    for i in range(len(gresults["links"])):
        try:
            title = gresults["titles"][i]
            link = gresults["links"][i]
            desc = gresults["descriptions"][i]
            msg += f"❍[{title}]({link})\n**{desc}**\n\n"
        except IndexError:
            break
            
    await webevent.edit("**Search Query:**\n`" + match + "`\n\n**Results:**\n" + msg, disable_web_page_preview=True)

@app.on_message(filters.command("img"))
async def img_sampler(_, message):
    if getattr(message, "forward_from", None):
        return

    query = message.text.split(None, 1)[1] if len(message.command) > 1 else ""
    if not query:
        return
        
    jit = f'"{query}"'
    downloader.download(
        jit,
        limit=4,
        output_dir="store",
        adult_filter_off=False,
        force_replace=False,
        timeout=60,
    )
    
    query_dir = f'./store/{query}'
    
    if os.path.exists(query_dir):
        types = ("*.png", "*.jpeg", "*.jpg")
        files_grabbed = []
        for tk in types:
            files_grabbed.extend(glob.glob(os.path.join(query_dir, tk)))
            
        if files_grabbed:
            media_group = [InputMediaPhoto(f) for f in files_grabbed]
            try:
                await app.send_media_group(message.chat.id, media=media_group, reply_to_message_id=message.id)
            except Exception:
                pass
    os.system("rm -rf store")

@app.on_message(filters.command(["reverse", "pp", "grs"]))
async def okgoogle(_, message):
    if os.path.isfile("okgoogle.png"):
        os.remove("okgoogle.png")

    r_message = message.reply_to_message
    if r_message and r_message.media:
        dev = await message.reply("`Processing...`")
        photo = await r_message.download("okgoogle.png")
    else:
        return await message.reply("`Reply to photo or sticker fu*ker`")

    if photo:
        try:
            image = Image.open(photo)
            image.save("okgoogle.png", "PNG")
            image.close()
        except OSError:
            await dev.edit("`Unsupported sexuality, most likely.`")
            return
            
        searchUrl = "https://www.google.com/searchbyimage/upload"
        multipart = {"encoded_image": ("okgoogle.png", open("okgoogle.png", "rb")), "image_content": ""}
        response = requests.post(searchUrl, files=multipart, allow_redirects=False)
        fetchUrl = response.headers.get("Location")

        if response.status_code != 400 and fetchUrl:
            await dev.edit("`Image successfully uploaded to Google. Maybe.`\n`Parsing source now. Maybe.`")
        else:
            return await dev.edit("`Google told me to fu*k off.`")

        os.remove("okgoogle.png")
        match_data = await ParseSauce(fetchUrl + "&preferences?hl=en&fg=1#languages")
        guess = match_data.get("best_guess")
        imgspage = match_data.get("similar_images")

        if guess and imgspage:
            await dev.edit(f"[{guess}]({fetchUrl})\n\n`Looking for this Image...`", disable_web_page_preview=True)
        else:
            return await dev.edit("`Can't find this piece of shit.`")

        lim = 3
        if len(message.command) > 1:
            try:
                lim = int(message.command[1])
            except ValueError:
                pass
                
        images = await scam(match_data, lim)
        yeet = []
        for i in images:
            try:
                k = requests.get(i)
                temp_file = f"temp_{images.index(i)}.jpg"
                with open(temp_file, "wb") as f:
                    f.write(k.content)
                yeet.append(temp_file)
            except Exception:
                pass
                
        if yeet:
            media_group = [InputMediaPhoto(f) for f in yeet]
            try:
                await app.send_media_group(message.chat.id, media=media_group, reply_to_message_id=message.id)
            except Exception:
                pass
            for f in yeet:
                if os.path.exists(f):
                    os.remove(f)
                    
        await dev.edit(f"[{guess}]({fetchUrl})\n\n[Visually similar images]({imgspage})", disable_web_page_preview=True)


async def ParseSauce(googleurl):
    source = opener.open(googleurl).read()
    soup = BeautifulSoup(source, "html.parser")
    results = {"similar_images": "", "best_guess": ""}
    try:
        for similar_image in soup.findAll("input", {"class": "gLFyf"}):
            url = "https://www.google.com/search?tbm=isch&q=" + urllib.parse.quote_plus(similar_image.get("value"))
            results["similar_images"] = url
    except BaseException:
        pass
    for best_guess in soup.findAll("div", attrs={"class": "r5a77d"}):
        results["best_guess"] = best_guess.get_text()
    return results

async def scam(results, lim):
    single = opener.open(results["similar_images"]).read()
    decoded = single.decode("utf-8")
    imglinks = []
    counter = 0
    pattern = r"^,\[\"(.*[.png|.jpg|.jpeg])\",[0-9]+,[0-9]+\]$"
    oboi = re.findall(pattern, decoded, re.I | re.M)
    for imglink in oboi:
        counter += 1
        if counter < int(lim):
            imglinks.append(imglink)
        else:
            break
    return imglinks

@app.on_message(filters.command("app"))
async def apk(_, message):
    try:
        app_name = message.text.split(None, 1)[1] if len(message.command) > 1 else ""
        if not app_name:
            return await message.reply("Please specify an app name.")
            
        remove_space = app_name.split(" ")
        final_name = "+".join(remove_space)
        page = requests.get("https://play.google.com/store/search?q=" + final_name + "&c=apps")
        soup = bs4.BeautifulSoup(page.content, "html.parser", from_encoding="utf-8")
        results = soup.findAll("div", "ZmHEEd")
        app_name = results[0].findNext("div", "Vpfmgd").findNext("div", "WsMG1c nnK0zc").text
        app_dev = results[0].findNext("div", "Vpfmgd").findNext("div", "KoLSrc").text
        app_dev_link = "https://play.google.com" + results[0].findNext("div", "Vpfmgd").findNext("a", "mnKHRc")["href"]
        app_rating = results[0].findNext("div", "Vpfmgd").findNext("div", "pf5lIe").find("div")["aria-label"]
        app_link = "https://play.google.com" + results[0].findNext("div", "Vpfmgd").findNext("div", "vU6FJ p63iDd").a["href"]
        app_icon = results[0].findNext("div", "Vpfmgd").findNext("div", "uzcko").img["data-src"]
        
        app_details = "<a href='" + app_icon + "'>📲&#8203;</a> <b>" + app_name + "</b>\n\n"
        app_details += "<code>Developer :</code> <a href='" + app_dev_link + "'>" + app_dev + "</a>\n"
        app_details += "<code>Rating :</code> " + app_rating.replace("Rated ", "⭐ ").replace(" out of ", "/").replace(" stars", "", 1).replace(" stars", "⭐ ").replace("five", "5") + "\n"
        app_details += "<code>Features :</code> <a href='" + app_link + "'>View in Play Store</a>\n\n===> Group Controller<==="
        await message.reply(app_details, disable_web_page_preview=False)
    except IndexError:
        await message.reply("No result found in search. Please enter **Valid app name**")
    except Exception as err:
        await message.reply("Exception Occured:- " + str(err))

__mod_name__ = "Gᴏᴏɢʟᴇ"
__help__ = """
 ❍ /google <text>*:* Perform a google search
 ❍ /img <text>*:* Search Google for images and returns them
 ❍ /app <appname>*:* Searches for an app in Play Store and returns its details.
 ❍ /reverse |pp |grs: Does a reverse image search of the media which it was replied to.
"""
