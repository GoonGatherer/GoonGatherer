import os
import requests
from urllib.parse import urlparse
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.error import TelegramError
import praw
import asyncio
from PIL import Image
from telegram import InputMediaPhoto
import random

# Reddit API setup
reddit = praw.Reddit(
    client_id='2lnV1OH02WbKcUt9T3wVTA',
    client_secret='uHgvGm1bGxMJqb8-vZyK4THWq8mpdQ',
    user_agent='Keyword Image Scraper by /u/NoCaptain9085'
)

def is_image_url(url):
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif')
    image_hosts = ('i.redd.it', 'imgur.com', 'i.imgur.com')
    return url.lower().endswith(image_extensions) or any(host in url.lower() for host in image_hosts)

def get_direct_image_url(url):
    if 'imgur.com' in url and not url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
        return url.replace('imgur.com', 'i.imgur.com') + '.jpg'
    return url

def is_valid_image(filepath):
    try:
        with Image.open(filepath) as img:
            img.verify()
        img = Image.open(filepath)  # Re-open after verify
        img.convert("RGB").save(filepath, "JPEG", quality=95)
        return True
    except Exception as e:
        print(f"❌ Invalid image {filepath}: {e}")
        return False

def compress_image(filepath, max_size_mb=10):
    try:
        img = Image.open(filepath)
        img = img.convert("RGB")
        quality = 95
        while os.path.getsize(filepath) > max_size_mb * 1_000_000 and quality > 10:
            img.save(filepath, "JPEG", quality=quality)
            quality -= 5
        return is_valid_image(filepath)
    except Exception as e:
        print(f"❌ Error compressing {filepath}: {e}")
        return False

def download_file(url, folder, filename=None):
    try:
        os.makedirs(folder, exist_ok=True)
        if not os.access(folder, os.W_OK):
            print(f"❌ No write permission for folder: {folder}")
            return None
        filename = os.path.splitext(os.path.basename(urlparse(url).path))[0] + ".jpg"
        filepath = os.path.join(folder, filename)
        r = requests.get(url, stream=True, timeout=10)
        if r.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            return filepath
        else:
            print(f"❌ HTTP {r.status_code} for {url}")
    except Exception as e:
        print(f"❌ Error downloading {url}: {e}")
    return None

def scrape_images_from_reddit(keyword, limit=300):
    banned_phrases = [
        '% off', 'discount', 'subscribe', 'sale',
        'free trial', 'dm', 'promo', 'fansly', 'join now',
        'free', 'telegram', '[m4f+m]', 'trans'
    ]
    downloaded_paths = []
    try:
        results = reddit.subreddit("all").search(
            query=keyword,
            sort="new",
            limit=limit,
            params={"include_over_18": "on"}
        )
        for post in results:
            title_lower = post.title.lower()
            if not post.over_18:
                continue
            if any(banned in title_lower for banned in banned_phrases):
                continue
            if keyword.lower() not in title_lower:
                continue
            if is_image_url(post.url):
                direct_url = get_direct_image_url(post.url)
                folder = f"downloads/{keyword}_nsfw"
                path = download_file(direct_url, folder)
                if path:
                    downloaded_paths.append(path)
    except Exception as e:
        print(f"❌ Reddit API error: {e}")
    return downloaded_paths

async def goon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /goon <keyword>")
        return

    keyword = " ".join(context.args).strip().lower()
    await update.message.reply_text(f"🔍 Searching Reddit for: '{keyword}'...")

    loop = asyncio.get_event_loop()
    image_paths = await loop.run_in_executor(None, scrape_images_from_reddit, keyword)
    random.shuffle(image_paths)

    if not image_paths:
        await update.message.reply_text("❌ No NSFW images found.")
        return

    media = []
    count = 0
    valid_paths = []

    for path in image_paths:
        if count >= 5:
            break
        try:
            if not is_valid_image(path):
                os.remove(path)
                continue
            if os.path.getsize(path) > 10_000_000:
                if not compress_image(path):
                    os.remove(path)
                    continue
            if not os.path.exists(path):
                continue
            with open(path, 'rb') as f:
                media.append(InputMediaPhoto(media=f.read(), filename=os.path.basename(path)))
            valid_paths.append(path)
            count += 1
        except Exception as e:
            print(f"⚠️ Error processing {path}: {e}")
            continue

    if media:
        try:
            await update.message.reply_media_group(media=media)
        except TelegramError as te:
            print(f"⚠️ Telegram error sending album: {te}")
    else:
        await update.message.reply_text("❌ No valid images to send.")

    # Clean up
    for path in valid_paths:
        try:
            os.remove(path)
        except:
            pass

    await update.message.reply_text(f"✅ Done. Sent {count} image(s).")


if __name__ == "__main__":
    TELEGRAM_BOT_TOKEN = "7864563370:AAHT2Axj0Wv6wjV61tlx-3IjCEcA0QCOIOk"
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("goon", goon))
    print("🤖 GoonBot is running...")
    app.run_polling()