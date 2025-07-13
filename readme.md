# Autonomous Content Strategist Agent

This project is a simple yet powerful autonomous agent designed to act as a social media content strategist agent. It monitors multiple RSS feeds for new articles, and when it finds one, it uses a Large Language Model (LLM) to draft an on-brand, multi-part social media thread about it.

This agent demonstrates a full "Perceive -> Think -> Act" loop, making it a great example of basic agentic AI in action.

## Features

-   **Multi-Source Monitoring:** Actively monitors a list of user-defined RSS feeds for new content.
-   **Brand Voice Awareness:** Reads a simple text file (`brand_voice.txt`) to learn and adopt a specific personality and tone for all generated content.
-   **Agentic Memory:** Keeps track of articles it has already processed in `seen_articles.txt` to avoid duplicate work.
-   **Automated Content Creation:** Generates multi-part Twitter/X style threads, complete with relevant hashtags, based on new article titles.
-   **LLM Agnostic:** Currently configured for Google's Gemini API, but can be easily adapted to use OpenAI or any other LLM.

## Demo Output

Here is an example of the agent finding a new article and drafting a thread based on its configured "witty and tech-savvy" brand voice:

```
--- Running Content Strategist Agent ---
🎨 Reading brand voice guidelines...
🤖 Checking feed: https://techcrunch.com/rss
✅ Article has been seen before. Skipping.
🤖 Checking feed: https://www.theverge.com/rss/index.xml
📰 Found article: 'The best Amazon Prime Day deals you can still shop'
✨ New article found! Processing 'The best Amazon Prime Day deals you can still shop'...
🤖 Asking Gemini to draft a thread...

--- 🚀 DRAFT COMPLETE ---
1/3 Prime Day is *over*?  Don't worry, fellow developers, your procrastination skills haven't gone unnoticed (by Amazon, at least). 😉  They're still peddling some of those "amazing" deals. Let's dive into the "best" of the leftover loot – prepare for some serious code-induced buyer's remorse! 💻

2/3  So, you missed the frantic click-frenzy of Prime Day?  Pathetic.  Just kidding (mostly).  But hey, these lingering deals might actually be *better* – fewer bots, less competition, more time to meticulously compare specs.  Think of it as unit testing your shopping prowess. 🤓  Check out the article linked below for some surprisingly decent discounts... maybe.

3/3  Okay, fine, I'll admit – some of these "deals" are less "deal" and more "slightly-less-expensive-than-yesterday."  But hey, a few bucks saved is a few more coffees, right?  Fuel those late-night coding sessions!  ☕️  Go forth and conquer (your shopping cart)!  Link to the articlle in the first tweet! 👇

---
Hashtags: #PrimeDay #AmazonDeals #DeveloperLife #TechDeals #CodingLife
----------------------

📝 Marked 'The best Amazon Prime Day deals you can still shop' as seen.
--- Agent run complete ---
```

## Tech Stack

-   **Language:** Python 3.8+
-   **LLM "Brain":** Google Gemini API (`models/gemini-1.5-flash`)
-   **Core Libraries:**
    -   `google-generativeai`: The official Python client for the Google AI SDK.
    -   `feedparser`: For robust and simple parsing of RSS feeds.
    -   `python-dotenv`: To manage environment variables for API keys.

## Project Structure

```
/autonomous-content-agent/
|
|-- .venv/                   # Folder for the Python virtual environment.
|-- __pycache__/             # Folder for Python's cached bytecode.
|
|-- .env                     # Stores secret API keys (ignored by Git).
|-- .gitignore               # Specifies files and folders for Git to ignore.
|
|-- agent.py                 # The main script containing the agent's logic.
|-- config.py                # Configuration settings (RSS feeds, file paths).
|-- brand_voice.txt          # Defines the agent's personality and tone.
|
|-- requirements.txt         # A list of required Python libraries for setup.
|-- seen_articles.txt        # A log of processed article links to prevent duplicates.
|
|-- test_gemini.py           # A simple script to test the connection to the Google Gemini API and verify that your API key is working correctly. Useful for initial setup and debugging.
|-- project_plan_workflow.txt# A text file for project planning and notes.
|
```

## Getting Started

Follow these steps to set up and run the project on your local machine.

### 1. Prerequisites

-   Python 3.8 or higher installed.
-   A Google Gemini API key. You can get one from [Google AI Studio](https://aistudio.google.com/app/apikey).

### 2. Clone the Repository

```bash
git clone https://github.com/your-username/autonomous-content-agent.git
cd autonomous-content-agent
```

### 3. Set Up a Virtual Environment

It is highly recommended to use a virtual environment to keep project dependencies isolated.

```bash
# Create the virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 4. Install Dependencies

Install the required Python libraries from the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 5. Configure the Agent

1.  **Create the `.env` file:** Create a file named `.env` in the root of the project folder.
2.  **Add your API key:** Add your Google Gemini API key to the `.env` file:
    ```
    GEMINI_API_KEY="Your-Google-API-Key-Here"
    ```
3.  **Customize RSS Feeds:** Open `config.py` and modify the `RSS_FEED_URLS` list to include the feeds you want to monitor.
4.  **Define Your Brand Voice:** Edit `brand_voice.txt` to describe the personality, tone, and formatting rules you want the agent to follow.
  
### 6. Verify API Key Connection (Recommended)

Before running the main agent, you can use the `test_gemini.py` script to ensure your API key is configured correctly. This is a crucial debugging step to isolate any potential connection or authentication issues.

Run the test script from your terminal:
```bash
python test_gemini.py
```
- On **success**, the script will print a short, successful response from the Gemini API.
- On **failure**, it will likely raise an AuthenticationError or another error, indicating a problem with your .env file or the API key itself.

### 7. Run the Agent

You are now ready to run the agent!

```bash
python agent.py
```

The agent will check the feeds, process any new articles it finds, print the drafted content to the console, and update its memory.

## Future Improvements

-   **Automate Execution:** Use `cron` (Linux/macOS) or Task Scheduler (Windows) to run the agent automatically on a schedule or Use a service like GitHub Actions (on a schedule) or a simple cloud server.
-   **Add More "Tools":** Give the agent the ability to do web searches for deeper context beyond the article title.
-   **Advanced Action-Taking:** Implement tools to send drafts to an email address, a Slack channel, or even post directly to a social media platform after approval.