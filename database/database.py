import time
import pymongo
from pyrogram.types import Message
from config import DB_URI, DB_NAME
import sqlite3


#autopay Bharat 
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        is_premium INTEGER DEFAULT 0
    )""")
    conn.commit()
    conn.close()

def set_premium(user_id: int):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (user_id, is_premium) VALUES (?, 1)", (user_id,))
    conn.commit()
    conn.close()

def is_premium(user_id: int) -> bool:
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT is_premium FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row and row[0] == 1



# Owner Telegram ID
OWNER_ID = 7089574265
    
# Mongo setup
dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]

user_data = database['users']
puser_collection = database["puser"]
admins_collection = database['admins']


# ----- USER FUNCTIONS -----
def new_user(id):
    return {'_id': id, 'premium': False, 'verified': False}


async def present_user(user_id: int):
    return bool(user_data.find_one({'_id': user_id}))


async def get_user(user_id: int):
    return user_data.find_one({'_id': user_id})


async def add_user(user_id: int):
    user = new_user(user_id)
    user_data.insert_one(user)


async def full_userbase():
    return [doc['_id'] for doc in user_data.find()]


async def del_user(user_id: int):
    user_data.delete_one({'_id': user_id})


# ----- ADMIN FUNCTIONS -----
async def add_admin(user_id: int):
    try:
        admins_collection.insert_one({'_id': user_id})
        return True
    except:
        return False


async def remove_admin(user_id: int):
    try:
        admins_collection.delete_one({'_id': user_id})
        return True
    except:
        return False


async def is_admin(user_id: int):
    return bool(admins_collection.find_one({'_id': user_id}))


async def get_admin_list():
    return [doc['_id'] for doc in admins_collection.find()]


# ----- PREMIUM FUNCTIONS -----
async def expire_premium_user(user_id: int, message: Message):
    current_ts = int(time.time())
    puser = puser_collection.find_one({"user_id": user_id})
    if puser and puser.get("expire_timestamp", 0) < current_ts:
        user_data.update_one({"_id": user_id}, {"$set": {"premium": False}})
        puser_collection.delete_one({"user_id": user_id})
        await message.reply("🎀 Your Premium Membership has expired ❗")
    else:
        user_data.update_one({"_id": user_id}, {"$set": {"premium": False}})


# ----- VERIFY FUNCTIONS -----
async def db_verify_status(user_id: int):
    user = user_data.find_one({"_id": user_id})
    if user:
        return user.get("verified", False)
    return False


async def db_update_verify_status(user_id: int, status: bool):
    user_data.update_one({"_id": user_id}, {"$set": {"verified": status}}, upsert=True)
