import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  Building, 
  Search, 
  Plus, 
  MoreVertical, 
  Filter, 
  CalendarDays, 
  Users, 
  FileText,
  ChevronUp,
  ChevronDown
} from 'lucide-react';

// UI Components
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Separator } from '@/components/ui/separator';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

// Mock service (replace with actual service when available)
const fetchProjects = async () => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Mock data
  return [
    {
      id: '1',
      name: 'Office Building Renovation',
      client: 'ABC Corporation',
      status: 'in-progress',
      progress: 65,
      startDate: '2025-01-15',
      endDate: '2025-05-30',
      budget: '$450,000',
      team: ['John Doe', 'Jane Smith', 'Alex Johnson'],
      documentCount: 12,
      estimationCount: 4,
      description: 'Comprehensive renovation of a 4-story office building including structural updates, MEP systems, and interior remodeling.',
      location: 'Downtown, New York, NY',
      type: 'Commercial'
    },
    {
      id: '2',
      name: 'Residential Complex',
      client: 'XYZ Developers',
      status: 'planning',
      progress: 25,
      startDate: '2025-02-10',
      endDate: '2025-08-15',
      budget: '$2,500,000',
      team: ['Mike Williams', 'Sarah Davis', 'Robert Chen'],
      documentCount: 18,
      estimationCount: 6,
      description: 'New construction of a 24-unit residential complex with amenities including pool, gym, and community spaces.',
      location: 'Suburb Area, Los Angeles, CA',
      type: 'Residential'
    },
    {
      id: '3',
      name: 'Hospital Wing Addition',
      client: 'City Medical Center',
      status: 'pending-approval',
      progress: 10,
      startDate: '2025-04-01',
      endDate: '2026-02-28',
      budget: '$5,800,000',
      team: ['Emma Taylor', 'David Brown'],
      documentCount: 24,
      estimationCount: 3,
      description: 'Addition of a new specialized care wing to existing hospital facility with state-of-the-art medical equipment infrastructure.',
      location: 'Medical District, Chicago, IL',
      type: 'Healthcare'
    },
    {
      id: '4',
      name: 'Shopping Mall Renovation',
      client: 'Retail Properties Inc.',
      status: 'completed',
      progress: 100,
      startDate: '2024-09-01',
      endDate: '2025-02-15',
      budget: '$3,200,000',
      team: ['Lisa Jackson', 'Tom Wilson', 'Karen Lee', 'Mark Smith'],
      documentCount: 32,
      estimationCount: 8,
      description: 'Complete renovation of aging shopping mall including structural repairs, facade update, and interior redesign.',
      location: 'Westside, Miami, FL',
      type: 'Commercial'
    },
    {
      id: '5',
      name: 'Elementary School Expansion',
      client: 'County School District',
      status: 'in-progress',
      progress: 40,
      startDate: '2025-01-05',
      endDate: '2025-07-25',
      budget: '$1,800,000',
      team: ['James Miller', 'Patricia White'],
      documentCount: 15,
      estimationCount: 2,
      description: 'Addition of new classrooms, cafeteria expansion, and playground renovation for growing elementary school.',
      location: 'North County, Portland, OR',
      type: 'Educational'
    },
    {
      id: '6',
      name: 'Industrial Warehouse',
      client: 'Logistics Solutions LLC',
      status: 'planning',
      progress: 15,
      startDate: '2025-03-15',
      endDate: '2025-10-30',
      budget: '$4,100,000',
      team: ['Richard Davis', 'Susan Martin', 'George Thompson'],
      documentCount: 9,
      estimationCount: 1,
      description: 'New construction of an industrial warehouse with advanced logistics systems, loading docks, and office space.',
      location: 'Industrial Park, Dallas, TX',
      type: 'Industrial'
    }
  ];
};

// Helper function to format date
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(date);
};

// Status badge component
const StatusBadge = ({ status }) => {
  const statusConfig = {
    'planning': { label: 'Planning', className: 'bg-blue-100 text-blue-800 hover:bg-blue-100' },
    'in-progress': { label: 'In Progress', className: 'bg-amber-100 text-amber-800 hover:bg-amber-100' },
    'pending-approval': { label: 'Pending Approval', className: 'bg-purple-100 text-purple-800 hover:bg-purple-100' },
    'completed': { label: 'Completed', className: 'bg-green-100 text-green-800 hover:bg-green-100' },
    'cancelled': { label: 'Cancelled', className: 'bg-red-100 text-red-800 hover:bg-red-100' }
  };

  const config = statusConfig[status] || { label: 'Unknown', className: 'bg-gray-100 text-gray-800' };

  return (
    <Badge variant="outline" className={config.className}>{config.label}</Badge>
  );
};

// Project creation form component
const ProjectCreationForm = ({ onSuccess }) => {
  const [formData, setFormData] = useState({
    name: '',
    client: '',
    type: '',
    description: '',
    location: '',
    startDate: '',
    endDate: '',
    budget: '',
  });

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Simulate API call
    setTimeout(() => {
      console.log('Project created:', formData);
      if (onSuccess) onSuccess();
    }, 1000);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="project-name">Project Name *</Label>
          <Input
            id="project-name"
            value={formData.name}
            onChange={(e) => handleChange('name', e.target.value)}
            placeholder="Enter project name"
            required
          />
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="project-client">Client Name *</Label>
          <Input
            id="project-client"
            value={formData.client}
            onChange={(e) => handleChange('client', e.target.value)}
            placeholder="Enter client name"
            required
          />
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="project-type">Project Type *</Label>
          <Select
            value={formData.type}
            onValueChange={(value) => handleChange('type', value)}
            required
          >
            <SelectTrigger id="project-type">
              <SelectValue placeholder="Select project type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="commercial">Commercial</SelectItem>
              <SelectItem value="residential">Residential</SelectItem>
              <SelectItem value="industrial">Industrial</SelectItem>
              <SelectItem value="educational">Educational</SelectItem>
              <SelectItem value="healthcare">Healthcare</SelectItem>
              <SelectItem value="mixed-use">Mixed-Use</SelectItem>
              <SelectItem value="infrastructure">Infrastructure</SelectItem>
              <SelectItem value="other">Other</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="project-location">Location</Label>
          <Input
            id="project-location"
            value={formData.location}
            onChange={(e) => handleChange('location', e.target.value)}
            placeholder="City, State"
          />
        </div>
      </div>
      
      <div className="space-y-2">
        <Label htmlFor="project-description">Project Description</Label>
        <Textarea
          id="project-description"
          value={formData.description}
          onChange={(e) => handleChange('description', e.target.value)}
          placeholder="Brief description of the project"
          rows={3}
        />
      </div>
      
      <div className="grid grid-cols-3 gap-4">
        <div className="space-y-2">
          <Label htmlFor="project-start-date">Start Date</Label>
          <Input
            id="project-start-date"
            type="date"
            value={formData.startDate}
            onChange={(e) => handleChange('startDate', e.target.value)}
          />
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="project-end-date">End Date</Label>
          <Input
            id="project-end-date"
            type="date"
            value={formData.endDate}
            onChange={(e) => handleChange('endDate', e.target.value)}
          />
        </div>
        
        <div className="space-y-2">
          <Label htmlFor="project-budget">Estimated Budget</Label>
          <Input
            id="project-budget"
            value={formData.budget}
            onChange={(e) => handleChange('budget', e.target.value)}
            placeholder="$0.00"
          />
        </div>
      </div>
      
      <div className="flex justify-end space-x-4 pt-4">
        <Button type="button" variant="outline">
          Cancel
        </Button>
        <Button type="submit">
          Create Project
        </Button>
      </div>
    </form>
  );
};

const Projects = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortField, setSortField] = useState('name');
  const [sortDirection, setSortDirection] = useState('asc');
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  
  // Fetch projects
  const { data: projects = [], isLoading, error } = useQuery({
    queryKey: ['projects'],
    queryFn: fetchProjects
  });

  // Filter projects based on search query
  const filteredProjects = projects.filter(project => 
    project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    project.client.toLowerCase().includes(searchQuery.toLowerCase()) ||
    project.type.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Sort projects
  const sortedProjects = [...filteredProjects].sort((a, b) => {
    const aValue = a[sortField];
    const bValue = b[sortField];
    
    const comparison = typeof aValue === 'string'
      ? aValue.localeCompare(bValue)
      : aValue - bValue;
    
    return sortDirection === 'asc' ? comparison : -comparison;
  });

  // Handle sort click
  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  // Handle project creation success
  const handleCreateSuccess = () => {
    setCreateDialogOpen(false);
    // Optionally refetch projects here
  };

  const renderSortIcon = (field) => {
    if (sortField !== field) return null;
    
    return sortDirection === 'asc'
      ? <ChevronUp className="ml-1 h-4 w-4" />
      : <ChevronDown className="ml-1 h-4 w-4" />;
  };

  return (
    <div className="container mx-auto p-6">
      <div className="flex flex-col space-y-4">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold">Projects</h1>
          <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                New Project
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[600px]">
              <DialogHeader>
                <DialogTitle>Create New Project</DialogTitle>
                <DialogDescription>
                  Enter the details for your new construction project.
                </DialogDescription>
              </DialogHeader>
              <ScrollArea className="max-h-[60vh]">
                <ProjectCreationForm onSuccess={handleCreateSuccess} />
              </ScrollArea>
            </DialogContent>
          </Dialog>
        </div>

        <div className="flex justify-between items-center space-x-4">
          <div className="relative flex-1">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search projects..."
              className="pl-8"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="icon">
              <Filter className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <Tabs defaultValue="all">
          <TabsList>
            <TabsTrigger value="all">All Projects</TabsTrigger>
            <TabsTrigger value="active">Active</TabsTrigger>
            <TabsTrigger value="planning">Planning</TabsTrigger>
            <TabsTrigger value="completed">Completed</TabsTrigger>
          </TabsList>
          
          <TabsContent value="all" className="mt-4">
            {isLoading ? (
              <div className="flex justify-center items-center h-64">
                <p>Loading projects...</p>
              </div>
            ) : error ? (
              <div className="flex justify-center items-center h-64">
                <p className="text-red-500">Error loading projects</p>
              </div>
            ) : sortedProjects.length === 0 ? (
              <div className="flex justify-center items-center h-64">
                <p>No projects found</p>
              </div>
            ) : (
              <div className="border rounded-md">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-[300px] cursor-pointer" onClick={() => handleSort('name')}>
                        <div className="flex items-center">
                          Project Name {renderSortIcon('name')}
                        </div>
                      </TableHead>
                      <TableHead className="cursor-pointer" onClick={() => handleSort('client')}>
                        <div className="flex items-center">
                          Client {renderSortIcon('client')}
                        </div>
                      </TableHead>
                      <TableHead className="cursor-pointer" onClick={() => handleSort('status')}>
                        <div className="flex items-center">
                          Status {renderSortIcon('status')}
                        </div>
                      </TableHead>
                      <TableHead className="cursor-pointer" onClick={() => handleSort('progress')}>
                        <div className="flex items-center">
                          Progress {renderSortIcon('progress')}
                        </div>
                      </TableHead>
                      <TableHead className="cursor-pointer" onClick={() => handleSort('startDate')}>
                        <div className="flex items-center">
                          Timeline {renderSortIcon('startDate')}
                        </div>
                      </TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {sortedProjects.map((project) => (
                      <TableRow key={project.id}>
                        <TableCell className="font-medium">
                          <Link to={`/projects/${project.id}`} className="hover:underline">
                            {project.name}
                          </Link>
                          <div className="text-xs text-muted-foreground mt-1">
                            {project.type}
                          </div>
                        </TableCell>
                        <TableCell>{project.client}</TableCell>
                        <TableCell>
                          <StatusBadge status={project.status} />
                        </TableCell>
                        <TableCell>
                          <div className="w-full flex items-center space-x-2">
                            <Progress value={project.progress} className="h-2 flex-1" />
                            <span className="text-xs font-medium w-8 text-right">{project.progress}%</span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center text-sm">
                            <CalendarDays className="mr-1 h-4 w-4 text-muted-foreground" />
                            <span>{formatDate(project.startDate)} - {formatDate(project.endDate)}</span>
                          </div>
                        </TableCell>
                        <TableCell className="text-right">
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="icon">
                                <MoreVertical className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuItem asChild>
                                <Link to={`/projects/${project.id}`}>
                                  View Details
                                </Link>
                              </DropdownMenuItem>
                              <DropdownMenuItem>Edit Project</DropdownMenuItem>
                              <DropdownMenuItem>Upload Documents</DropdownMenuItem>
                              <DropdownMenuItem>Create Estimation</DropdownMenuItem>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem className="text-red-600">
                                Archive Project
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </TabsContent>
          
          {/* Other tab contents would follow similar structure */}
          <TabsContent value="active" className="mt-4">
            <p className="text-center py-4">Active projects view</p>
          </TabsContent>
          <TabsContent value="planning" className="mt-4">
            <p className="text-center py-4">Planning projects view</p>
          </TabsContent>
          <TabsContent value="completed" className="mt-4">
            <p className="text-center py-4">Completed projects view</p>
          </TabsContent>
        </Tabs>

        <div className="mt-6">
          <h2 className="text-xl font-bold mb-4">Recent Projects</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sortedProjects.slice(0, 3).map((project) => (
              <Card key={project.id}>
                <CardHeader className="pb-2">
                  <div className="flex justify-between items-start">
                    <CardTitle className="text-lg">{project.name}</CardTitle>
                    <StatusBadge status={project.status} />
                  </div>
                  <CardDescription>{project.client}</CardDescription>
                </CardHeader>
                <CardContent className="pb-2">
                  <div className="space-y-2">
                    <p className="text-sm">{project.description}</p>
                    <div className="flex items-center justify-between text-sm text-muted-foreground">
                      <div className="flex items-center">
                        <Building className="mr-1 h-4 w-4" />
                        <span>{project.type}</span>
                      </div>
                      <div>${project.budget}</div>
                    </div>
                    <div className="pt-2">
                      <div className="text-xs mb-1 flex justify-between">
                        <span>Progress</span>
                        <span>{project.progress}%</span>
                      </div>
                      <Progress value={project.progress} className="h-2" />
                    </div>
                  </div>
                </CardContent>
                <CardFooter className="flex justify-between pt-2">
                  <div className="flex items-center text-sm text-muted-foreground">
                    <FileText className="mr-1 h-4 w-4" />
                    <span>{project.documentCount} docs</span>
                  </div>
                  <div className="flex items-center text-sm text-muted-foreground">
                    <Users className="mr-1 h-4 w-4" />
                    <span>{project.team.length} members</span>
                  </div>
                  <Button variant="ghost" size="sm" asChild>
                    <Link to={`/projects/${project.id}`}>
                      View
                    </Link>
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Projects;