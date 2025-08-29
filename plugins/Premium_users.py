from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime, timedelta
import pytz
import time

from bot import Bot
from database import user_data, puser_collection, OWNER_ID
from config import PREMIUM_CHANNEL_ID

INDIA_TZ = pytz.timezone("Asia/Kolkata")


@Bot.on_message(filters.command('approve') & filters.private)
async def approve_premium(client: Client, message: Message):
    user_id = message.from_user.id

    # Only bot owner can approve
    if user_id != OWNER_ID:
        await message.reply("❌ You are not authorized to use this command.")
        return

    try:
        # Expected format: /approve <user_id> <days>
        parts = message.text.strip().split()
        if len(parts) != 3:
            await message.reply("⚠️ Usage: `/approve <user_id> <days>`", quote=True)
            return

        target_user_id = int(parts[1])
        duration_days = int(parts[2])

        # Current time
        now_ist = datetime.now(INDIA_TZ)
        now_unix = int(time.time())
        expire_dt = now_ist + timedelta(days=duration_days)
        expire_unix = int(expire_dt.timestamp())

        # Update premium user collection
        puser_collection.update_one(
            {"user_id": target_user_id},
            {"$set": {
                "user_id": target_user_id,
                "approved_by": user_id,
                "purchase_time_ist": now_ist.strftime("%Y-%m-%d %H:%M:%S"),
                "purchase_timestamp": now_unix,
                "expire_time_ist": expire_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "expire_timestamp": expire_unix
            }},
            upsert=True
        )

        # Set 'premium': True in users collection
        user_data.update_one(
            {"_id": target_user_id},
            {"$set": {"premium": True}},
            upsert=True
        )

        # Reply to admin
        await message.reply(
            f"✅ Approved user `{target_user_id}` for {duration_days} days.\n"
            f"📅 Expires on: `{expire_dt.strftime('%Y-%m-%d %H:%M:%S')}`",
            quote=True
        )

        # Notify user
        try:
            await client.send_message(
                target_user_id,
                f"🎉 Your premium membership has been approved for {duration_days} days!\n"
                f"✅ Valid until: `{expire_dt.strftime('%Y-%m-%d %H:%M:%S')}`"
            )
        except:
            pass  # user may have blocked bot

        # Send log to PREMIUM_CHANNEL
        try:
            await client.send_message(
                PREMIUM_CHANNEL_ID,
                f"📢 **New Premium Approved**\n"
                f"👤 User ID: `{target_user_id}`\n"
                f"⏳ Duration: `{duration_days}` days\n"
                f"🕓 Approved At: `{now_ist.strftime('%Y-%m-%d %H:%M:%S')}`\n"
                f"📆 Expiry: `{expire_dt.strftime('%Y-%m-%d %H:%M:%S')}` (IST)"
            )
        except Exception as e:
            await message.reply(f"⚠️ Premium approved but failed to send log: `{e}`")

    except Exception as e:
        await message.reply(f"⚠️ Error: `{e}`")
