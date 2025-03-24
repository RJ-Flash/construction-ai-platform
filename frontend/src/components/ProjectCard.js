import React from 'react';
import { Link } from 'react-router-dom';

// Helper function to format dates
const formatDate = (dateString) => {
  if (!dateString) return 'Not set';
  
  const date = new Date(dateString);
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

// Helper function to get status badge color
const getStatusColor = (status) => {
  switch (status?.toLowerCase()) {
    case 'planning':
      return 'bg-blue-100 text-blue-800';
    case 'in-progress':
    case 'inprogress':
      return 'bg-yellow-100 text-yellow-800';
    case 'completed':
      return 'bg-green-100 text-green-800';
    case 'on-hold':
    case 'onhold':
      return 'bg-orange-100 text-orange-800';
    case 'cancelled':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

// Project card component
const ProjectCard = ({ project }) => {
  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="p-5">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-1 truncate">
              {project.name}
            </h3>
            <p className="text-sm text-gray-500 mb-3">
              {project.client_name || 'No client specified'}
            </p>
          </div>
          <span
            className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(
              project.status
            )}`}
          >
            {project.status?.charAt(0).toUpperCase() + project.status?.slice(1) || 'Unknown'}
          </span>
        </div>

        <p className="text-sm text-gray-600 mb-4 line-clamp-2">
          {project.description || 'No description provided'}
        </p>

        <div className="grid grid-cols-2 gap-2 text-sm mb-4">
          <div>
            <span className="text-gray-500">Location:</span>
            <p className="text-gray-800 truncate">
              {project.location || 'Not specified'}
            </p>
          </div>
          <div>
            <span className="text-gray-500">Start Date:</span>
            <p className="text-gray-800">{formatDate(project.start_date)}</p>
          </div>
        </div>

        <div className="flex justify-between items-center pt-2 border-t border-gray-200">
          <span className="text-xs text-gray-500">
            Created {formatDate(project.created_at)}
          </span>
          <Link
            to={`/projects/${project.id}`}
            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            View Details
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ProjectCard;
