import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { ENDPOINTS } from '../config/api';
import { useToast } from '../hooks/useToast';

// Components
import ElementsList from '../components/ElementsList';
import LoadingSpinner from '../components/LoadingSpinner';

const ElementsPage = () => {
  const { projectId } = useParams();
  const { showToast } = useToast();
  
  const [elements, setElements] = useState([]);
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalElements: 0,
    elementsByType: {},
    elementsByMaterial: {}
  });
  
  // Fetch data on component mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        let elementsResponse;
        
        // If projectId is provided, fetch project-specific elements
        if (projectId) {
          // Fetch project details
          const projectResponse = await axios.get(ENDPOINTS.PROJECTS.DETAILS(projectId));
          setProject(projectResponse.data);
          
          // Fetch project elements
          elementsResponse = await axios.get(ENDPOINTS.PROJECTS.ELEMENTS(projectId));
        } else {
          // Fetch all elements
          elementsResponse = await axios.get(ENDPOINTS.ELEMENTS.LIST);
        }
        
        setElements(elementsResponse.data);
        calculateStats(elementsResponse.data);
      } catch (error) {
        console.error('Error fetching elements data:', error);
        
        let errorMessage = 'Failed to load elements';
        if (error.response && error.response.data && error.response.data.detail) {
          errorMessage = error.response.data.detail;
        }
        
        showToast(errorMessage, 'error');
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [projectId, showToast]);
  
  // Calculate statistics from elements data
  const calculateStats = (elementsData) => {
    if (!elementsData || elementsData.length === 0) {
      return;
    }
    
    const elementsByType = {};
    const elementsByMaterial = {};
    
    // Count elements by type and material
    elementsData.forEach(element => {
      // Count by type
      if (element.type) {
        elementsByType[element.type] = (elementsByType[element.type] || 0) + 1;
      }
      
      // Count by material
      if (element.materials) {
        elementsByMaterial[element.materials] = (elementsByMaterial[element.materials] || 0) + 1;
      }
    });
    
    setStats({
      totalElements: elementsData.length,
      elementsByType,
      elementsByMaterial
    });
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
        <div>
          {project ? (
            <>
              <Link
                to={`/projects/${projectId}`}
                className="text-blue-600 hover:text-blue-800 mb-2 inline-flex items-center"
              >
                <svg className="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M15 19l-7-7 7-7"
                  />
                </svg>
                Back to Project
              </Link>
              <h1 className="text-2xl font-bold text-gray-800">Elements for {project.name}</h1>
            </>
          ) : (
            <h1 className="text-2xl font-bold text-gray-800">All Construction Elements</h1>
          )}
          <p className="text-gray-600 mt-1">
            {stats.totalElements} {stats.totalElements === 1 ? 'element' : 'elements'} found
          </p>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar with stats */}
        <div className="lg:col-span-1">
          <div className="bg-white shadow-sm rounded-lg overflow-hidden mb-6">
            <div className="p-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-800">Statistics</h2>
            </div>
            
            <div className="p-4">
              <div className="mb-6">
                <h3 className="text-sm font-medium text-gray-800 mb-2">Elements by Type</h3>
                <div className="space-y-2">
                  {Object.entries(stats.elementsByType)
                    .sort(([, countA], [, countB]) => countB - countA)
                    .map(([type, count]) => (
                      <div key={type} className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">{type}</span>
                        <span className="text-sm font-medium text-gray-900">{count}</span>
                      </div>
                    ))}
                </div>
              </div>
              
              <div>
                <h3 className="text-sm font-medium text-gray-800 mb-2">Elements by Material</h3>
                <div className="space-y-2">
                  {Object.entries(stats.elementsByMaterial)
                    .sort(([, countA], [, countB]) => countB - countA)
                    .map(([material, count]) => (
                      <div key={material} className="flex justify-between items-center">
                        <span className="text-sm text-gray-600">{material}</span>
                        <span className="text-sm font-medium text-gray-900">{count}</span>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          </div>
          
          {/* Actions */}
          {project && (
            <div className="bg-white shadow-sm rounded-lg overflow-hidden">
              <div className="p-4 border-b border-gray-200">
                <h2 className="text-lg font-medium text-gray-800">Actions</h2>
              </div>
              
              <div className="p-4">
                <Link
                  to={`/projects/${projectId}/quotes/new`}
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
                      d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                    />
                  </svg>
                  Generate Quote
                </Link>
                
                <div className="mt-3">
                  <Link
                    to={`/projects/${projectId}/documents`}
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
                    View Documents
                  </Link>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Main content - Elements list */}
        <div className="lg:col-span-3">
          <ElementsList elements={elements} projectId={projectId} />
        </div>
      </div>
    </div>
  );
};

export default ElementsPage;