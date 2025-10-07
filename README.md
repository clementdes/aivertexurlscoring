# Advanced Search Engine

A powerful search engine that combines **DataForSEO's live SERP results**, **advanced web crawling**, and **Google's latest Ranking API** to provide AI-powered search relevance scoring.

## 🚀 Features

- **Live SERP Data**: Real-time Google search results via DataForSEO API
- **Content Crawling**: Asynchronous web crawling to extract full page content
- **AI Ranking**: Google's latest semantic-ranker-default@latest model for precise relevance scoring
- **Modern Web Interface**: Beautiful, responsive UI with detailed result analysis
- **REST API**: Full API endpoints for programmatic access
- **Comprehensive Metadata**: Raw SERP data, crawl status, content analysis, and ranking scores

## 🏗️ Architecture

```
User Query → DataForSEO API → Web Crawler → Google Ranking API → Results
     ↓              ↓              ↓              ↓               ↓
   Input      Live SERPs    Page Content    AI Scoring      Ranked Results
```

1. **DataForSEO**: Fetches first 20 organic search results
2. **Web Crawler**: Extracts content from each URL concurrently  
3. **Google Ranking API**: Scores content relevance using AI
4. **Results**: Displays ranked results with metadata and scores

## 📋 Prerequisites

- Python 3.8+
- DataForSEO API account
- Google Cloud Project with Discovery Engine API enabled

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd ranking_api
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**

Create a `.env` file in the root directory:
```env
DATAFORSEO_LOGIN=your_dataforseo_login
DATAFORSEO_PASSWORD=your_dataforseo_password
GOOGLE_CLOUD_PROJECT_ID=your_google_cloud_project_id
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json
```

## 🔧 Service Setup

### DataForSEO API Setup

1. Register at [DataForSEO.com](https://dataforseo.com)
2. Get your API credentials from the dashboard
3. Add credentials to your `.env` file

### Google Cloud Setup

1. Create a Google Cloud Project
2. Enable the Discovery Engine API
3. Create a service account with appropriate permissions
4. Download the service account key JSON file
5. Set the path in your `.env` file

**Required Google Cloud APIs:**
- Discovery Engine API
- AI Platform API (if not included)

## 🚀 Running the Application

Start the FastAPI server:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The application will be available at: `http://localhost:8000`

## 🌐 Web Interface

### Home Page (`/`)
- Search interface with query, location, and language options
- Service overview and feature explanations

### Results Page (`/search`)
- Comprehensive search results with AI ranking scores
- Raw metadata for each crawled page
- Processing time and performance metrics
- Content previews and key headings

### Status Page (`/status`)
- Service connectivity checks
- Setup instructions
- API documentation

## 📡 API Endpoints

### POST `/api/search`
Perform a search with AI ranking.

**Request:**
```json
{
    "query": "artificial intelligence",
    "location": "United States",
    "language": "en"
}
```

**Response:**
```json
{
    "query": "artificial intelligence",
    "location": "United States", 
    "language": "en",
    "results": [
        {
            "serp_position": 1,
            "url": "https://example.com",
            "title": "Page Title",
            "content": "Extracted content...",
            "ranking_score": 0.95,
            "word_count": 1500,
            "crawl_status": "success"
        }
    ],
    "metadata": {
        "total_time_seconds": 12.5,
        "serp_count": 20,
        "successful_crawls": 18,
        "google_ranking_api_used": true
    }
}
```

### GET `/api/status`
Check service connectivity.

### GET `/api/summary/{query}`
Get search summary statistics.

## 🔍 How It Works

1. **SERP Retrieval**: Uses DataForSEO's live Google organic results API to get the first 20 search results for your query

2. **Content Extraction**: Concurrently crawls each URL to extract:
   - Page title and meta description
   - Main content text (cleaned and normalized)
   - Key headings (H1, H2, H3)
   - Word count and other metadata

3. **AI Ranking**: Sends extracted content to Google's Ranking API which:
   - Uses the latest semantic-ranker-default@latest model
   - Provides precise relevance scores (0.0 to 1.0) 
   - Goes beyond simple semantic similarity

4. **Results Display**: Shows results ranked by AI score with:
   - Original SERP position vs. AI-ranked position
   - Detailed crawl metadata and status
   - Content previews and analysis
   - Performance metrics

## 📊 Result Data Structure

Each result includes:

**SERP Data:**
- Original search position
- SERP title and description  
- Domain and breadcrumb info

**Crawled Data:**
- Extracted page title
- Meta description
- Full content text
- Key headings
- Word count
- Crawl status and HTTP codes

**AI Ranking:**
- Relevance score (0.0-1.0)
- Ranking position vs. original
- Confidence metrics

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATAFORSEO_LOGIN` | DataForSEO API username | Yes |
| `DATAFORSEO_PASSWORD` | DataForSEO API password | Yes |
| `GOOGLE_CLOUD_PROJECT_ID` | Google Cloud project ID | Yes |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service account JSON | Yes |

### Application Settings

Configure in `config.py`:
- `MAX_CONTENT_LENGTH`: Maximum content length per page (default: 5000)
- `REQUEST_TIMEOUT`: HTTP request timeout (default: 30s)
- `MAX_CONCURRENT_REQUESTS`: Concurrent crawling limit (default: 5)

## 🚨 Error Handling

The application includes comprehensive error handling:

- **DataForSEO failures**: Graceful error messages
- **Crawl failures**: Individual URL timeout/error handling
- **Google API issues**: Fallback ranking using content-based scoring
- **Partial results**: Shows available data even with some failures

## 📈 Performance

**Typical Performance:**
- SERP retrieval: 2-5 seconds
- Content crawling: 5-15 seconds (concurrent)
- AI ranking: 2-8 seconds
- **Total time: 10-30 seconds** for 20 results

## 🔐 Security

- Environment variable configuration
- No hardcoded credentials
- Request timeout limits
- Input validation and sanitization

## 📝 License

This project is provided as-is for educational and development purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the `/status` page for service connectivity
2. Review the setup instructions
3. Verify API credentials and quotas

---

**Powered by:**
- [DataForSEO API](https://dataforseo.com) - Live SERP data
- [Google Ranking API](https://cloud.google.com/generative-ai-app-builder/docs/ranking) - AI-powered ranking
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework 