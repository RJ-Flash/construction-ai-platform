import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useAtom } from 'jotai'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { FilePlus, FileText, Calculator, LayoutDashboard, PlusCircle, ChevronRight } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { userAtom } from '@/store/auth'
import { formatCurrency } from '@/lib/utils'
import api from '@/services/api'

const Dashboard = () => {
  const [user] = useAtom(userAtom)
  
  // Fetch recent projects
  const { data: recentProjects = [] } = useQuery({
    queryKey: ['recentProjects'],
    queryFn: async () => {
      const response = await api.get('/projects?limit=5')
      return response.data
    },
    enabled: !!user,
  })
  
  // Fetch recent documents
  const { data: recentDocuments = [] } = useQuery({
    queryKey: ['recentDocuments'],
    queryFn: async () => {
      const response = await api.get('/documents?limit=5')
      return response.data
    },
    enabled: !!user,
  })
  
  // Fetch recent estimations
  const { data: recentEstimations = [] } = useQuery({
    queryKey: ['recentEstimations'],
    queryFn: async () => {
      const response = await api.get('/estimations?limit=5')
      return response.data
    },
    enabled: !!user,
  })
  
  // Mock data for demo purposes
  const projectStats = [
    { name: 'Active', value: 12 },
    { name: 'Completed', value: 8 },
    { name: 'Draft', value: 5 },
  ]
  
  const documentTypeStats = [
    { name: 'Architectural', value: 15 },
    { name: 'Structural', value: 10 },
    { name: 'MEP', value: 8 },
    { name: 'Other', value: 3 },
  ]
  
  const estimationMonthlyData = [
    { name: 'Jan', value: 12000 },
    { name: 'Feb', value: 19000 },
    { name: 'Mar', value: 15000 },
    { name: 'Apr', value: 21000 },
    { name: 'May', value: 18000 },
    { name: 'Jun', value: 24000 },
  ]
  
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8']
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <div className="flex space-x-2">
          <Button asChild>
            <Link to="/projects/new">
              <PlusCircle className="mr-2 h-4 w-4" />
              New Project
            </Link>
          </Button>
        </div>
      </div>
      
      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Projects</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{projectStats.reduce((acc, curr) => acc + curr.value, 0)}</div>
            <p className="text-xs text-muted-foreground">
              +12% from last month
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Documents</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{documentTypeStats.reduce((acc, curr) => acc + curr.value, 0)}</div>
            <p className="text-xs text-muted-foreground">
              +8% from last month
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Estimations</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{estimationMonthlyData.length}</div>
            <p className="text-xs text-muted-foreground">
              +15% from last month
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Average Estimate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(estimationMonthlyData.reduce((acc, curr) => acc + curr.value, 0) / estimationMonthlyData.length)}
            </div>
            <p className="text-xs text-muted-foreground">
              +5% from last month
            </p>
          </CardContent>
        </Card>
      </div>
      
      {/* Charts */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Project Status</CardTitle>
            <CardDescription>Distribution of projects by status</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={projectStats}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    fill="#8884d8"
                    paddingAngle={5}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {projectStats.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [value, 'Projects']} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Monthly Estimation</CardTitle>
            <CardDescription>Estimation amounts by month</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={estimationMonthlyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis tickFormatter={(value) => `$${value / 1000}K`} />
                  <Tooltip formatter={(value) => [formatCurrency(value), 'Estimate']} />
                  <Bar dataKey="value" fill="#0066FF" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Recent Items */}
      <Tabs defaultValue="projects" className="space-y-4">
        <TabsList>
          <TabsTrigger value="projects">Recent Projects</TabsTrigger>
          <TabsTrigger value="documents">Recent Documents</TabsTrigger>
          <TabsTrigger value="estimations">Recent Estimations</TabsTrigger>
        </TabsList>
        
        <TabsContent value="projects" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Projects</CardTitle>
              <CardDescription>Your recently created or updated projects</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {/* For demo purposes, using mock data instead of recentProjects */}
                {[
                  { id: 1, name: "Office Building Renovation", client_name: "ABC Corp", status: "active", created_at: "2025-03-10T12:00:00Z" },
                  { id: 2, name: "Residential Tower", client_name: "XYZ Development", status: "draft", created_at: "2025-03-08T14:30:00Z" },
                  { id: 3, name: "Shopping Mall Extension", client_name: "Retail Properties Inc", status: "active", created_at: "2025-03-05T09:15:00Z" },
                  { id: 4, name: "Hospital Wing", client_name: "Healthcare Group", status: "completed", created_at: "2025-03-01T11:00:00Z" },
                ].map((project) => (
                  <div key={project.id} className="flex items-center justify-between border-b pb-2">
                    <div>
                      <Link 
                        to={`/projects/${project.id}`}
                        className="font-medium hover:underline"
                      >
                        {project.name}
                      </Link>
                      <p className="text-sm text-muted-foreground">{project.client_name}</p>
                    </div>
                    <div className="flex items-center">
                      <div className={`text-xs rounded-full px-2 py-1 capitalize mr-2 ${
                        project.status === 'active' ? 'bg-green-100 text-green-800' :
                        project.status === 'draft' ? 'bg-amber-100 text-amber-800' :
                        'bg-blue-100 text-blue-800'
                      }`}>
                        {project.status}
                      </div>
                      <Link to={`/projects/${project.id}`}>
                        <Button variant="ghost" size="icon">
                          <ChevronRight className="h-4 w-4" />
                        </Button>
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
            <CardFooter>
              <Button asChild variant="outline" className="w-full">
                <Link to="/projects">View All Projects</Link>
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
        
        <TabsContent value="documents" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Documents</CardTitle>
              <CardDescription>Your recently uploaded or processed documents</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {/* For demo purposes, using mock data instead of recentDocuments */}
                {[
                  { id: 1, original_filename: "Floor Plan.pdf", project_name: "Office Building Renovation", status: "analyzed", created_at: "2025-03-15T09:00:00Z" },
                  { id: 2, original_filename: "Structural Drawings.dwg", project_name: "Residential Tower", status: "processing", created_at: "2025-03-14T14:00:00Z" },
                  { id: 3, original_filename: "Elevations.pdf", project_name: "Shopping Mall Extension", status: "analyzed", created_at: "2025-03-12T10:30:00Z" },
                  { id: 4, original_filename: "MEP Plan.ifc", project_name: "Hospital Wing", status: "uploaded", created_at: "2025-03-11T16:45:00Z" },
                ].map((document) => (
                  <div key={document.id} className="flex items-center justify-between border-b pb-2">
                    <div>
                      <Link 
                        to={`/documents/${document.id}`}
                        className="font-medium hover:underline"
                      >
                        {document.original_filename}
                      </Link>
                      <p className="text-sm text-muted-foreground">{document.project_name}</p>
                    </div>
                    <div className="flex items-center">
                      <div className={`text-xs rounded-full px-2 py-1 capitalize mr-2 ${
                        document.status === 'analyzed' ? 'bg-green-100 text-green-800' :
                        document.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                        'bg-amber-100 text-amber-800'
                      }`}>
                        {document.status}
                      </div>
                      <Link to={`/documents/${document.id}`}>
                        <Button variant="ghost" size="icon">
                          <ChevronRight className="h-4 w-4" />
                        </Button>
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
            <CardFooter>
              <Button asChild variant="outline" className="w-full">
                <Link to="/documents">View All Documents</Link>
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
        
        <TabsContent value="estimations" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Estimations</CardTitle>
              <CardDescription>Your recently created estimations</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {/* For demo purposes, using mock data instead of recentEstimations */}
                {[
                  { id: 1, name: "Initial Estimation", project_name: "Office Building Renovation", status: "draft", total_cost: 125000, created_at: "2025-03-18T10:00:00Z" },
                  { id: 2, name: "Complete Estimation", project_name: "Residential Tower", status: "finalized", total_cost: 780000, created_at: "2025-03-16T15:30:00Z" },
                  { id: 3, name: "Initial Estimation", project_name: "Shopping Mall Extension", status: "draft", total_cost: 450000, created_at: "2025-03-14T11:15:00Z" },
                  { id: 4, name: "Final Estimation", project_name: "Hospital Wing", status: "approved", total_cost: 920000, created_at: "2025-03-10T09:30:00Z" },
                ].map((estimation) => (
                  <div key={estimation.id} className="flex items-center justify-between border-b pb-2">
                    <div>
                      <Link 
                        to={`/estimations/${estimation.id}`}
                        className="font-medium hover:underline"
                      >
                        {estimation.name}
                      </Link>
                      <p className="text-sm text-muted-foreground">{estimation.project_name}</p>
                    </div>
                    <div className="flex items-center">
                      <div className="text-sm font-medium mr-4">
                        {formatCurrency(estimation.total_cost)}
                      </div>
                      <div className={`text-xs rounded-full px-2 py-1 capitalize mr-2 ${
                        estimation.status === 'approved' ? 'bg-green-100 text-green-800' :
                        estimation.status === 'finalized' ? 'bg-blue-100 text-blue-800' :
                        'bg-amber-100 text-amber-800'
                      }`}>
                        {estimation.status}
                      </div>
                      <Link to={`/estimations/${estimation.id}`}>
                        <Button variant="ghost" size="icon">
                          <ChevronRight className="h-4 w-4" />
                        </Button>
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
            <CardFooter>
              <Button asChild variant="outline" className="w-full">
                <Link to="/estimations">View All Estimations</Link>
              </Button>
            </CardFooter>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default Dashboard
