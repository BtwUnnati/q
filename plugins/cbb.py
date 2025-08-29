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
                        InlineKeyboardButton("Buy Prime Membership", callback_data="buy_premium")
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
##Auto Payment 
init_db()
app = Client("bharatpe_bot", api_id=APP_ID, api_hash=API_HASH, bot_token=TG_BOT_TOKEN)

def fmt_time_left(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    return f"{m:02d}:{s:02d}"

@app.on_callback_query(filters.regex("buy_premium"))
async def buy_premium(_, cq):
    user_id = cq.from_user.id
    payment = create_payment(user_id)
    txn_id = payment.get("txnId")
    pay_url = payment.get("qrUrl") or payment.get("url")

    start_time = int(time.time())
    expire_time = start_time + PAY_WINDOW

    msg = await cq.message.reply(
        f"💰 Please pay ₹{PREMIUM_PRICE} via Any Upi Payment Apps :\n\n{pay_url}\n\n"
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
                    f"💰 Please pay ₹{PREMIUM_PRICE} via any upi payment app:\n\n{pay_url}\n\n"
                    f"⏳ Time left: {fmt_time_left(left)}",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Pay Now", url=pay_url)]])
                )
            except:
                pass

            await asyncio.sleep(15)

    app.loop.create_task(monitor_payment())

app.run()

