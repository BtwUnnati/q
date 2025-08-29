#@Nation_bots

from pyrogram import Client, filters, enums
from pyrogram.types import ChatJoinRequest, Message 
from database.join_reqs1 import JoinReqs1
from database.database import is_admin
from config import ADMINS, FORCE_SUB_CHANNEL

db1 = JoinReqs1

@Client.on_chat_join_request(filters.chat(FORCE_SUB_CHANNEL if FORCE_SUB_CHANNEL else "self"))
async def join_reqs1(client, join_req1: ChatJoinRequest):

    if db1().isActive():
        user_id = join_req1.from_user.id
        first_name = join_req1.from_user.first_name
        username = join_req1.from_user.username
        date = join_req1.date

        await db1().add_user(
            user_id=user_id,
            first_name=first_name,
            username=username,
            date=date
        )

@Client.on_message(filters.command('total1'))
async def total_requests(client, message):
    user_id = message.from_user.id
    is_user_admin = await is_admin(user_id)
    if not is_user_admin and user_id not in ADMINS:        
        return

    if db1().isActive():
        total = db1().get_all_users_count()
        await message.reply_text(
            text=f"Total Requests: {total} ",
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )


@Client.on_message(filters.command('clear1'))
async def purge_requests(client, message):
    user_id = message.from_user.id
    is_user_admin = is_admin(user_id)
    if not is_user_admin and user_id not in ADMINS:        
        return
    
    if db1().isActive():
        db1().delete_all_users()
        await message.reply_text(
            text="Cleared All Requests 🧹",
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        
