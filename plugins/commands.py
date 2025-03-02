

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import pyrogram.errors
from bs4 import BeautifulSoup
from plugins.headers import*
from helper.database import*
from plugins.queue import*
from config import START_PIC, ADMIN
import random
import asyncio

user_queries = {}


@Client.on_message(filters.command("start") & filters.private)
async def start(client, message):
    # Choose a random image from the list
    id = message.from_user.id
    if not present_user(id):
        try:
            add_user(id)
        except Exception as e:
            await client.send_message(-1002457905787, f"{e}")  # Use await
            pass
    start_pic = random.choice(START_PIC)
    
    # Create inline buttons
    buttons = [
        [
            InlineKeyboardButton("Owner", url="https://t.me/rohit_1888"),
            InlineKeyboardButton("Help", callback_data="help")
        ],
        [
            InlineKeyboardButton("Close", callback_data="close")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    
    # Send the welcome message with the random image and inline buttons
    await client.send_photo(  # Use await here
        chat_id=message.chat.id,
        photo=start_pic,
        caption="👋 Welcome to the Anime PaheBot! \n\nUse the buttons below for assistance or to contact the owner",
        reply_markup=reply_markup
    )

@Client.on_message(filters.command("anime") & filters.private)
async def search_anime(client, message):
    id = message.from_user.id
    if not present_user(id):
        try:
            add_user(id)
        except Exception as e:
            await client.send_message(-1002457905787, f"{e}")
    
    try:
        query = message.text.split("/anime ", maxsplit=1)[1]
    except IndexError:
        await message.reply_text("Usage: <code>/anime anime_name</code>")
        return

    search_url = f"https://animepahe.ru/api?m=search&q={query.replace(' ', '+')}"
    response = session.get(search_url).json()

    if response['total'] == 0:
        await message.reply_text("Anime not found.")
        return

    user_queries[message.chat.id] = query
    anime_buttons = [
        [InlineKeyboardButton(anime['title'], callback_data=f"anime_{anime['session']}")]
        for anime in response['data']
    ]
    reply_markup = InlineKeyboardMarkup(anime_buttons)

    gif_url = "https://telegra.ph/file/33067bb12f7165f8654f9.mp4"
    await message.reply_video(
        video=gif_url,
        caption=f"Search Result for <code>{query}</code>",
        reply_markup=reply_markup,
        quote=True
    )


@Client.on_message(filters.command("set_thumb") & filters.private)
async def set_thumbnail(client, message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply_text("Please reply to a photo with this command.")
        return

    file_id = message.reply_to_message.photo.file_id
    save_thumbnail(message.from_user.id, file_id)
    await message.reply_text("Thumbnail saved successfully!")


@Client.on_message(filters.command("see_thumb") & filters.private)
async def see_thumbnail(client, message):
    thumbnail = get_thumbnail(message.from_user.id)
    if thumbnail:
        await client.send_photo(message.chat.id, thumbnail, caption="Your custom thumbnail.")
    else:
        await message.reply_text("No custom thumbnail found in the database.")


@Client.on_message(filters.command("del_thumb") & filters.private)
async def del_thumbnail(client, message):
    if get_thumbnail(message.from_user.id):
        delete_thumbnail(message.from_user.id)
        await message.reply_text("Custom thumbnail deleted successfully!")
    else:
        await message.reply_text("No custom thumbnail found in the database.")


@Client.on_message(filters.command("set_caption") & filters.private)
async def save_caption_command(client, message):
    if message.reply_to_message and message.reply_to_message.text:
        caption = message.reply_to_message.text    
        save_caption(message.from_user.id, caption)
        await message.reply_text(f"<b>Caption saved:</b> \n\n <code>{caption}</code>")
    else:
        await message.reply_text("Please reply to a text message to save it as a caption.")


@Client.on_message(filters.command("see_caption") & filters.private)
async def see_caption_command(client, message):
    caption = get_caption(message.from_user.id)
    if caption:
        await message.reply_text(f"<b>Your current caption:</b> \n\n <code>{caption}</code>")
    else:
        await message.reply_text("No custom caption found in the database.")


@Client.on_message(filters.command("del_caption") & filters.private)
async def delete_caption_command(client, message):
    if get_caption(message.from_user.id):
        delete_caption(message.from_user.id)
        await message.reply_text("Custom caption deleted successfully!")
    else:
        await message.reply_text("No custom caption found in the database.")


@Client.on_message(filters.command("options") & filters.private)
async def set_upload_options(client, message):
    user_id = message.from_user.id
    current_method = get_upload_method(user_id)

    document_status = "✅" if current_method == "document" else "❌"
    video_status = "✅" if current_method == "video" else "❌"

    buttons = [
        [
            InlineKeyboardButton(f"Document ({document_status})", callback_data="set_method_document"),
            InlineKeyboardButton(f"Video ({video_status})", callback_data="set_method_video")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text(f"Your Current Upload Method: {current_method.capitalize()}", reply_markup=reply_markup)


@Client.on_message(filters.command("queue") & filters.private)
async def view_queue(client, message):
    with download_lock:
        if not global_queue:
            await message.reply_text("No active downloads.")
            return

        user_task_counts = {}
        for username, link in global_queue:
            user_task_counts[username] = user_task_counts.get(username, 0) + 1

        queue_text = "Active Downloads:\n"
        for i, (username, task_count) in enumerate(user_task_counts.items(), start=1):
            user_profile_link = f"[{username}](https://t.me/{username})"
            queue_text += f"{i}. {user_profile_link} (Active Task = {task_count})\n"

        await message.reply_text(queue_text, disable_web_page_preview=True)


@Client.on_message(filters.command("users") & filters.private & filters.user(ADMIN))
async def get_users(client, message):
    msg = await message.reply(WAIT_MSG)
    users = full_userbase()
    await msg.edit(f"{len(users)} users are using this bot")


@Client.on_message(filters.private & filters.command('broadcast') & filters.user(ADMIN))
async def send_text(client, message):
    if message.reply_to_message:
        query = full_userbase()
        broadcast_msg = message.reply_to_message
        total = successful = blocked = deleted = unsuccessful = 0

        pls_wait = await message.reply("<i>Broadcasting Message.. This will Take Some Time</i>")
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except pyrogram.errors.FloodWait as e:
                await asyncio.sleep(e.x)
                await broadcast_msg.copy(chat_id)
                successful += 1
            except pyrogram.errors.UserIsBlocked:
                del_user(chat_id)
                blocked += 1
            except pyrogram.errors.InputUserDeactivated:
                del_user(chat_id)
                deleted += 1
            except:
                unsuccessful += 1
                pass
            total += 1

        status = f"""<b><u>Broadcast Completed</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""

        await pls_wait.edit(status)

    else:
        msg = await message.reply(REPLY_ERROR)
        await asyncio.sleep(8)
        await msg.delete()

@Client.on_message(filters.command("queue") & filters.private)
async def view_queue(client, message):
    with download_lock:
        if not global_queue:
            await message.reply_text("No active downloads.")
            return

        # Count active tasks for each user
        user_task_counts = {}
        for username, link in global_queue:
            user_task_counts[username] = user_task_counts.get(username, 0) + 1

        # Prepare the queue display
        queue_text = "Active Downloads:\n"
        for i, (username, task_count) in enumerate(user_task_counts.items(), start=1):
            # Create a clickable profile link for the user           
            user_profile_link = f"[{username}](https://t.me/{username})"
            queue_text += f"{i}. {user_profile_link} (Active Task = {task_count})\n"

        await message.reply_text(queue_text, disable_web_page_preview=True)


@Client.on_message(filters.command("latest") & filters.private)
async def send_latest_anime(client, message):
    try:
        # Fetch the latest airing anime from AnimePahe
        API_URL = "https://animepahe.ru/api?m=airing&page=1"
        response = session.get(API_URL)
        if response.status_code == 200:
            data = response.json()
            anime_list = data.get('data', [])

            # Check if any anime is available
            if not anime_list:
                await message.reply_text("No latest anime available at the moment.")
                return

            # Prepare the message content with titles and links
            latest_anime_text = "<b>📺 Latest Airing Anime:</b>\n\n"
            for idx, anime in enumerate(anime_list, start=1):
                title = anime.get('anime_title')
                anime_session = anime.get('anime_session')
                episode = anime.get('episode')
                link = f"https://animepahe.ru/anime/{anime_session}"
                latest_anime_text += f"<b>{idx}) <a href='{link}'>{title}</a> [E{episode}]</b>\n"

            # Send the formatted anime list with clickable links
            await message.reply_text(latest_anime_text, disable_web_page_preview=True)
        else:
            await message.reply_text(f"Failed to fetch data from the API. Status code: {response.status_code}")

    except Exception as e:
        await client.send_message(-1002457905787, f"Error: {e}")
        await message.reply_text("Something went wrong. Please try again later.")


@Client.on_message(filters.command("airing") & filters.private)
async def send_airing_anime(client, message):
    try:
        # Fetch the latest airing anime from AnimePahe
        API_URL = "https://animepahe.ru/anime/airing"
        response = session.get(API_URL)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Find all anime links
            anime_list = soup.select(".index-wrapper .index a")

            # Check if any anime is available
            if not anime_list:
                await message.reply_text("No airing anime available at the moment.")
                return

            # Prepare the message content with titles and links
            airing_anime_text = "<b>🎬 Currently Airing Anime:</b>\n\n"
            for idx, anime in enumerate(anime_list, start=1):
                title = anime.get("title", "Unknown Title")
                link = "https://animepahe.ru" + anime["href"]
                airing_anime_text += f"<b>{idx}) {title}</b>\n"

            # Send the formatted anime list with clickable links
            await message.reply_text(airing_anime_text, disable_web_page_preview=True)
        else:
            await message.reply_text(f"Failed to fetch data. Status Code: {response.status_code}")

    except Exception as e:
        await message.reply_text("Something went wrong. Please try again later.")