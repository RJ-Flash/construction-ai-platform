# Construction AI Platform

A comprehensive platform for construction document analysis, element extraction, and quote generation powered by AI.

## Features

- **Document Analysis**: Upload and analyze construction plans and specifications using AI
- **Element Extraction**: Automatically extract construction elements, materials, and specifications
- **Quote Generation**: Create detailed quotes based on the extracted elements
- **Project Management**: Organize documents, elements, and quotes by project
- **Client Management**: Track client information and manage client-specific quotes

## Technology Stack

### Frontend
- React.js
- React Router for navigation
- Tailwind CSS for styling
- Axios for API communication

### Backend (API)
- FastAPI (Python)
- PostgreSQL database
- JWT authentication
- AI document processing pipeline

## Installation

### Prerequisites
- Node.js (v14+)
- npm or yarn
- Python 3.8+
- PostgreSQL

### Frontend Setup

```bash
# Clone the repository
git clone https://github.com/RJ-Flash/construction-ai-platform.git
cd construction-ai-platform/frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env file with your configuration

# Start development server
npm start
```

### Backend Setup

```bash
# Navigate to backend directory
cd ../backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env file with your configuration

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

## Project Structure

```
├── frontend/
│   ├── public/
│   └── src/
│       ├── components/      # Reusable UI components
│       ├── config/          # Configuration files
│       ├── contexts/        # React context providers
│       ├── hooks/           # Custom React hooks
│       ├── pages/           # Page components
│       ├── styles/          # Global styles
│       ├── utils/           # Utility functions
│       ├── App.js           # Main application component
│       └── index.js         # Entry point
│
└── backend/
    ├── app/
    │   ├── api/             # API routes
    │   ├── core/            # Core functionality
    │   ├── db/              # Database models and migrations
    │   ├── services/        # Business logic
    │   └── main.py          # Application entry point
    ├── alembic/             # Database migrations
    └── requirements.txt     # Python dependencies
```

## Key Components

### Document Analysis Page
- Upload construction documents
- View analysis progress
- Display extracted elements and specifications

### Elements Management
- View all extracted elements
- Filter by type, material, and other properties
- Edit and annotate elements

### Quote Generator
- Select elements to include in quotes
- Customize pricing and quantities
- Add client information and notes
- Generate professional quote PDFs

## License

[MIT License](LICENSE)

## About

The Construction AI Platform is designed to help construction professionals automate the tedious process of analyzing construction documents, extracting relevant elements, and creating accurate quotes. By leveraging AI technology, the platform reduces the time spent on manual calculations and data entry, allowing construction firms to focus on delivering high-quality work to their clients.