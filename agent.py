# agent.py

import os
import csv
from datetime import datetime
import feedparser
import google.generativeai as genai
from dotenv import load_dotenv
import time
from google.api_core.exceptions import ResourceExhausted
import config  # Import our settings
import requests
from bs4 import BeautifulSoup

# --- Load Environment ---
load_dotenv()
# Make sure GEMINI_API_KEY is in your .env file
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Using the new, faster Gemini 1.5 Flash model is a great choice for this
model = genai.GenerativeModel("models/gemini-1.5-flash")

# --- 1. Tool Functions: The agent's capabilities ---

def get_recent_articles(feed_url, num_articles=2):
    """
    Parses a given RSS feed and returns a list of the most recent articles.
    Each article in the list is an object with .title and .link attributes.
    """
    print(f"🤖 Checking feed for the latest {num_articles} articles: {feed_url}")
    feed = feedparser.parse(feed_url)
    if feed.entries:
        return feed.entries[:num_articles]
    return []

def get_article_summary(url):
    """Scrapes the first few paragraphs of an article."""
    try:
        print(f"🔎 Scraping summary from {url}...")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        paragraphs = soup.find_all('p')
        summary = ' '.join([p.get_text() for p in paragraphs[:5]])
        
        if len(summary.strip()) < 50:
            print("⚠️ Summary was too short, likely a cookie banner or error page.")
            return None 

        return summary
    except Exception as e:
        print(f"⚠️ Could not scrape summary for {url}: {e}")
        return None

def is_article_relevant(title, summary):
    """
    Uses a fast LLM call to determine if an article is significant enough for a social media post.
    """
    print(f"🤔 Checking relevance of '{title}'...")

    if not summary:
        summary = "No summary available."

    try:
        prompt = f"""
        You are a news editor's assistant. Your job is to decide if an article is important enough to be featured on social media.
        Consider if the topic is a major product launch, a significant industry event, a major breakthrough, or a widely impactful story.
        Ignore minor updates, opinion pieces, or niche stories.

        Analyze the following article details:
        Title: "{title}"
        Summary: "{summary}"

        Based on these details, is this article significant enough to create a social media post about?
        Respond with only the word "Yes" or "No".
        """

        response = model.generate_content(prompt)
        decision = response.text.strip().lower()
        print(f"🧠 Relevance decision: {decision}")

        return 'yes' in decision
            
    except Exception as e:
        print(f"⚠️ Could not determine relevance due to an error: {e}")
        return False

def has_been_seen(article_link):
    """Checks if an article link is already in our CSV log."""
    try:
        with open(config.SEEN_ARTICLES_FILE, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) > 2 and row[2] == article_link:
                    return True
        return False
    except FileNotFoundError:
        return False

def mark_as_seen(article_link, article_title):
    """Adds a new article's info as a row in our CSV log."""
    header = ['timestamp', 'title', 'link']
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_row = [timestamp, article_title, article_link]

    try:
        # Check if file exists and is not empty
        file_exists_and_has_content = os.path.getsize(config.SEEN_ARTICLES_FILE) > 0
    except FileNotFoundError:
        file_exists_and_has_content = False

    with open(config.SEEN_ARTICLES_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists_and_has_content:
            writer.writerow(header) # Write header only if file is new/empty
        
        writer.writerow(new_row)

def get_brand_voice():
    """Reads the brand voice instructions from the file."""
    with open(config.BRAND_VOICE_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def send_to_slack(message_text):
    """Sends a message to a Slack channel using a webhook."""
    if not config.SLACK_WEBHOOK_URL:
        return # Silently exit if not configured
    payload = {"blocks": [{"type": "header", "text": {"type": "plain_text", "text": "🚀 New Content Draft Ready for Approval!", "emoji": True}}, {"type": "section", "text": {"type": "mrkdwn", "text": message_text}}]}
    print("📢 Sending draft to Slack...")
    try:
        response = requests.post(config.SLACK_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print("✅ Successfully sent to Slack.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send to Slack: {e}")

def send_to_discord(message_text):
    """Sends a formatted message to a Discord channel using a webhook."""
    if not config.DISCORD_WEBHOOK_URL:
        return # Silently exit if not configured
    payload = {"content": "🚀 New Content Draft Ready for Approval!", "embeds": [{"description": message_text, "color": 5814783, "footer": {"text": "Generated by Autonomous Content Agent"}}]}
    print("📢 Sending draft to Discord...")
    try:
        response = requests.post(config.DISCORD_WEBHOOK_URL, json=payload)
        response.raise_for_status()
        print("✅ Successfully sent to Discord.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send to Discord: {e}")

def draft_post_with_llm(title, summary, brand_voice, max_retries=4):
    """
    Uses Google Gemini to draft a social media thread with an exponential backoff retry mechanism.
    """
    print("🤖 Asking Gemini to draft a thread...")
    backoff_seconds = 15
    prompt = f"""
    You are an expert social media manager. Your goal is to draft a complete, ready-to-publish Twitter/X thread based on the article title and summary.

    Article Title: "{title}"
    Article Summary: "{summary if summary else 'No summary available.'}"

    Brand Voice & Formatting Guidelines:
    ---
    {brand_voice}
    ---

    Please generate the thread now.
    """
    for attempt in range(1, max_retries + 1):
        try:
            response = model.generate_content(prompt)
            return response.text
        except ResourceExhausted as e:
            if attempt == max_retries:
                print("❌ Final attempt failed. Giving up on this article.")
                return None
            print(f"⚠️ Rate limit hit (attempt {attempt}/{max_retries}). Waiting {backoff_seconds} seconds...")
            time.sleep(backoff_seconds)
            backoff_seconds *= 2
        except Exception as e:
            print(f"An unexpected error occurred during drafting: {e}")
            return None
    return None

# --- 2. The Main Agentic Loop ---

def run_agent():
    print("--- Running Content Strategist Agent ---")
    
    brand_voice = get_brand_voice()

    for url in config.RSS_FEED_URLS:
        recent_articles = get_recent_articles(url)

        if not recent_articles:
            print(f"⚠️ No articles found for {url}. Skipping.")
            continue
        
        recent_articles.reverse()

        for article in recent_articles:
            article_title = article.title
            article_link = article.link

            if has_been_seen(article_link):
                continue
            
            summary = get_article_summary(article_link)
            
            if not is_article_relevant(article_title, summary):
                print("❌ Article deemed not significant. Skipping and marking as seen.")
                mark_as_seen(article_link, article_title)
                continue

            print(f"✨ New and relevant article found! Processing '{article_title}'...")

            draft = draft_post_with_llm(article_title, summary, brand_voice)
            
            if not draft:
                print(f"🤷‍♂️ Skipping article '{article_title}' due to drafting failure.")
                mark_as_seen(article_link, article_title) 
                continue
            
            # --- START: THE ONLY SECTION WITH CHANGES ---

            # Create formatted messages for both platforms
            # Slack uses a special mrkdwn format for links: <url|text>
            message_for_slack = f"*{article_title}*\n\n{draft}\n\nSource: <{article_link}|Read original article>"
            
            # Discord uses standard markdown for links: [text](url)
            message_for_discord = f"**{article_title}**\n\n{draft}\n\nSource: [Read original article]({article_link})"

            # Send notifications to all configured platforms
            send_to_slack(message_for_slack)
            send_to_discord(message_for_discord)

            # --- END: THE ONLY SECTION WITH CHANGES ---

            mark_as_seen(article_link, article_title)
            print(f"📝 Marked '{article_title}' as seen in the CSV log.")
    
    print("--- Agent run complete ---")

if __name__ == "__main__":
    run_agent()