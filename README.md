# Chatbot Buddy

A Flask-based chatbot system that scrapes news articles, analyzes them with OpenAI, and sends notifications via LINE Bot. Perfect for language learners who want daily German vocabulary practice!

![Ginny Bot Demo](ginnybot_demo.gif)

## Features

- **Flexible News Scraping**: Pluggable scraper architecture supporting multiple news sources
- **LINE Bot Integration**: Receive news and interact via LINE messaging
- **AI-Powered Vocabulary Extraction**: Automatically extract B2-C1 level German vocabularies from articles
- **Multi-Language Translation**: Get vocabularies with English and Traditional Chinese translations
- **Smart Article Detection**: Automatically detects German text and processes it
- **Database Storage**: Store articles and vocabularies in MySQL for future reference
- **Secure Webhooks**: HMAC signature verification for API endpoints
- **Cloud-Ready**: Supports both configuration files and environment variables for easy Cloud Run deployment
- **Configurable**: Easy configuration via `.conf` files

## Architecture

```
chatbot-buddy/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Configuration loader
│   ├── routes/
│   │   ├── analyzer.py          # Article analysis endpoints
│   │   ├── news.py              # News scraping and push
│   │   └── webhook.py           # LINE bot webhook handler
│   ├── services/
│   │   ├── line_bot.py          # LINE bot service
│   │   ├── news_scraper.py      # Scraper factory
│   │   ├── openai_service.py    # OpenAI GPT integration
│   │   ├── signature.py         # HMAC signature verification
│   │   └── scrapers/
│   │       ├── __init__.py      # BaseScraper abstract class
│   │       ├── ts_learn_german.py  # Example scraper implementation
│   │       └── README.md        # Scraper development guide
│   ├── models/
│   │   └── database.py          # Database layer 
├── main_bot.py                  # Entry point for bot service
├── requirements.txt             # Python dependencies
├── service.conf                 # Configuration template
└── Dockerfile                   # Docker configuration

```

## Quick Start

### 1. Prerequisites

- Python 3.10+
- MySQL database
- LINE Bot account ([Setup Guide](https://developers.line.biz/en/docs/messaging-api/))
- OpenAI API key

### 2. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd chatbot-buddy

# Create virtual environment
python -m venv venv
source venv/bin/activate  # For Mac
venv\Scripts\activate # For Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

Copy the example configuration file and fill in your credentials:

```bash
cp service.example.conf service.conf
```

Edit `service.conf` with your actual credentials:

```ini
[app]
host = 0.0.0.0
port = 5000
analyzer.key = your-secret-key-here

[news]
scraper.type = ts_learn_german
request.url = https://www.tagesschau.de/wissen
line.access.token = YOUR_LINE_ACCESS_TOKEN
line.user.id = YOUR_LINE_USER_ID
line.channel.secret = YOUR_LINE_CHANNEL_SECRET

[analyzer]
host = http://localhost
port = 5000
send.save.url = /save_news
ask.bot.url = /get_article_voca
gen.voca.url = /generate_voca

[mysql]
host = localhost
port = 3306
username = your_db_user
password = your_db_password
dbname = news_db

[openai]
api.key = sk-your-openai-api-key
lang.model = gpt-3.5-turbo
```

### 4. Database Setup

Create the required database tables:

```sql
CREATE TABLE news_articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    article_title VARCHAR(500),
    article_content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE article_vocabularies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    article_id INT,
    german VARCHAR(200),
    english TEXT,
    chinese TEXT,
    sentence TEXT,
    FOREIGN KEY (article_id) REFERENCES news_articles(id)
);
```

**If you have an existing database**, run the migration to add the `english` column:

```bash
# SSH to your MySQL instance
gcloud compute ssh mysql-instance --zone=europe-west1-c

# Run migration
mysql -u YOUR_DB_USER -p YOUR_DB_NAME < /path/to/scripts/add_english_column.sql
```

### 5. Run the Application

```bash
# Start the bot service
python main_bot.py
```

The server will start on the configured host and port.

## Usage

### Daily News Push

The bot automatically scrapes and pushes daily German news articles:

```bash
# Trigger manually
curl http://localhost:5000/pushnews

# Or set up automatic daily push with Cloud Scheduler (see Deployment section)
```

### German Vocabulary Extraction

Simply paste any German article (>200 characters) into your LINE chat with the bot:

**Example Conversation:**
```
You: [Paste German article text]

Bot: 📚 Found 10 German vocabularies:

1. Wissenschaftler
   🇬🇧 Scientist
   🇹🇼 科學家
   📝 Die Wissenschaftler haben eine neue Entdeckung gemacht.

2. Forschung
   🇬🇧 Research
   🇹🇼 研究
   📝 Die Forschung zeigt interessante Ergebnisse.

[... 8 more vocabularies ...]
```

The bot will:
1. Detect it's a German article
2. Extract 10 B2-C1 level vocabularies using OpenAI
3. Provide English and Traditional Chinese translations
4. Include example sentences from the article
5. Save everything to your MySQL database

## API Endpoints

### News Routes

- **GET `/pushnews`**: Scrape latest news and push to LINE user

### Webhook Routes

- **POST `/callback`**: LINE bot webhook endpoint
- **GET `/`**: Welcome message

### Analyzer Routes

- **POST `/save_news`**: Save article to database
  ```json
  {
    "title": "Article Title",
    "content": "Article content..."
  }
  ```

- **POST `/get_article_voca`**: Get vocabularies from saved article
  ```json
  {
    "text": "Save to DB \"Article Title\"",
    "timestamp": "2025-12-08 10:30:00"
  }
  ```

- **POST `/generate_voca`**: Generate vocabularies from article content
  ```json
  {
    "content": "Article text in German..."
  }
  ```

## Adding Custom News Scrapers

The project uses a pluggable scraper architecture that makes it easy to add support for different news sources.

### How It Works

Each scraper:
- Implements the `BaseScraper` abstract class
- Takes a single `request_url` parameter (full URL to scrape)
- Returns a dictionary with `title`, `link`, and `content`

### Example: Tagesschau Scraper

The included `ts_learn_german.py` scraper demonstrates the pattern:

```python
from app.services.scrapers import BaseScraper

class TSLearnGermanScraper(BaseScraper):
    def __init__(self, request_url: str):
        self.request_url = request_url

    def scrape(self):
        # Fetch and parse news
        # Return {"title": "...", "link": "...", "content": "..."}
```

Configuration:
```ini
[news]
scraper.type = ts_learn_german
request.url = https://www.tagesschau.de/wissen
```

### Adding Your Own Scraper

1. **Create your scraper** in `app/services/scrapers/my_scraper.py`:

```python
from app.services.scrapers import BaseScraper
import requests
from bs4 import BeautifulSoup

class MyNewsScraper(BaseScraper):
    def __init__(self, request_url: str):
        self.request_url = request_url

    def scrape(self):
        resp = requests.get(self.request_url)
        soup = BeautifulSoup(resp.text, "html.parser")

        # Customize selectors for your site
        title = soup.find("h1", class_="title").text
        link = soup.find("a", class_="article-link")["href"]

        # Handle relative URLs - construct from request_url base
        if not link.startswith("http"):
            link = self.request_url.rsplit('/', 1)[0] + link

        return {"title": title, "link": link, "content": "..."}

    def get_name(self):
        return "My News Site"
```

2. **Register your scraper** in `app/services/news_scraper.py`:

```python
from app.services.scrapers.my_scraper import MyNewsScraper

SCRAPERS = {
    "ts_learn_german": TSLearnGermanScraper,
    "my_scraper": MyNewsScraper,  # Add here
}
```

3. **Update configuration** in `service_real.conf`:

```ini
[news]
scraper.type = my_scraper
request.url = https://yoursite.com/news
```

## License

MIT License - feel free to use and modify!

## Acknowledgments

- LINE Messaging API for bot integration
- OpenAI for GPT-powered analysis
- Beautiful Soup for web scraping
- Flask for the web framework