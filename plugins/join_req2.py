#@Nation_bots

from pyrogram import Client, filters, enums
from pyrogram.types import ChatJoinRequest, Message 
from database.join_reqs2 import JoinReqs2
from database.database import is_admin
from config import ADMINS, FORCE_SUB_CHANNEL2

db2 = JoinReqs2

@Client.on_chat_join_request(filters.chat(FORCE_SUB_CHANNEL2 if FORCE_SUB_CHANNEL2 else "self"))
async def join_reqs(client, join_req2: ChatJoinRequest):

    if db2().isActive():
        user_id = join_req2.from_user.id
        first_name = join_req2.from_user.first_name
        username = join_req2.from_user.username
        date = join_req2.date

        await db2().add_user(
            user_id=user_id,
            first_name=first_name,
            username=username,
            date=date
        )

@Client.on_message(filters.command('total2'))
async def total_requests(client, message):
    user_id = message.from_user.id
    is_user_admin = await is_admin(user_id)
    if not is_user_admin and user_id not in ADMINS:        
        return

    if db2().isActive():
        total = db2().get_all_users_count()
        await message.reply_text(
            text=f"Total Requests: {total} ",
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )


@Client.on_message(filters.command('clear2'))
async def purge_requests(client, message):
    user_id = message.from_user.id
    is_user_admin = is_admin(user_id)
    if not is_user_admin and user_id not in ADMINS:        
        return
    
    if db2().isActive():
        db2().delete_all_users()
        await message.reply_text(
            text="Cleared All Requests 🧹",
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        
