import React, { useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  ChevronLeft, 
  Building, 
  MapPin, 
  Calendar, 
  DollarSign, 
  Clock, 
  Users, 
  FileText, 
  BarChart,
  Plus,
  Edit,
  Settings,
  MoreHorizontal,
  User,
  CheckCircle2,
  AlertCircle,
  CircleDashed,
  FileSpreadsheet
} from 'lucide-react';

// UI Components
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

// Mock service (replace with actual service later)
const fetchProjectDetails = async (projectId: string) => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Mock data
  return {
    id: projectId,
    name: 'Office Building Renovation',
    client: 'ABC Corporation',
    status: 'in-progress',
    progress: 65,
    startDate: '2025-01-15',
    endDate: '2025-05-30',
    budget: '$450,000',
    currentSpend: '$292,500',
    team: [
      { id: '1', name: 'John Doe', role: 'Project Manager', avatar: 'https://i.pravatar.cc/150?img=1' },
      { id: '2', name: 'Jane Smith', role: 'Lead Architect', avatar: 'https://i.pravatar.cc/150?img=5' },
      { id: '3', name: 'Alex Johnson', role: 'Cost Estimator', avatar: 'https://i.pravatar.cc/150?img=8' }
    ],
    description: 'Comprehensive renovation of a 4-story office building including structural updates, MEP systems, and interior remodeling.',
    location: 'Downtown, New York, NY',
    type: 'Commercial',
    documents: [
      { id: '1', name: 'Floor Plans', type: 'PDF', uploadedAt: '2025-01-18T10:30:00Z', status: 'processed' },
      { id: '2', name: 'Structural Assessment', type: 'PDF', uploadedAt: '2025-01-20T15:45:00Z', status: 'processed' },
      { id: '3', name: 'Electrical Layouts', type: 'CAD', uploadedAt: '2025-01-25T09:15:00Z', status: 'processed' },
      { id: '4', name: 'MEP Systems', type: 'BIM', uploadedAt: '2025-02-05T14:20:00Z', status: 'processing' },
      { id: '5', name: 'Interior Finishes', type: 'PDF', uploadedAt: '2025-02-10T11:35:00Z', status: 'processed' }
    ],
    estimations: [
      { id: '1', name: 'Initial Cost Estimation', createdAt: '2025-01-22T09:30:00Z', total: '$420,000', status: 'approved' },
      { id: '2', name: 'Revised Structural Costs', createdAt: '2025-02-08T13:45:00Z', total: '$455,000', status: 'approved' },
      { id: '3', name: 'MEP Systems Update', createdAt: '2025-02-15T10:15:00Z', total: '$450,000', status: 'pending' },
      { id: '4', name: 'Interior Finishes Breakdown', createdAt: '2025-03-01T14:20:00Z', total: '$448,500', status: 'draft' }
    ],
    tasks: [
      { id: '1', name: 'Initial Site Assessment', status: 'completed', dueDate: '2025-01-20', assignee: 'John Doe' },
      { id: '2', name: 'Structural Reinforcement Design', status: 'completed', dueDate: '2025-02-10', assignee: 'Jane Smith' },
      { id: '3', name: 'MEP Systems Installation', status: 'in-progress', dueDate: '2025-03-15', assignee: 'Alex Johnson' },
      { id: '4', name: 'Interior Wall Construction', status: 'in-progress', dueDate: '2025-03-30', assignee: 'John Doe' },
      { id: '5', name: 'Finishes and Fixtures', status: 'pending', dueDate: '2025-04-20', assignee: 'Jane Smith' },
      { id: '6', name: 'Final Inspection', status: 'pending', dueDate: '2025-05-15', assignee: 'Alex Johnson' }
    ],
    milestones: [
      { id: '1', name: 'Project Kickoff', date: '2025-01-15', status: 'completed' },
      { id: '2', name: 'Structural Work Complete', date: '2025-02-28', status: 'completed' },
      { id: '3', name: 'MEP Installation Complete', date: '2025-03-30', status: 'in-progress' },
      { id: '4', name: 'Interior Construction Complete', date: '2025-04-25', status: 'pending' },
      { id: '5', name: 'Final Handover', date: '2025-05-30', status: 'pending' }
    ]
  };
};

// Helper function to format date
const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(date);
};

// Status badge component
const StatusBadge = ({ status }: { status: string }) => {
  const statusConfig: Record<string, { label: string, className: string }> = {
    'planning': { label: 'Planning', className: 'bg-blue-100 text-blue-800 hover:bg-blue-100' },
    'in-progress': { label: 'In Progress', className: 'bg-amber-100 text-amber-800 hover:bg-amber-100' },
    'pending-approval': { label: 'Pending Approval', className: 'bg-purple-100 text-purple-800 hover:bg-purple-100' },
    'completed': { label: 'Completed', className: 'bg-green-100 text-green-800 hover:bg-green-100' },
    'cancelled': { label: 'Cancelled', className: 'bg-red-100 text-red-800 hover:bg-red-100' },
    'pending': { label: 'Pending', className: 'bg-slate-100 text-slate-800 hover:bg-slate-100' },
    'approved': { label: 'Approved', className: 'bg-green-100 text-green-800 hover:bg-green-100' },
    'draft': { label: 'Draft', className: 'bg-blue-100 text-blue-800 hover:bg-blue-100' },
    'processed': { label: 'Processed', className: 'bg-green-100 text-green-800 hover:bg-green-100' },
    'processing': { label: 'Processing', className: 'bg-amber-100 text-amber-800 hover:bg-amber-100' }
  };

  const config = statusConfig[status] || { label: 'Unknown', className: 'bg-gray-100 text-gray-800' };

  return (
    <Badge variant="outline" className={config.className}>{config.label}</Badge>
  );
};

// Task status icon component
const TaskStatusIcon = ({ status }: { status: string }) => {
  switch(status) {
    case 'completed':
      return <CheckCircle2 className="h-5 w-5 text-green-500" />;
    case 'in-progress':
      return <AlertCircle className="h-5 w-5 text-amber-500" />;
    case 'pending':
    default:
      return <CircleDashed className="h-5 w-5 text-slate-400" />;
  }
};

const ProjectDetails = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  
  // Fetch project details
  const { data: project, isLoading, error } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => fetchProjectDetails(projectId || '')
  });

  if (isLoading) {
    return (
      <div className="container mx-auto p-6 flex justify-center items-center h-96">
        <p>Loading project details...</p>
      </div>
    );
  }

  if (error || !project) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center mb-4">
          <Button variant="ghost" size="sm" asChild>
            <Link to="/projects">
              <ChevronLeft className="mr-2 h-4 w-4" />
              Back to Projects
            </Link>
          </Button>
        </div>
        <div className="flex justify-center items-center h-96">
          <p className="text-red-500">Error loading project details</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <div className="flex items-center mb-6">
        <Button variant="ghost" size="sm" asChild>
          <Link to="/projects">
            <ChevronLeft className="mr-2 h-4 w-4" />
            Back to Projects
          </Link>
        </Button>
      </div>

      <div className="flex flex-col space-y-6">
        {/* Project Header */}
        <div className="flex justify-between items-start">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-3xl font-bold">{project.name}</h1>
              <StatusBadge status={project.status} />
            </div>
            <p className="text-muted-foreground mt-1">{project.client}</p>
          </div>
          <div className="flex items-center space-x-2">
            <Button variant="outline">
              <Edit className="mr-2 h-4 w-4" />
              Edit Project
            </Button>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="icon">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem>
                  <Settings className="mr-2 h-4 w-4" />
                  Project Settings
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Users className="mr-2 h-4 w-4" />
                  Manage Team
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem className="text-red-600">
                  Archive Project
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        {/* Project Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle>Project Overview</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p>{project.description}</p>
              
              <div className="grid grid-cols-2 gap-4 pt-2">
                <div className="flex items-start">
                  <Building className="h-5 w-5 text-muted-foreground mr-2 mt-0.5" />
                  <div>
                    <p className="text-sm text-muted-foreground">Type</p>
                    <p className="font-medium">{project.type}</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <MapPin className="h-5 w-5 text-muted-foreground mr-2 mt-0.5" />
                  <div>
                    <p className="text-sm text-muted-foreground">Location</p>
                    <p className="font-medium">{project.location}</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <Calendar className="h-5 w-5 text-muted-foreground mr-2 mt-0.5" />
                  <div>
                    <p className="text-sm text-muted-foreground">Timeline</p>
                    <p className="font-medium">{formatDate(project.startDate)} - {formatDate(project.endDate)}</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <DollarSign className="h-5 w-5 text-muted-foreground mr-2 mt-0.5" />
                  <div>
                    <p className="text-sm text-muted-foreground">Budget</p>
                    <p className="font-medium">{project.budget}</p>
                  </div>
                </div>
              </div>
              
              <div className="pt-2">
                <p className="text-sm text-muted-foreground mb-2">Progress</p>
                <div className="flex items-center space-x-4">
                  <Progress value={project.progress} className="h-2 flex-1" />
                  <span className="text-sm font-medium">{project.progress}%</span>
                </div>
                <div className="flex justify-between mt-2 text-sm">
                  <span className="text-muted-foreground">Started: {formatDate(project.startDate)}</span>
                  <span className="text-muted-foreground">Expected Completion: {formatDate(project.endDate)}</span>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Project Team</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {project.team.map((member) => (
                  <div key={member.id} className="flex items-center justify-between">
                    <div className="flex items-center">
                      <Avatar className="h-10 w-10 mr-3">
                        <AvatarImage src={member.avatar} alt={member.name} />
                        <AvatarFallback>{member.name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="font-medium">{member.name}</p>
                        <p className="text-sm text-muted-foreground">{member.role}</p>
                      </div>
                    </div>
                    <Button variant="ghost" size="sm">
                      <User className="h-4 w-4 mr-2" />
                      Profile
                    </Button>
                  </div>
                ))}
                
                <Button variant="outline" className="w-full mt-2">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Team Member
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Project Details Tabs */}
        <Tabs defaultValue="documents" className="pt-2">
          <TabsList className="grid grid-cols-4 w-full">
            <TabsTrigger value="documents">Documents</TabsTrigger>
            <TabsTrigger value="estimations">Estimations</TabsTrigger>
            <TabsTrigger value="tasks">Tasks</TabsTrigger>
            <TabsTrigger value="milestones">Milestones</TabsTrigger>
          </TabsList>
          
          <TabsContent value="documents" className="mt-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Project Documents</h2>
              <Button onClick={() => navigate('/documents')}>
                <Plus className="mr-2 h-4 w-4" />
                Upload Document
              </Button>
            </div>
            
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Document Name</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Uploaded</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {project.documents.map((doc) => (
                  <TableRow key={doc.id}>
                    <TableCell className="font-medium">
                      <Link to={`/documents/${doc.id}`} className="hover:underline">
                        {doc.name}
                      </Link>
                    </TableCell>
                    <TableCell>{doc.type}</TableCell>
                    <TableCell>{formatDate(doc.uploadedAt)}</TableCell>
                    <TableCell>
                      <StatusBadge status={doc.status} />
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="sm" asChild>
                        <Link to={`/documents/${doc.id}`}>
                          View
                        </Link>
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TabsContent>
          
          <TabsContent value="estimations" className="mt-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Cost Estimations</h2>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                New Estimation
              </Button>
            </div>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle>Budget Overview</CardTitle>
                <CardDescription>Current spend vs. total budget</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="text-sm text-muted-foreground">Total Budget</p>
                      <p className="text-2xl font-bold">{project.budget}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Current Spend</p>
                      <p className="text-2xl font-bold">{project.currentSpend}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Remaining</p>
                      <p className="text-2xl font-bold text-green-600">${parseFloat(project.budget.replace('$', '').replace(',', '')) - parseFloat(project.currentSpend.replace('$', '').replace(',', ''))}</p>
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Spend Progress</span>
                      <span>
                        {Math.round((parseFloat(project.currentSpend.replace('$', '').replace(',', '')) / parseFloat(project.budget.replace('$', '').replace(',', ''))) * 100)}%
                      </span>
                    </div>
                    <Progress 
                      value={Math.round((parseFloat(project.currentSpend.replace('$', '').replace(',', '')) / parseFloat(project.budget.replace('$', '').replace(',', ''))) * 100)} 
                      className="h-2" 
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <div className="mt-6">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Estimation Name</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead>Total</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {project.estimations.map((estimation) => (
                    <TableRow key={estimation.id}>
                      <TableCell className="font-medium">
                        <Link to={`/estimations/${estimation.id}`} className="hover:underline">
                          {estimation.name}
                        </Link>
                      </TableCell>
                      <TableCell>{formatDate(estimation.createdAt)}</TableCell>
                      <TableCell>{estimation.total}</TableCell>
                      <TableCell>
                        <StatusBadge status={estimation.status} />
                      </TableCell>
                      <TableCell className="text-right">
                        <Button variant="ghost" size="sm" asChild>
                          <Link to={`/estimations/${estimation.id}`}>
                            <FileSpreadsheet className="h-4 w-4 mr-2" />
                            View
                          </Link>
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </TabsContent>
          
          <TabsContent value="tasks" className="mt-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Project Tasks</h2>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Add Task
              </Button>
            </div>
            
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Task</TableHead>
                  <TableHead>Assignee</TableHead>
                  <TableHead>Due Date</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {project.tasks.map((task) => (
                  <TableRow key={task.id}>
                    <TableCell className="font-medium">
                      <div className="flex items-center">
                        <TaskStatusIcon status={task.status} />
                        <span className="ml-2">{task.name}</span>
                      </div>
                    </TableCell>
                    <TableCell>{task.assignee}</TableCell>
                    <TableCell>{formatDate(task.dueDate)}</TableCell>
                    <TableCell>
                      <StatusBadge status={task.status} />
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="sm">
                        <Edit className="h-4 w-4 mr-2" />
                        Edit
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TabsContent>
          
          <TabsContent value="milestones" className="mt-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Project Milestones</h2>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Add Milestone
              </Button>
            </div>
            
            <div className="space-y-6">
              {project.milestones.map((milestone, index) => (
                <div key={milestone.id} className="relative pl-6 pb-6 last:pb-0">
                  {/* Timeline connector */}
                  {index < project.milestones.length - 1 && (
                    <div className="absolute top-6 bottom-0 left-3 border-l-2 border-gray-200" />
                  )}
                  
                  {/* Milestone dot */}
                  <div className={`absolute top-1 left-0 w-6 h-6 rounded-full flex items-center justify-center ${
                    milestone.status === 'completed' 
                      ? 'bg-green-100' 
                      : milestone.status === 'in-progress' 
                        ? 'bg-amber-100' 
                        : 'bg-gray-100'
                  }`}>
                    <div className={`w-3 h-3 rounded-full ${
                      milestone.status === 'completed' 
                        ? 'bg-green-500' 
                        : milestone.status === 'in-progress' 
                          ? 'bg-amber-500' 
                          : 'bg-gray-400'
                    }`} />
                  </div>
                  
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-medium">{milestone.name}</h3>
                      <p className="text-sm text-muted-foreground">
                        <Calendar className="inline h-4 w-4 mr-1 mb-1" />
                        {formatDate(milestone.date)}
                      </p>
                    </div>
                    <StatusBadge status={milestone.status} />
                  </div>
                </div>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default ProjectDetails;