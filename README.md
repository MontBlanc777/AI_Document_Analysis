# MCP AI Document Analysis

A professional AI-powered document analysis system built with FastAPI and Gemini 2.5 Pro, featuring MCP (Model Context Protocol) integration for enhanced document processing capabilities.

## Features

- **Multi-format Document Processing**: Support for PDF, DOCX, PPTX, XLSX, emails, images, and text files
- **AI-powered Analysis**: Leverages Gemini 2.5 Pro for document understanding and question answering
- **MCP Integration**: Uses Model Context Protocol for enhanced document processing capabilities
- **Interactive Web Interface**: User-friendly interface for document upload, analysis, and querying
- **RESTful API**: Comprehensive API for programmatic access to all features
- **Modular Architecture**: Well-organized codebase with separation of concerns

## Project Structure

```
├── config/                 # Configuration files
│   ├── .env               # Environment variables
│   └── config.py          # Configuration loader
├── logs/                  # Application logs
├── src/                   # Source code
│   ├── api/               # API endpoints
│   │   ├── routers/       # API route definitions
│   │   └── app.py         # FastAPI application factory
│   ├── core/              # Core business logic
│   │   ├── models.py      # Data models
│   │   ├── document_processor.py  # Document processing logic
│   │   └── mcp_handler.py # MCP integration
│   ├── services/          # Service layer
│   │   ├── analysis_service.py  # Analysis service
│   │   ├── document_service.py  # Document management
│   │   └── gemini_service.py    # Gemini API integration
│   ├── utils/             # Utility functions
│   │   ├── file_utils.py  # File handling utilities
│   │   └── logging_utils.py  # Logging setup
│   └── main.py            # Application entry point
├── static/                # Static assets
│   ├── css/               # Stylesheets
│   └── js/                # JavaScript files
├── templates/             # HTML templates
│   └── index.html         # Main application template
├── uploads/               # Document storage
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key

### Installation

1. Clone the repository

2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Configure environment variables:

   - Copy `config/.env.example` to `config/.env` (if not already present)
   - Add your Gemini API key to the `.env` file

4. Run the application:

   ```
   python -m src.main
   ```

5. Access the web interface at http://localhost:8000

## API Documentation

Once the server is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

| Variable           | Description                  | Default        |
| ------------------ | ---------------------------- | -------------- |
| GEMINI_API_KEY     | Google Gemini API key        | (required)     |
| HOST               | Server host                  | 0.0.0.0        |
| PORT               | Server port                  | 5000           |
| DEBUG              | Debug mode                   | False          |
| UPLOAD_FOLDER      | Path to upload directory     | ./uploads      |
| MAX_CONTENT_LENGTH | Maximum upload size in bytes | 16777216       |
| MODEL_NAME         | Gemini model name            | gemini-2.5-pro |
