# plugins/start.py
import os
import sys
import asyncio
import time
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

from bot import Bot
from config import (
    ADMINS, OWNER_ID, FORCE_MSG, START_MSG, CUSTOM_CAPTION,
    DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, BOT_USERNAME, 
    APP_ID, API_HASH, TG_BOT_TOKEN, PREMIUM_PRICE, PAY_WINDOW
)
from helper_func import (
    is_subscribed1, is_subscribed2, is_subscribed3,
    subscribed1, subscribed2, subscribed3,
    encode, decode, get_messages, get_shortlink,
    get_verify_status, update_verify_status, get_exp_time,
    encode_link_to_base64, fetch_encrypted_url
)
from database.database import add_user, del_user, full_userbase, present_user, is_admin, get_user, expire_premium_user, init_db, is_premium, set_premium
from plugins.payment import create_payment, check_payment

##Auto Payment 
init_db()
app = Client("bharatpe_bot", api_id=APP_ID, api_hash=API_HASH, bot_token=TG_BOT_TOKEN)

def fmt_time_left(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    return f"{m:02d}:{s:02d}"

@app.on_message(filters.command("start"))
async def start(_, m):
    user_id = m.from_user.id
    if is_premium(user_id):
        await m.reply("✅ You already have Premium Access!")
    else:
        btns = InlineKeyboardMarkup([[InlineKeyboardButton("💎 Buy Premium", callback_data="buy_premium")]])
        await m.reply(
            f"👋 Hello {m.from_user.first_name}!\n\n"
            f"⭐ Premium Plan: ₹{PREMIUM_PRICE}/30 Days\n\n"
            "Click below to unlock Premium instantly 👇",
            reply_markup=btns
        )

@app.on_callback_query(filters.regex("buy_premium"))
async def buy_premium(_, cq):
    user_id = cq.from_user.id
    payment = create_payment(user_id)
    txn_id = payment.get("txnId")
    pay_url = payment.get("qrUrl") or payment.get("url")

    start_time = int(time.time())
    expire_time = start_time + PAY_WINDOW

    msg = await cq.message.reply(
        f"💰 Please pay ₹{PREMIUM_PRICE} via BharatPe:\n\n{pay_url}\n\n"
        f"⏳ Time left: {fmt_time_left(PAY_WINDOW)}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Pay Now", url=pay_url)]])
    )

    async def monitor_payment():
        while True:
            now = int(time.time())
            left = expire_time - now

            if left <= 0:
                await msg.edit_text("❌ Payment not received in 5 minutes. Link expired.")
                return

            # check BharatPe API
            if check_payment(txn_id, user_id):
                set_premium(user_id)
                await msg.edit_text("🎉 Payment received! ✅ You are now a Premium User.")
                return

            # update countdown
            try:
                await msg.edit_text(
                    f"💰 Please pay ₹{PREMIUM_PRICE} via BharatPe:\n\n{pay_url}\n\n"
                    f"⏳ Time left: {fmt_time_left(left)}",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Pay Now", url=pay_url)]])
                )
            except:
                pass

            await asyncio.sleep(15)

    app.loop.create_task(monitor_payment())

app.run()



##END






# utility to auto-delete copies after delay
async def delete_after_delay(message: Message, delay):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except:
        pass

WAIT_MSG = "<b>Processing...</b>"
REPLY_ERROR = "<code>Use this command as a reply to a message.</code>"

@Bot.on_message(filters.command('start') & filters.private & subscribed1 & subscribed2 & subscribed3)
async def start_command(client: Bot, message: Message):
    uid = message.from_user.id

    # ensure user present
    if not await present_user(uid):
        try:
            await add_user(uid)
        except Exception:
            pass

    # always get a dict back so .get won't fail
    premium_user_data = await get_user(uid) or {"premium": False}

    # expire premium if needed
    if premium_user_data.get("premium", False):
        await expire_premium_user(uid, message)

    # refresh user doc
    user_data_doc = await get_user(uid) or {"premium": False}

    if user_data_doc.get('premium', False) or uid == OWNER_ID:
        # handle start payload (channel link based)
        if len(message.text) > 7:
            try:
                base64_string = message.text.split(" ", 1)[1]
                string_decoded = await decode(base64_string)
                argument = string_decoded.split("-")

                if len(argument) == 3:
                    start = int(int(argument[1]) / abs(client.db_channel.id))
                    end = int(int(argument[2]) / abs(client.db_channel.id))
                    ids = range(start, end+1) if start <= end else list(range(start, end-1, -1))
                elif len(argument) == 2:
                    ids = [int(int(argument[1]) / abs(client.db_channel.id))]
                else:
                    return

                temp_msg = await message.reply("Pʟᴇᴀsᴇ ᴡᴀɪᴛ...")
                try:
                    messages = await get_messages(client, ids)
                    await temp_msg.delete()
                    copied_msg = None
                    for msg in messages:
                        caption = CUSTOM_CAPTION.format(
                            previouscaption="" if not msg.caption else msg.caption.html,
                            filename=(msg.document.file_name if msg.document else "")
                        ) if bool(CUSTOM_CAPTION) and getattr(msg, "document", None) else ("" if not msg.caption else msg.caption.html)

                        reply_markup = None if DISABLE_CHANNEL_BUTTON else msg.reply_markup

                        try:
                            copied_msg = await msg.copy(
                                chat_id=message.from_user.id,
                                caption=caption,
                                parse_mode=ParseMode.HTML,
                                reply_markup=reply_markup,
                                protect_content=PROTECT_CONTENT
                            )
                            await asyncio.sleep(0.5)
                            if copied_msg:
                                asyncio.create_task(delete_after_delay(copied_msg, 600))
                        except FloodWait as e:
                            await asyncio.sleep(e.x)
                            copied_msg = await msg.copy(
                                chat_id=message.from_user.id,
                                caption=caption,
                                parse_mode=ParseMode.HTML,
                                reply_markup=reply_markup,
                                protect_content=PROTECT_CONTENT
                            )
                            if copied_msg:
                                asyncio.create_task(delete_after_delay(copied_msg, 600))
                        except Exception:
                            pass
                    if copied_msg:
                        await copied_msg.reply(
                            "<b>⚠️ PLEASE NOTE :\nThis file will be automatically deleted after 10 minutes. ⏳</b>"
                        )
                except Exception:
                    await message.reply_text("Something went wrong while fetching messages.")
                return
            except Exception:
                pass

        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("About Me", callback_data="about"), InlineKeyboardButton("Close", callback_data="close")]
        ])
        await message.reply_text(
            text=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            quote=True
        )
    else:
        # not premium
        btn = [[InlineKeyboardButton("✨ GET PREMIUM ACCESS", callback_data="buy_prem")]]
        await message.reply(
            f"<b>⚠️ Premium Access Required ⚠️</b>\n\nThis link requires premium access to view all files.\n\nUpgrade now to unlock all content!",
            reply_markup=InlineKeyboardMarkup(btn),
            protect_content=False,
            quote=True
        )

# fallback start when subscription filters fail (shows join buttons)
@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Bot, message: Message):
    user_id = message.from_user.id
    sub1 = await is_subscribed1(None, client, message)
    sub2 = await is_subscribed2(None, client, message)
    sub3 = await is_subscribed3(None, client, message)

    buttons = []
    try:
        # dynamic invite links set on Bot init (client.invitelink1/2/3)
        if sub1 and not sub2 and not sub3:
            buttons.append([InlineKeyboardButton(text="Join channel", url=client.invitelink2)])
            buttons.append([InlineKeyboardButton(text="Join channel", url=client.invitelink3)])
        elif sub2 and not sub1 and not sub3:
            buttons.append([InlineKeyboardButton(text="Join channel", url=client.invitelink1)])
            buttons.append([InlineKeyboardButton(text="Join channel", url=client.invitelink3)])
        elif sub3 and not sub1 and not sub2:
            buttons.append([InlineKeyboardButton(text="Join channel", url=client.invitelink1)])
            buttons.append([InlineKeyboardButton(text="Join channel", url=client.invitelink2)])
        elif not sub1 and not sub2 and not sub3:
            buttons.append([InlineKeyboardButton(text="Join channel", url=client.invitelink1)])
            buttons.append([InlineKeyboardButton(text="Join channel", url=client.invitelink2)])
            buttons.append([InlineKeyboardButton(text="Join channel", url=client.invitelink3)])
        elif sub1 and sub2 and not sub3:
            buttons.append([InlineKeyboardButton(text="Join channel", url=client.invitelink3)])
        elif sub1 and sub3 and not sub2:
            buttons.append([InlineKeyboardButton(text="Join channel", url=client.invitelink2)])
        elif sub2 and sub3 and not sub1:
            buttons.append([InlineKeyboardButton(text="Join channel", url=client.invitelink1)])
    except Exception:
        # ignore invite link availability issues
        pass

    try:
        buttons.append([InlineKeyboardButton(text='Try Again', url=f"https://t.me/{client.username}?start={message.command[1]}")])
    except IndexError:
        pass

    await message.reply(
        text = FORCE_MSG.format(
                first = message.from_user.first_name,
                last = message.from_user.last_name,
                username = None if not message.from_user.username else '@' + message.from_user.username,
                mention = message.from_user.mention,
                id = message.from_user.id
            ),
        reply_markup = InlineKeyboardMarkup(buttons),
        quote = True,
        disable_web_page_preview = True
    )

# admin & broadcast commands
@Bot.on_message(filters.command('users') & filters.private)
async def get_users(client: Bot, message: Message):
    user_id = message.from_user.id
    is_user_admin = await is_admin(user_id)
    if not is_user_admin and user_id != OWNER_ID:
        return
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG)
    users = await full_userbase()
    await msg.edit(f"{len(users)} users are using this bot")

@Bot.on_message(filters.command('broadcast') & filters.private)
async def send_text(client: Bot, message: Message):
    user_id = message.from_user.id
    is_user_admin = await is_admin(user_id)
    if not is_user_admin and user_id != OWNER_ID:
        return
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total = successful = blocked = deleted = unsuccessful = 0
        pls_wait = await message.reply("<i>Broadcast running...</i>")
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                try:
                    await broadcast_msg.copy(chat_id)
                    successful += 1
                except:
                    unsuccessful += 1
            except Exception:
                try:
                    await del_user(chat_id)
                except:
                    pass
                unsuccessful += 1
            total += 1
        status = f"""<b><u>Broadcast Completed</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked/Removed/Unsuccessful: <code>{unsuccessful}</code></b>"""
        return await pls_wait.edit(status)
    else:
        msg = await message.reply(REPLY_ERROR)
        await asyncio.sleep(8)
        await msg.delete()

# restart by owner
@Bot.on_message(filters.private & filters.command("restart") & filters.user(OWNER_ID))
async def restart_bot(b, m):
    restarting_message = await m.reply_text(f"⚡️<b><i>Restarting....</i></b>", disable_notification=True)
    await asyncio.sleep(3)
    await restarting_message.edit_text("✅ <b><i>Successfully Restarted</i></b>")
    os.execl(sys.executable, sys.executable, *sys.argv)
