import React, { useState } from 'react';
import { Link } from 'react-router-dom';

const QuotesList = ({ quotes, projectId = null, className = '' }) => {
  const [expandedQuoteId, setExpandedQuoteId] = useState(null);
  
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
  
  // Toggle expanded/collapsed state for a quote
  const toggleQuote = (quoteId) => {
    if (expandedQuoteId === quoteId) {
      setExpandedQuoteId(null);
    } else {
      setExpandedQuoteId(quoteId);
    }
  };
  
  return (
    <div className={`bg-white shadow-sm rounded-lg overflow-hidden ${className}`}>
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-medium text-gray-800">Quotes</h2>
        <p className="mt-1 text-sm text-gray-600">
          {quotes.length} {quotes.length === 1 ? 'quote' : 'quotes'} found
        </p>
      </div>
      
      {quotes.length > 0 ? (
        <div className="divide-y divide-gray-200">
          {quotes.map((quote) => (
            <div key={quote.id} className="group">
              <div 
                className="p-4 hover:bg-gray-50 cursor-pointer"
                onClick={() => toggleQuote(quote.id)}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-sm font-medium text-gray-900">
                      Quote #{quote.id} - {quote.title || 'Untitled Quote'}
                    </h3>
                    
                    <div className="mt-1 text-xs text-gray-500">
                      Created: {formatDate(quote.created_at)}
                      {quote.client_name && (
                        <span className="ml-3">Client: {quote.client_name}</span>
                      )}
                    </div>
                    
                    <div className="mt-2 flex items-center">
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
                      
                      {quote.expiry_date && (
                        <span className="ml-3 text-xs text-gray-500">
                          Expires: {formatDate(quote.expiry_date)}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center">
                    <span className="text-lg font-semibold text-gray-900 mr-3">
                      {formatCurrency(quote.total_amount)}
                    </span>
                    
                    <svg
                      className={`h-5 w-5 text-gray-400 transform transition-transform ${
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
                  </div>
                </div>
              </div>
              
              {/* Expanded details */}
              {expandedQuoteId === quote.id && (
                <div className="px-4 pb-4 bg-gray-50">
                  <div className="border-t border-gray-200 pt-4">
                    {/* Quote details */}
                    <div className="mb-4">
                      <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
                        Quote Details
                      </h4>
                      
                      <dl className="grid grid-cols-1 md:grid-cols-3 gap-x-4 gap-y-2 text-sm">
                        {quote.client_name && (
                          <div>
                            <dt className="text-gray-500">Client</dt>
                            <dd className="font-medium text-gray-900">{quote.client_name}</dd>
                          </div>
                        )}
                        
                        {quote.client_email && (
                          <div>
                            <dt className="text-gray-500">Email</dt>
                            <dd className="font-medium text-gray-900">{quote.client_email}</dd>
                          </div>
                        )}
                        
                        {quote.client_phone && (
                          <div>
                            <dt className="text-gray-500">Phone</dt>
                            <dd className="font-medium text-gray-900">{quote.client_phone}</dd>
                          </div>
                        )}
                      </dl>
                    </div>
                    
                    {/* Quote items summary */}
                    <div className="mb-4">
                      <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
                        Quote Summary
                      </h4>
                      
                      <dl className="grid grid-cols-1 md:grid-cols-4 gap-x-4 gap-y-2 text-sm">
                        <div>
                          <dt className="text-gray-500">Subtotal</dt>
                          <dd className="font-medium text-gray-900">
                            {formatCurrency(quote.subtotal_amount || 0)}
                          </dd>
                        </div>
                        
                        <div>
                          <dt className="text-gray-500">Tax</dt>
                          <dd className="font-medium text-gray-900">
                            {formatCurrency(quote.tax_amount || 0)}
                          </dd>
                        </div>
                        
                        {quote.discount_amount > 0 && (
                          <div>
                            <dt className="text-gray-500">Discount</dt>
                            <dd className="font-medium text-gray-900">
                              {formatCurrency(quote.discount_amount)}
                            </dd>
                          </div>
                        )}
                        
                        <div>
                          <dt className="text-gray-500">Total</dt>
                          <dd className="font-medium text-gray-900">
                            {formatCurrency(quote.total_amount)}
                          </dd>
                        </div>
                      </dl>
                    </div>
                    
                    {/* Line items preview */}
                    {quote.items && quote.items.length > 0 && (
                      <div className="mb-4">
                        <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
                          Items ({quote.items.length})
                        </h4>
                        
                        <div className="overflow-x-auto">
                          <table className="min-w-full divide-y divide-gray-200 text-sm">
                            <thead className="bg-gray-100">
                              <tr>
                                <th scope="col" className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                  Item
                                </th>
                                <th scope="col" className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                  Quantity
                                </th>
                                <th scope="col" className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                  Unit Price
                                </th>
                                <th scope="col" className="px-3 py-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                                  Total
                                </th>
                              </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                              {quote.items.map((item, idx) => (
                                <tr key={idx} className="hover:bg-gray-50">
                                  <td className="px-3 py-2 whitespace-nowrap text-xs text-gray-900">
                                    <div className="font-medium">{item.description}</div>
                                    {item.details && (
                                      <div className="text-gray-500">{item.details}</div>
                                    )}
                                  </td>
                                  <td className="px-3 py-2 whitespace-nowrap text-xs text-right text-gray-900">
                                    {item.quantity}
                                  </td>
                                  <td className="px-3 py-2 whitespace-nowrap text-xs text-right text-gray-900">
                                    {formatCurrency(item.unit_price)}
                                  </td>
                                  <td className="px-3 py-2 whitespace-nowrap text-xs text-right text-gray-900 font-medium">
                                    {formatCurrency(item.total_price || (item.quantity * item.unit_price))}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    )}
                    
                    {/* Notes */}
                    {quote.notes && (
                      <div className="mb-4">
                        <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
                          Notes
                        </h4>
                        <p className="text-sm text-gray-700 whitespace-pre-wrap">{quote.notes}</p>
                      </div>
                    )}
                    
                    {/* Actions */}
                    <div className="mt-4 pt-4 border-t border-gray-200 flex justify-end space-x-3">
                      <Link
                        to={`${projectId ? `/projects/${projectId}` : ''}/quotes/${quote.id}`}
                        className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
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
                            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                          />
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth="2"
                            d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                          />
                        </svg>
                        View Quote
                      </Link>
                      
                      {quote.status === 'draft' && (
                        <Link
                          to={`${projectId ? `/projects/${projectId}` : ''}/quotes/${quote.id}/edit`}
                          className="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
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
                      )}
                      
                      {(quote.status === 'draft' || quote.status === 'sent') && (
                        <button
                          type="button"
                          className="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                          onClick={(e) => {
                            e.stopPropagation();
                            window.open(`${projectId ? `/projects/${projectId}` : ''}/quotes/${quote.id}/pdf`, '_blank');
                          }}
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
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="p-6 text-center">
          <p className="text-gray-500">No quotes found.</p>
          {projectId && (
            <Link
              to={`/projects/${projectId}/quotes/new`}
              className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
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
                  d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                />
              </svg>
              Create Quote
            </Link>
          )}
        </div>
      )}
    </div>
  );
};

export default QuotesList;