import React, { useState } from 'react';
import { ENDPOINTS } from '../config/api';

const ElementsList = ({ elements, projectId, onGenerateQuote }) => {
  const [groupBy, setGroupBy] = useState('type');
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedElement, setExpandedElement] = useState(null);

  // Group and filter elements
  const filteredElements = elements.filter(element => {
    const searchString = `${element.type} ${element.dimensions || ''} ${
      element.materials || ''
    } ${element.notes || ''}`.toLowerCase();

    return searchTerm === '' || searchString.includes(searchTerm.toLowerCase());
  });

  // Group elements by the selected grouping
  const groupedElements = filteredElements.reduce((groups, element) => {
    const groupKey = element[groupBy] || 'Unknown';
    if (!groups[groupKey]) {
      groups[groupKey] = [];
    }
    groups[groupKey].push(element);
    return groups;
  }, {});

  // Sort group keys
  const sortedGroupKeys = Object.keys(groupedElements).sort();

  // Toggle element details
  const toggleElementDetails = (elementId) => {
    setExpandedElement(expandedElement === elementId ? null : elementId);
  };

  return (
    <div className="bg-white shadow-sm rounded-lg overflow-hidden">
      <div className="p-4 flex justify-between items-center border-b border-gray-200">
        <h2 className="text-lg font-medium text-gray-800">
          Construction Elements
        </h2>
        <button
          onClick={onGenerateQuote}
          className="inline-flex items-center px-3 py-1.5 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
        >
          <svg className="mr-1 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          Generate Quote
        </button>
      </div>
      
      {/* Filters and search */}
      <div className="p-4 bg-gray-50 border-b border-gray-200">
        <div className="flex flex-col md:flex-row md:items-center space-y-3 md:space-y-0 md:space-x-4">
          <div className="w-full md:w-1/3">
            <label htmlFor="search" className="sr-only">
              Search elements
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg 
                  className="h-5 w-5 text-gray-400" 
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
              </div>
              <input
                type="search"
                id="search"
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="Search elements"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
          
          <div className="w-full md:w-1/3">
            <label htmlFor="group-by" className="sr-only">
              Group by
            </label>
            <select
              id="group-by"
              className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              value={groupBy}
              onChange={(e) => setGroupBy(e.target.value)}
            >
              <option value="type">Group by Type</option>
              <option value="materials">Group by Material</option>
              <option value="source_document_id">Group by Document</option>
            </select>
          </div>
          
          <div className="w-full md:w-1/3 text-right">
            <span className="text-sm text-gray-500">
              {filteredElements.length} elements
            </span>
          </div>
        </div>
      </div>
      
      {filteredElements.length === 0 ? (
        <div className="p-6 text-center">
          <p className="text-gray-500">No elements found for this project.</p>
          <p className="mt-2 text-sm text-gray-500">
            Upload and analyze construction documents to extract elements.
          </p>
        </div>
      ) : (
        <div className="overflow-hidden">
          {sortedGroupKeys.map((groupKey) => (
            <div key={groupKey} className="border-b border-gray-200 last:border-b-0">
              <div className="px-4 py-3 bg-gray-50">
                <h3 className="text-sm font-medium text-gray-800">
                  {groupBy === 'type' && 'Type: '}
                  {groupBy === 'materials' && 'Material: '}
                  {groupBy === 'source_document_id' && 'Document: '}
                  {groupKey}
                  <span className="ml-2 text-xs text-gray-500">
                    ({groupedElements[groupKey].length} elements)
                  </span>
                </h3>
              </div>
              
              <ul>
                {groupedElements[groupKey].map((element) => (
                  <li
                    key={element.id}
                    className="border-t border-gray-100 first:border-t-0"
                  >
                    <div
                      className="px-4 py-3 flex justify-between items-start cursor-pointer hover:bg-gray-50"
                      onClick={() => toggleElementDetails(element.id)}
                    >
                      <div>
                        <h4 className="text-sm font-medium text-gray-900">
                          {element.type}
                          {element.dimensions && (
                            <span className="ml-2 text-sm font-normal text-gray-500">
                              ({element.dimensions})
                            </span>
                          )}
                        </h4>
                        {element.materials && (
                          <p className="mt-1 text-xs text-gray-500">
                            Material: {element.materials}
                          </p>
                        )}
                        {element.quantity && (
                          <p className="text-xs text-gray-500">
                            Quantity: {element.quantity}
                          </p>
                        )}
                      </div>
                      
                      <svg
                        className={`h-5 w-5 text-gray-400 transform transition-transform ${
                          expandedElement === element.id ? 'rotate-180' : ''
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
                    
                    {expandedElement === element.id && (
                      <div className="px-4 py-3 bg-gray-50 border-t border-gray-100">
                        <dl className="grid grid-cols-1 gap-x-4 gap-y-3 sm:grid-cols-2">
                          <div className="sm:col-span-1">
                            <dt className="text-xs font-medium text-gray-500">Type</dt>
                            <dd className="mt-1 text-sm text-gray-900">{element.type || 'N/A'}</dd>
                          </div>
                          
                          <div className="sm:col-span-1">
                            <dt className="text-xs font-medium text-gray-500">Dimensions</dt>
                            <dd className="mt-1 text-sm text-gray-900">{element.dimensions || 'N/A'}</dd>
                          </div>
                          
                          <div className="sm:col-span-1">
                            <dt className="text-xs font-medium text-gray-500">Materials</dt>
                            <dd className="mt-1 text-sm text-gray-900">{element.materials || 'N/A'}</dd>
                          </div>
                          
                          <div className="sm:col-span-1">
                            <dt className="text-xs font-medium text-gray-500">Quantity</dt>
                            <dd className="mt-1 text-sm text-gray-900">{element.quantity || 'N/A'}</dd>
                          </div>
                          
                          {element.notes && (
                            <div className="sm:col-span-2">
                              <dt className="text-xs font-medium text-gray-500">Notes</dt>
                              <dd className="mt-1 text-sm text-gray-900">{element.notes}</dd>
                            </div>
                          )}
                          
                          {element.specifications && Object.keys(element.specifications).length > 0 && (
                            <div className="sm:col-span-2">
                              <dt className="text-xs font-medium text-gray-500">Specifications</dt>
                              <dd className="mt-1 space-y-1">
                                {Object.entries(element.specifications).map(([key, value]) => (
                                  <div key={key} className="text-sm text-gray-900">
                                    <span className="font-medium">{key}:</span> {value}
                                  </div>
                                ))}
                              </dd>
                            </div>
                          )}
                        </dl>
                      </div>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ElementsList;
