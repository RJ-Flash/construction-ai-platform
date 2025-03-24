import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { ENDPOINTS } from '../config/api';
import { useToast } from '../hooks/useToast';

// Components
import LoadingSpinner from '../components/LoadingSpinner';

const ElementDetailsPage = () => {
  const { projectId, elementId } = useParams();
  const navigate = useNavigate();
  const { showToast } = useToast();
  
  const [element, setElement] = useState(null);
  const [document, setDocument] = useState(null);
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    type: '',
    materials: '',
    dimensions: '',
    quantity: '',
    notes: ''
  });
  
  // Fetch element data on component mount
  useEffect(() => {
    const fetchElementData = async () => {
      try {
        setLoading(true);
        
        // Fetch element details
        const elementResponse = await axios.get(ENDPOINTS.ELEMENTS.DETAILS(elementId));
        setElement(elementResponse.data);
        setFormData({
          type: elementResponse.data.type || '',
          materials: elementResponse.data.materials || '',
          dimensions: elementResponse.data.dimensions || '',
          quantity: elementResponse.data.quantity || '',
          notes: elementResponse.data.notes || ''
        });
        
        // If element has a document_id, fetch document details
        if (elementResponse.data.document_id) {
          const documentResponse = await axios.get(
            ENDPOINTS.DOCUMENTS.DETAILS(elementResponse.data.document_id)
          );
          setDocument(documentResponse.data);
          
          // If document has project_id and no projectId in URL, fetch project details
          if (documentResponse.data.project_id && !projectId) {
            const projectResponse = await axios.get(
              ENDPOINTS.PROJECTS.DETAILS(documentResponse.data.project_id)
            );
            setProject(projectResponse.data);
          }
        }
        
        // If projectId is provided in URL, fetch project details
        if (projectId) {
          const projectResponse = await axios.get(ENDPOINTS.PROJECTS.DETAILS(projectId));
          setProject(projectResponse.data);
        }
      } catch (error) {
        console.error('Error fetching element data:', error);
        
        let errorMessage = 'Failed to load element data';
        if (error.response && error.response.data && error.response.data.detail) {
          errorMessage = error.response.data.detail;
        }
        
        showToast(errorMessage, 'error');
        
        if (error.response && error.response.status === 404) {
          navigate(projectId ? `/projects/${projectId}/elements` : '/elements');
        }
      } finally {
        setLoading(false);
      }
    };
    
    fetchElementData();
  }, [elementId, projectId, navigate, showToast]);
  
  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const response = await axios.put(
        ENDPOINTS.ELEMENTS.UPDATE(elementId),
        formData
      );
      
      setElement(response.data);
      setIsEditing(false);
      showToast('Element updated successfully', 'success');
    } catch (error) {
      console.error('Error updating element:', error);
      
      let errorMessage = 'Failed to update element';
      if (error.response && error.response.data && error.response.data.detail) {
        errorMessage = error.response.data.detail;
      }
      
      showToast(errorMessage, 'error');
    }
  };
  
  // Handle element deletion
  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this element? This action cannot be undone.')) {
      return;
    }
    
    try {
      await axios.delete(ENDPOINTS.ELEMENTS.DELETE(elementId));
      
      showToast('Element deleted successfully', 'success');
      navigate(projectId ? `/projects/${projectId}/elements` : '/elements');
    } catch (error) {
      console.error('Error deleting element:', error);
      
      let errorMessage = 'Failed to delete element';
      if (error.response && error.response.data && error.response.data.detail) {
        errorMessage = error.response.data.detail;
      }
      
      showToast(errorMessage, 'error');
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
          to={projectId ? `/projects/${projectId}/elements` : '/elements'}
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
          Back to Elements
        </Link>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main content */}
        <div className="lg:col-span-2">
          <div className="bg-white shadow-sm rounded-lg overflow-hidden">
            <div className="p-6">
              <div className="flex justify-between items-start mb-6">
                <h1 className="text-2xl font-bold text-gray-800">
                  {element.type}
                  {element.dimensions && (
                    <span className="ml-2 text-lg font-normal text-gray-500">
                      ({element.dimensions})
                    </span>
                  )}
                </h1>
                
                <div className="flex space-x-2">
                  {!isEditing && (
                    <>
                      <button
                        type="button"
                        onClick={() => setIsEditing(true)}
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
                            d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"
                          />
                        </svg>
                        Edit
                      </button>
                      
                      <button
                        type="button"
                        onClick={handleDelete}
                        className="inline-flex items-center px-3 py-1.5 border border-red-300 shadow-sm text-sm font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
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
                        Delete
                      </button>
                    </>
                  )}
                </div>
              </div>
              
              {isEditing ? (
                <form onSubmit={handleSubmit}>
                  <div className="space-y-4">
                    <div>
                      <label htmlFor="type" className="block text-sm font-medium text-gray-700">
                        Element Type
                      </label>
                      <input
                        type="text"
                        id="type"
                        name="type"
                        value={formData.type}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                        required
                      />
                    </div>
                    
                    <div>
                      <label htmlFor="materials" className="block text-sm font-medium text-gray-700">
                        Materials
                      </label>
                      <input
                        type="text"
                        id="materials"
                        name="materials"
                        value={formData.materials}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                      />
                    </div>
                    
                    <div>
                      <label htmlFor="dimensions" className="block text-sm font-medium text-gray-700">
                        Dimensions
                      </label>
                      <input
                        type="text"
                        id="dimensions"
                        name="dimensions"
                        value={formData.dimensions}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                      />
                    </div>
                    
                    <div>
                      <label htmlFor="quantity" className="block text-sm font-medium text-gray-700">
                        Quantity
                      </label>
                      <input
                        type="text"
                        id="quantity"
                        name="quantity"
                        value={formData.quantity}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                      />
                    </div>
                    
                    <div>
                      <label htmlFor="notes" className="block text-sm font-medium text-gray-700">
                        Notes
                      </label>
                      <textarea
                        id="notes"
                        name="notes"
                        rows="3"
                        value={formData.notes}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                      ></textarea>
                    </div>
                    
                    <div className="flex justify-end space-x-3 pt-4">
                      <button
                        type="button"
                        onClick={() => setIsEditing(false)}
                        className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                      >
                        Cancel
                      </button>
                      
                      <button
                        type="submit"
                        className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                      >
                        Save Changes
                      </button>
                    </div>
                  </div>
                </form>
              ) : (
                <div className="space-y-6">
                  {element.materials && (
                    <div>
                      <h3 className="text-sm font-medium text-gray-500">Materials</h3>
                      <p className="mt-1 text-sm text-gray-900">{element.materials}</p>
                    </div>
                  )}
                  
                  {element.dimensions && (
                    <div>
                      <h3 className="text-sm font-medium text-gray-500">Dimensions</h3>
                      <p className="mt-1 text-sm text-gray-900">{element.dimensions}</p>
                    </div>
                  )}
                  
                  {element.quantity && (
                    <div>
                      <h3 className="text-sm font-medium text-gray-500">Quantity</h3>
                      <p className="mt-1 text-sm text-gray-900">{element.quantity}</p>
                    </div>
                  )}
                  
                  {element.notes && (
                    <div>
                      <h3 className="text-sm font-medium text-gray-500">Notes</h3>
                      <p className="mt-1 text-sm text-gray-900">{element.notes}</p>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
          
          {/* Related Elements Section */}
          {element.related_elements && element.related_elements.length > 0 && (
            <div className="bg-white shadow-sm rounded-lg overflow-hidden mt-6">
              <div className="p-4 border-b border-gray-200">
                <h2 className="text-lg font-medium text-gray-800">Related Elements</h2>
              </div>
              
              <div className="divide-y divide-gray-200">
                {element.related_elements.map((relatedElement) => (
                  <div key={relatedElement.id} className="p-4 hover:bg-gray-50">
                    <Link
                      to={`${projectId ? `/projects/${projectId}` : ''}/elements/${relatedElement.id}`}
                      className="block"
                    >
                      <h3 className="text-sm font-medium text-gray-900">
                        {relatedElement.type}
                        {relatedElement.dimensions && (
                          <span className="ml-1 font-normal text-gray-500">
                            ({relatedElement.dimensions})
                          </span>
                        )}
                      </h3>
                      
                      {relatedElement.materials && (
                        <p className="mt-1 text-xs text-gray-500">
                          Material: {relatedElement.materials}
                        </p>
                      )}
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
        
        {/* Sidebar */}
        <div className="lg:col-span-1">
          {/* Element Info */}
          <div className="bg-white shadow-sm rounded-lg overflow-hidden mb-6">
            <div className="p-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-800">Element Information</h2>
            </div>
            
            <div className="p-4">
              <dl className="space-y-4">
                <div>
                  <dt className="text-sm font-medium text-gray-500">Element ID</dt>
                  <dd className="mt-1 text-sm text-gray-900">{element.id}</dd>
                </div>
                
                {document && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Source Document</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      <Link
                        to={`/documents/${document.id}`}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        {document.filename}
                      </Link>
                    </dd>
                  </div>
                )}
                
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
                
                {element.created_at && (
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Added On</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {new Date(element.created_at).toLocaleDateString(undefined, {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric'
                      })}
                    </dd>
                  </div>
                )}
              </dl>
            </div>
          </div>
          
          {/* Actions */}
          <div className="bg-white shadow-sm rounded-lg overflow-hidden">
            <div className="p-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-800">Actions</h2>
            </div>
            
            <div className="p-4">
              <div className="space-y-3">
                {project && (
                  <Link
                    to={`/projects/${project.id}/quotes/new?elementId=${element.id}`}
                    className="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
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
                        d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    Include in Quote
                  </Link>
                )}
                
                {document && (
                  <Link
                    to={`/documents/${document.id}`}
                    className="w-full inline-flex justify-center items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
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
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                      />
                    </svg>
                    View Source Document
                  </Link>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ElementDetailsPage;