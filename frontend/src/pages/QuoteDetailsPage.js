import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { ENDPOINTS } from '../config/api';
import { useToast } from '../hooks/useToast';

// Components
import LoadingSpinner from '../components/LoadingSpinner';

const QuoteDetailsPage = () => {
  const { projectId, quoteId } = useParams();
  const navigate = useNavigate();
  const { showToast } = useToast();
  
  const [loading, setLoading] = useState(true);
  const [quote, setQuote] = useState(null);
  const [project, setProject] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  
  // Fetch quote data on component mount
  useEffect(() => {
    const fetchQuoteData = async () => {
      try {
        setLoading(true);
        
        // Fetch quote details
        const quoteResponse = await axios.get(ENDPOINTS.QUOTES.DETAILS(quoteId));
        setQuote(quoteResponse.data);
        
        // If quote has project_id, fetch project details
        if (quoteResponse.data.project_id) {
          const projectResponse = await axios.get(
            ENDPOINTS.PROJECTS.DETAILS(quoteResponse.data.project_id)
          );
          setProject(projectResponse.data);
        }
      } catch (error) {
        console.error('Error fetching quote data:', error);
        
        let errorMessage = 'Failed to load quote data';
        if (error.response && error.response.data && error.response.data.detail) {
          errorMessage = error.response.data.detail;
        }
        
        showToast(errorMessage, 'error');
        
        if (error.response && error.response.status === 404) {
          navigate(projectId ? `/projects/${projectId}/quotes` : '/quotes');
        }
      } finally {
        setLoading(false);
      }
    };
    
    fetchQuoteData();
  }, [quoteId, projectId, navigate, showToast]);
  
  // Format currency helper
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(amount);
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
  
  // Handle quote actions
  const handleUpdateStatus = async (newStatus) => {
    try {
      setActionLoading(true);
      
      // Update quote status
      const response = await axios.patch(
        ENDPOINTS.QUOTES.UPDATE_STATUS(quoteId),
        {
          status: newStatus
        }
      );
      
      setQuote(response.data);
      
      showToast(`Quote status updated to ${newStatus}`, 'success');
    } catch (error) {
      console.error('Error updating quote status:', error);
      
      let errorMessage = 'Failed to update quote status';
      if (error.response && error.response.data && error.response.data.detail) {
        errorMessage = error.response.data.detail;
      }
      
      showToast(errorMessage, 'error');
    } finally {
      setActionLoading(false);
    }
  };
  
  // Handle quote deletion
  const handleDeleteQuote = async () => {
    if (!window.confirm('Are you sure you want to delete this quote? This action cannot be undone.')) {
      return;
    }
    
    try {
      setActionLoading(true);
      
      await axios.delete(ENDPOINTS.QUOTES.DELETE(quoteId));
      
      showToast('Quote deleted successfully', 'success');
      
      navigate(projectId ? `/projects/${projectId}` : '/quotes');
    } catch (error) {
      console.error('Error deleting quote:', error);
      
      let errorMessage = 'Failed to delete quote';
      if (error.response && error.response.data && error.response.data.detail) {
        errorMessage = error.response.data.detail;
      }
      
      showToast(errorMessage, 'error');
    } finally {
      setActionLoading(false);
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
      <div className="mb-8">
        <Link
          to={projectId ? `/projects/${projectId}` : '/quotes'}
          className="text-blue-600 hover:text-blue-800 inline-flex items-center"
        >
          <svg className="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M15 19l-7-7 7-7"
            />
          </svg>
          {projectId ? 'Back to Project' : 'Back to Quotes'}
        </Link>
      </div>
      
      <div className="mb-6 flex flex-col md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">
            {quote.title || `Quote #${quote.id}`}
          </h1>
          <p className="text-gray-600 mt-1">
            Created on {formatDate(quote.created_at)}
            {quote.expiry_date && (
              <span className="ml-3">
                Expires on {formatDate(quote.expiry_date)}
              </span>
            )}
          </p>
          <div className="mt-2">
            <span 
              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                quote.status === 'draft' ? 'bg-gray-100 text-gray-800' :
                quote.status === 'sent' ? 'bg-blue-100 text-blue-800' :
                quote.status === 'accepted' ? 'bg-green-100 text-green-800' :
                quote.status === 'declined' ? 'bg-red-100 text-red-800' : 
                'bg-gray-100 text-gray-800'
              }`}
            >
              {quote.status ? quote.status.charAt(0).toUpperCase() + quote.status.slice(1) : 'Draft'}
            </span>
          </div>
        </div>
        
        <div className="mt-4 md:mt-0 flex flex-wrap gap-2">
          {quote.status === 'draft' && (
            <>
              <button
                type="button"
                onClick={() => handleUpdateStatus('sent')}
                disabled={actionLoading}
                className="inline-flex items-center px-3 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg
                  className="mr-1.5 h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                  />
                </svg>
                Mark as Sent
              </button>
              
              <Link
                to={`${projectId ? `/projects/${projectId}` : ''}/quotes/${quoteId}/edit`}
                className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <svg
                  className="mr-1.5 h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
                  />
                </svg>
                Edit Quote
              </Link>
            </>
          )}
          
          {quote.status === 'sent' && (
            <>
              <button
                type="button"
                onClick={() => handleUpdateStatus('accepted')}
                disabled={actionLoading}
                className="inline-flex items-center px-3 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg
                  className="mr-1.5 h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                Mark as Accepted
              </button>
              
              <button
                type="button"
                onClick={() => handleUpdateStatus('declined')}
                disabled={actionLoading}
                className="inline-flex items-center px-3 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg
                  className="mr-1.5 h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
                Mark as Declined
              </button>
            </>
          )}
          
          <button
            type="button"
            onClick={() => window.open(`${projectId ? `/projects/${projectId}` : ''}/quotes/${quoteId}/pdf`, '_blank')}
            className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg
              className="mr-1.5 h-4 w-4"
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
            Download PDF
          </button>
          
          {quote.status === 'draft' && (
            <button
              type="button"
              onClick={handleDeleteQuote}
              disabled={actionLoading}
              className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg
                className="mr-1.5 h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
              Delete Quote
            </button>
          )}
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Main content - Quote details */}
        <div className="md:col-span-2">
          <div className="bg-white shadow-sm rounded-lg overflow-hidden mb-6">
            <div className="p-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-800">Quote Details</h2>
            </div>
            
            {/* Client Information */}
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">
                Client Information
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {quote.client_name || 'N/A'}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">Client Name</p>
                </div>
                
                {quote.client_email && (
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {quote.client_email}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">Email</p>
                  </div>
                )}
                
                {quote.client_phone && (
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {quote.client_phone}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">Phone</p>
                  </div>
                )}
              </div>
            </div>
            
            {/* Quote Items */}
            <div className="border-b border-gray-200">
              <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
                <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider">
                  Quote Items
                </h3>
              </div>
              
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Description
                      </th>
                      <th scope="col" className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Quantity
                      </th>
                      <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Unit Price
                      </th>
                      <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Total
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {quote.items && quote.items.map((item, index) => (
                      <tr key={index}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">
                            {item.description}
                          </div>
                          {item.details && (
                            <div className="text-sm text-gray-500">
                              {item.details}
                            </div>
                          )}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-500">
                          {item.quantity}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500">
                          {formatCurrency(item.unit_price)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-medium text-gray-900">
                          {formatCurrency(item.total_price || (item.quantity * item.unit_price))}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            
            {/* Quote Totals */}
            <div className="px-6 py-4 bg-gray-50">
              <div className="flex justify-end">
                <dl className="w-full md:w-64 space-y-2 text-sm">
                  <div className="flex justify-between">
                    <dt>Subtotal</dt>
                    <dd className="font-medium text-gray-900">
                      {formatCurrency(quote.subtotal_amount)}
                    </dd>
                  </div>
                  
                  {quote.tax_rate > 0 && (
                    <div className="flex justify-between">
                      <dt>Tax ({quote.tax_rate}%)</dt>
                      <dd className="font-medium text-gray-900">
                        {formatCurrency(quote.tax_amount)}
                      </dd>
                    </div>
                  )}
                  
                  {quote.discount_percentage > 0 && (
                    <div className="flex justify-between">
                      <dt>Discount ({quote.discount_percentage}%)</dt>
                      <dd className="font-medium text-red-600">
                        -{formatCurrency(quote.discount_amount)}
                      </dd>
                    </div>
                  )}
                  
                  <div className="flex justify-between pt-2 border-t border-gray-200">
                    <dt className="font-medium">Total</dt>
                    <dd className="font-bold text-lg text-gray-900">
                      {formatCurrency(quote.total_amount)}
                    </dd>
                  </div>
                </dl>
              </div>
            </div>
            
            {/* Notes */}
            {quote.notes && (
              <div className="p-6 border-t border-gray-200">
                <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-3">
                  Notes
                </h3>
                <p className="text-sm text-gray-700 whitespace-pre-line">{quote.notes}</p>
              </div>
            )}
          </div>
          
          {/* Activity Log (if implemented) */}
          {quote.activity_log && quote.activity_log.length > 0 && (
            <div className="bg-white shadow-sm rounded-lg overflow-hidden">
              <div className="p-4 border-b border-gray-200">
                <h2 className="text-lg font-medium text-gray-800">Activity Log</h2>
              </div>
              
              <div className="p-6">
                <ul className="space-y-4">
                  {quote.activity_log.map((activity, index) => (
                    <li key={index} className="relative pl-6 pb-4 border-l border-gray-200 last:pb-0">
                      <div className="absolute top-0 left-0 w-4 h-4 -ml-2 rounded-full bg-blue-500"></div>
                      <div className="text-sm">
                        <p className="font-medium text-gray-900">{activity.action}</p>
                        <p className="text-gray-500 mt-1">
                          {activity.user ? `By ${activity.user}` : ''} on {formatDate(activity.timestamp)}
                        </p>
                        {activity.notes && (
                          <p className="text-gray-700 mt-1">{activity.notes}</p>
                        )}
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
        
        {/* Sidebar */}
        <div className="md:col-span-1">
          {/* Quote Info */}
          <div className="bg-white shadow-sm rounded-lg overflow-hidden mb-6">
            <div className="p-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-800">Quote Information</h2>
            </div>
            
            <div className="p-4">
              <dl className="space-y-4">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Quote ID</dt>
                  <dd className="mt-1 text-sm text-gray-900">#{quote.id}</dd>
                </div>
                
                <div>
                  <dt className="text-sm font-medium text-gray-500">Status</dt>
                  <dd className="mt-1 text-sm">
                    <span 
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        quote.status === 'draft' ? 'bg-gray-100 text-gray-800' :
                        quote.status === 'sent' ? 'bg-blue-100 text-blue-800' :
                        quote.status === 'accepted' ? 'bg-green-100 text-green-800' :
                        quote.status === 'declined' ? 'bg-red-100 text-red-800' : 
                        'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {quote.status ? quote.status.charAt(0).toUpperCase() + quote.status.slice(1) : 'Draft'}
                    </span>
                  </dd>
                </div>
                
                {project && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Project</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      <Link
                        to={`/projects/${project.id}`}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        {project.name}
                      </Link>
                    </dd>
                  </div>
                )}
                
                <div>
                  <dt className="text-sm font-medium text-gray-500">Created On</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {formatDate(quote.created_at)}
                  </dd>
                </div>
                
                {quote.expiry_date && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Expires On</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {formatDate(quote.expiry_date)}
                    </dd>
                  </div>
                )}
                
                {quote.updated_at && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Last Updated</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {formatDate(quote.updated_at)}
                    </dd>
                  </div>
                )}
              </dl>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuoteDetailsPage;