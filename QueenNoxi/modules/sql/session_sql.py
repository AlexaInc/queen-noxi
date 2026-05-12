import threading
from sqlalchemy import Column, String, Text
from QueenNoxi.modules.sql import BASE, SESSION

class SessionStore(BASE):
    __tablename__ = "sessions"
    bot_id = Column(String(50), primary_key=True)
    session_string = Column(Text)

    def __init__(self, bot_id, session_string):
        self.bot_id = str(bot_id)
        self.session_string = session_string

SessionStore.__table__.create(BASE.metadata.bind, checkfirst=True)
SESSION_LOCK = threading.RLock()

def get_session(bot_id):
    try:
        res = SESSION.query(SessionStore).get(str(bot_id))
        return res.session_string if res else None
    finally:
        SESSION.close()

def save_session(bot_id, session_string):
    with SESSION_LOCK:
        curr = SESSION.query(SessionStore).get(str(bot_id))
        if curr:
            curr.session_string = session_string
        else:
            curr = SessionStore(bot_id, session_string)
            SESSION.add(curr)
        SESSION.commit()

def delete_session(bot_id):
    with SESSION_LOCK:
        curr = SESSION.query(SessionStore).get(str(bot_id))
        if curr:
            SESSION.delete(curr)
            SESSION.commit()
