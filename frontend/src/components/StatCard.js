import React from 'react';

// Stat card component for displaying statistics on dashboard
const StatCard = ({ title, value, icon, color = 'bg-blue-50' }) => {
  return (
    <div className={`${color} p-6 rounded-lg shadow`}>
      <div className="flex items-center">
        <div className="flex-shrink-0">{icon}</div>
        <div className="ml-4">
          <h3 className="text-lg font-medium text-gray-900">{title}</h3>
          <div className="mt-1 text-3xl font-semibold text-gray-900">{value}</div>
        </div>
      </div>
    </div>
  );
};

export default StatCard;
