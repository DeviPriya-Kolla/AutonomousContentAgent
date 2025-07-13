# agent.py

import os
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
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("models/gemini-1.5-flash")

# --- 1. Tool Functions: The agent's capabilities ---

def get_recent_articles(feed_url, num_articles=10):
    """
    Parses a given RSS feed and returns a list of the most recent articles.
    Each article in the list is an object with .title and .link attributes.
    """
    print(f"🤖 Checking feed for the latest {num_articles} articles: {feed_url}")
    feed = feedparser.parse(feed_url)
    if feed.entries:
        # Return the 10 most recent entries
        return feed.entries[:num_articles]
    return [] # Return an empty list if the feed is empty or fails

# --- This function is for summarizing the content ---
def get_article_summary(url):
    """Scrapes the first few paragraphs of an article."""
    try:
        print(f"🔎 Scraping summary from {url}...")
        # Use a common user-agent to avoid being blocked
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = requests.get(url, headers=headers, timeout=10) # Add a timeout
        response.raise_for_status() # Raise an exception for bad status codes
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all paragraph tags (<p>) and join the text of the first 3
        paragraphs = soup.find_all('p')
        summary = ' '.join([p.get_text() for p in paragraphs[:3]])
        
        # A simple check to ensure we got meaningful content
        if len(summary.strip()) < 50:
            return None 

        return summary
    except Exception as e:
        print(f"⚠️ Could not scrape summary for {url}: {e}")
        return None # Return None if scraping fails for any reason

def is_article_relevant(title, summary):
    """
    Uses a fast LLM call to determine if an article is significant enough for a social media post.
    """
    print(f"🤔 Checking relevance of '{title}'...")

    if not summary: # Fallback if scraping failed
        summary = "No summary available."

    try:
        # We use a very specific, directive prompt for a simple Yes/No answer
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
        
        # Clean up the response to be safe
        decision = response.text.strip().lower()
        print(f"🧠 Relevance decision: {decision}")

        if 'yes' in decision:
            return True
        else:
            return False
            
    except Exception as e:
        print(f"⚠️ Could not determine relevance due to an error: {e}")
        # Default to False to be safe and avoid wasting API calls
        return False

def has_been_seen(article_link):
    """Checks if an article link is already in our 'seen' file."""
    try:
        with open(config.SEEN_ARTICLES_FILE, 'r') as f:
            seen_links = f.read().splitlines()
        return article_link in seen_links
    except FileNotFoundError:
        return False

def mark_as_seen(article_link):
    """Adds a new article link to our 'seen' file."""
    with open(config.SEEN_ARTICLES_FILE, 'a') as f:
        f.write(article_link + '\n')

def get_brand_voice():
    """Reads the brand voice instructions from the file."""
    with open(config.BRAND_VOICE_FILE, 'r') as f:
        return f.read()

def draft_post_with_llm(title, summary, brand_voice, max_retries=4):
    """
    Uses Google Gemini to draft a social media thread with a dynamic,
    exponential backoff retry mechanism.
    """
    print("🤖 Asking Gemini to draft a thread...")
    
    # --- DYNAMIC BACKOFF CONFIGURATION ---
    # Start with a 15-second wait. This can be tuned.
    backoff_seconds = 15
    
    prompt = f"""
    You are an expert social media manager.
    
    Your goal is to draft a complete, ready-to-publish Twitter/X thread based on the following article title and brand voice guidelines.

    Article Title: "{title}"
    Article Summary: "{summary if summary else 'No summary available.'}"

    Brand Voice & Formatting Guidelines:
    ---
    {brand_voice}
    ---

    Please generate the thread now.
    """

    # --- THE RETRY LOOP ---
    for attempt in range(1, max_retries + 1):
        try:
            response = model.generate_content(prompt)
            # If we get here, the call was successful!
            return response.text
            
        except ResourceExhausted as e:
            # This is the specific error for rate limiting.
            
            # Check if this was our last attempt.
            if attempt == max_retries:
                print(f"❌ Final attempt failed. Giving up on this article.")
                # We'll return None to signal failure gracefully.
                return None 
            
            print(f"⚠️ Rate limit hit (attempt {attempt}/{max_retries}). "
                  f"Waiting {backoff_seconds} seconds before retrying...")
            
            time.sleep(backoff_seconds)
            
            # Double the wait time for the next attempt, with a cap.
            backoff_seconds *= 2
            
        except Exception as e:
            # Catch any other unexpected errors (e.g., network issues)
            print(f"An unexpected error occurred: {e}")
            # We'll also return None for other failures to prevent the agent from crashing.
            return None

    # This part of the code should ideally not be reached, but as a fallback:
    return None

# --- 2. The Main Agentic Loop ---

def run_agent():
    print("--- Running Content Strategist Agent ---")
    
    # Get the brand voice once at the start
    print("🎨 Reading brand voice guidelines...")
    brand_voice = get_brand_voice()

    # Loop through each feed URL from our config
    for url in config.RSS_FEED_URLS:
        
        # 1. Perceive a BATCH of recent articles
        recent_articles = get_recent_articles(url)

        if not recent_articles:
            print(f"⚠️ No articles found for {url}. Skipping.")
            continue
        
        # Reverse the list so we process the oldest new article first
        recent_articles.reverse()

        # 2. Loop through each individual article in the batch
        for article in recent_articles:
            article_title = article.title
            article_link = article.link

            # 1. Check Memory for EACH article
            if has_been_seen(article_link):
                # We've seen this one, so we can assume anything before it is also seen.
                # No need to print, this is normal behavior.
                continue # Move to the next article in the list
            
            # 2. GATHER CONTEXT (Scrape First!)
            summary = get_article_summary(article_link)
            
            # 3. SMART FILTER
            if not is_article_relevant(article_title, summary):
                print("❌ Article deemed not significant. Skipping and marking as seen.")
                mark_as_seen(article_link) # IMPORTANT: Mark as seen to avoid re-checking
                continue # Move to the next article

            # If we get here, the article is NEW!
            print(f"✨ New article found! Processing '{article_title}'...")
            # After confirming an article is new and relevant

            # 4. Think & Act
            draft = draft_post_with_llm(article_title, summary, brand_voice)
            
            # --- NEW CHECK FOR FAILED DRAFT ---
            if not draft:
                print(f"🤷‍♂️ Skipping article '{article_title}' due to drafting failure.")
                mark_as_seen(article_link) 
                # Use 'continue' to immediately jump to the next article in the for loop
                continue
            # --- END OF NEW CHECK ---
            
            print("\n--- 🚀 DRAFT COMPLETE ---")
            print(draft)
            print("----------------------\n")

            # 5. Update Memory
            mark_as_seen(article_link)
            print(f"📝 Marked '{article_title}' as seen.")
    
    print("--- Agent run complete ---")

# This makes the script runnable from the command line
if __name__ == "__main__":
    run_agent()