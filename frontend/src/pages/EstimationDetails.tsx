import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  ChevronLeft, 
  Building, 
  Calendar, 
  DollarSign, 
  FileText, 
  BarChart, 
  Edit, 
  Download, 
  Printer, 
  Share2, 
  MoreHorizontal,
  Plus,
  Trash2,
  CheckCircle,
  XCircle
} from 'lucide-react';

// UI Components
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
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
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';

// Mock service (replace with actual service later)
const fetchEstimationDetails = async (estimationId: string) => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Mock data
  return {
    id: estimationId,
    name: 'Office Building Renovation - Revised Structural',
    projectId: '1',
    projectName: 'Office Building Renovation',
    client: 'ABC Corporation',
    createdAt: '2025-02-08T13:45:00Z',
    modifiedAt: '2025-02-10T09:15:00Z',
    createdBy: 'Alex Johnson',
    approvedBy: 'John Doe',
    approvedAt: '2025-02-12T14:30:00Z',
    totalEstimate: '$455,000',
    previousEstimate: '$420,000',
    status: 'approved',
    description: 'Revised estimation with updated structural costs due to additional reinforcement requirements identified during initial site inspection.',
    notes: [
      { id: '1', author: 'Alex Johnson', content: 'Updated the structural costs based on engineer's report.', createdAt: '2025-02-09T10:15:00Z' },
      { id: '2', author: 'John Doe', content: 'Reviewed and approved the revisions. Please notify the client about the budget increase.', createdAt: '2025-02-12T14:25:00Z' }
    ],
    categories: [
      { 
        name: 'Structural',
        amount: '$145,000',
        previousAmount: '$120,000',
        items: [
          { id: '1', name: 'Steel Beams', quantity: '25 tons', unitCost: '$2,800/ton', total: '$70,000' },
          { id: '2', name: 'Concrete Reinforcement', quantity: '850 cubic yards', unitCost: '$65/cubic yard', total: '$55,250' },
          { id: '3', name: 'Structural Engineering', quantity: '1 service', unitCost: '$19,750', total: '$19,750' }
        ]
      },
      { 
        name: 'Electrical',
        amount: '$90,000',
        previousAmount: '$85,000',
        items: [
          { id: '1', name: 'Wiring', quantity: '8,500 linear ft', unitCost: '$3.50/ft', total: '$29,750' },
          { id: '2', name: 'Electrical Panels', quantity: '5 units', unitCost: '$4,500/unit', total: '$22,500' },
          { id: '3', name: 'Lighting Fixtures', quantity: '120 units', unitCost: '$180/unit', total: '$21,600' },
          { id: '4', name: 'Installation Labor', quantity: '320 hours', unitCost: '$50/hour', total: '$16,000' }
        ]
      },
      { 
        name: 'Plumbing',
        amount: '$70,000',
        previousAmount: '$65,000',
        items: [
          { id: '1', name: 'Pipes and Fittings', quantity: '1 lot', unitCost: '$32,000', total: '$32,000' },
          { id: '2', name: 'Fixtures', quantity: '25 units', unitCost: '$480/unit', total: '$12,000' },
          { id: '3', name: 'Installation Labor', quantity: '520 hours', unitCost: '$50/hour', total: '$26,000' }
        ]
      },
      { 
        name: 'Finishes',
        amount: '$110,000',
        previousAmount: '$110,000',
        items: [
          { id: '1', name: 'Drywall', quantity: '12,000 sqft', unitCost: '$2.25/sqft', total: '$27,000' },
          { id: '2', name: 'Paint', quantity: '15,000 sqft', unitCost: '$1.80/sqft', total: '$27,000' },
          { id: '3', name: 'Flooring', quantity: '8,000 sqft', unitCost: '$5.50/sqft', total: '$44,000' },
          { id: '4', name: 'Trim and Molding', quantity: '1,500 linear ft', unitCost: '$8/ft', total: '$12,000' }
        ]
      },
      { 
        name: 'Labor',
        amount: '$40,000',
        previousAmount: '$40,000',
        items: [
          { id: '1', name: 'Project Management', quantity: '300 hours', unitCost: '$75/hour', total: '$22,500' },
          { id: '2', name: 'General Labor', quantity: '700 hours', unitCost: '$25/hour', total: '$17,500' }
        ]
      }
    ],
    comparisonData: {
      categories: ['Structural', 'Electrical', 'Plumbing', 'Finishes', 'Labor'],
      current: [145000, 90000, 70000, 110000, 40000],
      previous: [120000, 85000, 65000, 110000, 40000]
    },
    documents: [
      { id: '1', name: 'Structural Engineer Report', type: 'PDF', createdAt: '2025-02-05T10:30:00Z' },
      { id: '2', name: 'Revised Floor Plans', type: 'CAD', createdAt: '2025-02-06T14:45:00Z' },
      { id: '3', name: 'Material Quotations', type: 'PDF', createdAt: '2025-02-07T09:15:00Z' }
    ]
  };
};

// Helper function to format date
const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: 'numeric'
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

// Calculate difference and display with color
const DisplayDifference = ({ current, previous }: { current: string, previous: string }) => {
  const currentValue = parseFloat(current.replace(/[^0-9.-]+/g, ''));
  const previousValue = parseFloat(previous.replace(/[^0-9.-]+/g, ''));
  const difference = currentValue - previousValue;
  const percentDiff = (difference / previousValue) * 100;
  
  if (difference === 0) return null;
  
  const formattedDiff = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(Math.abs(difference));
  
  const textColorClass = difference > 0
    ? 'text-red-600'
    : 'text-green-600';
  
  return (
    <span className={`ml-2 font-medium ${textColorClass}`}>
      {difference > 0 ? '+' : '-'}{formattedDiff} ({Math.abs(percentDiff).toFixed(1)}%)
    </span>
  );
};

// Approval dialog component
const ApprovalDialog = ({ onApprove, onReject }: { onApprove: () => void, onReject: () => void }) => {
  const [notes, setNotes] = useState('');
  
  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <label htmlFor="approval-notes" className="block text-sm font-medium">
          Approval Notes (Optional)
        </label>
        <textarea
          id="approval-notes"
          className="w-full min-h-[100px] p-2 border rounded-md"
          placeholder="Add any notes or comments about your decision..."
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
        />
      </div>
      
      <div className="flex justify-end space-x-2">
        <Button variant="outline" onClick={onReject}>
          <XCircle className="mr-2 h-4 w-4" />
          Reject
        </Button>
        <Button onClick={onApprove}>
          <CheckCircle className="mr-2 h-4 w-4" />
          Approve
        </Button>
      </div>
    </div>
  );
};

const EstimationDetails = () => {
  const { estimationId } = useParams<{ estimationId: string }>();
  const [approveDialogOpen, setApproveDialogOpen] = useState(false);
  
  // Fetch estimation details
  const { data: estimation, isLoading, error } = useQuery({
    queryKey: ['estimation', estimationId],
    queryFn: () => fetchEstimationDetails(estimationId || '')
  });

  // Handle approve/reject actions
  const handleApprove = () => {
    console.log('Estimation approved');
    setApproveDialogOpen(false);
    // Implement actual approval logic here
  };
  
  const handleReject = () => {
    console.log('Estimation rejected');
    setApproveDialogOpen(false);
    // Implement actual rejection logic here
  };

  if (isLoading) {
    return (
      <div className="container mx-auto p-6 flex justify-center items-center h-96">
        <p>Loading estimation details...</p>
      </div>
    );
  }

  if (error || !estimation) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center mb-4">
          <Button variant="ghost" size="sm" asChild>
            <Link to="/estimations">
              <ChevronLeft className="mr-2 h-4 w-4" />
              Back to Estimations
            </Link>
          </Button>
        </div>
        <div className="flex justify-center items-center h-96">
          <p className="text-red-500">Error loading estimation details</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <div className="flex items-center mb-6">
        <Button variant="ghost" size="sm" asChild>
          <Link to="/estimations">
            <ChevronLeft className="mr-2 h-4 w-4" />
            Back to Estimations
          </Link>
        </Button>
      </div>

      <div className="flex flex-col space-y-6">
        {/* Estimation Header */}
        <div className="flex justify-between items-start">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-3xl font-bold">{estimation.name}</h1>
              <StatusBadge status={estimation.status} />
            </div>
            <p className="text-muted-foreground mt-1">
              <Link to={`/projects/${estimation.projectId}`} className="hover:underline">
                {estimation.projectName}
              </Link>
              {' - '}
              {estimation.client}
            </p>
          </div>
          <div className="flex items-center space-x-2">
            {estimation.status === 'pending-approval' && (
              <Dialog open={approveDialogOpen} onOpenChange={setApproveDialogOpen}>
                <DialogTrigger asChild>
                  <Button>
                    <CheckCircle className="mr-2 h-4 w-4" />
                    Review
                  </Button>
                </DialogTrigger>
                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Review Estimation</DialogTitle>
                    <DialogDescription>
                      Approve or reject this estimation. This action cannot be undone.
                    </DialogDescription>
                  </DialogHeader>
                  <ApprovalDialog onApprove={handleApprove} onReject={handleReject} />
                </DialogContent>
              </Dialog>
            )}
            
            <Button variant="outline">
              <Edit className="mr-2 h-4 w-4" />
              Edit
            </Button>
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline">
                  <MoreHorizontal className="mr-2 h-4 w-4" />
                  Actions
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent>
                <DropdownMenuItem>
                  <Download className="mr-2 h-4 w-4" />
                  Download PDF
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Printer className="mr-2 h-4 w-4" />
                  Print
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Share2 className="mr-2 h-4 w-4" />
                  Share
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem className="text-red-600">
                  <Trash2 className="mr-2 h-4 w-4" />
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        {/* Estimation Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle>Estimation Overview</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {estimation.description && (
                <div className="mb-4">
                  <p>{estimation.description}</p>
                </div>
              )}
              
              <div className="grid grid-cols-2 gap-4 pt-2">
                <div className="flex items-start">
                  <Building className="h-5 w-5 text-muted-foreground mr-2 mt-0.5" />
                  <div>
                    <p className="text-sm text-muted-foreground">Project</p>
                    <p className="font-medium">
                      <Link to={`/projects/${estimation.projectId}`} className="hover:underline">
                        {estimation.projectName}
                      </Link>
                    </p>
                  </div>
                </div>
                <div className="flex items-start">
                  <Calendar className="h-5 w-5 text-muted-foreground mr-2 mt-0.5" />
                  <div>
                    <p className="text-sm text-muted-foreground">Created</p>
                    <p className="font-medium">{formatDate(estimation.createdAt)}</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <FileText className="h-5 w-5 text-muted-foreground mr-2 mt-0.5" />
                  <div>
                    <p className="text-sm text-muted-foreground">Status</p>
                    <p className="font-medium">
                      <StatusBadge status={estimation.status} />
                    </p>
                  </div>
                </div>
                <div className="flex items-start">
                  <DollarSign className="h-5 w-5 text-muted-foreground mr-2 mt-0.5" />
                  <div>
                    <p className="text-sm text-muted-foreground">Total Estimate</p>
                    <div className="font-medium flex items-center">
                      <span>{estimation.totalEstimate}</span>
                      {estimation.previousEstimate && (
                        <DisplayDifference 
                          current={estimation.totalEstimate} 
                          previous={estimation.previousEstimate} 
                        />
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Estimation Details</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-start">
                  <div className="text-sm text-muted-foreground w-32">Created By</div>
                  <div className="font-medium">{estimation.createdBy}</div>
                </div>
                
                {estimation.status === 'approved' && estimation.approvedBy && (
                  <>
                    <div className="flex items-start">
                      <div className="text-sm text-muted-foreground w-32">Approved By</div>
                      <div className="font-medium">{estimation.approvedBy}</div>
                    </div>
                    <div className="flex items-start">
                      <div className="text-sm text-muted-foreground w-32">Approved On</div>
                      <div className="font-medium">{formatDate(estimation.approvedAt!)}</div>
                    </div>
                  </>
                )}
                
                <div className="flex items-start">
                  <div className="text-sm text-muted-foreground w-32">Last Modified</div>
                  <div className="font-medium">{formatDate(estimation.modifiedAt)}</div>
                </div>
                
                <Separator />
                
                <div className="flex items-start">
                  <div className="text-sm text-muted-foreground w-32">Documents</div>
                  <div className="space-y-1">
                    {estimation.documents.map((doc) => (
                      <Link to={`/documents/${doc.id}`} key={doc.id} className="block hover:underline">
                        <FileText className="inline-block mr-1 h-4 w-4" />
                        {doc.name}
                      </Link>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Estimation Details Tabs */}
        <Tabs defaultValue="summary" className="pt-2">
          <TabsList className="grid grid-cols-3 w-full">
            <TabsTrigger value="summary">Summary</TabsTrigger>
            <TabsTrigger value="lineItems">Line Items</TabsTrigger>
            <TabsTrigger value="notes">Notes</TabsTrigger>
          </TabsList>
          
          <TabsContent value="summary" className="mt-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Estimation Summary</h2>
              <Button variant="outline">
                <BarChart className="mr-2 h-4 w-4" />
                View Chart
              </Button>
            </div>
            
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Category</TableHead>
                  <TableHead className="text-right">Current Amount</TableHead>
                  {estimation.previousEstimate && (
                    <>
                      <TableHead className="text-right">Previous Amount</TableHead>
                      <TableHead className="text-right">Difference</TableHead>
                    </>
                  )}
                </TableRow>
              </TableHeader>
              <TableBody>
                {estimation.categories.map((category) => (
                  <TableRow key={category.name}>
                    <TableCell className="font-medium">{category.name}</TableCell>
                    <TableCell className="text-right">{category.amount}</TableCell>
                    {estimation.previousEstimate && (
                      <>
                        <TableCell className="text-right">{category.previousAmount}</TableCell>
                        <TableCell className="text-right">
                          <DisplayDifference 
                            current={category.amount} 
                            previous={category.previousAmount} 
                          />
                        </TableCell>
                      </>
                    )}
                  </TableRow>
                ))}
                <TableRow className="bg-muted/50 font-bold">
                  <TableCell>TOTAL</TableCell>
                  <TableCell className="text-right">{estimation.totalEstimate}</TableCell>
                  {estimation.previousEstimate && (
                    <>
                      <TableCell className="text-right">{estimation.previousEstimate}</TableCell>
                      <TableCell className="text-right">
                        <DisplayDifference 
                          current={estimation.totalEstimate} 
                          previous={estimation.previousEstimate} 
                        />
                      </TableCell>
                    </>
                  )}
                </TableRow>
              </TableBody>
            </Table>
          </TabsContent>
          
          <TabsContent value="lineItems" className="mt-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Line Items</h2>
              <Button variant="outline">
                <Download className="mr-2 h-4 w-4" />
                Export CSV
              </Button>
            </div>
            
            <div className="space-y-6">
              {estimation.categories.map((category) => (
                <Card key={category.name}>
                  <CardHeader className="py-4">
                    <div className="flex justify-between items-center">
                      <CardTitle className="text-lg">{category.name}</CardTitle>
                      <div className="flex items-center">
                        <span className="font-bold">{category.amount}</span>
                        {category.previousAmount && (
                          <DisplayDifference 
                            current={category.amount} 
                            previous={category.previousAmount}
                          />
                        )}
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="p-0">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Item</TableHead>
                          <TableHead>Quantity</TableHead>
                          <TableHead>Unit Cost</TableHead>
                          <TableHead className="text-right">Total</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {category.items.map((item) => (
                          <TableRow key={item.id}>
                            <TableCell className="font-medium">{item.name}</TableCell>
                            <TableCell>{item.quantity}</TableCell>
                            <TableCell>{item.unitCost}</TableCell>
                            <TableCell className="text-right">{item.total}</TableCell>
                          </TableRow>
                        ))}
                        <TableRow className="bg-muted/20">
                          <TableCell colSpan={3} className="font-medium">Subtotal</TableCell>
                          <TableCell className="text-right font-bold">{category.amount}</TableCell>
                        </TableRow>
                      </TableBody>
                    </Table>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
          
          <TabsContent value="notes" className="mt-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Notes & Comments</h2>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Add Note
              </Button>
            </div>
            
            <div className="space-y-4">
              {estimation.notes.map((note) => (
                <Card key={note.id}>
                  <CardHeader className="py-3">
                    <div className="flex justify-between items-center">
                      <CardTitle className="text-base font-medium">{note.author}</CardTitle>
                      <CardDescription>{formatDate(note.createdAt)}</CardDescription>
                    </div>
                  </CardHeader>
                  <CardContent className="py-0">
                    <p>{note.content}</p>
                  </CardContent>
                </Card>
              ))}
              
              {estimation.notes.length === 0 && (
                <div className="flex justify-center items-center py-12 bg-muted/20 rounded-lg">
                  <p className="text-muted-foreground">No notes have been added to this estimation.</p>
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default EstimationDetails;