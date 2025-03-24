# Construction AI Platform - Backend

This is the backend implementation for the AI-Powered Construction Plan Analysis & Quote Generation System.

## Technology Stack

- FastAPI for RESTful API
- TensorFlow/PyTorch for AI models
- MySQL for database
- Python 3.9+

## Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/RJ-Flash/construction-ai-platform.git
cd construction-ai-platform/backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn app.main:app --reload
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application initialization
│   ├── core/                    # Core application modules
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration settings
│   │   ├── security.py          # Security utilities
│   │   └── exceptions.py        # Custom exception handlers
│   ├── db/                      # Database models and utilities
│   │   ├── __init__.py
│   │   ├── session.py           # Database session
│   │   └── models/              # Database models
│   ├── api/                     # API endpoints
│   │   ├── __init__.py
│   │   ├── deps.py              # API dependencies
│   │   └── routes/              # API route modules
│   ├── services/                # Business logic services
│   │   ├── __init__.py
│   │   ├── document/            # Document processing services
│   │   ├── ai/                  # AI services
│   │   ├── estimation/          # Estimation services
│   │   └── plugin/              # Plugin management services
│   └── schemas/                 # Pydantic models for request/response
├── tests/                       # Test cases
├── requirements.txt             # Project dependencies
└── alembic/                     # Database migrations
```
