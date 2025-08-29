import asyncio
from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

from bot import Bot
from config import ADMINS, CHANNEL_ID, DISABLE_CHANNEL_BUTTON
from helper_func import encode
from database.database import is_admin, user_data  # now works with fixed database.py


@Bot.on_message(filters.private & ~filters.command([
    'start', 'users', 'broadcast', 'restart', 'total', 'clear', 'batch', 'genlink', 'stats'
]))
async def channel_post(client: Client, message: Message):
    user_id = message.from_user.id
    if not await is_admin(user_id) and user_id not in ADMINS:
        return

    reply_text = await message.reply_text("Please Wait...!", quote=True)

    try:
        post_message = await message.copy(
            chat_id=client.db_channel.id,
            disable_notification=True
        )
    except FloodWait as e:
        await asyncio.sleep(e.x)
        post_message = await message.copy(
            chat_id=client.db_channel.id,
            disable_notification=True
        )
    except Exception as e:
        print(e)
        await reply_text.edit_text("Something went Wrong..!")
        return

    converted_id = post_message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"

    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]]
    )

    await reply_text.edit(
        f"<b>🎀 Heading\n\n🔐 Premium Link: {link}</b>",
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )

    if not DISABLE_CHANNEL_BUTTON:
        await post_message.edit_reply_markup(reply_markup)


@Bot.on_message(filters.channel & filters.incoming & filters.chat(CHANNEL_ID))
async def new_post(client: Client, message: Message):
    if DISABLE_CHANNEL_BUTTON:
        return

    converted_id = message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"https://t.me/{client.username}?start={base64_string}"

    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔁 Share URL", url=f'https://telegram.me/share/url?url={link}')]]
    )

    try:
        await message.edit_reply_markup(reply_markup)
    except Exception as e:
        print(e)
        pass
