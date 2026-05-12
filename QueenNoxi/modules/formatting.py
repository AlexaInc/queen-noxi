from pyrogram import filters, Client
from QueenNoxi import pbot

__mod_name__ = "Formatting"

__help__ = """
You can use the following placeholders to personalize your welcome, filters, or notes:

**User Info:**
• `{first}`: The user's first name.
• `{last}`: The user's last name (or first name if empty).
• `{fullname}`: The user's full name.
• `{username}`: The user's @username (or mention if empty).
• `{id}`: The user's ID.
• `{mention}`: A clickable mention of the user.

**Chat Info:**
• `{chatname}`: The name of the current group.
• `{rules}`: A clickable link to the group rules.

**Advanced Control Tags:**
• `{preview}`: Enables link previews (enabled by default unless this is absent).
• `{nonotif}`: Sends the message without a notification sound.
• `{protect}`: Prevents the message from being forwarded or screenshotted.
• `{mediaspoiler}`: Hides the photo/video behind a spoiler blur (if applicable).

**Buttons:**
• `[Button Text](buttonurl://link)`: Creates a URL button.
• `[Button Text](buttonurl#danger://link)`: Creates a Red (danger) button.
• `[Button Text](buttonurl#success://link)`: Creates a Green (success) button.
• `[Button Text](buttonurl#primary://link)`: Creates a Blue (primary) button.
• `[Button Text](buttonurl://btn_next)`: Creates a "Next" navigation button.
• `[Button Text](buttonurl://btn_back)`: Creates a "Back" navigation button.

**Note on Previews:**
Link previews are **DISABLED** by default. To enable them, include `{preview}` anywhere in your message.
"""
