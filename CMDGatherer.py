import praw
import requests
import os
import subprocess
from urllib.parse import urlparse

# Reddit API client
reddit = praw.Reddit(
    client_id='YOUR CLIENT ID',
    client_secret='YOUR CLIENT SECRET',
    user_agent='YOUR USER AGENT'
)

# Check if the URL is an image
def is_image_url(url):
    return url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))

# Check if post has Reddit-hosted video
def is_video_url(post):
    return hasattr(post, 'media') and post.media and post.media.get('reddit_video')

# Download file (for images)
def download_file(url, folder, filename=None):
    os.makedirs(folder, exist_ok=True)
    filename = filename or os.path.basename(urlparse(url).path)
    filepath = os.path.join(folder, filename)

    try:
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)
            print(f"✅ Downloaded: {filename}")
        else:
            print(f"❌ Failed to download: {url}")
    except Exception as e:
        print(f"❌ Error downloading {url}: {e}")

# Download and merge Reddit-hosted video with audio (if available)
def download_and_merge_reddit_video(video_url, folder, post_id):
    os.makedirs(folder, exist_ok=True)
    base_url = video_url.split("/DASH_")[0]
    video_file = os.path.join(folder, f"{post_id}_video.mp4")
    audio_file = os.path.join(folder, f"{post_id}_audio.mp4")
    final_file = os.path.join(folder, f"{post_id}.mp4")

    audio_url = f"{base_url}/DASH_audio.mp4"

    try:
        # Download video
        r = requests.get(video_url, stream=True)
        with open(video_file, 'wb') as f:
            for chunk in r.iter_content(1024):
                f.write(chunk)

        # Try to download audio
        r = requests.get(audio_url, stream=True)
        if r.status_code == 200:
            with open(audio_file, 'wb') as f:
                for chunk in r.iter_content(1024):
                    f.write(chunk)

            # Merge video and audio using ffmpeg
            cmd = [
                "ffmpeg", "-y",
                "-i", video_file,
                "-i", audio_file,
                "-c:v", "copy",
                "-c:a", "aac",
                "-strict", "experimental",
                final_file
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✅ Merged with audio: {final_file}")
            os.remove(audio_file)

        else:
            os.rename(video_file, final_file)
            #print(f"⚠️ No audio found, saved video only: {final_file}")

        os.remove(video_file)

    except Exception as e:
        #print(f"❌ Failed to download or merge video: {e}")
        pass

# Search Reddit for matching NSFW posts with media
def search_and_download_media(keywords, limit=500):
    banned_phrases = [
        '% off', 'discount', 'subscribe', 'sale',
        'free trial', 'dm', 'promo', 'fansly', 'join now',
        'free', 'telegram', '[m4f+m]', 'trans'
    ]

    for keyword in keywords:
        print(f"\n🌐 Searching r/all for NSFW posts with: '{keyword}'...")

        # Counters
        scanned = 0
        image_count = 0
        video_count = 0

        results = reddit.subreddit("all").search(
            query=keyword,
            sort="new",
            limit=limit,
            params={"include_over_18": "on"}
        )

        for post in results:
            scanned += 1
            title_lower = post.title.lower()

            if not post.over_18:
                continue
            if any(banned in title_lower for banned in banned_phrases):
                continue
            if keyword.lower() not in title_lower:
                continue

            folder = f"downloads/{keyword}_nsfw"

            # Handle image
            if is_image_url(post.url):
                print(f"📷 {post.title[:50]}... → {post.url}")
                download_file(post.url, folder)
                image_count += 1
                continue

            # Handle Reddit-hosted video
            elif is_video_url(post):
                video_url = post.media['reddit_video'].get('fallback_url')
                if not video_url:
                    post_url = f"https://www.reddit.com{post.permalink}"
                    print(f"⚠️ Skipping post (no fallback_url): {post.title[:50]}")
                    print(f"🔗 Post URL: {post_url}")
                    continue

                print(f"🎥 {post.title[:50]}... → {video_url}")
                download_and_merge_reddit_video(video_url, folder, post.id)
                video_count += 1

        # Final summary
        print(f"\n📊 Summary for '{keyword}':")
        print(f"🔎 Posts scanned: {scanned}")
        print(f"📷 Images downloaded: {image_count}")
        print(f"🎥 Videos downloaded: {video_count}")
        print(f"{'=' * 40}")


# Run script
if __name__ == "__main__":
    keywords = input("Enter keyword(s), separated by commas: ").split(',')
    search_and_download_media([k.strip().lower() for k in keywords], limit=500)
