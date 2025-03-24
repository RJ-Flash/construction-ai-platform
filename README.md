# Construction AI Platform

An AI-powered platform for the construction industry, focused on improving workflows and automating tedious tasks.

## Features

- **MEP Plugins**: Analyze Mechanical, Electrical, and Plumbing specifications to extract structured data
  - Electrical Systems Estimator
  - Plumbing Systems Estimator
  - HVAC & Mechanical Estimator

## Architecture

The platform is built with a modular, plugin-based architecture:

- **Backend**: FastAPI-based Python API with plugin system
- **Frontend**: (Coming soon) React-based web application

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- OpenAI API Key

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/RJ-Flash/construction-ai-platform.git
   cd construction-ai-platform
   ```

2. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file to add your OpenAI API key and other settings.

4. Start the services with Docker Compose:
   ```bash
   docker-compose up -d
   ```

5. Access the API at http://localhost:8000 and the API documentation at http://localhost:8000/docs

### Running Without Docker

1. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. Start the backend API:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

## Testing

Run the tests with pytest:

```bash
cd backend
pytest
```

## Adding New Plugins

1. Create a new plugin class inheriting from the appropriate base class
2. Implement the required methods
3. Register the plugin using the `@register_plugin` decorator

Example:

```python
from app.plugins.mep.base import MEPPlugin
from app.plugins.registry import register_plugin

@register_plugin
class MyNewPlugin(MEPPlugin):
    @property
    def id(self) -> str:
        return "mep.my_new_plugin"
    
    @property
    def name(self) -> str:
        return "My New Plugin"
    
    # ... implement other required methods
```

## API Documentation

Once running, access the API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

This project is licensed under the MIT License - see the LICENSE file for details.
