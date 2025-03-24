import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { ENDPOINTS } from '../config/api';
import { useToast } from '../hooks/useToast';

// Components
import LoadingSpinner from './LoadingSpinner';

const DocumentsList = ({ documents, projectId, onUploadClick, onDocumentAnalyzed }) => {
  const { showToast } = useToast();
  const [analyzeLoading, setAnalyzeLoading] = useState({});
  const [expandedDocId, setExpandedDocId] = useState(null);

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

  // Handle document analysis
  const handleAnalyze = async (document) => {
    // Skip if already analyzed
    if (document.is_analyzed) {
      showToast('Document already analyzed', 'info');
      return;
    }
    
    try {
      // Set loading state for this document
      setAnalyzeLoading(prev => ({ ...prev, [document.id]: true }));
      
      // Request document analysis
      const response = await axios.post(
        ENDPOINTS.DOCUMENTS.ANALYZE,
        {
          file_path: document.file_path,
          project_id: projectId
        }
      );
      
      showToast('Document analysis completed', 'success');
      
      // Call the callback with analyzed document
      if (onDocumentAnalyzed) {
        onDocumentAnalyzed(response.data);
      }
    } catch (error) {
      console.error('Error analyzing document:', error);
      
      let errorMessage = 'Failed to analyze document';
      if (error.response && error.response.data && error.response.data.detail) {
        errorMessage = error.response.data.detail;
      }
      
      showToast(errorMessage, 'error');
    } finally {
      setAnalyzeLoading(prev => ({ ...prev, [document.id]: false }));
    }
  };

  // Toggle document details
  const toggleDetails = (docId) => {
    setExpandedDocId(expandedDocId === docId ? null : docId);
  };

  // Get status badge for document
  const getStatusBadge = (document) => {
    if (document.is_analyzed) {
      return (
        <span className="bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
          Analyzed
        </span>
      );
    }
    
    if (document.analysis_status === 'pending') {
      return (
        <span className="bg-yellow-100 text-yellow-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
          Pending
        </span>
      );
    }
    
    if (document.analysis_status === 'failed') {
      return (
        <span className="bg-red-100 text-red-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
          Failed
        </span>
      );
    }
    
    return (
      <span className="bg-gray-100 text-gray-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
        Not Analyzed
      </span>
    );
  };

  return (
    <div className="bg-white shadow-sm rounded-lg overflow-hidden">
      <div className="p-4 flex justify-between items-center border-b border-gray-200">
        <h2 className="text-lg font-medium text-gray-800">
          Documents
        </h2>
        <button
          onClick={onUploadClick}
          className="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <svg className="mr-1 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M12 6v6m0 0v6m0-6h6m-6 0H6"
            />
          </svg>
          Upload
        </button>
      </div>
      
      {documents.length === 0 ? (
        <div className="p-6 text-center">
          <p className="text-gray-500">No documents found for this project.</p>
          <button
            onClick={onUploadClick}
            className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Upload your first document
          </button>
        </div>
      ) : (
        <ul className="divide-y divide-gray-200">
          {documents.map((document) => (
            <li key={document.id} className="p-4 hover:bg-gray-50">
              <div className="flex justify-between items-start">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 mt-1">
                    <svg className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                      />
                    </svg>
                  </div>
                  <div>
                    <div className="flex items-center">
                      <h3 className="text-sm font-medium text-gray-900">{document.filename}</h3>
                      <span className="ml-2">
                        {getStatusBadge(document)}
                      </span>
                    </div>
                    <p className="mt-1 text-xs text-gray-500">
                      Uploaded {formatDate(document.upload_date)}
                    </p>
                    {document.is_analyzed && document.analysis_date && (
                      <p className="text-xs text-gray-500">
                        Analyzed {formatDate(document.analysis_date)}
                      </p>
                    )}
                  </div>
                </div>
                
                <div className="flex space-x-2">
                  <button
                    onClick={() => toggleDetails(document.id)}
                    className="inline-flex items-center p-1 border border-transparent rounded-full text-gray-400 hover:bg-gray-100 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    <svg
                      className="h-5 w-5"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      aria-hidden="true"
                    >
                      {expandedDocId === document.id ? (
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="2"
                          d="M5 15l7-7 7 7"
                        />
                      ) : (
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="2"
                          d="M19 9l-7 7-7-7"
                        />
                      )}
                    </svg>
                  </button>
                  
                  <a
                    href={`${document.file_path}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center p-1 border border-transparent rounded-full text-gray-400 hover:bg-gray-100 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    <svg
                      className="h-5 w-5"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      aria-hidden="true"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth="2"
                        d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                      />
                    </svg>
                  </a>
                  
                  {!document.is_analyzed && (
                    <button
                      onClick={() => handleAnalyze(document)}
                      disabled={analyzeLoading[document.id]}
                      className="inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      {analyzeLoading[document.id] ? (
                        <LoadingSpinner size="small" className="mr-1" />
                      ) : (
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
                      )}
                      {analyzeLoading[document.id] ? 'Analyzing...' : 'Analyze'}
                    </button>
                  )}
                </div>
              </div>
              
              {/* Expanded document details */}
              {expandedDocId === document.id && (
                <div className="mt-3 bg-gray-50 p-3 rounded-md">
                  {document.is_analyzed ? (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Analysis Results</h4>
                      <div className="space-y-2">
                        <div>
                          <span className="text-xs font-medium text-gray-500">Elements Detected:</span>
                          <span className="ml-2 text-xs text-gray-900">
                            {document.elements && document.elements.length > 0
                              ? document.elements.length
                              : 'None'}
                          </span>
                        </div>
                        
                        {document.elements && document.elements.length > 0 && (
                          <div className="mt-1">
                            <span className="text-xs font-medium text-gray-500">Element Types:</span>
                            <div className="mt-1 flex flex-wrap gap-1">
                              {Array.from(
                                new Set(document.elements.map(elem => elem.type))
                              ).map(type => (
                                <span
                                  key={type}
                                  className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                                >
                                  {type}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {document.analysis_message && (
                          <div>
                            <span className="text-xs font-medium text-gray-500">Notes:</span>
                            <p className="mt-1 text-xs text-gray-700">
                              {document.analysis_message}
                            </p>
                          </div>
                        )}
                      </div>
                      
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <Link
                          to={`/documents/${document.id}/elements`}
                          className="text-xs font-medium text-blue-600 hover:text-blue-800"
                        >
                          View detailed analysis
                        </Link>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-2">
                      <p className="text-sm text-gray-500">
                        This document has not been analyzed yet.
                      </p>
                      <button
                        onClick={() => handleAnalyze(document)}
                        disabled={analyzeLoading[document.id]}
                        className="mt-2 inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                      >
                        {analyzeLoading[document.id] ? (
                          <>
                            <LoadingSpinner size="small" color="white" className="mr-2" />
                            Analyzing...
                          </>
                        ) : (
                          'Analyze Now'
                        )}
                      </button>
                    </div>
                  )}
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default DocumentsList;
