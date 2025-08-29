# plugins/start.py
import os, sys, asyncio, time
from aiohttp import ClientSession
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait
from bot import Bot
from config import (
    ADMINS, OWNER_ID, FORCE_MSG, START_MSG, CUSTOM_CAPTION,
    DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, BOT_USERNAME
)
from helper_func import (
    is_subscribed1, is_subscribed2, is_subscribed3,
    subscribed1, subscribed2, subscribed3,
    encode, decode, get_messages, get_shortlink,
    get_verify_status, update_verify_status, get_exp_time,
    encode_link_to_base64, fetch_encrypted_url
)
from database.database import (
    add_user, del_user, full_userbase, present_user,
    is_admin, get_user, expire_premium_user, user_data
)

# -------------------------------------------------------------------
# BharatPe credentials
BHARATPE_API_TOKEN = "bcc467040e43979777b03881bf2916"
BHARATPE_MERCHANT_ID = "56433931"
# -------------------------------------------------------------------

WAIT_MSG = "<b>Processing...</b>"
REPLY_ERROR = "<code>Use this command as a reply to a message.</code>"

# -------------------- PAYMENT POLLER --------------------
async def poll_payment_status(user_id, txn_id):
    """Poll BharatPe API until payment success."""
    async with ClientSession() as session:
        url = f"https://api.bharatpe.in/transaction/{txn_id}"  # BharatPe transaction status endpoint
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {BHARATPE_API_TOKEN}"
        }

        for _ in range(30):  # 30 attempts = ~5 minutes
            await asyncio.sleep(10)  # check every 10 sec
            try:
                async with session.get(url, headers=headers) as resp:
                    data = await resp.json()
            except Exception:
                continue

            status = data.get("status")
            if status == "SUCCESS":
                # Update DB
                user_data.update_one(
                    {"_id": user_id}, {"$set": {"premium": True}}, upsert=True
                )
                # Notify user
                try:
                    await Bot().send_message(
                        user_id,
                        "✅ Payment received! You are now a Premium User 🎉"
                    )
                except:
                    pass
                break
# --------------------------------------------------------

# BUY PREMIUM CALLBACK
@Bot.on_callback_query(filters.regex("buy_premium"))
async def buy_premium_callback(client: Bot, cq: CallbackQuery):
    user_id = cq.from_user.id
    txn_id = f"TXN_{user_id}_{int(time.time())}"

    async with ClientSession() as session:
        url = "https://api.bharatpe.in/payment/merchant/create"   # BharatPe payment link endpoint
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {BHARATPE_API_TOKEN}"
        }
        payload = {
            "amount": 5900,  # = ₹59.00 (paise me dena hota hai)
            "currency": "INR",
            "merchantId": BHARATPE_MERCHANT_ID,
            "transactionId": txn_id
        }
        async with session.post(url, headers=headers, json=payload) as resp:
            data = await resp.json()

    payment_url = data.get("payment_url", "https://bharatpe.com")

    btn = [[InlineKeyboardButton("💳 Pay ₹59", url=payment_url)]]
    await cq.message.reply(
        f"💳 <b>Payment Link Generated!</b>\n\nClick below to pay <b>₹59</b> and unlock premium instantly.\n\nTransaction ID: <code>{txn_id}</code>",
        reply_markup=InlineKeyboardMarkup(btn)
    )
    await cq.answer()

    # Start polling in background
    asyncio.create_task(poll_payment_status(user_id, txn_id))


# -------------------- START COMMAND --------------------
async def delete_after_delay(message: Message, delay):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except:
        pass

@Bot.on_message(filters.command('start') & filters.private & subscribed1 & subscribed2 & subscribed3)
async def start_command(client: Bot, message: Message):
    uid = message.from_user.id

    if not await present_user(uid):
        try:
            await add_user(uid)
        except Exception:
            pass

    premium_user_data = await get_user(uid) or {"premium": False}
    if premium_user_data.get("premium", False):
        await expire_premium_user(uid, message)

    user_data_doc = await get_user(uid) or {"premium": False}

    if user_data_doc.get('premium', False) or uid == OWNER_ID:
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("About Me", callback_data="about"),
             InlineKeyboardButton("Close", callback_data="close")]
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
        btn = [[InlineKeyboardButton("✨ GET PREMIUM ACCESS", callback_data="buy_premium")]]
        await message.reply(
            f"<b>⚠️ Premium Access Required ⚠️</b>\n\nThis link requires premium access.\n\nUpgrade now to unlock all content for just ₹59!",
            reply_markup=InlineKeyboardMarkup(btn),
            protect_content=False,
            quote=True
        )


# -------------------- NOT JOINED HANDLER --------------------
@Bot.on_message(filters.command('start') & filters.private)
async def not_joined(client: Bot, message: Message):
    user_id = message.from_user.id
    sub1 = await is_subscribed1(None, client, message)
    sub2 = await is_subscribed2(None, client, message)
    sub3 = await is_subscribed3(None, client, message)

    buttons = []
    try:
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
        pass

    try:
        buttons.append([InlineKeyboardButton(
            text='Try Again',
            url=f"https://t.me/{client.username}?start={message.command[1]}")])
    except IndexError:
        pass

    await message.reply(
        text=FORCE_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=None if not message.from_user.username else '@' + message.from_user.username,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True,
        disable_web_page_preview=True
    )
