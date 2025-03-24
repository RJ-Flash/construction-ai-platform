# Construction AI Platform

AI-Powered Construction Plan Analysis &amp; Quote Generation System

## Overview

Construction AI Platform is an intelligent system that analyzes construction documents, identifies building elements, and generates accurate cost estimates. The platform leverages AI to streamline the bid preparation process, reducing the time and effort required by construction professionals.

### Key Features

- **Document Analysis**: Upload PDF construction plans and automatically extract key elements and specifications.
- **Element Detection**: Identify walls, foundations, roofs, windows, doors, and other construction elements with their dimensions and materials.
- **Cost Estimation**: Generate detailed cost estimates based on detected elements, with material and labor breakdowns.
- **Project Management**: Organize documents, elements, and quotes by project for better workflow.
- **Client Management**: Maintain client information and customize quotes based on preferences.

## Technology Stack

### Backend

- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **AI/ML**: OpenAI GPT-4o for document analysis and element extraction
- **Authentication**: JWT based authentication system
- **API Documentation**: Automatic Swagger/OpenAPI documentation

### Frontend

- **Framework**: React.js with React Router
- **Styling**: TailwindCSS for responsive UI components
- **State Management**: React Context API and Hooks
- **HTTP Client**: Axios for API requests

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- OpenAI API key

### Setup

#### Backend

1. Clone the repository:
   ```bash
   git clone https://github.com/RJ-Flash/construction-ai-platform.git
   cd construction-ai-platform/backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env file to add your OpenAI API key and database connection details
   ```

5. Start the backend server:
   ```bash
   uvicorn app.main:app --reload
   ```

#### Frontend

1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

## Usage

1. Register an account on the platform
2. Create a new construction project
3. Upload construction plan PDFs
4. Analyze documents to extract elements
5. Generate quotes based on extracted elements
6. Review and customize quotes as needed
7. Export quotes in PDF format

## System Architecture

The system follows a modern microservices architecture:

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  Web Frontend │     │   API Server  │     │  AI Services  │
│   (React.js)  │────▶│   (FastAPI)   │────▶│   (OpenAI)    │
└───────────────┘     └───────────────┘     └───────────────┘
                             │
                             ▼
                      ┌───────────────┐
                      │   Database    │
                      │ (PostgreSQL)  │
                      └───────────────┘
```

## API Documentation

When running the backend server, the API documentation is available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
construction-ai-platform/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core functionality
│   │   ├── db/           # Database models and session management
│   │   ├── schemas/      # Pydantic schemas for validation
│   │   ├── services/     # Business logic and external service integration
│   │   └── main.py       # Application entry point
│   ├── scripts/          # Utility scripts
│   ├── .env.example      # Example environment variables
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/   # Reusable UI components
│   │   ├── config/       # Configuration files
│   │   ├── hooks/        # Custom React hooks
│   │   ├── pages/        # Page components
│   │   ├── App.js        # Main application component
│   │   └── index.js      # Entry point
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
