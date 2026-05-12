from pyrogram import filters
from QueenNoxi import DEMONS, DEV_USERS, DRAGONS

class CustomFilters:
    support_filter = filters.create(lambda _, __, m: bool(m.from_user and m.from_user.id in DEMONS))
    sudo_filter = filters.create(lambda _, __, m: bool(m.from_user and m.from_user.id in DRAGONS))
    dev_filter = filters.create(lambda _, __, m: bool(m.from_user and m.from_user.id in DEV_USERS))

    @staticmethod
    def mime_type(mimetype):
        return filters.create(lambda _, __, m: bool(m.document and m.document.mime_type == mimetype))

    has_text = filters.create(lambda _, __, m: bool(
        m.text or m.sticker or m.photo or m.document or m.video
    ))
