import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  Search, 
  Plus, 
  FileSpreadsheet, 
  Filter, 
  Building, 
  Calendar, 
  DollarSign,
  ChevronUp,
  ChevronDown,
  Clock,
  BarChart,
  MoreVertical
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
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

// Mock service (replace with actual service when available)
const fetchEstimations = async () => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Mock data
  return [
    {
      id: '1',
      name: 'Office Building Renovation - Initial',
      projectId: '1',
      projectName: 'Office Building Renovation',
      client: 'ABC Corporation',
      createdAt: '2025-01-22T09:30:00Z',
      modifiedAt: '2025-01-22T14:45:00Z',
      totalEstimate: '$420,000',
      status: 'approved',
      categories: [
        { name: 'Structural', amount: '$120,000' },
        { name: 'Electrical', amount: '$85,000' },
        { name: 'Plumbing', amount: '$65,000' },
        { name: 'Finishes', amount: '$110,000' },
        { name: 'Labor', amount: '$40,000' }
      ]
    },
    {
      id: '2',
      name: 'Office Building Renovation - Revised Structural',
      projectId: '1',
      projectName: 'Office Building Renovation',
      client: 'ABC Corporation',
      createdAt: '2025-02-08T13:45:00Z',
      modifiedAt: '2025-02-10T09:15:00Z',
      totalEstimate: '$455,000',
      status: 'approved',
      categories: [
        { name: 'Structural', amount: '$145,000' },
        { name: 'Electrical', amount: '$90,000' },
        { name: 'Plumbing', amount: '$70,000' },
        { name: 'Finishes', amount: '$110,000' },
        { name: 'Labor', amount: '$40,000' }
      ]
    },
    {
      id: '3',
      name: 'Office Building Renovation - MEP Systems Update',
      projectId: '1',
      projectName: 'Office Building Renovation',
      client: 'ABC Corporation',
      createdAt: '2025-02-15T10:15:00Z',
      modifiedAt: '2025-02-16T11:30:00Z',
      totalEstimate: '$450,000',
      status: 'pending',
      categories: [
        { name: 'Structural', amount: '$145,000' },
        { name: 'Electrical', amount: '$85,000' },
        { name: 'Plumbing', amount: '$65,000' },
        { name: 'Finishes', amount: '$115,000' },
        { name: 'Labor', amount: '$40,000' }
      ]
    },
    {
      id: '4',
      name: 'Office Building Renovation - Interior Finishes',
      projectId: '1',
      projectName: 'Office Building Renovation',
      client: 'ABC Corporation',
      createdAt: '2025-03-01T14:20:00Z',
      modifiedAt: '2025-03-01T16:45:00Z',
      totalEstimate: '$448,500',
      status: 'draft',
      categories: [
        { name: 'Structural', amount: '$145,000' },
        { name: 'Electrical', amount: '$85,000' },
        { name: 'Plumbing', amount: '$65,000' },
        { name: 'Finishes', amount: '$113,500' },
        { name: 'Labor', amount: '$40,000' }
      ]
    },
    {
      id: '5',
      name: 'Residential Complex - Initial Estimate',
      projectId: '2',
      projectName: 'Residential Complex',
      client: 'XYZ Developers',
      createdAt: '2025-02-12T11:20:00Z',
      modifiedAt: '2025-02-14T16:10:00Z',
      totalEstimate: '$2,450,000',
      status: 'approved',
      categories: [
        { name: 'Foundation', amount: '$420,000' },
        { name: 'Structural', amount: '$780,000' },
        { name: 'Electrical', amount: '$320,000' },
        { name: 'Plumbing', amount: '$280,000' },
        { name: 'Finishes', amount: '$460,000' },
        { name: 'Exterior', amount: '$190,000' }
      ]
    },
    {
      id: '6',
      name: 'Hospital Wing Addition - Preliminary',
      projectId: '3',
      projectName: 'Hospital Wing Addition',
      client: 'City Medical Center',
      createdAt: '2025-02-01T09:45:00Z',
      modifiedAt: '2025-02-05T14:30:00Z',
      totalEstimate: '$5,750,000',
      status: 'pending-approval',
      categories: [
        { name: 'Foundation', amount: '$820,000' },
        { name: 'Structural', amount: '$1,350,000' },
        { name: 'Electrical', amount: '$950,000' },
        { name: 'Plumbing', amount: '$780,000' },
        { name: 'Medical Systems', amount: '$1,200,000' },
        { name: 'Finishes', amount: '$650,000' }
      ]
    }
  ];
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
    'draft': { label: 'Draft', className: 'bg-blue-100 text-blue-800 hover:bg-blue-100' },
    'pending': { label: 'Pending', className: 'bg-amber-100 text-amber-800 hover:bg-amber-100' },
    'pending-approval': { label: 'Pending Approval', className: 'bg-purple-100 text-purple-800 hover:bg-purple-100' },
    'approved': { label: 'Approved', className: 'bg-green-100 text-green-800 hover:bg-green-100' },
    'rejected': { label: 'Rejected', className: 'bg-red-100 text-red-800 hover:bg-red-100' }
  };

  const config = statusConfig[status] || { label: 'Unknown', className: 'bg-gray-100 text-gray-800' };

  return (
    <Badge variant="outline" className={config.className}>{config.label}</Badge>
  );
};

// Estimation creation form component
const EstimationCreationForm = ({ onSuccess }: { onSuccess?: () => void }) => {
  const [formData, setFormData] = useState({
    name: '',
    projectId: '',
    estimationType: 'manual',
    description: '',
  });

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Simulate API call
    setTimeout(() => {
      console.log('Estimation created:', formData);
      if (onSuccess) onSuccess();
    }, 1000);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="estimation-name">Estimation Name *</Label>
        <Input
          id="estimation-name"
          value={formData.name}
          onChange={(e) => handleChange('name', e.target.value)}
          placeholder="Enter estimation name"
          required
        />
      </div>
      
      <div className="space-y-2">
        <Label htmlFor="project-select">Project *</Label>
        <Select
          value={formData.projectId}
          onValueChange={(value) => handleChange('projectId', value)}
          required
        >
          <SelectTrigger id="project-select">
            <SelectValue placeholder="Select project" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="1">Office Building Renovation</SelectItem>
            <SelectItem value="2">Residential Complex</SelectItem>
            <SelectItem value="3">Hospital Wing Addition</SelectItem>
            <SelectItem value="4">Shopping Mall Renovation</SelectItem>
            <SelectItem value="5">Elementary School Expansion</SelectItem>
          </SelectContent>
        </Select>
      </div>
      
      <div className="space-y-2">
        <Label>Estimation Type</Label>
        <RadioGroup
          value={formData.estimationType}
          onValueChange={(value) => handleChange('estimationType', value)}
          className="flex flex-col space-y-1"
        >
          <div className="flex items-start space-x-2">
            <RadioGroupItem value="ai" id="estimation-ai" />
            <div>
              <Label htmlFor="estimation-ai" className="font-medium">AI-Generated Estimation</Label>
              <p className="text-sm text-muted-foreground">
                Create an estimation based on AI analysis of project documents
              </p>
            </div>
          </div>
          <div className="flex items-start space-x-2">
            <RadioGroupItem value="manual" id="estimation-manual" />
            <div>
              <Label htmlFor="estimation-manual" className="font-medium">Manual Estimation</Label>
              <p className="text-sm text-muted-foreground">
                Create an estimation manually with custom categories and line items
              </p>
            </div>
          </div>
          <div className="flex items-start space-x-2">
            <RadioGroupItem value="template" id="estimation-template" />
            <div>
              <Label htmlFor="estimation-template" className="font-medium">Template-Based</Label>
              <p className="text-sm text-muted-foreground">
                Create an estimation based on a predefined template
              </p>
            </div>
          </div>
        </RadioGroup>
      </div>
      
      <div className="flex justify-end space-x-4 pt-4">
        <Button type="button" variant="outline">
          Cancel
        </Button>
        <Button type="submit">
          Create Estimation
        </Button>
      </div>
    </form>
  );
};

const Estimations = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortField, setSortField] = useState('createdAt');
  const [sortDirection, setSortDirection] = useState('desc');
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  
  // Fetch estimations
  const { data: estimations = [], isLoading, error } = useQuery({
    queryKey: ['estimations'],
    queryFn: fetchEstimations
  });

  // Filter estimations based on search query
  const filteredEstimations = estimations.filter(estimation => 
    estimation.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    estimation.projectName.toLowerCase().includes(searchQuery.toLowerCase()) ||
    estimation.client.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Sort estimations
  const sortedEstimations = [...filteredEstimations].sort((a, b) => {
    let aValue = a[sortField as keyof typeof a];
    let bValue = b[sortField as keyof typeof b];
    
    // Handle string values that represent numbers (like totalEstimate)
    if (sortField === 'totalEstimate') {
      aValue = parseFloat((aValue as string).replace(/[^0-9.-]+/g, ''));
      bValue = parseFloat((bValue as string).replace(/[^0-9.-]+/g, ''));
    }
    
    const comparison = typeof aValue === 'string'
      ? (aValue as string).localeCompare(bValue as string)
      : (aValue as number) - (bValue as number);
    
    return sortDirection === 'asc' ? comparison : -comparison;
  });

  // Handle sort click
  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  // Handle estimation creation success
  const handleCreateSuccess = () => {
    setCreateDialogOpen(false);
    // Optionally refetch estimations here
  };

  const renderSortIcon = (field: string) => {
    if (sortField !== field) return null;
    
    return sortDirection === 'asc'
      ? <ChevronUp className="ml-1 h-4 w-4" />
      : <ChevronDown className="ml-1 h-4 w-4" />;
  };

  return (
    <div className="container mx-auto p-6">
      <div className="flex flex-col space-y-4">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold">Estimations</h1>
          <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                New Estimation
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Estimation</DialogTitle>
                <DialogDescription>
                  Create a new cost estimation for your construction project.
                </DialogDescription>
              </DialogHeader>
              <ScrollArea className="max-h-[60vh]">
                <EstimationCreationForm onSuccess={handleCreateSuccess} />
              </ScrollArea>
            </DialogContent>
          </Dialog>
        </div>

        <div className="flex justify-between items-center space-x-4">
          <div className="relative flex-1">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search estimations..."
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
            <TabsTrigger value="all">All Estimations</TabsTrigger>
            <TabsTrigger value="draft">Drafts</TabsTrigger>
            <TabsTrigger value="pending">Pending</TabsTrigger>
            <TabsTrigger value="approved">Approved</TabsTrigger>
          </TabsList>
          
          <TabsContent value="all" className="mt-4">
            {isLoading ? (
              <div className="flex justify-center items-center h-64">
                <p>Loading estimations...</p>
              </div>
            ) : error ? (
              <div className="flex justify-center items-center h-64">
                <p className="text-red-500">Error loading estimations</p>
              </div>
            ) : sortedEstimations.length === 0 ? (
              <div className="flex justify-center items-center h-64">
                <p>No estimations found</p>
              </div>
            ) : (
              <div className="border rounded-md">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-[300px] cursor-pointer" onClick={() => handleSort('name')}>
                        <div className="flex items-center">
                          Estimation Name {renderSortIcon('name')}
                        </div>
                      </TableHead>
                      <TableHead className="cursor-pointer" onClick={() => handleSort('projectName')}>
                        <div className="flex items-center">
                          Project {renderSortIcon('projectName')}
                        </div>
                      </TableHead>
                      <TableHead className="cursor-pointer" onClick={() => handleSort('client')}>
                        <div className="flex items-center">
                          Client {renderSortIcon('client')}
                        </div>
                      </TableHead>
                      <TableHead className="cursor-pointer" onClick={() => handleSort('createdAt')}>
                        <div className="flex items-center">
                          Created {renderSortIcon('createdAt')}
                        </div>
                      </TableHead>
                      <TableHead className="cursor-pointer" onClick={() => handleSort('totalEstimate')}>
                        <div className="flex items-center">
                          Total {renderSortIcon('totalEstimate')}
                        </div>
                      </TableHead>
                      <TableHead className="cursor-pointer" onClick={() => handleSort('status')}>
                        <div className="flex items-center">
                          Status {renderSortIcon('status')}
                        </div>
                      </TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {sortedEstimations.map((estimation) => (
                      <TableRow key={estimation.id}>
                        <TableCell className="font-medium">
                          <Link to={`/estimations/${estimation.id}`} className="hover:underline">
                            {estimation.name}
                          </Link>
                        </TableCell>
                        <TableCell>
                          <Link to={`/projects/${estimation.projectId}`} className="hover:underline">
                            {estimation.projectName}
                          </Link>
                        </TableCell>
                        <TableCell>{estimation.client}</TableCell>
                        <TableCell>{formatDate(estimation.createdAt)}</TableCell>
                        <TableCell className="font-medium">{estimation.totalEstimate}</TableCell>
                        <TableCell>
                          <StatusBadge status={estimation.status} />
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
                                <Link to={`/estimations/${estimation.id}`}>
                                  View Details
                                </Link>
                              </DropdownMenuItem>
                              <DropdownMenuItem>Edit Estimation</DropdownMenuItem>
                              <DropdownMenuItem>Export as PDF</DropdownMenuItem>
                              <DropdownMenuItem>Share with Client</DropdownMenuItem>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem className="text-red-600">
                                Delete Estimation
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
          <TabsContent value="draft" className="mt-4">
            <p className="text-center py-4">Draft estimations view</p>
          </TabsContent>
          <TabsContent value="pending" className="mt-4">
            <p className="text-center py-4">Pending estimations view</p>
          </TabsContent>
          <TabsContent value="approved" className="mt-4">
            <p className="text-center py-4">Approved estimations view</p>
          </TabsContent>
        </Tabs>

        <div className="mt-6">
          <h2 className="text-xl font-bold mb-4">Recent Estimations</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sortedEstimations.slice(0, 3).map((estimation) => (
              <Card key={estimation.id}>
                <CardHeader className="pb-2">
                  <div className="flex justify-between items-start">
                    <CardTitle className="text-lg">{estimation.name}</CardTitle>
                    <StatusBadge status={estimation.status} />
                  </div>
                  <CardDescription>
                    {estimation.projectName} - {estimation.client}
                  </CardDescription>
                </CardHeader>
                <CardContent className="pb-2">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <Building className="mr-1 h-4 w-4 text-muted-foreground" />
                        <span className="text-sm">{estimation.projectName}</span>
                      </div>
                      <div className="text-sm">
                        <Calendar className="inline h-4 w-4 mr-1 mb-1 text-muted-foreground" />
                        {formatDate(estimation.createdAt)}
                      </div>
                    </div>
                    
                    <div className="pt-1">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-muted-foreground">Total Estimation</span>
                        <span className="font-bold">{estimation.totalEstimate}</span>
                      </div>
                    </div>
                    
                    <div className="space-y-1 pt-1">
                      <p className="text-sm text-muted-foreground">Top Categories</p>
                      {estimation.categories.slice(0, 3).map((category, index) => (
                        <div key={index} className="flex justify-between text-sm">
                          <span>{category.name}</span>
                          <span>{category.amount}</span>
                        </div>
                      ))}
                      {estimation.categories.length > 3 && (
                        <p className="text-xs text-muted-foreground text-right">
                          +{estimation.categories.length - 3} more categories
                        </p>
                      )}
                    </div>
                  </div>
                </CardContent>
                <CardFooter className="flex justify-between pt-2">
                  <div className="flex items-center text-sm text-muted-foreground">
                    <Clock className="mr-1 h-4 w-4" />
                    <span>Last updated: {formatDate(estimation.modifiedAt)}</span>
                  </div>
                  <Button variant="ghost" size="sm" asChild>
                    <Link to={`/estimations/${estimation.id}`}>
                      <BarChart className="h-4 w-4 mr-2" />
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

export default Estimations;