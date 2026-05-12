import regex
from pyrogram import filters, Client, enums
from pyrogram.types import Message
from pyrogram.errors import RPCError

from QueenNoxi import LOGGER, pbot
from QueenNoxi.modules.helper_funcs.regex_helper import infinite_loop_check

DELIMITERS = ("/", ":", "|", "_")

def separate_sed(sed_string):
    if (
        len(sed_string) >= 3
        and sed_string[1] in DELIMITERS
        and sed_string.count(sed_string[1]) >= 2
    ):
        delim = sed_string[1]
        start = counter = 2
        while counter < len(sed_string):
            if sed_string[counter] == "\\":
                counter += 1
            elif sed_string[counter] == delim:
                replace = sed_string[start:counter]
                counter += 1
                start = counter
                break
            counter += 1
        else:
            return None

        while counter < len(sed_string):
            if (
                sed_string[counter] == "\\"
                and counter + 1 < len(sed_string)
                and sed_string[counter + 1] == delim
            ):
                sed_string = sed_string[:counter] + sed_string[counter + 1 :]
            elif sed_string[counter] == delim:
                replace_with = sed_string[start:counter]
                counter += 1
                break
            counter += 1
        else:
            return replace, sed_string[start:], ""

        flags = ""
        if counter < len(sed_string):
            flags = sed_string[counter:]
        return replace, replace_with, flags.lower()
    return None

@pbot.on_message(filters.regex(r"s([{}]).*?\1.*".format("".join(DELIMITERS))) & filters.group)
async def sed(client: Client, message: Message):
    sed_result = separate_sed(message.text)
    if not sed_result or not message.reply_to_message:
        return

    to_fix = message.reply_to_message.text or message.reply_to_message.caption
    if not to_fix:
        return

    repl, repl_with, flags = sed_result
    if not repl:
        await message.reply_text("You're trying to replace... nothing with something?")
        return

    try:
        if infinite_loop_check(repl):
            await message.reply_text("I'm afraid I can't run that regex.")
            return

        count = 0 if "g" in flags else 1
        regex_flags = regex.I if "i" in flags else 0
        
        text = regex.sub(repl, repl_with, to_fix, count=count, flags=regex_flags, timeout=3).strip()
        
        if text:
            await message.reply_to_message.reply_text(text)
            
    except TimeoutError:
        await message.reply_text("Regex timeout.")
    except Exception as e:
        LOGGER.warning(f"Sed error: {e}")
        await message.reply_text("Do you even sed? Apparently not.")

__mod_name__ = "Sᴇᴅ"
