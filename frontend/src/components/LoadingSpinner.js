import React from 'react';

/**
 * Loading spinner component for indicating loading states.
 * 
 * @param {Object} props
 * @param {string} props.size - Size of the spinner: 'small', 'medium', or 'large'
 * @param {string} props.color - Color of the spinner
 * @param {string} props.className - Additional CSS classes
 */
const LoadingSpinner = ({ size = 'medium', color = 'blue', className = '' }) => {
  // Determine spinner size
  const sizeClass = {
    small: 'h-4 w-4',
    medium: 'h-8 w-8',
    large: 'h-12 w-12'
  }[size] || 'h-8 w-8';
  
  // Determine spinner color
  const colorClass = {
    blue: 'border-blue-500',
    green: 'border-green-500',
    red: 'border-red-500',
    yellow: 'border-yellow-500',
    purple: 'border-purple-500',
    gray: 'border-gray-500',
    white: 'border-white'
  }[color] || 'border-blue-500';

  return (
    <div className={`flex justify-center items-center ${className}`}>
      <div
        className={`${sizeClass} animate-spin rounded-full border-t-2 border-b-2 ${colorClass}`}
        role="status"
        aria-label="Loading"
      />
    </div>
  );
};

export default LoadingSpinner;
