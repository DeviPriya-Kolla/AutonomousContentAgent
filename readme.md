# Autonomous Content Strategist Agent

[![Live App](https://img.shields.io/badge/Live_App-Visit_Dashboard-brightgreen)](https://autonomouscontentagent.onrender.com) <!-- Replace with your actual Render URL -->

This project is an intelligent autonomous agent and a full-stack web application. The backend agent automates the entire content discovery and creation pipeline, while the live web dashboard provides a user-friendly interface to monitor the agent's activity.

The project demonstrates a sophisticated `Perceive -> Orient -> Decide -> Act -> Report` loop, making it an excellent example of a practical, deployed agentic AI system.

## Key Features

-   **Intelligent Backend Agent:**
    -   **Multi-Source Monitoring:** Actively monitors a list of user-defined RSS feeds for new content.
    -   **Content Scraping:** Scrapes source articles to get a summary for deeper context.
    -   **LLM-Powered Relevance Filter:** Uses a fast LLM call to decide if an article is "significant" enough to post about.
    -   **Agentic Memory:** Logs all processed articles in a structured `seen_articles.csv` file, providing a clear audit trail.
    -   **Automated Content Creation:** Generates multi-part Twitter/X style threads with relevant hashtags in a specific brand voice.

-   **Web Dashboard & UI:**
    -   **Flask Front-End:** A clean web interface for interacting with the agent's data.
    -   **Live & Deployed:** The web application is deployed on a cloud platform (Render) and is accessible via a public URL.
    -   **Activity Log Dashboard:** A dedicated page that displays the `seen_articles.csv` log in a readable table, showing all of the agent's past actions.

-   **The Handoff Protocol (Notification System):**
    -   **Automated Delivery:** The agent dispatches completed drafts directly to configured **Slack** and/or **Discord** channels for final human review.

-   **Production-Ready & Automated:**
    -   **Cloud-Native Deployment:** The backend agent runs on a schedule via **GitHub Actions**, and the frontend is deployed as a persistent web service.
    -   **Production Web Server:** Uses **Gunicorn** for a robust, production-ready frontend deployment.
    -   **Rate Limit Handling:** Includes an exponential backoff retry mechanism to gracefully handle API rate limits.

## Demo Output

The agent delivers its work via notifications. Here is an example of a notification sent to Discord:
### Discord Notification
![Example notification sent to Discord](screenshots/Discord.png)

### Slack Notification
![Example notification sent to Slack](screenshots/Slack.png)

## Tech Stack

-   **Backend:** Python 3.8+, Google Gemini API
-   **Frontend:** Flask (Python Web Framework), HTML, CSS
-   **Deployment:** Gunicorn (WSGI Server), Render (Cloud Hosting), GitHub Actions (CI/CD)
-   **Core Libraries:**
    -   `google-generativeai`, `feedparser`, `requests`, `beautifulsoup4`, `python-dotenv`, `Flask`, `gunicorn`

## Project Structure

```
/autonomous-content-agent/
|
|-- .github/workflows/run_agent.yml
|-- templates/
|   |-- landing_page.html
|   |-- dashboard.html
|-- .venv/
|
|-- .env
|-- .gitignore
|-- Procfile                       # Command for the production web server
|
|-- app.py                         # The Flask web server application
|-- agent.py                       # The backend autonomous agent script
|-- config.py
|-- brand_voice.txt
|
|-- requirements.txt
|-- seen_articles.csv
```

## Getting Started & Deployment

### 1. Local Setup

First, set up and run the project on your local machine for testing.

```bash
# Clone the repository
git clone https://github.com/your-username/autonomous-content-agent.git
cd autonomous-content-agent

# Create and activate a virtual environment
python -m venv venv
# On Windows: venv\Scripts\activate
# On macOS/Linux: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

1.  **Create `.env` file:** Create a `.env` file in the project's root folder.
2.  **Add your secrets:** Add your API key and any optional webhook URLs.
    ```
    GEMINI_API_KEY="Your-Google-API-Key-Here"
    SLACK_WEBHOOK_URL="Your-Slack-Webhook-URL-Here"
    DISCORD_WEBHOOK_URL="Your-Discord-Webhook-URL-Here"
    ```
3.  **Customize Config:** Open `config.py` to set your RSS feeds and `brand_voice.txt` to define the agent's tone.

### 3. Running Locally

This application has two parts. For local testing, you can run them in two separate terminals.

-   **Run the Backend Agent (Terminal 1):**
    ```bash
    python agent.py
    ```
-   **Run the Frontend Web Server (Terminal 2):**
    ```bash
    python app.py
    ```
    Now, visit `http://127.0.0.1:5000` in your browser.

### 4. Deployment to the Cloud

This project is configured for a full cloud deployment.

1.  **Deploy the Frontend (Render):**
    -   Push your code to a GitHub repository.
    -   Create a new **Web Service** on [Render](https://render.com), connecting it to your repository.
    -   Render will automatically use the `Procfile` to run `gunicorn app:app`.
    -   In the Render dashboard, add your `GEMINI_API_KEY` and other secrets as **Environment Variables**.
    -   Your web app will be live on a public URL.

2.  **Automate the Backend (GitHub Actions):**
    -   The workflow in `.github/workflows/run_agent.yml` is configured to run the `agent.py` script every hour.
    -   It automatically commits the updated `seen_articles.csv` file back to the repository.
    -   Render will detect this change and automatically re-deploy your web app, ensuring the dashboard is always up-to-date with the latest agent activity.