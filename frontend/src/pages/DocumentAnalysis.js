import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { ENDPOINTS } from '../config/api';
import { useToast } from '../hooks/useToast';

// Components
import LoadingSpinner from '../components/LoadingSpinner';

const DocumentAnalysis = () => {
  const { id: documentId } = useParams();
  const navigate = useNavigate();
  const { showToast } = useToast();
  
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [document, setDocument] = useState(null);
  const [project, setProject] = useState(null);
  const [elements, setElements] = useState([]);
  const [analysisStatus, setAnalysisStatus] = useState('');
  const [analysisProgress, setAnalysisProgress] = useState(0);
  
  // Fetch document data on component mount
  useEffect(() => {
    const fetchDocumentData = async () => {
      try {
        setLoading(true);
        
        // Fetch document details
        const documentResponse = await axios.get(ENDPOINTS.DOCUMENTS.DETAILS(documentId));
        setDocument(documentResponse.data);
        
        // If document is already analyzed, fetch elements
        if (documentResponse.data.is_analyzed) {
          const elementsResponse = await axios.get(ENDPOINTS.DOCUMENTS.ELEMENTS(documentId));
          setElements(elementsResponse.data);
        }
        
        // Fetch project details
        if (documentResponse.data.project_id) {
          const projectResponse = await axios.get(
            ENDPOINTS.PROJECTS.DETAILS(documentResponse.data.project_id)
          );
          setProject(projectResponse.data);
        }
        
        // Set initial analysis status
        setAnalysisStatus(documentResponse.data.analysis_status || 'not_analyzed');
      } catch (error) {
        console.error('Error fetching document data:', error);
        showToast('Failed to load document data', 'error');
        
        if (error.response && error.response.status === 404) {
          navigate('/documents');
        }
      } finally {
        setLoading(false);
      }
    };
    
    fetchDocumentData();
  }, [documentId, navigate, showToast]);
  
  // Start document analysis
  const handleStartAnalysis = async () => {
    try {
      setAnalyzing(true);
      setAnalysisStatus('pending');
      setAnalysisProgress(10);
      
      // Request document analysis
      const response = await axios.post(
        ENDPOINTS.DOCUMENTS.ANALYZE,
        {
          file_path: document.file_path,
          project_id: document.project_id
        }
      );
      
      // Update document with analysis results
      setDocument(response.data);
      setElements(response.data.elements || []);
      setAnalysisStatus('completed');
      setAnalysisProgress(100);
      
      showToast('Document analysis completed successfully', 'success');
    } catch (error) {
      console.error('Error analyzing document:', error);
      
      let errorMessage = 'Failed to analyze document';
      if (error.response && error.response.data && error.response.data.detail) {
        errorMessage = error.response.data.detail;
      }
      
      showToast(errorMessage, 'error');
      setAnalysisStatus('failed');
    } finally {
      setAnalyzing(false);
    }
  };
  
  // Format date helper
  const formatDate = (dateString) => {
    if (!dateString) return 'Not available';
    
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };
  
  // Simulate analysis progress
  useEffect(() => {
    let interval;
    
    if (analyzing && analysisProgress < 90) {
      interval = setInterval(() => {
        setAnalysisProgress(prev => {
          // Increment by random amount between 5-15%
          const increment = Math.floor(Math.random() * 10) + 5;
          return Math.min(prev + increment, 90);
        });
      }, 2000);
    }
    
    return () => clearInterval(interval);
  }, [analyzing, analysisProgress]);
  
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
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-8">
        <div className="flex items-center">
          <Link
            to={project ? `/projects/${project.id}` : '/documents'}
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
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Document Analysis</h1>
            <p className="text-gray-600">{document.filename}</p>
          </div>
        </div>
        
        {!document.is_analyzed && !analyzing && (
          <button
            onClick={handleStartAnalysis}
            className="mt-4 md:mt-0 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg 
              className="mr-2 h-5 w-5" 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
            Start Analysis
          </button>
        )}
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Document Info Panel */}
        <div className="lg:col-span-1">
          <div className="bg-white shadow-sm rounded-lg overflow-hidden">
            <div className="p-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-800">Document Information</h2>
            </div>
            
            <div className="p-4">
              <dl className="space-y-4">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Filename</dt>
                  <dd className="mt-1 text-sm text-gray-900">{document.filename}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Type</dt>
                  <dd className="mt-1 text-sm text-gray-900">{document.file_type || 'PDF'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Upload Date</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {formatDate(document.upload_date)}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Project</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {project ? (
                      <Link
                        to={`/projects/${project.id}`}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        {project.name}
                      </Link>
                    ) : (
                      'Not associated with a project'
                    )}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Analysis Status</dt>
                  <dd className="mt-1 text-sm">
                    {analysisStatus === 'completed' || document.is_analyzed ? (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Analyzed
                      </span>
                    ) : analysisStatus === 'pending' || analyzing ? (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                        In Progress
                      </span>
                    ) : analysisStatus === 'failed' ? (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        Failed
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                        Not Analyzed
                      </span>
                    )}
                  </dd>
                </div>
                
                {document.is_analyzed && document.analysis_date && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Analysis Date</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {formatDate(document.analysis_date)}
                    </dd>
                  </div>
                )}
              </dl>
              
              <div className="mt-4 pt-4 border-t border-gray-200">
                <a
                  href={document.file_path}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  <svg
                    className="mr-1 h-4 w-4"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                    />
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                    />
                  </svg>
                  View Document
                </a>
              </div>
            </div>
          </div>
        </div>
        
        {/* Main Content Panel */}
        <div className="lg:col-span-2">
          {/* Analysis Progress */}
          {analyzing && (
            <div className="bg-white shadow-sm rounded-lg p-6 mb-6">
              <h2 className="text-lg font-medium text-gray-800 mb-4">Analysis in Progress</h2>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm font-medium text-gray-700">
                      Analyzing document...
                    </span>
                    <span className="text-sm font-medium text-gray-700">
                      {analysisProgress}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div
                      className="bg-blue-600 h-2.5 rounded-full"
                      style={{ width: `${analysisProgress}%` }}
                    ></div>
                  </div>
                </div>
                <p className="text-sm text-gray-500">
                  We're analyzing your document to identify construction elements, materials, and specifications.
                  This may take a few minutes.
                </p>
              </div>
            </div>
          )}
          
          {/* Analysis Results */}
          {(document.is_analyzed || analysisStatus === 'completed') && (
            <div className="bg-white shadow-sm rounded-lg overflow-hidden mb-6">
              <div className="p-4 border-b border-gray-200">
                <h2 className="text-lg font-medium text-gray-800">Analysis Results</h2>
              </div>
              
              <div className="p-4">
                <div className="mb-6">
                  <h3 className="text-md font-medium text-gray-800 mb-2">
                    Elements Detected
                  </h3>
                  {elements.length === 0 ? (
                    <p className="text-sm text-gray-500">
                      No construction elements were detected in this document.
                    </p>
                  ) : (
                    <div>
                      <p className="text-sm text-gray-500 mb-4">
                        {elements.length} construction elements detected.
                      </p>
                      
                      <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                        <ul className="divide-y divide-gray-200">
                          {elements.map((element) => (
                            <li key={element.id} className="py-3">
                              <div>
                                <h4 className="text-sm font-medium text-gray-900">
                                  {element.type}
                                  {element.dimensions && (
                                    <span className="ml-1 font-normal text-gray-500">
                                      ({element.dimensions})
                                    </span>
                                  )}
                                </h4>
                                <div className="mt-1 text-xs text-gray-500">
                                  {element.materials && (
                                    <p>Material: {element.materials}</p>
                                  )}
                                  {element.quantity && (
                                    <p>Quantity: {element.quantity}</p>
                                  )}
                                  {element.notes && (
                                    <p>Notes: {element.notes}</p>
                                  )}
                                </div>
                              </div>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}
                </div>
                
                {document.specifications && Object.keys(document.specifications).length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-md font-medium text-gray-800 mb-2">
                      Specifications
                    </h3>
                    <div className="bg-gray-50 rounded-lg p-4">
                      {Object.entries(document.specifications).map(([key, value]) => (
                        <div key={key} className="mb-4 last:mb-0">
                          <h4 className="text-sm font-medium text-gray-900 capitalize">
                            {key.replace(/_/g, ' ')}
                          </h4>
                          <ul className="mt-1 list-disc list-inside text-xs text-gray-700 space-y-1">
                            {Array.isArray(value) ? (
                              value.map((item, index) => (
                                <li key={index}>{item}</li>
                              ))
                            ) : (
                              <li>{value}</li>
                            )}
                          </ul>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {document.recommendations && document.recommendations.length > 0 && (
                  <div>
                    <h3 className="text-md font-medium text-gray-800 mb-2">
                      Recommendations
                    </h3>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                        {document.recommendations.map((recommendation, index) => (
                          <li key={index}>{recommendation}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </div>
              
              <div className="p-4 border-t border-gray-200 bg-gray-50">
                <div className="flex justify-end space-x-3">
                  {project && (
                    <Link
                      to={`/projects/${project.id}/quotes/new`}
                      className="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                    >
                      <svg
                        className="mr-1 h-4 w-4"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="2"
                          d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                      </svg>
                      Generate Quote
                    </Link>
                  )}
                  
                  <Link
                    to={project ? `/projects/${project.id}/elements` : '/elements'}
                    className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    <svg
                      className="mr-1 h-4 w-4"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                      />
                    </svg>
                    View All Elements
                  </Link>
                </div>
              </div>
            </div>
          )}
          
          {/* Not Analyzed State */}
          {!document.is_analyzed && !analyzing && (
            <div className="bg-white shadow-sm rounded-lg p-6">
              <div className="text-center py-8">
                <svg
                  className="mx-auto h-12 w-12 text-gray-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                  />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">Document Not Analyzed</h3>
                <p className="mt-1 text-sm text-gray-500">
                  This document has not been analyzed yet. Start the analysis to extract construction
                  elements, materials, and specifications.
                </p>
                <div className="mt-6">
                  <button
                    onClick={handleStartAnalysis}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    <svg
                      className="mr-2 h-5 w-5"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                      />
                    </svg>
                    Start Analysis
                  </button>
                </div>
              </div>
            </div>
          )}
          
          {/* Failed Analysis State */}
          {analysisStatus === 'failed' && !analyzing && (
            <div className="bg-white shadow-sm rounded-lg p-6">
              <div className="text-center py-8">
                <svg
                  className="mx-auto h-12 w-12 text-red-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">Analysis Failed</h3>
                <p className="mt-1 text-sm text-gray-500">
                  The document analysis failed. Please try again or contact support if the issue persists.
                </p>
                <div className="mt-6">
                  <button
                    onClick={handleStartAnalysis}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    <svg
                      className="mr-2 h-5 w-5"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                      />
                    </svg>
                    Retry Analysis
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DocumentAnalysis;
