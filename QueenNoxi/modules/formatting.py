from pyrogram import filters, Client
from QueenNoxi import pbot

__mod_name__ = "Formatting"

__help__ = """
Personalize your welcome, filters, or notes with these placeholders:

**User Info:**
• `{first}`: First name.
• `{last}`: Last name.
• `{fullname}`: Full name.
• `{username}`: @username.
• `{id}`: User ID.
• `{mention}`: Mention user.

**Chat Info:**
• `{chatname}`: Group name.
• `{rules}`: Link to rules.

**Control Tags:**
• `{preview}`: Enable link previews.
• `{nonotif}`: Muted message.
• `{protect}`: Prevent forward/screenshot.
• `{mediaspoiler}`: Blur media.

**Buttons:**
• `[Text](buttonurl://link)`: URL button.
• `[Text](buttonurl#danger://link)`: Red button.
• `[Text](buttonurl#success://link)`: Green button.
• `[Text](buttonurl#primary://link)`: Blue button.
• `[Text](buttonurl://btn_next)`: Next page.
• `[Text](buttonurl://btn_back)`: Previous page.

**Note:** Previews are **DISABLED** by default. Use `{preview}` to enable.
"""
