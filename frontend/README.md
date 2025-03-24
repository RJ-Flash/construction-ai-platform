# Construction AI Platform - Frontend

This is the frontend for the AI-Powered Construction Plan Analysis & Quote Generation System.

## Technology Stack

- React.js for the UI framework
- Tailwind CSS for styling
- ShadCN UI components
- React Query for data fetching
- React Router for routing
- React Hook Form for form handling

## Getting Started

### Prerequisites

- Node.js 16+ and npm/yarn

### Installation

```bash
# Clone the repository
git clone https://github.com/RJ-Flash/construction-ai-platform.git
cd construction-ai-platform/frontend

# Install dependencies
npm install
# or
yarn

# Start the development server
npm run dev
# or
yarn dev
```

## Folder Structure

```
frontend/
├── public/            # Static files
├── src/
│   ├── assets/        # Images, fonts, etc.
│   ├── components/    # Reusable components
│   │   ├── common/    # Common UI components
│   │   ├── layouts/   # Layout components
│   │   └── ui/        # ShadCN UI components
│   ├── hooks/         # Custom React hooks
│   ├── lib/           # Utility functions and libraries
│   ├── pages/         # Page components
│   ├── services/      # API services
│   ├── store/         # State management
│   ├── styles/        # Global styles and Tailwind config
│   ├── types/         # TypeScript types and interfaces
│   ├── App.tsx        # Main App component
│   ├── main.tsx       # Entry point
│   └── router.tsx     # Application routing
├── .env.example       # Environment variables template
├── index.html         # HTML template
├── package.json       # Dependencies and scripts
├── tailwind.config.js # Tailwind CSS configuration
├── tsconfig.json      # TypeScript configuration
└── vite.config.ts     # Vite configuration
```

## Development

### Environment Variables

Copy the `.env.example` file to `.env` and update the variables as needed:

```bash
cp .env.example .env
```

### Available Scripts

- `npm run dev`: Start development server
- `npm run build`: Build for production
- `npm run preview`: Preview production build
- `npm run lint`: Lint code
- `npm run test`: Run tests

## Deployment

### Building for Production

```bash
npm run build
```

This will create a `dist` folder with the compiled assets.

### Deployment to HostGator

1. Build the project
2. Upload the contents of the `dist` folder to your HostGator hosting account
3. For SPA routing to work, make sure to set up the appropriate .htaccess file

## Additional Features

- **Theme Support**: Light and dark mode
- **Responsive Design**: Mobile-friendly interface
- **Accessibility**: WCAG 2.1 compliant components
- **Plugin System**: Support for installing custom plugins

## License

MIT
