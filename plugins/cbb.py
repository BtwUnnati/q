#(©)Codexbotz

from pyrogram import __version__
from bot import Bot
from config import OWNER_ID, BUY_URL, BUY_TEXT, ADMIN_URL, CONTACT_USERNAME
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "about":
        await query.message.edit_text(
            text=(
                "<b>⟦⟧ Hi there! 👋\n"
                "┏━━━━━━━❪❂❫━━━━━━━\n"
                f"◈ Creator : @{CONTACT_USERNAME}\n"
                "◈ Language : Python 3\n"
                "◈ Library : <a href='https://github.com/pyrogram/pyrogram'>Pyrogram</a>\n"
                "◈ My Server : VPS Server\n"
                f"◈ Developer : @{CONTACT_USERNAME}\n"
                "┗━━━━━━━❪❂❫━━━━━━━</b>"
            ),
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Close", callback_data = "close")
                    ]
                ]
            )
        )
    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass

    elif data == "buy_prem":
        await query.message.edit_text(
            text=f"{BUY_TEXT}",
            disable_web_page_preview=True,
            reply_markup = InlineKeyboardMarkup(
                [   
                    [
                        InlineKeyboardButton("Buy Prime Membership", url=(BUY_URL))
                    ],
                    [
                        InlineKeyboardButton("Help & Support", url=(ADMIN_URL))
                    ],
                    [
                        InlineKeyboardButton("🔒 Close", callback_data = "close")
                    ]
                ]
            )
            )
