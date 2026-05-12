import io
import os
import textwrap
import traceback
from contextlib import redirect_stdout

from pyrogram import filters, Client, enums
from pyrogram.types import Message

from QueenNoxi import LOGGER, pbot, OWNER_ID
from QueenNoxi.modules.helper_funcs.chat_status import dev_plus

namespaces = {}


def namespace_of(chat, message, client):
    if chat not in namespaces:
        namespaces[chat] = {
            "__builtins__": globals()["__builtins__"],
            "client": client,
            "pbot": pbot,
            "message": message,
            "user": message.from_user,
            "chat": message.chat,
        }

    return namespaces[chat]


async def send(msg, message: Message):
    if len(str(msg)) > 4000:
        with io.BytesIO(str.encode(msg)) as out_file:
            out_file.name = "output.txt"
            await message.reply_document(document=out_file, caption="Output too long, sent as file.")
    else:
        await message.reply_text(f"```python\n{msg}```", parse_mode=enums.ParseMode.MARKDOWN)


@pbot.on_message(filters.command(["e", "eval"]) & filters.user(OWNER_ID))
@dev_plus
async def evaluate(client: Client, message: Message):
    await send(await do(eval, client, message), message)


@pbot.on_message(filters.command(["x", "ex", "exec", "py"]) & filters.user(OWNER_ID))
@dev_plus
async def execute(client: Client, message: Message):
    await send(await do(exec, client, message), message)


def cleanup_code(code):
    if code.startswith("```") and code.endswith("```"):
        return "\n".join(code.split("\n")[1:-1])
    return code.strip("` \n")


async def do(func, client, message):
    content = message.text.split(None, 1)[-1]
    body = cleanup_code(content)
    env = namespace_of(message.chat.id, message, client)

    stdout = io.StringIO()

    to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

    try:
        exec(to_compile, env)
    except Exception as e:
        return f"{e.__class__.__name__}: {e}"

    func = env["func"]

    try:
        with redirect_stdout(stdout):
            func_return = await func()
    except Exception:
        value = stdout.getvalue()
        return f"{value}{traceback.format_exc()}"
    else:
        value = stdout.getvalue()
        result = None
        if func_return is None:
            if value:
                result = f"{value}"
            else:
                try:
                    result = f"{repr(eval(body, env))}"
                except:
                    pass
        else:
            result = f"{value}{func_return}"
        if result:
            return result
        return "Clean execution (No output)"


@pbot.on_message(filters.command("clearlocals") & filters.user(OWNER_ID))
@dev_plus
async def clear_locals(client: Client, message: Message):
    global namespaces
    if message.chat.id in namespaces:
        del namespaces[message.chat.id]
    await message.reply_text("Locals cleared for this chat.")


__mod_name__ = "Eᴠᴀʟ"
__help__ = """
★ᴏᴡɴᴇʀ ᴄᴍᴅ ★
 ❍ /eval: ᴇᴠᴀʟᴜᴀᴛᴇ ᴘʏᴛʜᴏɴ ᴄᴏᴅᴇ
 ❍ /exec: ᴇxᴇᴄᴜᴛᴇ ᴘʏᴛʜᴏɴ ᴄᴏᴅᴇ
 ❍ /clearlocals: ᴄʟᴇᴀʀ ʟᴏᴄᴀʟ variables
"""
