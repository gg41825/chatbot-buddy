# Chatbot Buddy

A cloud-ready Flask-based chatbot platform that automatically scrapes German news, analyzes content using OpenAI, and delivers interactive language-learning features via LINE Messaging API.
Ideal for learners seeking daily exposure to German vocabulary in an engaging, automated workflow.

![Ginny Bot Demo](chatbot_demo.gif)

## Features
### Core Learning Functionality
  - **ModularModular News Scraping**: Flexible scraper architecture supporting multiple news sources.
  - **LINE Bot Integration**: Receive news and interact via LINE messaging. A scheduler is set to push daily article to the user.
  - **AI-Powered Vocabulary Extraction**: Automatically extract B2-C1 level German vocabularies from articles
  - **AI-Driven Vocabulary Extraction**: Automatically identifies and extracts high-value (B2-C1 level) German vocabulary items per request with **English** and **Traditional Chinese**.
  - **Smart Article Detection**: Automatically detects German text and processes it
### Technical Architecture
- **Database Storage**: Store vocabularies in MySQL for future reference
- **Secure Webhooks**: HMAC signature verification for API endpoints
- **Cloud-Ready**: Supports both configuration files and environment variables for easy Cloud Run deployment
- **Configurable**: Easy configuration via `.env` files

## Architecture

```
chatbot-buddy/
├── .github/
│   └── workflows/
│       └── deploy.yml               # GitHub Actions workflow for CI/CD deployment
│
├── app/
│   ├── __init__.py                  # Flask application factory
│
│   ├── constants/
│   │   └── line_request_constants.py   # Constants for parsing LINE webhook event types
│
│   ├── models/
│   │   └── database.py              # Database connection and initialization
│
│   ├── routes/
│   │   ├── analyzer.py              # Endpoints for analysis (reserved for future features)
│   │   ├── news.py                  # News scraping and push notification endpoints
│   │   └── webhook.py               # LINE webhook handler
│
│   ├── services/
│   │   ├── analyzer.py              # Core logic for text analysis
│   │   ├── line_bot.py              # LINE Messaging API handling and reply utilities
│   │   ├── news_scraper.py          # Scraper factory and loader
│   │   ├── openai_service.py        # Integration layer for OpenAI GPT models
│   │   ├── signature.py             # HMAC signature verification
│   │   └── scrapers/
│   │       ├── __init__.py          # BaseScraper abstract class and registration
│   │       └── ts_learn_german.py   # Example scraper implementation (Tagesschau)
│
│   ├── utils/
│   │   └── config.py                # Configuration loader (ENV and .env support)
│
│   ├── scripts/
│   │   └── create_vocabularies_table.sql   # SQL schema for vocabulary storage
│
├── .dockerignore                    # Docker ignore rules
├── .env.example                     # Example environment variable file
├── .gitignore                       # Git ignore rules
├── Dockerfile                       # Docker image build configuration
├── README.md                        # Project documentation
├── docker-compose.yml               # Docker Compose configuration for local deployment
├── chatbot_demo.gif                 # Demonstration animation of the chatbot
├── main_bot.py                      # Application entry point
└── requirements.txt                 # Python dependencies

```

## Quick Start

### 1. Prerequisites
Before running the application, ensure you have the following:
- Python 3.10+
- A MySQL instance (local or cloud)
- A LINE Messaging API bot ([Setup Guide](https://developers.line.biz/en/docs/messaging-api/))
- An OpenAI API key

### 2. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd chatbot-buddy
```

### 3. Configuration

Copy the example environment file and update the values with your own credentials:

```bash
cp .env.example .env
```
Edit `.env` to configure:

- LINE Messaging API credentials
- OpenAI API key
- MySQL connection settings
- Scraper configuration

If deploying to Cloud Run, these values can also be provided as environment variables or stored in Secret Manager.

### 4. Database Setup

If you plan to persist extracted vocabularies, create the database schema using the SQL file provided:
```
scripts/create_vocabularies_table.sql
```
Note: Database writes are disabled by default to avoid unnecessary hosting costs.
The storage logic is included and can be enabled or customized as needed.

### 5. Run the Application (Docker Compose)

The recommended way to run the application locally is via Docker Compose:

```bash
docker compose build --no-cache
docker compose up
```
This will:
- Build the application image
- Start the Flask service
- Run the bot server on the configured port

## Usage

### Daily News Push

The bot automatically scrapes and delivers daily German news articles.

To trigger the push manually:

```bash
curl http://{APP_HOST}:{APP_PORT}/pushnews
```

### German Vocabulary Extraction

You can extract vocabulary simply by sending any German text (10+ characters) to the bot via LINE.

**Example Conversation:**
```
You: Generate Voca: [Paste German article text]

Bot: Found 10 German vocabularies:

1. Wissenschaftler
   Scientist
   科學家
   Die Wissenschaftler haben eine neue Entdeckung gemacht.

2. Forschung
   Research
   研究
   Die Forschung zeigt interessante Ergebnisse.

[... 8 more vocabularies ...]
```

The bot will:
1. Detect Vocabulary Requests
- Determine if the user wants to generate vocabularies.
2. Generate Vocabularies (if applicable)
- Extract **10 B2-C1 level vocabularies** using OpenAI
- Provide **English** and **Traditional Chinese** translations
- Include example sentences from the article
3. Regular Chat Functionality
- If the request is not a vocabulary generation request, respond as a standard chat bot.

## Extending the News Scraper System

The project uses a **pluggable scraper architecture** that allows you to easily integrate additional news sources.

Each scraper:
- Inherit from the `BaseScraper` abstract class
- Takes a single `request_url` parameter (full URL to scrape)
- Returns a dictionary with `title`, `link`, and `content`

### Example: Tagesschau Scraper

The included `ts_learn_german.py` scraper demonstrates the structure:

```python
from app.services.scrapers import BaseScraper

class TSLearnGermanScraper(BaseScraper):
    def __init__(self, request_url: str):
        self.request_url = request_url

    def scrape(self):
        # Fetch and parse news
        # Return {"title": "...", "link": "...", "content": "..."}
```

Configuration Example:
```ini
NEWS_SCRAPER_TYPE=ts_learn_german
NEWS_REQUEST_URL=https://www.tagesschau.de/wissen
```

## Further Development
1. [ ] Identify a cost-effective database solution for storing extracted vocabularies
2. [ ] Explore personalized learning workflows
  - (Option 1) Automatically integrate generated vocabularies into Anki
  - (Option 2) Generate reading-based tests to reinforce vocabulary retention
  - (Option 3) Leverage additional LLM models to provide context-aware assistance, such as retrieving daily information like weather updates

## License

MIT License - see [LICENSE](LICENSE) file for details

## Acknowledgments

- LINE Messaging API for bot integration
- OpenAI for GPT-powered analysis
- Flask for the web framework