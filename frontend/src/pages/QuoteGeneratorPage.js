import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link, useLocation } from 'react-router-dom';
import axios from 'axios';
import { ENDPOINTS } from '../config/api';
import { useToast } from '../hooks/useToast';

// Components
import LoadingSpinner from '../components/LoadingSpinner';

const QuoteGeneratorPage = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { showToast } = useToast();
  
  // Get elementId from query params if available
  const queryParams = new URLSearchParams(location.search);
  const preselectedElementId = queryParams.get('elementId');
  
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [project, setProject] = useState(null);
  const [elements, setElements] = useState([]);
  const [selectedElements, setSelectedElements] = useState([]);
  
  const [formData, setFormData] = useState({
    title: '',
    client_name: '',
    client_email: '',
    client_phone: '',
    notes: '',
    tax_rate: 0,
    discount_percentage: 0,
    expiry_days: 30
  });
  
  // Fetch project data and elements on component mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch project details
        const projectResponse = await axios.get(
          ENDPOINTS.PROJECTS.DETAILS(projectId)
        );
        setProject(projectResponse.data);
        
        // Pre-fill client details if available
        if (projectResponse.data.client) {
          setFormData(prev => ({
            ...prev,
            client_name: projectResponse.data.client.name || '',
            client_email: projectResponse.data.client.email || '',
            client_phone: projectResponse.data.client.phone || ''
          }));
        }
        
        // Fetch project elements
        const elementsResponse = await axios.get(
          ENDPOINTS.PROJECTS.ELEMENTS(projectId)
        );
        setElements(elementsResponse.data);
        
        // If an element ID was passed in URL, pre-select it
        if (preselectedElementId) {
          const element = elementsResponse.data.find(el => el.id === parseInt(preselectedElementId));
          if (element) {
            setSelectedElements([{
              ...element,
              quantity: element.quantity || 1,
              unit_price: element.estimated_price || 0,
              notes: ''
            }]);
          }
        }
      } catch (error) {
        console.error('Error fetching project data:', error);
        
        let errorMessage = 'Failed to load project data';
        if (error.response && error.response.data && error.response.data.detail) {
          errorMessage = error.response.data.detail;
        }
        
        showToast(errorMessage, 'error');
        
        if (error.response && error.response.status === 404) {
          navigate('/projects');
        }
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [projectId, preselectedElementId, navigate, showToast]);
  
  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  // Handle selecting an element
  const handleElementSelect = (element) => {
    // Check if element is already selected
    if (selectedElements.some(el => el.id === element.id)) {
      return;
    }
    
    // Add element to selected list with quantity and price
    setSelectedElements(prev => [
      ...prev,
      {
        ...element,
        quantity: element.quantity || 1,
        unit_price: element.estimated_price || 0,
        notes: ''
      }
    ]);
  };
  
  // Handle removing a selected element
  const handleRemoveElement = (elementId) => {
    setSelectedElements(prev => prev.filter(el => el.id !== elementId));
  };
  
  // Handle changing quantity or price for a selected element
  const handleElementUpdate = (elementId, field, value) => {
    setSelectedElements(prev =>
      prev.map(el =>
        el.id === elementId
          ? { ...el, [field]: field === 'quantity' || field === 'unit_price' 
              ? (isNaN(parseFloat(value)) ? 0 : parseFloat(value))
              : value }
          : el
      )
    );
  };
  
  // Calculate totals
  const calculateTotals = () => {
    const subtotal = selectedElements.reduce(
      (sum, el) => sum + (el.quantity * el.unit_price),
      0
    );
    
    const taxRate = parseFloat(formData.tax_rate) || 0;
    const taxAmount = subtotal * (taxRate / 100);
    
    const discountPercentage = parseFloat(formData.discount_percentage) || 0;
    const discountAmount = subtotal * (discountPercentage / 100);
    
    const total = subtotal + taxAmount - discountAmount;
    
    return {
      subtotal: subtotal.toFixed(2),
      tax_amount: taxAmount.toFixed(2),
      discount_amount: discountAmount.toFixed(2),
      total: total.toFixed(2)
    };
  };
  
  // Format currency helper
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2
    }).format(amount);
  };
  
  // Generate and save quote
  const handleQuoteGenerate = async (e) => {
    e.preventDefault();
    
    if (selectedElements.length === 0) {
      showToast('Please select at least one element to include in the quote', 'error');
      return;
    }
    
    try {
      setGenerating(true);
      
      const totals = calculateTotals();
      
      // Prepare quote data
      const quoteData = {
        project_id: projectId,
        title: formData.title || `Quote for ${project.name}`,
        client_name: formData.client_name,
        client_email: formData.client_email,
        client_phone: formData.client_phone,
        notes: formData.notes,
        tax_rate: parseFloat(formData.tax_rate) || 0,
        discount_percentage: parseFloat(formData.discount_percentage) || 0,
        subtotal_amount: parseFloat(totals.subtotal),
        tax_amount: parseFloat(totals.tax_amount),
        discount_amount: parseFloat(totals.discount_amount),
        total_amount: parseFloat(totals.total),
        status: 'draft',
        items: selectedElements.map(el => ({
          element_id: el.id,
          description: `${el.type}${el.dimensions ? ` (${el.dimensions})` : ''}${el.materials ? ` - ${el.materials}` : ''}`,
          details: el.notes || '',
          quantity: el.quantity,
          unit_price: el.unit_price,
          total_price: el.quantity * el.unit_price
        })),
        expiry_date: new Date(Date.now() + parseInt(formData.expiry_days) * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
      };
      
      // Send quote data to API
      const response = await axios.post(
        ENDPOINTS.QUOTES.CREATE,
        quoteData
      );
      
      showToast('Quote generated successfully', 'success');
      
      // Navigate to the new quote
      navigate(`/projects/${projectId}/quotes/${response.data.id}`);
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
  
  // If loading, show spinner
  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }
  
  // Calculate totals for display
  const totals = calculateTotals();
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <Link
          to={`/projects/${projectId}`}
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
          Back to Project
        </Link>
        <h1 className="text-2xl font-bold text-gray-800 mt-2">Generate Quote</h1>
        <p className="text-gray-600 mt-1">Create a new quote for {project.name}</p>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Form */}
        <div className="lg:col-span-2">
          <form onSubmit={handleQuoteGenerate}>
            <div className="bg-white shadow-sm rounded-lg overflow-hidden mb-6">
              <div className="p-4 border-b border-gray-200">
                <h2 className="text-lg font-medium text-gray-800">Quote Details</h2>
              </div>
              
              <div className="p-6 space-y-4">
                <div>
                  <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                    Quote Title
                  </label>
                  <input
                    type="text"
                    id="title"
                    name="title"
                    placeholder={`Quote for ${project.name}`}
                    value={formData.title}
                    onChange={handleInputChange}
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  />
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="client_name" className="block text-sm font-medium text-gray-700">
                      Client Name
                    </label>
                    <input
                      type="text"
                      id="client_name"
                      name="client_name"
                      value={formData.client_name}
                      onChange={handleInputChange}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    />
                  </div>
                  
                  <div>
                    <label htmlFor="client_email" className="block text-sm font-medium text-gray-700">
                      Client Email
                    </label>
                    <input
                      type="email"
                      id="client_email"
                      name="client_email"
                      value={formData.client_email}
                      onChange={handleInputChange}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    />
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="client_phone" className="block text-sm font-medium text-gray-700">
                      Client Phone
                    </label>
                    <input
                      type="text"
                      id="client_phone"
                      name="client_phone"
                      value={formData.client_phone}
                      onChange={handleInputChange}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    />
                  </div>
                  
                  <div>
                    <label htmlFor="expiry_days" className="block text-sm font-medium text-gray-700">
                      Quote Valid For (days)
                    </label>
                    <input
                      type="number"
                      id="expiry_days"
                      name="expiry_days"
                      min="1"
                      value={formData.expiry_days}
                      onChange={handleInputChange}
                      className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    />
                  </div>
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
                    placeholder="Additional information, terms, or notes for the client..."
                  ></textarea>
                </div>
              </div>
            </div>
            
            <div className="bg-white shadow-sm rounded-lg overflow-hidden mb-6">
              <div className="p-4 border-b border-gray-200">
                <h2 className="text-lg font-medium text-gray-800">Selected Elements</h2>
              </div>
              
              <div className="overflow-x-auto">
                {selectedElements.length > 0 ? (
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Element
                        </th>
                        <th scope="col" className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Quantity
                        </th>
                        <th scope="col" className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Unit Price
                        </th>
                        <th scope="col" className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Total
                        </th>
                        <th scope="col" className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Actions
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {selectedElements.map((element) => (
                        <tr key={element.id}>
                          <td className="px-4 py-3 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">
                              {element.type}
                              {element.dimensions && (
                                <span className="text-gray-500">
                                  {' '}({element.dimensions})
                                </span>
                              )}
                            </div>
                            <div className="text-sm text-gray-500">
                              {element.materials && `Material: ${element.materials}`}
                            </div>
                            <div className="mt-1">
                              <input
                                type="text"
                                placeholder="Additional notes for this item..."
                                value={element.notes || ''}
                                onChange={(e) => handleElementUpdate(element.id, 'notes', e.target.value)}
                                className="block w-full text-xs border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500"
                              />
                            </div>
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap">
                            <input
                              type="number"
                              min="1"
                              step="1"
                              value={element.quantity}
                              onChange={(e) => handleElementUpdate(element.id, 'quantity', e.target.value)}
                              className="block w-20 mx-auto text-center border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                            />
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap">
                            <div className="flex items-center justify-center">
                              <span className="mr-1">$</span>
                              <input
                                type="number"
                                min="0"
                                step="0.01"
                                value={element.unit_price}
                                onChange={(e) => handleElementUpdate(element.id, 'unit_price', e.target.value)}
                                className="block w-24 text-right border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                              />
                            </div>
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap text-sm text-right font-medium">
                            {formatCurrency(element.quantity * element.unit_price)}
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap text-right text-sm font-medium">
                            <button
                              type="button"
                              onClick={() => handleRemoveElement(element.id)}
                              className="text-red-600 hover:text-red-900"
                            >
                              Remove
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <div className="p-6 text-center">
                    <p className="text-gray-500">No elements selected for this quote.</p>
                    <p className="text-sm text-gray-500 mt-1">
                      Use the "Available Elements" panel to select elements to include.
                    </p>
                  </div>
                )}
              </div>
              
              {/* Quote Summary */}
              <div className="bg-gray-50 px-4 py-3 sm:px-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label htmlFor="tax_rate" className="block text-sm font-medium text-gray-700">
                          Tax Rate (%)
                        </label>
                        <input
                          type="number"
                          id="tax_rate"
                          name="tax_rate"
                          min="0"
                          step="0.1"
                          value={formData.tax_rate}
                          onChange={handleInputChange}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                        />
                      </div>
                      <div>
                        <label htmlFor="discount_percentage" className="block text-sm font-medium text-gray-700">
                          Discount (%)
                        </label>
                        <input
                          type="number"
                          id="discount_percentage"
                          name="discount_percentage"
                          min="0"
                          step="0.1"
                          value={formData.discount_percentage}
                          onChange={handleInputChange}
                          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                        />
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex flex-col justify-end">
                    <dl className="text-sm">
                      <div className="flex justify-between">
                        <dt>Subtotal</dt>
                        <dd className="font-medium">{formatCurrency(totals.subtotal)}</dd>
                      </div>
                      <div className="flex justify-between mt-1">
                        <dt>Tax ({formData.tax_rate || 0}%)</dt>
                        <dd className="font-medium">{formatCurrency(totals.tax_amount)}</dd>
                      </div>
                      {parseFloat(formData.discount_percentage) > 0 && (
                        <div className="flex justify-between mt-1">
                          <dt>Discount ({formData.discount_percentage || 0}%)</dt>
                          <dd className="font-medium text-red-600">-{formatCurrency(totals.discount_amount)}</dd>
                        </div>
                      )}
                      <div className="flex justify-between mt-2 pt-2 border-t border-gray-200">
                        <dt className="font-medium">Total</dt>
                        <dd className="font-bold text-lg">{formatCurrency(totals.total)}</dd>
                      </div>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="flex justify-end space-x-3">
              <Link
                to={`/projects/${projectId}`}
                className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Cancel
              </Link>
              
              <button
                type="submit"
                disabled={generating || selectedElements.length === 0}
                className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white 
                  ${generating || selectedElements.length === 0 
                    ? 'bg-gray-400 cursor-not-allowed' 
                    : 'bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'
                  }`}
              >
                {generating ? (
                  <>
                    <svg 
                      className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" 
                      xmlns="http://www.w3.org/2000/svg" 
                      fill="none" 
                      viewBox="0 0 24 24"
                    >
                      <circle 
                        className="opacity-25" 
                        cx="12" 
                        cy="12" 
                        r="10" 
                        stroke="currentColor" 
                        strokeWidth="4"
                      ></circle>
                      <path 
                        className="opacity-75" 
                        fill="currentColor" 
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    Generating...
                  </>
                ) : (
                  'Generate Quote'
                )}
              </button>
            </div>
          </form>
        </div>
        
        {/* Sidebar - Available Elements */}
        <div className="lg:col-span-1">
          <div className="bg-white shadow-sm rounded-lg overflow-hidden">
            <div className="p-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-800">Available Elements</h2>
              <p className="mt-1 text-sm text-gray-600">
                Select elements to include in the quote
              </p>
            </div>
            
            <div className="overflow-y-auto max-h-96">
              {elements.length > 0 ? (
                <div className="divide-y divide-gray-200">
                  {elements.map((element) => (
                    <div 
                      key={element.id}
                      className={`p-4 hover:bg-gray-50 cursor-pointer ${
                        selectedElements.some(el => el.id === element.id) 
                          ? 'bg-blue-50' 
                          : ''
                      }`}
                      onClick={() => handleElementSelect(element)}
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="text-sm font-medium text-gray-900">
                            {element.type}
                            {element.dimensions && (
                              <span className="ml-1 font-normal text-gray-500">
                                ({element.dimensions})
                              </span>
                            )}
                          </h3>
                          
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
                        
                        {element.estimated_price > 0 && (
                          <span className="text-sm font-medium text-gray-900">
                            {formatCurrency(element.estimated_price)}
                          </span>
                        )}
                      </div>
                      
                      {selectedElements.some(el => el.id === element.id) && (
                        <div className="mt-2">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            Selected
                          </span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-6 text-center">
                  <p className="text-gray-500">No elements available for this project.</p>
                  <Link
                    to={`/projects/${projectId}/elements`}
                    className="mt-2 inline-flex items-center text-sm text-blue-600 hover:text-blue-800"
                  >
                    Manage project elements
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuoteGeneratorPage;