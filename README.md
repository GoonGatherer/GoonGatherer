# GoonGatherer README 
 
## Overview 
GoonGatherer is a Telegram bot that searches Reddit for NSFW images based on a user-provided keyword and sends up to 5 images as a single media group (album) to a Telegram chat. The bot uses the Reddit API to scrape images, validates and compresses them to meet Telegram's requirements, and handles errors gracefully. 
 
## Dependencies 
To run GoonGatherer, install the following Python packages using `pip`: 
 
```bash 
pip install python-telegram-bot==20.7 praw requests pillow 
``` 
 
- **`python-telegram-bot`**: Handles Telegram bot interactions (version 20.7 for compatibility). 
- **`praw`**: Python Reddit API Wrapper for accessing Reddit data. 
- **`requests`**: Downloads images from URLs. 
- **`pillow`**: Processes and validates images. 
 
Ensure Python 3.8 or higher is installed. 
 
## Setup Instructions 
1. **Clone or Download the Code** 
   - Save the bot code as `goonbot.py` (or your preferred filename). 
 
2. **Configure API Keys** 
   - The bot requires Reddit API credentials and a Telegram Bot Token. Replace the placeholder values in `goonbot.py` with your own credentials: 
     - **Reddit API Credentials**: 
       - Locate the `reddit` object initialization (around line 15): 
         ```python 
         reddit = praw.Reddit( 
             client_id='YOUR_REDDIT_CLIENT_ID', 
             client_secret='YOUR_REDDIT_CLIENT_SECRET', 
             user_agent='YOUR_REDDIT_USER_AGENT' 
         ) 
         ``` 
       - Replace `'YOUR_REDDIT_CLIENT_ID'` with your Reddit App Client ID. 
       - Replace `'YOUR_REDDIT_CLIENT_SECRET'` with your Reddit App Client Secret. 
       - Replace `'YOUR_REDDIT_USER_AGENT'` with a unique user agent (e.g., `Keyword Image Scraper by /u/YourRedditUsername`). 
       - To obtain Reddit API credentials: 
         1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps). 
         2. Create a new application (select "script" type). 
         3. Copy the `client_id` (under the app name) and `client_secret`. 
     - **Telegram Bot Token**: 
       - Locate the `TELEGRAM_BOT_TOKEN` variable (around line 150): 
         ```python 
         TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN" 
         ``` 
       - Replace `'YOUR_TELEGRAM_BOT_TOKEN'` with your Telegram Bot Token. 
       - To obtain a Telegram Bot Token: 
         1. Open Telegram and message `@BotFather`. 
         2. Use the `/newbot` command, follow the prompts, and copy the provided token. 
 
3. **Run the Bot** 
   - Ensure all dependencies are installed. 
   - Run the script using Python: 
     ```bash 
     python goonbot.py 
     ``` 
   - The console should display: 
     ```bash 
     ?? GoonBot is running... 
     ``` 
 
4. **Using the Bot** 
   - Add the bot to a Telegram chat or message it directly. 
