import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../hooks/useAuth';
import { useToast } from '../hooks/useToast';
import { ENDPOINTS } from '../config/api';

// Components
import ProjectCard from '../components/ProjectCard';
import StatCard from '../components/StatCard';

const Dashboard = () => {
  const { user } = useAuth();
  const { showToast } = useToast();
  const [projects, setProjects] = useState([]);
  const [stats, setStats] = useState({
    totalProjects: 0,
    activeProjects: 0,
    documentsAnalyzed: 0,
    quotesGenerated: 0
  });
  const [loading, setLoading] = useState(true);

  // Fetch projects and stats on component mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch projects
        const projectsResponse = await axios.get(ENDPOINTS.PROJECTS.LIST);
        setProjects(projectsResponse.data);
        
        // Calculate stats
        const totalProjects = projectsResponse.data.length;
        const activeProjects = projectsResponse.data.filter(
          project => project.status !== 'completed'
        ).length;
        
        // Fetch total documents analyzed
        let documentsAnalyzed = 0;
        let quotesGenerated = 0;
        
        // For each project, get document and quote counts
        for (const project of projectsResponse.data) {
          const documentsResponse = await axios.get(
            ENDPOINTS.PROJECTS.DOCUMENTS(project.id)
          );
          
          documentsAnalyzed += documentsResponse.data.filter(
            doc => doc.is_analyzed
          ).length;
          
          const quotesResponse = await axios.get(
            ENDPOINTS.PROJECTS.QUOTES(project.id)
          );
          
          quotesGenerated += quotesResponse.data.length;
        }
        
        setStats({
          totalProjects,
          activeProjects,
          documentsAnalyzed,
          quotesGenerated
        });
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        showToast('Failed to load dashboard data', 'error');
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [showToast]);

  // Display loading spinner while data is being fetched
  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">
            Welcome, {user?.full_name || 'User'}
          </h1>
          <p className="text-gray-600">
            {user?.company_name ? `${user.company_name}` : 'Construction AI Platform'}
          </p>
        </div>
        <Link
          to="/projects/new"
          className="mt-4 md:mt-0 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <svg className="mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
          </svg>
          New Project
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          title="Total Projects"
          value={stats.totalProjects}
          icon={
            <svg className="h-6 w-6 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
              />
            </svg>
          }
          color="bg-blue-50"
        />
        <StatCard
          title="Active Projects"
          value={stats.activeProjects}
          icon={
            <svg className="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
          }
          color="bg-green-50"
        />
        <StatCard
          title="Documents Analyzed"
          value={stats.documentsAnalyzed}
          icon={
            <svg className="h-6 w-6 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          }
          color="bg-purple-50"
        />
        <StatCard
          title="Quotes Generated"
          value={stats.quotesGenerated}
          icon={
            <svg className="h-6 w-6 text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          }
          color="bg-yellow-50"
        />
      </div>

      {/* Recent Projects */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-800">Recent Projects</h2>
          <Link
            to="/projects"
            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            View All
          </Link>
        </div>

        {projects.length === 0 ? (
          <div className="bg-white shadow rounded-lg p-6 text-center">
            <p className="text-gray-500">No projects yet. Create your first project to get started.</p>
            <Link
              to="/projects/new"
              className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Create Project
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {projects
              .slice(0, 6) // Show only the 6 most recent projects
              .map((project) => (
                <ProjectCard key={project.id} project={project} />
              ))}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link
            to="/projects/new"
            className="bg-white shadow rounded-lg p-6 flex flex-col items-center justify-center hover:shadow-md transition-shadow"
          >
            <svg className="h-10 w-10 text-blue-500 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M12 4v16m8-8H4"
              />
            </svg>
            <span className="text-gray-800 font-medium">New Project</span>
          </Link>
          
          <Link
            to="/documents/upload"
            className="bg-white shadow rounded-lg p-6 flex flex-col items-center justify-center hover:shadow-md transition-shadow"
          >
            <svg className="h-10 w-10 text-green-500 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
            <span className="text-gray-800 font-medium">Upload Document</span>
          </Link>
          
          <Link
            to="/quotes/generate"
            className="bg-white shadow rounded-lg p-6 flex flex-col items-center justify-center hover:shadow-md transition-shadow"
          >
            <svg className="h-10 w-10 text-purple-500 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"
              />
            </svg>
            <span className="text-gray-800 font-medium">Generate Quote</span>
          </Link>
          
          <Link
            to="/settings"
            className="bg-white shadow rounded-lg p-6 flex flex-col items-center justify-center hover:shadow-md transition-shadow"
          >
            <svg className="h-10 w-10 text-gray-500 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
              />
            </svg>
            <span className="text-gray-800 font-medium">Account Settings</span>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
