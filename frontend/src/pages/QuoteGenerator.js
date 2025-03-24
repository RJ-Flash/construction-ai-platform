import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import { ENDPOINTS } from '../config/api';
import { useToast } from '../hooks/useToast';

// Components
import LoadingSpinner from '../components/LoadingSpinner';
import ElementsList from '../components/ElementsList';

const QuoteGenerator = () => {
  const { id: projectId } = useParams();
  const navigate = useNavigate();
  const { showToast } = useToast();
  
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [project, setProject] = useState(null);
  const [elements, setElements] = useState([]);
  const [selectedElements, setSelectedElements] = useState([]);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    region: 'United States',
    preferences: {}
  });
  
  // Fetch project data on component mount
  useEffect(() => {
    const fetchProjectData = async () => {
      try {
        setLoading(true);
        
        // Fetch project details
        const projectResponse = await axios.get(ENDPOINTS.PROJECTS.DETAILS(projectId));
        setProject(projectResponse.data);
        
        // Update quote name with project name
        setFormData(prev => ({
          ...prev,
          name: `Quote for ${projectResponse.data.name}`
        }));
        
        // Fetch project elements
        const elementsResponse = await axios.get(ENDPOINTS.PROJECTS.ELEMENTS(projectId));
        setElements(elementsResponse.data);
        
        // By default, select all elements
        setSelectedElements(elementsResponse.data.map(element => element.id));
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
  }, [projectId, navigate, showToast]);
  
  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };
  
  // Handle checkbox changes for selecting elements
  const handleElementSelection = (elementId) => {
    setSelectedElements(prev => {
      if (prev.includes(elementId)) {
        return prev.filter(id => id !== elementId);
      } else {
        return [...prev, elementId];
      }
    });
  };
  
  // Handle toggle all elements
  const handleToggleAll = (selectAll) => {
    if (selectAll) {
      setSelectedElements(elements.map(element => element.id));
    } else {
      setSelectedElements([]);
    }
  };
  
  // Handle preference changes
  const handlePreferenceChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    setFormData(prev => ({
      ...prev,
      preferences: {
        ...prev.preferences,
        [name]: type === 'checkbox' ? checked : value
      }
    }));
  };
  
  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.name) {
      showToast('Quote name is required', 'error');
      return;
    }
    
    if (selectedElements.length === 0) {
      showToast('Please select at least one element', 'error');
      return;
    }
    
    try {
      setGenerating(true);
      
      // Create quote first
      const quoteResponse = await axios.post(ENDPOINTS.QUOTES.CREATE, {
        name: formData.name,
        description: formData.description,
        region: formData.region,
        project_id: projectId,
        preferences: formData.preferences,
        status: 'draft'
      });
      
      const quoteId = quoteResponse.data.id;
      
      // Get the selected element objects
      const elementsToUse = elements.filter(element => 
        selectedElements.includes(element.id)
      );
      
      // Generate quote items from elements
      await axios.post(ENDPOINTS.QUOTES.GENERATE(quoteId), {
        elements: elementsToUse,
        region: formData.region,
        project_id: projectId
      });
      
      showToast('Quote generated successfully', 'success');
      
      // Navigate to the quote details page
      navigate(`/quotes/${quoteId}`);
    } catch (error) {
      console.error('Error generating quote:', error);
      
      let errorMessage = 'Failed to generate quote';
      if (error.response && error.response.data && error.response.data.detail) {
        errorMessage = error.response.data.detail;
      }
      
      showToast(errorMessage, 'error');
    } finally {
      setGenerating(false);
    }
  };
  
  // Handle cancel button
  const handleCancel = () => {
    navigate(`/projects/${projectId}`);
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
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-8">
        <div className="flex items-center">
          <Link
            to={`/projects/${projectId}`}
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
            <h1 className="text-2xl font-bold text-gray-800">Generate Quote</h1>
            <p className="text-gray-600">Project: {project?.name}</p>
          </div>
        </div>
      </div>
      
      <div className="bg-white shadow-sm rounded-lg mb-8">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-800">Quote Information</h2>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Quote Name */}
            <div className="col-span-1 md:col-span-2">
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                Quote Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                name="name"
                id="name"
                required
                className="mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                value={formData.name}
                onChange={handleChange}
              />
            </div>
            
            {/* Description */}
            <div className="col-span-1 md:col-span-2">
              <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                Description
              </label>
              <textarea
                id="description"
                name="description"
                rows={3}
                className="mt-1 focus:ring-blue-500 focus:border-blue-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md"
                placeholder="Enter quote description"
                value={formData.description}
                onChange={handleChange}
              />
            </div>
            
            {/* Region */}
            <div>
              <label htmlFor="region" className="block text-sm font-medium text-gray-700">
                Region <span className="text-red-500">*</span>
              </label>
              <select
                id="region"
                name="region"
                className="mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                value={formData.region}
                onChange={handleChange}
              >
                <option value="United States">United States</option>
                <option value="Canada">Canada</option>
                <option value="United Kingdom">United Kingdom</option>
                <option value="Europe">Europe</option>
                <option value="Australia">Australia</option>
                <option value="Asia">Asia</option>
                <option value="Other">Other</option>
              </select>
            </div>
            
            {/* Client Preferences */}
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Client Preferences
              </label>
              <div className="mt-2 space-y-2">
                <div className="flex items-start">
                  <div className="flex items-center h-5">
                    <input
                      id="premium_materials"
                      name="premium_materials"
                      type="checkbox"
                      className="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded"
                      checked={formData.preferences.premium_materials || false}
                      onChange={handlePreferenceChange}
                    />
                  </div>
                  <div className="ml-3 text-sm">
                    <label htmlFor="premium_materials" className="font-medium text-gray-700">
                      Premium Materials
                    </label>
                    <p className="text-gray-500">
                      Include premium quality materials in the quote
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start">
                  <div className="flex items-center h-5">
                    <input
                      id="sustainable_materials"
                      name="sustainable_materials"
                      type="checkbox"
                      className="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded"
                      checked={formData.preferences.sustainable_materials || false}
                      onChange={handlePreferenceChange}
                    />
                  </div>
                  <div className="ml-3 text-sm">
                    <label htmlFor="sustainable_materials" className="font-medium text-gray-700">
                      Eco-Friendly Materials
                    </label>
                    <p className="text-gray-500">
                      Prioritize sustainable and eco-friendly materials
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="mt-8">
            <h3 className="text-md font-medium text-gray-700 mb-4">
              Select Elements to Include
            </h3>
            
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-500">
                {selectedElements.length} of {elements.length} elements selected
              </span>
              <div className="space-x-2">
                <button
                  type="button"
                  onClick={() => handleToggleAll(true)}
                  className="inline-flex items-center px-2.5 py-1.5 border border-gray-300 text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Select All
                </button>
                <button
                  type="button"
                  onClick={() => handleToggleAll(false)}
                  className="inline-flex items-center px-2.5 py-1.5 border border-gray-300 text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Deselect All
                </button>
              </div>
            </div>
            
            <div className="bg-gray-50 p-4 rounded-lg max-h-96 overflow-y-auto">
              {elements.length === 0 ? (
                <p className="text-gray-500 text-center py-4">
                  No elements found for this project.
                </p>
              ) : (
                <ul className="divide-y divide-gray-200">
                  {elements.map((element) => (
                    <li key={element.id} className="py-3">
                      <div className="flex items-start">
                        <div className="flex items-center h-5">
                          <input
                            id={`element-${element.id}`}
                            type="checkbox"
                            className="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded"
                            checked={selectedElements.includes(element.id)}
                            onChange={() => handleElementSelection(element.id)}
                          />
                        </div>
                        <div className="ml-3">
                          <label 
                            htmlFor={`element-${element.id}`} 
                            className="font-medium text-gray-700 cursor-pointer"
                          >
                            {element.type}
                            {element.dimensions && (
                              <span className="ml-1 font-normal text-gray-500">
                                ({element.dimensions})
                              </span>
                            )}
                          </label>
                          <p className="text-xs text-gray-500">
                            {element.materials && `Material: ${element.materials}`}
                            {element.quantity && ` • Quantity: ${element.quantity}`}
                          </p>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
          
          <div className="mt-8 flex justify-end space-x-3">
            <button
              type="button"
              onClick={handleCancel}
              className="inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={generating || selectedElements.length === 0}
              className={`inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white ${
                generating || selectedElements.length === 0
                  ? 'bg-green-400 cursor-not-allowed'
                  : 'bg-green-600 hover:bg-green-700'
              } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500`}
            >
              {generating ? (
                <>
                  <LoadingSpinner size="small" color="white" className="mr-2" />
                  Generating Quote...
                </>
              ) : (
                'Generate Quote'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default QuoteGenerator;
