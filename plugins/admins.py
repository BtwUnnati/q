from pyrogram import filters
from pyrogram.types import Message

from bot import Bot
from config import OWNER_ID
from database.database import add_admin, is_admin, remove_admin, get_admin_list


@Bot.on_message(filters.command('addadmin') & filters.private)
async def add_admin_command(client: Bot, message: Message):
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        await message.reply_text("Only Bot Owner can use this command.")
        return

    # Check if the command has the expected number of arguments
    if len(message.command) != 2:
        await message.reply_text("<b>Usage:</b> /addadmin userid")
        return
    try:
        user_id_to_add = int(message.command[1])
    except ValueError:
        await message.reply_text("Invalid user ID. Please provide a valid user ID.")
        return
    # Add the user to the admin list in the database
    added = await add_admin(user_id_to_add)
    if added:
        await message.reply_text(f"<b>User {user_id_to_add} has been added to the admin list.</b>")
    else:
        await message.reply_text(f"<b>User {user_id_to_add} is already an admin.</b>")


@Bot.on_message(filters.command('removeadmin') & filters.private)
async def remove_admin_command(client: Bot, message: Message):
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        await message.reply_text("Only Bot Owner can use this command.")
        return
    # Check if the command has the expected number of arguments
    if len(message.command) != 2:
        await message.reply_text("<b>Usage:</b> /removeadmin userid")
        return
    try:
        user_id_to_remove = int(message.command[1])
    except ValueError:
        await message.reply_text("Invalid user ID. Please provide a valid user ID.")
        return
    # Remove the user from the admin list in the database
    removed = await remove_admin(user_id_to_remove)
    if removed:
        await message.reply_text(f"<b>User {user_id_to_remove} has been removed from the admin list.</b>")
    else:
        await message.reply_text(f"<b>User {user_id_to_remove} is not an admin or was not found in the admin list.</b>")


@Bot.on_message(filters.command('admins') & filters.private)
async def admin_list_command(client: Bot, message: Message):
    user_id = message.from_user.id
    is_user_admin = await is_admin(user_id)
    if not is_user_admin and user_id != OWNER_ID:
        await message.reply_text("Only Bot Owner and Admins can use this command.")
        return

    admin_user_ids = await get_admin_list()  # Fetch the list of admin user IDs
    formatted_admins = []

    for user_id in admin_user_ids:
        user = await client.get_users(user_id)
        if user:
            username = user.username
            full_name = user.first_name if user.first_name else ""  # Use empty string if first_name is None
            full_name += " " + user.last_name if user.last_name else ""  # Concatenate last_name if available
            full_name = full_name.strip()  # Remove any leading/trailing whitespace

            if username:
                profile_link = f"{full_name} - @{username}"
            else:
                profile_link = full_name
            formatted_admins.append(profile_link)

    if formatted_admins:
        admins_text = "\n".join(formatted_admins)
        text = f"<b>ADMEMES:</b>\n\n{admins_text}"
    else:
        text = "<b>No ADMEMES found.</b>"

    await message.reply_text(text, disable_web_page_preview=True)
