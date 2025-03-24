import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { ENDPOINTS } from '../config/api';
import { useToast } from '../hooks/useToast';

// Components
import LoadingSpinner from './LoadingSpinner';

const QuotesList = ({ quotes, projectId, onNewQuote }) => {
  const { showToast } = useToast();
  const [expandedQuoteId, setExpandedQuoteId] = useState(null);
  const [exportLoading, setExportLoading] = useState(false);

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

  // Format currency helper
  const formatCurrency = (amount, currency = 'USD') => {
    if (amount === null || amount === undefined) return 'N/A';
    
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency
    }).format(amount);
  };

  // Toggle quote details
  const toggleQuoteDetails = (quoteId) => {
    setExpandedQuoteId(expandedQuoteId === quoteId ? null : quoteId);
  };

  // Export quote to PDF
  const handleExportPDF = async (quote) => {
    try {
      setExportLoading(true);
      
      // Call API to generate PDF
      const response = await axios.post(
        `${ENDPOINTS.QUOTES.EXPORT(quote.id)}`,
        { format: 'pdf' }
      );
      
      // Create a download link for the PDF
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `Quote_${quote.id}.pdf`);
      document.body.appendChild(link);
      link.click();
      
      showToast('Quote exported successfully', 'success');
    } catch (error) {
      console.error('Error exporting quote:', error);
      
      let errorMessage = 'Failed to export quote';
      if (error.response && error.response.data && error.response.data.detail) {
        errorMessage = error.response.data.detail;
      }
      
      showToast(errorMessage, 'error');
    } finally {
      setExportLoading(false);
    }
  };

  // Get status badge
  const getStatusBadge = (status) => {
    switch (status?.toLowerCase()) {
      case 'draft':
        return (
          <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
            Draft
          </span>
        );
      case 'submitted':
        return (
          <span className="bg-yellow-100 text-yellow-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
            Submitted
          </span>
        );
      case 'approved':
        return (
          <span className="bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
            Approved
          </span>
        );
      case 'rejected':
        return (
          <span className="bg-red-100 text-red-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
            Rejected
          </span>
        );
      default:
        return (
          <span className="bg-gray-100 text-gray-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
            {status?.charAt(0).toUpperCase() + status?.slice(1) || 'Unknown'}
          </span>
        );
    }
  };

  return (
    <div className="bg-white shadow-sm rounded-lg overflow-hidden">
      <div className="p-4 flex justify-between items-center border-b border-gray-200">
        <h2 className="text-lg font-medium text-gray-800">
          Quotes
        </h2>
        <button
          onClick={onNewQuote}
          className="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
        >
          <svg className="mr-1 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M12 6v6m0 0v6m0-6h6m-6 0H6"
            />
          </svg>
          New Quote
        </button>
      </div>
      
      {quotes.length === 0 ? (
        <div className="p-6 text-center">
          <p className="text-gray-500">No quotes found for this project.</p>
          <p className="mt-2 text-sm text-gray-500">
            Generate a quote based on the extracted elements to get started.
          </p>
          <button
            onClick={onNewQuote}
            className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            Generate Quote
          </button>
        </div>
      ) : (
        <ul className="divide-y divide-gray-200">
          {quotes.map((quote) => (
            <li key={quote.id}>
              <div className="px-4 py-4 hover:bg-gray-50">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center">
                      <h3 className="text-sm font-medium text-gray-900">
                        {quote.name || `Quote #${quote.version}`}
                      </h3>
                      <span className="ml-2">
                        {getStatusBadge(quote.status)}
                      </span>
                    </div>
                    <p className="mt-1 text-xs text-gray-500">
                      Created on {formatDate(quote.created_at)}
                    </p>
                    <div className="mt-2">
                      <span className="text-sm font-medium text-gray-900">
                        {formatCurrency(quote.total_min)} - {formatCurrency(quote.total_max)}
                      </span>
                      <span className="ml-1 text-xs text-gray-500">
                        {quote.currency}
                      </span>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => toggleQuoteDetails(quote.id)}
                      className="inline-flex items-center p-1 border border-transparent rounded-full text-gray-400 hover:bg-gray-100 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      <svg
                        className={`h-5 w-5 transform transition-transform ${
                          expandedQuoteId === quote.id ? 'rotate-180' : ''
                        }`}
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="2"
                          d="M19 9l-7 7-7-7"
                        />
                      </svg>
                    </button>
                    
                    <Link
                      to={`/quotes/${quote.id}`}
                      className="inline-flex items-center p-1 border border-transparent rounded-full text-gray-400 hover:bg-gray-100 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      <svg
                        className="h-5 w-5"
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
                    </Link>
                    
                    <button
                      onClick={() => handleExportPDF(quote)}
                      disabled={exportLoading}
                      className="inline-flex items-center p-1 border border-transparent rounded-full text-gray-400 hover:bg-gray-100 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      {exportLoading ? (
                        <LoadingSpinner size="small" />
                      ) : (
                        <svg
                          className="h-5 w-5"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth="2"
                            d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                          />
                        </svg>
                      )}
                    </button>
                  </div>
                </div>
                
                {/* Expanded quote details */}
                {expandedQuoteId === quote.id && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
                          Quote Details
                        </h4>
                        <dl className="space-y-2">
                          <div className="flex justify-between">
                            <dt className="text-sm font-medium text-gray-500">Region</dt>
                            <dd className="text-sm text-gray-900">{quote.region || 'Not specified'}</dd>
                          </div>
                          <div className="flex justify-between">
                            <dt className="text-sm font-medium text-gray-500">Version</dt>
                            <dd className="text-sm text-gray-900">{quote.version}</dd>
                          </div>
                          <div className="flex justify-between">
                            <dt className="text-sm font-medium text-gray-500">Status</dt>
                            <dd className="text-sm text-gray-900">{quote.status}</dd>
                          </div>
                          <div className="flex justify-between">
                            <dt className="text-sm font-medium text-gray-500">Last Updated</dt>
                            <dd className="text-sm text-gray-900">{formatDate(quote.updated_at)}</dd>
                          </div>
                        </dl>
                      </div>
                      
                      <div>
                        <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
                          Cost Summary
                        </h4>
                        <dl className="space-y-2">
                          <div className="flex justify-between">
                            <dt className="text-sm font-medium text-gray-500">Minimum Cost</dt>
                            <dd className="text-sm text-gray-900">{formatCurrency(quote.total_min)}</dd>
                          </div>
                          <div className="flex justify-between">
                            <dt className="text-sm font-medium text-gray-500">Maximum Cost</dt>
                            <dd className="text-sm text-gray-900">{formatCurrency(quote.total_max)}</dd>
                          </div>
                          <div className="flex justify-between">
                            <dt className="text-sm font-medium text-gray-500">Currency</dt>
                            <dd className="text-sm text-gray-900">{quote.currency}</dd>
                          </div>
                          <div className="flex justify-between">
                            <dt className="text-sm font-medium text-gray-500">Items</dt>
                            <dd className="text-sm text-gray-900">{quote.items?.length || 0}</dd>
                          </div>
                        </dl>
                      </div>
                    </div>
                    
                    {quote.description && (
                      <div className="mt-4">
                        <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
                          Description
                        </h4>
                        <p className="text-sm text-gray-700">
                          {quote.description}
                        </p>
                      </div>
                    )}
                    
                    <div className="mt-4 flex justify-end">
                      <Link
                        to={`/quotes/${quote.id}`}
                        className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                      >
                        View Full Quote
                      </Link>
                    </div>
                  </div>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default QuotesList;
