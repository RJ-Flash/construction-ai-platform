# Construction AI Platform

A comprehensive platform for construction document analysis, element extraction, and quote generation powered by AI.

## Features

- **Document Analysis**: Upload and analyze construction plans and specifications using AI
- **Element Extraction**: Automatically extract construction elements, materials, and specifications
- **Quote Generation**: Create detailed quotes based on the extracted elements
- **Project Management**: Organize documents, elements, and quotes by project
- **Client Management**: Track client information and manage client-specific quotes
- **Specialized Plugins**: Extend functionality with trade-specific analysis tools
- **Subscription Management**: Flexible subscription plans with usage tracking and plugin licensing

## Specialized Plugin Modules

The platform offers a comprehensive suite of specialized plugins to enhance analysis capabilities:

### Architectural Estimating
- Walls and Partitions Estimator
- Doors and Windows Quantifier
- Flooring and Ceilings Module
- Paint and Finishes Calculator
- Millwork and Cabinetry Estimator

### Structural Estimating
- Concrete Structures Plugin
- Steel Structures Module
- Wood & Timber Structures Plugin
- Masonry & Brickwork Estimator
- Foundations & Footings Analyzer

### MEP (Mechanical, Electrical, Plumbing) Estimating
- Electrical Systems Estimator (load calculation, wiring, fixtures, etc.)
- Plumbing Systems Estimator (piping, fixtures, drainage, etc.)
- HVAC & Mechanical Estimator (equipment, ductwork, controls, etc.)
- Fire Protection Systems Plugin

### Additional Specialized Plugins
- Site Work & Civil Estimating
- Building Envelope Estimating
- Specialty Equipment Estimating
- Green Building & Sustainability Analysis

## Pricing

### Subscription Plans

| Plan | Description | Price |
|------|-------------|-------|
| **Free** | 1 PDF per month | Free |
| **Starter** | 5 PDFs per month | $49/month |
| **Essential** | 10 documents (PDF, CAD, BIM) | $129/month |
| **Professional** | 20 documents per month | $249/month |
| **Advanced** | 10 User Seats, 40 documents per month | $599/month |
| **Ultimate** | Unlimited seats, custom document allowance | Contact Sales |

### Add-Ons

- **Specialized Plugins**: $99-$299 each
- **Premium Setup & Training**: $499 one-time fee
- **Annual Subscription**: 10-15% discount

### Subscription Features

- **Organization Management**: Create and manage organizations with multiple users
- **Usage Tracking**: Monitor document uploads and analysis operations
- **Plugin Licensing**: Purchase and manage plugin licenses
- **Billing Management**: Flexible billing cycles (monthly/annual)
- **Usage Reports**: Track usage and optimize subscription plans

For detailed information about the subscription management system, see [Subscription Management Documentation](docs/subscription_management.md).

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
- Subscription management system

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
    │   ├── plugins/         # Specialized estimating plugins
    │   └── main.py          # Application entry point
    ├── alembic/             # Database migrations
    ├── docs/                # Project documentation 
    ├── tests/               # Unit and integration tests
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

### Plugin Management
- Install and manage specialized estimating plugins
- Apply trade-specific analysis to projects
- Enhanced accuracy for specialized construction fields

### Subscription Management
- Organization dashboard for subscription status
- Usage monitoring and reporting
- Plugin license management
- User seat management

## License

[MIT License](LICENSE)

## About

The Construction AI Platform is designed to help construction professionals automate the tedious process of analyzing construction documents, extracting relevant elements, and creating accurate quotes. By leveraging AI technology, the platform reduces the time spent on manual calculations and data entry, allowing construction firms to focus on delivering high-quality work to their clients.

The subscription management system provides flexible pricing options to suit construction firms of all sizes, from small contractors to large enterprises. Organizations can select the plan that best fits their needs and scale up as their requirements grow.