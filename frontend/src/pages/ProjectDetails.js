import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { ENDPOINTS } from '../config/api';
import { useToast } from '../hooks/useToast';

// Components
import DocumentUpload from '../components/DocumentUpload';
import TabNavigation from '../components/TabNavigation';
import DocumentsList from '../components/DocumentsList';
import ElementsList from '../components/ElementsList';
import QuotesList from '../components/QuotesList';
import LoadingSpinner from '../components/LoadingSpinner';

const ProjectDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { showToast } = useToast();
  
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [showUploadModal, setShowUploadModal] = useState(false);
  
  // Data for tabs
  const [documents, setDocuments] = useState([]);
  const [elements, setElements] = useState([]);
  const [quotes, setQuotes] = useState([]);

  // Fetch project data on component mount
  useEffect(() => {
    const fetchProjectData = async () => {
      try {
        setLoading(true);
        
        // Fetch project details
        const projectResponse = await axios.get(ENDPOINTS.PROJECTS.DETAILS(id));
        setProject(projectResponse.data);
        
        // Fetch project documents
        const documentsResponse = await axios.get(ENDPOINTS.PROJECTS.DOCUMENTS(id));
        setDocuments(documentsResponse.data);
        
        // Fetch project elements
        const elementsResponse = await axios.get(ENDPOINTS.PROJECTS.ELEMENTS(id));
        setElements(elementsResponse.data);
        
        // Fetch project quotes
        const quotesResponse = await axios.get(ENDPOINTS.PROJECTS.QUOTES(id));
        setQuotes(quotesResponse.data);
      } catch (error) {
        console.error('Error fetching project data:', error);
        showToast('Failed to load project data', 'error');
        
        if (error.response && error.response.status === 404) {
          navigate('/projects');
        }
      } finally {
        setLoading(false);
      }
    };
    
    fetchProjectData();
  }, [id, navigate, showToast]);

  // Handle tab changes
  const handleTabChange = (tab) => {
    setActiveTab(tab);
  };

  // Toggle document upload modal
  const handleUploadClick = () => {
    setShowUploadModal(true);
  };

  // Handle document upload success
  const handleUploadSuccess = (uploadedDocument) => {
    setShowUploadModal(false);
    setDocuments(prevDocuments => [...prevDocuments, uploadedDocument]);
    showToast('Document uploaded successfully', 'success');
  };

  // Format date helper
  const formatDate = (dateString) => {
    if (!dateString) return 'Not set';
    
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  // Get status badge color
  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'planning':
        return 'bg-blue-100 text-blue-800';
      case 'in-progress':
      case 'inprogress':
        return 'bg-yellow-100 text-yellow-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'on-hold':
      case 'onhold':
        return 'bg-orange-100 text-orange-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // If loading, show spinner
  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Project header */}
      <div className="mb-8">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-2">
          <div className="flex items-center">
            <Link
              to="/projects"
              className="text-blue-600 hover:text-blue-800 mr-3"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M15 19l-7-7 7-7"
                />
              </svg>
            </Link>
            <h1 className="text-2xl font-bold text-gray-800">{project?.name}</h1>
            <span
              className={`ml-4 px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(
                project?.status
              )}`}
            >
              {project?.status?.charAt(0).toUpperCase() + project?.status?.slice(1) || 'Unknown'}
            </span>
          </div>
          
          <div className="mt-4 md:mt-0 flex space-x-2">
            <button
              onClick={handleUploadClick}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg className="mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
              Upload Document
            </button>
            
            <Link
              to={`/projects/${id}/edit`}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg className="mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                />
              </svg>
              Edit Project
            </Link>
          </div>
        </div>
        
        <p className="text-gray-600 mb-4">
          {project?.description || 'No description provided'}
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <span className="text-gray-500 text-sm">Client</span>
            <p className="text-gray-800 font-medium">
              {project?.client_name || 'Not specified'}
            </p>
          </div>
          
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <span className="text-gray-500 text-sm">Location</span>
            <p className="text-gray-800 font-medium">
              {project?.location || 'Not specified'}
            </p>
          </div>
          
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <span className="text-gray-500 text-sm">Start Date</span>
            <p className="text-gray-800 font-medium">
              {formatDate(project?.start_date)}
            </p>
          </div>
          
          <div className="bg-white p-4 rounded-lg shadow-sm">
            <span className="text-gray-500 text-sm">End Date</span>
            <p className="text-gray-800 font-medium">
              {formatDate(project?.end_date)}
            </p>
          </div>
        </div>
      </div>
      
      {/* Tab navigation */}
      <TabNavigation
        tabs={[
          { id: 'overview', label: 'Overview' },
          { id: 'documents', label: 'Documents', count: documents.length },
          { id: 'elements', label: 'Elements', count: elements.length },
          { id: 'quotes', label: 'Quotes', count: quotes.length }
        ]}
        activeTab={activeTab}
        onChange={handleTabChange}
      />
      
      {/* Tab content */}
      <div className="mt-6">
        {activeTab === 'overview' && (
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-medium text-gray-800 mb-4">Project Overview</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-md font-medium text-gray-700 mb-3">Project Details</h3>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <dl className="space-y-3">
                    <div className="flex justify-between">
                      <dt className="text-sm font-medium text-gray-500">Project Name</dt>
                      <dd className="text-sm text-gray-900">{project?.name}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-sm font-medium text-gray-500">Client</dt>
                      <dd className="text-sm text-gray-900">{project?.client_name || 'Not specified'}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-sm font-medium text-gray-500">Location</dt>
                      <dd className="text-sm text-gray-900">{project?.location || 'Not specified'}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-sm font-medium text-gray-500">Status</dt>
                      <dd className="text-sm text-gray-900">{project?.status || 'Not specified'}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-sm font-medium text-gray-500">Created On</dt>
                      <dd className="text-sm text-gray-900">{formatDate(project?.created_at)}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-sm font-medium text-gray-500">Last Updated</dt>
                      <dd className="text-sm text-gray-900">{formatDate(project?.updated_at)}</dd>
                    </div>
                  </dl>
                </div>
              </div>
              
              <div>
                <h3 className="text-md font-medium text-gray-700 mb-3">Project Stats</h3>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <dl className="space-y-3">
                    <div className="flex justify-between">
                      <dt className="text-sm font-medium text-gray-500">Documents</dt>
                      <dd className="text-sm text-gray-900">{documents.length}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-sm font-medium text-gray-500">Analyzed Documents</dt>
                      <dd className="text-sm text-gray-900">
                        {documents.filter(doc => doc.is_analyzed).length}
                      </dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-sm font-medium text-gray-500">Elements Detected</dt>
                      <dd className="text-sm text-gray-900">{elements.length}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt className="text-sm font-medium text-gray-500">Quotes Generated</dt>
                      <dd className="text-sm text-gray-900">{quotes.length}</dd>
                    </div>
                    {quotes.length > 0 && (
                      <div className="flex justify-between">
                        <dt className="text-sm font-medium text-gray-500">Latest Quote</dt>
                        <dd className="text-sm text-gray-900">
                          ${quotes[0]?.total_min?.toLocaleString()} - ${quotes[0]?.total_max?.toLocaleString()}
                        </dd>
                      </div>
                    )}
                  </dl>
                </div>
              </div>
            </div>
            
            <div className="mt-6">
              <h3 className="text-md font-medium text-gray-700 mb-3">Quick Actions</h3>
              <div className="flex flex-wrap gap-3">
                <button
                  onClick={handleUploadClick}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Upload Document
                </button>
                
                <Link
                  to={`/projects/${id}/quotes/new`}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                >
                  Generate Quote
                </Link>
                
                <button
                  onClick={() => setActiveTab('elements')}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  View Elements
                </button>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'documents' && (
          <DocumentsList 
            documents={documents} 
            projectId={id} 
            onUploadClick={handleUploadClick}
            onDocumentAnalyzed={(analyzedDocument) => {
              // Update documents list with analyzed document
              setDocuments(prevDocuments => 
                prevDocuments.map(doc => 
                  doc.id === analyzedDocument.id ? analyzedDocument : doc
                )
              );
              
              // If elements were extracted, update elements list
              if (analyzedDocument.elements && analyzedDocument.elements.length > 0) {
                setElements(prevElements => [...prevElements, ...analyzedDocument.elements]);
              }
            }}
          />
        )}
        
        {activeTab === 'elements' && (
          <ElementsList 
            elements={elements} 
            projectId={id}
            onGenerateQuote={() => {
              navigate(`/projects/${id}/quotes/new`);
            }}
          />
        )}
        
        {activeTab === 'quotes' && (
          <QuotesList 
            quotes={quotes} 
            projectId={id}
            onNewQuote={() => {
              navigate(`/projects/${id}/quotes/new`);
            }}
          />
        )}
      </div>
      
      {/* Document upload modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-1/2 lg:w-1/3 shadow-lg rounded-md bg-white">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">Upload Document</h3>
              <button
                onClick={() => setShowUploadModal(false)}
                className="text-gray-400 hover:text-gray-500"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>
            
            <DocumentUpload 
              projectId={id} 
              onUploadSuccess={handleUploadSuccess} 
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default ProjectDetails;
