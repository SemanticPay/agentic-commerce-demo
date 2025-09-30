# Simple Search Server

A simple Flask server that provides a search API for items based on keywords in their titles.

## Features

- **Search Endpoint**: `/api/search` - Search items by keywords in their titles
- **Health Check**: `/health` - Check server status
- **Home**: `/` - API information and documentation

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python server.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Search Items
**Endpoint**: `GET/POST /api/search`

**Parameters**:
- `query` (string): Search query
- `keywords` (string): Additional keywords to search for

**Response Format**:
```json
{
  "items": [
    {
      "id": 1,
      "title": "Python Programming Guide",
      "description": "Learn Python programming from basics to advanced concepts"
    }
  ]
}
```

**Example Requests**:
```bash
# GET request
curl "http://localhost:5000/api/search?query=python&keywords=programming"

# POST request
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "web", "keywords": "development"}'
```

### Health Check
**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "total_items": 10
}
```

### Home
**Endpoint**: `GET /`

Returns API information and available endpoints.

## Testing

Run the test script to verify the API functionality:

```bash
python test_api.py
```

Make sure the server is running before executing the tests.

## Sample Data

The server includes 10 sample items covering various programming and technology topics:
- Python Programming Guide
- Web Development Tutorial
- Machine Learning Basics
- Data Science Handbook
- JavaScript Fundamentals
- Database Design Principles
- API Development Guide
- Mobile App Development
- Cloud Computing Overview
- Cybersecurity Essentials

## Search Logic

The search functionality:
1. Combines `query` and `keywords` parameters
2. Splits the combined search terms into individual words
3. Filters items where the title contains any of the search words (case-insensitive)
4. Returns matching items in the specified JSON format
