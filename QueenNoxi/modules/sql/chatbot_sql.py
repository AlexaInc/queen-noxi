import threading

from sqlalchemy import Column, String

from QueenNoxi.modules.sql import BASE, SESSION


class QueenNoxiChats(BASE):
    __tablename__ = "queennoxi_chats"
    chat_id = Column(String(14), primary_key=True)

    def __init__(self, chat_id):
        self.chat_id = chat_id


QueenNoxiChats.__table__.create(BASE.metadata.bind, checkfirst=True)
INSERTION_LOCK = threading.RLock()


def is_queennoxi(chat_id):
    try:
        chat = SESSION.query(QueenNoxiChats).get(str(chat_id))
        return bool(chat)
    finally:
        SESSION.close()


def set_queennoxi(chat_id):
    with INSERTION_LOCK:
        queennoxichat = SESSION.query(QueenNoxiChats).get(str(chat_id))
        if not queennoxichat:
            queennoxichat = QueenNoxiChats(str(chat_id))
        SESSION.add(queennoxichat)
        SESSION.commit()


def rem_queennoxi(chat_id):
    with INSERTION_LOCK:
        queennoxichat = SESSION.query(QueenNoxiChats).get(str(chat_id))
        if queennoxichat:
            SESSION.delete(queennoxichat)
        SESSION.commit()
