# config.py
import os
from dotenv import load_dotenv

load_dotenv() # This loads the variables from .env

# Your secret key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# The list of RSS feeds you want to monitor
RSS_FEED_URLS = [
    "https://techcrunch.com/rss", # A good, active feed for testing
    "https://www.theverge.com/rss/index.xml",
    "https://blog.google/rss/"
]

# The file to store links of articles we've already seen
SEEN_ARTICLES_FILE = "seen_articles.csv"

# The file that defines the agent's personality
BRAND_VOICE_FILE = "brand_voice.txt"