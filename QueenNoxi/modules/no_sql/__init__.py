from motor.motor_asyncio import AsyncIOMotorClient as MongoCli
from pymongo import MongoClient, collection
from pymongo.errors import PyMongoError
from QueenNoxi import MONGO_DB_URI

# ── Motor async client (used by users_db, chats_db, gban_db) ─────────────────
mongo = MongoCli(MONGO_DB_URI)
QueenNoxidb = mongo.MUK_ROB

# ── Sync client for legacy MongoDB class ─────────────────────────────────────
try:
    client = MongoClient(MONGO_DB_URI)
except PyMongoError:
    exit(1)
main_db = client["QUEEN_NOXI_DB"]
QueenNoxiXdb = main_db

# Sub-module imports AFTER QueenNoxidb is defined to avoid circular imports
from QueenNoxi.modules.no_sql.users_db import *
from QueenNoxi.modules.no_sql.chats_db import *
from QueenNoxi.modules.no_sql.gban_db import *


def get_collection(name: str) -> collection:
    """Get the collection from database."""
    return QueenNoxiXdb[name]


class MongoDB:
    """Class for interacting with Bot database."""

    def __init__(self, collection_name) -> None:
        self.collection = QueenNoxiXdb[collection_name]

    def insert_one(self, document):
        result = self.collection.insert_one(document)
        return repr(result.inserted_id)

    def find_one(self, query):
        result = self.collection.find_one(query)
        return result if result else False

    def find_all(self, query=None):
        if query is None:
            query = {}
        return list(self.collection.find(query))

    def count(self, query=None):
        if query is None:
            query = {}
        return self.collection.count_documents(query)

    def delete_one(self, query):
        self.collection.delete_many(query)
        return self.collection.count_documents({})

    def replace(self, query, new_data):
        old = self.collection.find_one(query)
        _id = old["_id"]
        self.collection.replace_one({"_id": _id}, new_data)
        new = self.collection.find_one({"_id": _id})
        return old, new

    def update(self, query, update):
        result = self.collection.update_one(query, {"$set": update})
        new_document = self.collection.find_one(query)
        return result.modified_count, new_document

    @staticmethod
    def close():
        return client.close()


def __connect_first():
    _ = MongoDB("test")


__connect_first()
