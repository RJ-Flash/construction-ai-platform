import React from 'react';
import { Link } from 'react-router-dom';
import { Home, ArrowLeft, Search } from 'lucide-react';

// UI Components
import { Button } from '@/components/ui/button';

const NotFound = () => {
  return (
    <div className="container flex flex-col items-center justify-center h-screen px-4 mx-auto">
      <div className="text-center space-y-6 max-w-md">
        <h1 className="text-9xl font-bold text-primary">404</h1>
        
        <div className="space-y-2">
          <h2 className="text-2xl font-bold tracking-tight">Page not found</h2>
          <p className="text-muted-foreground">
            The page you're looking for doesn't exist or has been moved.
          </p>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-2 justify-center">
          <Button asChild>
            <Link to="/">
              <Home className="mr-2 h-4 w-4" />
              Go to Dashboard
            </Link>
          </Button>
          
          <Button variant="outline" asChild>
            <Link to="/" onClick={() => window.history.back()}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Go Back
            </Link>
          </Button>
        </div>
        
        <div className="pt-8">
          <p className="text-sm text-muted-foreground">
            Looking for something specific?
          </p>
          <div className="mt-2 flex items-center justify-center">
            <Button variant="link">
              <Search className="mr-2 h-4 w-4" />
              Search documentation
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotFound;