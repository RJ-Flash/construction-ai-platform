import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { PlusCircle, FileText, Calculator, Upload, Settings } from 'lucide-react'
import { useAtom } from 'jotai'
import { userAtom } from '@/store/auth'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

import { formatCurrency, formatDate, formatFileSize } from '@/lib/utils'
import { request } from '@/services/api'

// API function to get dashboard data
const fetchDashboardData = async () => {
  return request({
    url: '/dashboard',
    method: 'GET'
  })
}

const Dashboard = () => {
  const [user] = useAtom(userAtom)
  const [activeTab, setActiveTab] = useState('overview')
  
  // Query for dashboard data
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboardData'],
    queryFn: fetchDashboardData,
    // Fallback to mock data for development
    placeholderData: {
      projectCount: 5,
      documentCount: 12,
      estimationCount: 7,
      storage: {
        used: 256000000, // 256 MB
        total: 1000000000 // 1 GB
      },
      recentProjects: [
        {
          id: 1,
          name: 'Commercial Office Building',
          client_name: 'ABC Corporation',
          status: 'active',
          created_at: '2025-03-15T09:30:00Z', 
          document_count: 5,
          estimation_count: 2,
          total_estimate: 1250000
        },
        {
          id: 2,
          name: 'Residential Complex',
          client_name: 'XYZ Developers',
          status: 'active',
          created_at: '2025-03-10T14:20:00Z',
          document_count: 4,
          estimation_count: 3,
          total_estimate: 850000
        },
        {
          id: 3,
          name: 'School Renovation',
          client_name: 'City School District',
          status: 'draft',
          created_at: '2025-03-05T11:45:00Z',
          document_count: 3,
          estimation_count: 2,
          total_estimate: 450000
        }
      ],
      recentDocuments: [
        {
          id: 1,
          filename: 'floor-plan.pdf',
          original_filename: 'Floor Plan - First Floor.pdf',
          document_type: 'architectural',
          status: 'analyzed',
          created_at: '2025-03-17T10:20:00Z',
          file_size: 2450000,
          project_id: 1,
          project_name: 'Commercial Office Building'
        },
        {
          id: 2,
          filename: 'electrical.dwg',
          original_filename: 'Electrical Layout.dwg',
          document_type: 'mep',
          status: 'analyzed',
          created_at: '2025-03-16T14:30:00Z',
          file_size: 3200000,
          project_id: 1,
          project_name: 'Commercial Office Building'
        },
        {
          id: 3,
          filename: 'foundation.pdf',
          original_filename: 'Foundation Plan.pdf',
          document_type: 'structural',
          status: 'processing',
          created_at: '2025-03-16T09:15:00Z',
          file_size: 1840000,
          project_id: 2,
          project_name: 'Residential Complex'
        }
      ],
      recentEstimations: [
        {
          id: 1,
          name: 'Commercial Office - Initial',
          status: 'finalized',
          created_at: '2025-03-18T11:30:00Z',
          project_id: 1,
          project_name: 'Commercial Office Building',
          total_cost: 1250000
        },
        {
          id: 2,
          name: 'Residential Complex - Phase 1',
          status: 'draft',
          created_at: '2025-03-15T15:45:00Z',
          project_id: 2,
          project_name: 'Residential Complex',
          total_cost: 450000
        },
        {
          id: 3,
          name: 'Residential Complex - Full Project',
          status: 'draft',
          created_at: '2025-03-14T12:20:00Z',
          project_id: 2,
          project_name: 'Residential Complex',
          total_cost: 850000
        }
      ]
    }
  })

  // Calculate storage percentage
  const storagePercentage = data?.storage 
    ? Math.round((data.storage.used / data.storage.total) * 100) 
    : 0
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back, {user?.full_name || 'User'}
          </p>
        </div>
        <div>
          <Button asChild>
            <Link to="/projects/new">
              <PlusCircle className="mr-2 h-4 w-4" />
              New Project
            </Link>
          </Button>
        </div>
      </div>
      
      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Projects
            </CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{isLoading ? '...' : data?.projectCount}</div>
            <p className="text-xs text-muted-foreground">
              {data?.recentProjects?.length} recently active
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Documents
            </CardTitle>
            <Upload className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{isLoading ? '...' : data?.documentCount}</div>
            <p className="text-xs text-muted-foreground">
              {data?.recentDocuments?.filter(d => d.status === 'analyzed').length} analyzed
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Estimations
            </CardTitle>
            <Calculator className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{isLoading ? '...' : data?.estimationCount}</div>
            <p className="text-xs text-muted-foreground">
              {data?.recentEstimations?.filter(e => e.status === 'finalized').length} finalized
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Storage
            </CardTitle>
            <Settings className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isLoading 
                ? '...' 
                : data?.storage 
                  ? formatFileSize(data.storage.used) 
                  : '0 MB'
              }
            </div>
            <div className="mt-2 space-y-1">
              <Progress value={storagePercentage} className="h-2" />
              <p className="text-xs text-muted-foreground">
                {storagePercentage}% of {data?.storage ? formatFileSize(data.storage.total) : '1 GB'} used
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Recent activity tabs */}
      <Tabs defaultValue="overview" value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="projects">Projects</TabsTrigger>
          <TabsTrigger value="documents">Documents</TabsTrigger>
          <TabsTrigger value="estimations">Estimations</TabsTrigger>
        </TabsList>
        
        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {/* Recent projects */}
            <Card className="col-span-2">
              <CardHeader>
                <CardTitle>Recent Projects</CardTitle>
                <CardDescription>You have {data?.projectCount || 0} total projects</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {isLoading ? (
                    <p>Loading projects...</p>
                  ) : data?.recentProjects?.length ? (
                    <div className="grid grid-cols-1 gap-4">
                      {data.recentProjects.map((project) => (
                        <Link key={project.id} to={`/projects/${project.id}`}>
                          <div className="flex items-center space-x-4 rounded-md border p-4 transition-all hover:bg-accent">
                            <div className="flex-1 space-y-1">
                              <p className="font-medium leading-none">{project.name}</p>
                              <p className="text-sm text-muted-foreground">
                                {project.client_name} • {formatDate(project.created_at, 'MMM d, yyyy')}
                              </p>
                            </div>
                            <div className="flex flex-col items-end">
                              <span className="font-semibold">
                                {formatCurrency(project.total_estimate)}
                              </span>
                              <span className={`text-xs px-2 py-1 rounded-full ${
                                project.status === 'active' 
                                  ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100' 
                                  : 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-100'
                              }`}>
                                {project.status.charAt(0).toUpperCase() + project.status.slice(1)}
                              </span>
                            </div>
                          </div>
                        </Link>
                      ))}
                    </div>
                  ) : (
                    <p className="text-muted-foreground">No projects found</p>
                  )}
                </div>
              </CardContent>
              <CardFooter>
                <Button asChild variant="outline" className="w-full">
                  <Link to="/projects">View all projects</Link>
                </Button>
              </CardFooter>
            </Card>
            
            {/* Recent documents */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Documents</CardTitle>
                <CardDescription>Recently uploaded documents</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {isLoading ? (
                    <p>Loading documents...</p>
                  ) : data?.recentDocuments?.length ? (
                    <div className="grid grid-cols-1 gap-2">
                      {data.recentDocuments.map((doc) => (
                        <Link key={doc.id} to={`/documents/${doc.id}`}>
                          <div className="flex items-center space-x-2 rounded-md border p-2 transition-all hover:bg-accent">
                            <div className="flex-1 space-y-1 overflow-hidden">
                              <p className="font-medium leading-none truncate" title={doc.original_filename}>
                                {doc.original_filename}
                              </p>
                              <p className="text-xs text-muted-foreground">
                                {formatDate(doc.created_at, 'MMM d')} • {formatFileSize(doc.file_size)}
                              </p>
                            </div>
                            <div className="flex-shrink-0">
                              <span className={`text-xs px-2 py-1 rounded-full ${
                                doc.status === 'analyzed' 
                                  ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100'
                                  : doc.status === 'processing'
                                  ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100'
                                  : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                              }`}>
                                {doc.status}
                              </span>
                            </div>
                          </div>
                        </Link>
                      ))}
                    </div>
                  ) : (
                    <p className="text-muted-foreground">No recent documents</p>
                  )}
                </div>
              </CardContent>
              <CardFooter>
                <Button asChild variant="outline" className="w-full">
                  <Link to="/documents">View all documents</Link>
                </Button>
              </CardFooter>
            </Card>
          </div>
          
          {/* Recent estimations */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Estimations</CardTitle>
              <CardDescription>Recently created or updated estimations</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {isLoading ? (
                  <p>Loading estimations...</p>
                ) : data?.recentEstimations?.length ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {data.recentEstimations.map((estimation) => (
                      <Link key={estimation.id} to={`/estimations/${estimation.id}`}>
                        <div className="flex flex-col space-y-2 rounded-md border p-4 transition-all hover:bg-accent h-full">
                          <div className="flex justify-between items-start">
                            <p className="font-medium leading-none">{estimation.name}</p>
                            <span className={`text-xs px-2 py-1 rounded-full ${
                              estimation.status === 'finalized' 
                                ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100'
                                : estimation.status === 'approved'
                                ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100'
                                : 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-100'
                            }`}>
                              {estimation.status}
                            </span>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            {estimation.project_name}
                          </p>
                          <div className="mt-auto pt-2 flex justify-between items-end">
                            <p className="text-xs text-muted-foreground">
                              {formatDate(estimation.created_at, 'MMM d, yyyy')}
                            </p>
                            <p className="font-semibold">
                              {formatCurrency(estimation.total_cost)}
                            </p>
                          </div>
                        </div>
                      </Link>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground">No recent estimations</p>
                )}
              </div>
            </CardContent>
            <CardFooter>
              <Button asChild variant="outline" className="w-full">
                <Link to="/estimations">View all estimations</Link>
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
        
        <TabsContent value="projects">
          <Card>
            <CardHeader>
              <CardTitle>Projects</CardTitle>
              <CardDescription>Manage your construction projects</CardDescription>
            </CardHeader>
            <CardContent>
              <p>Full project management view will be implemented here</p>
            </CardContent>
            <CardFooter>
              <Button asChild className="w-full">
                <Link to="/projects">Go to Projects</Link>
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
        
        <TabsContent value="documents">
          <Card>
            <CardHeader>
              <CardTitle>Documents</CardTitle>
              <CardDescription>Manage your construction plans and documents</CardDescription>
            </CardHeader>
            <CardContent>
              <p>Full document management view will be implemented here</p>
            </CardContent>
            <CardFooter>
              <Button asChild className="w-full">
                <Link to="/documents">Go to Documents</Link>
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
        
        <TabsContent value="estimations">
          <Card>
            <CardHeader>
              <CardTitle>Estimations</CardTitle>
              <CardDescription>Manage your cost estimations</CardDescription>
            </CardHeader>
            <CardContent>
              <p>Full estimation management view will be implemented here</p>
            </CardContent>
            <CardFooter>
              <Button asChild className="w-full">
                <Link to="/estimations">Go to Estimations</Link>
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default Dashboard
