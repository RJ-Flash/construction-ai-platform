import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Components
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import ToastContainer from './components/ToastContainer';

// Pages
import Dashboard from './pages/Dashboard';
import ProjectsPage from './pages/ProjectsPage';
import ProjectDetailsPage from './pages/ProjectDetailsPage';
import DocumentsPage from './pages/DocumentsPage';
import DocumentAnalysis from './pages/DocumentAnalysis';
import ElementsPage from './pages/ElementsPage';
import ElementDetailsPage from './pages/ElementDetailsPage';
import QuoteGeneratorPage from './pages/QuoteGeneratorPage';
import QuoteDetailsPage from './pages/QuoteDetailsPage';
import SettingsPage from './pages/SettingsPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import NotFoundPage from './pages/NotFoundPage';

// Providers
import { ToastProvider } from './contexts/ToastContext';
import { AuthProvider } from './contexts/AuthContext';

const App = () => {
  return (
    <Router>
      <AuthProvider>
        <ToastProvider>
          <div className="flex h-screen bg-gray-100">
            <Sidebar />
            <div className="flex-1 flex flex-col overflow-hidden">
              <Navbar />
              <main className="flex-1 overflow-y-auto">
                <Routes>
                  {/* Auth Routes */}
                  <Route path="/login" element={<LoginPage />} />
                  <Route path="/register" element={<RegisterPage />} />
                  
                  {/* Dashboard */}
                  <Route path="/" element={<Dashboard />} />
                  
                  {/* Projects Routes */}
                  <Route path="/projects" element={<ProjectsPage />} />
                  <Route path="/projects/:projectId" element={<ProjectDetailsPage />} />
                  
                  {/* Documents Routes */}
                  <Route path="/documents" element={<DocumentsPage />} />
                  <Route path="/documents/:id" element={<DocumentAnalysis />} />
                  <Route path="/projects/:projectId/documents" element={<DocumentsPage />} />
                  
                  {/* Elements Routes */}
                  <Route path="/elements" element={<ElementsPage />} />
                  <Route path="/elements/:elementId" element={<ElementDetailsPage />} />
                  <Route path="/projects/:projectId/elements" element={<ElementsPage />} />
                  <Route path="/projects/:projectId/elements/:elementId" element={<ElementDetailsPage />} />
                  
                  {/* Quotes Routes */}
                  <Route path="/projects/:projectId/quotes/new" element={<QuoteGeneratorPage />} />
                  <Route path="/projects/:projectId/quotes/:quoteId" element={<QuoteDetailsPage />} />
                  <Route path="/projects/:projectId/quotes/:quoteId/edit" element={<QuoteGeneratorPage />} />
                  
                  {/* Settings */}
                  <Route path="/settings" element={<SettingsPage />} />
                  
                  {/* Not Found */}
                  <Route path="*" element={<NotFoundPage />} />
                </Routes>
              </main>
            </div>
          </div>
          <ToastContainer />
        </ToastProvider>
      </AuthProvider>
    </Router>
  );
};

export default App;