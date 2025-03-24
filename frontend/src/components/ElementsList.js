import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const ElementsList = ({ elements, projectId = null, onElementSelect = null }) => {
  const [filteredElements, setFilteredElements] = useState(elements || []);
  const [filters, setFilters] = useState({
    type: '',
    material: '',
    searchTerm: '',
  });
  
  // Get unique element types and materials for filter dropdowns
  const elementTypes = [...new Set(elements.map(el => el.type))].filter(Boolean).sort();
  const elementMaterials = [...new Set(elements.map(el => el.materials))].filter(Boolean).sort();
  
  // Apply filters when filters or elements change
  useEffect(() => {
    if (!elements) return;
    
    let results = [...elements];
    
    // Apply type filter
    if (filters.type) {
      results = results.filter(el => el.type === filters.type);
    }
    
    // Apply material filter
    if (filters.material) {
      results = results.filter(el => el.materials === filters.material);
    }
    
    // Apply search term
    if (filters.searchTerm) {
      const term = filters.searchTerm.toLowerCase();
      results = results.filter(el => 
        (el.type && el.type.toLowerCase().includes(term)) ||
        (el.materials && el.materials.toLowerCase().includes(term)) ||
        (el.dimensions && el.dimensions.toLowerCase().includes(term)) ||
        (el.notes && el.notes.toLowerCase().includes(term))
      );
    }
    
    setFilteredElements(results);
  }, [filters, elements]);
  
  // Reset all filters
  const handleResetFilters = () => {
    setFilters({
      type: '',
      material: '',
      searchTerm: '',
    });
  };
  
  // Handle filter changes
  const handleFilterChange = (name, value) => {
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  return (
    <div className="bg-white shadow-sm rounded-lg overflow-hidden">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-medium text-gray-800">Construction Elements</h2>
        <p className="mt-1 text-sm text-gray-600">
          {filteredElements.length} {filteredElements.length === 1 ? 'element' : 'elements'} found
        </p>
      </div>
      
      {/* Filters */}
      <div className="p-4 bg-gray-50 border-b border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div>
            <label htmlFor="search" className="block text-sm font-medium text-gray-700">
              Search
            </label>
            <input
              type="text"
              id="search"
              placeholder="Search elements..."
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              value={filters.searchTerm}
              onChange={(e) => handleFilterChange('searchTerm', e.target.value)}
            />
          </div>
          
          {/* Type Filter */}
          <div>
            <label htmlFor="type-filter" className="block text-sm font-medium text-gray-700">
              Element Type
            </label>
            <select
              id="type-filter"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              value={filters.type}
              onChange={(e) => handleFilterChange('type', e.target.value)}
            >
              <option value="">All Types</option>
              {elementTypes.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </div>
          
          {/* Material Filter */}
          <div>
            <label htmlFor="material-filter" className="block text-sm font-medium text-gray-700">
              Material
            </label>
            <select
              id="material-filter"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              value={filters.material}
              onChange={(e) => handleFilterChange('material', e.target.value)}
            >
              <option value="">All Materials</option>
              {elementMaterials.map((material) => (
                <option key={material} value={material}>
                  {material}
                </option>
              ))}
            </select>
          </div>
          
          {/* Reset Filters */}
          <div className="flex items-end">
            <button
              type="button"
              className="px-3 py-2 text-sm text-blue-600 hover:text-blue-800 focus:outline-none"
              onClick={handleResetFilters}
            >
              Reset Filters
            </button>
          </div>
        </div>
      </div>
      
      {/* Elements List */}
      {filteredElements.length > 0 ? (
        <div className="divide-y divide-gray-200">
          {filteredElements.map((element) => (
            <div 
              key={element.id} 
              className={`p-4 hover:bg-gray-50 ${onElementSelect ? 'cursor-pointer' : ''}`}
              onClick={onElementSelect ? () => onElementSelect(element) : undefined}
            >
              <div className="flex justify-between">
                <div>
                  <h3 className="text-sm font-medium text-gray-900">
                    {element.type}
                    {element.dimensions && (
                      <span className="ml-1 font-normal text-gray-500">
                        ({element.dimensions})
                      </span>
                    )}
                  </h3>
                  
                  <div className="mt-2 text-sm text-gray-500 space-y-1">
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
                  
                  {element.document_id && (
                    <div className="mt-2 text-xs text-gray-500">
                      From document: 
                      <Link 
                        to={`/documents/${element.document_id}`}
                        className="ml-1 text-blue-600 hover:text-blue-800"
                        onClick={(e) => e.stopPropagation()}
                      >
                        {element.document_name || `Document #${element.document_id}`}
                      </Link>
                    </div>
                  )}
                </div>
                
                <div className="flex space-x-2">
                  {!onElementSelect && (
                    <Link
                      to={`${projectId ? `/projects/${projectId}` : ''}/elements/${element.id}`}
                      className="text-blue-600 hover:text-blue-800"
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
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-4 text-center">
          <p className="text-gray-500">No elements found matching your filters.</p>
          {(filters.type || filters.material || filters.searchTerm) && (
            <button
              type="button"
              className="mt-2 text-sm text-blue-600 hover:text-blue-800 focus:outline-none"
              onClick={handleResetFilters}
            >
              Reset Filters
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default ElementsList;