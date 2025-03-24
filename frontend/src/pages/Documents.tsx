import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  LayoutGrid, 
  List, 
  Search, 
  Filter, 
  Plus, 
  FileText, 
  Clock, 
  MoreVertical,
  Trash2,
  Download,
  Share2,
  Eye
} from 'lucide-react';

// Components
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
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
import DocumentUploadForm from '@/components/documents/DocumentUploadForm';

// Mock service (replace with actual service when available)
const fetchDocuments = async () => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1000));

  // Mock data
  return [
    {
      id: '1',
      name: 'Office Building Floor Plan',
      type: 'PDF',
      uploadedAt: '2025-03-20T14:30:00Z',
      size: '4.2 MB',
      status: 'processed',
      thumbnailUrl: 'https://via.placeholder.com/300x200?text=Floor+Plan'
    },
    {
      id: '2',
      name: 'Residential Blueprint',
      type: 'CAD',
      uploadedAt: '2025-03-18T09:15:00Z',
      size: '8.7 MB',
      status: 'processing',
      thumbnailUrl: 'https://via.placeholder.com/300x200?text=Blueprint'
    },
    {
      id: '3',
      name: 'Kitchen Renovation Details',
      type: 'PDF',
      uploadedAt: '2025-03-15T11:20:00Z',
      size: '2.1 MB',
      status: 'processed',
      thumbnailUrl: 'https://via.placeholder.com/300x200?text=Kitchen'
    },
    {
      id: '4',
      name: 'Commercial Space MEP Plan',
      type: 'BIM',
      uploadedAt: '2025-03-12T16:45:00Z',
      size: '12.5 MB',
      status: 'processed',
      thumbnailUrl: 'https://via.placeholder.com/300x200?text=MEP'
    },
    {
      id: '5',
      name: 'Site Survey',
      type: 'PDF',
      uploadedAt: '2025-03-10T13:00:00Z',
      size: '3.8 MB',
      status: 'processed',
      thumbnailUrl: 'https://via.placeholder.com/300x200?text=Survey'
    },
    {
      id: '6',
      name: 'Structural Details',
      type: 'PDF',
      uploadedAt: '2025-03-08T10:30:00Z',
      size: '5.4 MB',
      status: 'failed',
      thumbnailUrl: 'https://via.placeholder.com/300x200?text=Structural'
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

const Documents = () => {
  const [view, setView] = useState<'grid' | 'list'>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  
  // Fetch documents
  const { data: documents = [], isLoading, error } = useQuery({
    queryKey: ['documents'],
    queryFn: fetchDocuments
  });

  // Filter documents based on search query
  const filteredDocuments = documents.filter(doc => 
    doc.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Handle document upload success
  const handleUploadSuccess = () => {
    setUploadDialogOpen(false);
    // Optionally refetch documents here
  };

  return (
    <div className="container mx-auto p-6">
      <div className="flex flex-col space-y-4">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold">Documents</h1>
          <Dialog open={uploadDialogOpen} onOpenChange={setUploadDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Upload Document
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[600px]">
              <DialogHeader>
                <DialogTitle>Upload New Document</DialogTitle>
                <DialogDescription>
                  Upload construction plans for AI analysis and estimation.
                </DialogDescription>
              </DialogHeader>
              <DocumentUploadForm onSuccess={handleUploadSuccess} />
            </DialogContent>
          </Dialog>
        </div>

        <div className="flex justify-between items-center space-x-4">
          <div className="relative flex-1">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search documents..."
              className="pl-8"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="icon">
              <Filter className="h-4 w-4" />
            </Button>
            <Button
              variant={view === 'grid' ? 'default' : 'outline'}
              size="icon"
              onClick={() => setView('grid')}
            >
              <LayoutGrid className="h-4 w-4" />
            </Button>
            <Button
              variant={view === 'list' ? 'default' : 'outline'}
              size="icon"
              onClick={() => setView('list')}
            >
              <List className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {isLoading ? (
          <div className="flex justify-center items-center h-64">
            <p>Loading documents...</p>
          </div>
        ) : error ? (
          <div className="flex justify-center items-center h-64">
            <p className="text-red-500">Error loading documents</p>
          </div>
        ) : filteredDocuments.length === 0 ? (
          <div className="flex justify-center items-center h-64">
            <p>No documents found</p>
          </div>
        ) : (
          <Tabs defaultValue="all" className="w-full">
            <TabsList>
              <TabsTrigger value="all">All Documents</TabsTrigger>
              <TabsTrigger value="processed">Processed</TabsTrigger>
              <TabsTrigger value="processing">Processing</TabsTrigger>
              <TabsTrigger value="failed">Failed</TabsTrigger>
            </TabsList>
            <TabsContent value="all" className="mt-4">
              {view === 'grid' ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                  {filteredDocuments.map((doc) => (
                    <Card key={doc.id} className="overflow-hidden">
                      <div className="relative aspect-[4/3] bg-muted">
                        <img
                          src={doc.thumbnailUrl}
                          alt={doc.name}
                          className="object-cover w-full h-full"
                        />
                        <div 
                          className={`absolute top-2 right-2 px-2 py-1 rounded-full text-xs font-medium ${
                            doc.status === 'processed' ? 'bg-green-100 text-green-800' :
                            doc.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                            'bg-red-100 text-red-800'
                          }`}
                        >
                          {doc.status.charAt(0).toUpperCase() + doc.status.slice(1)}
                        </div>
                      </div>
                      <CardHeader className="p-4">
                        <CardTitle className="text-lg font-medium">
                          <Link to={`/documents/${doc.id}`} className="hover:underline">
                            {doc.name}
                          </Link>
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="p-4 pt-0">
                        <div className="flex items-center text-sm text-muted-foreground">
                          <FileText className="mr-1 h-4 w-4" />
                          <span>{doc.type}</span>
                          <span className="mx-2">•</span>
                          <span>{doc.size}</span>
                        </div>
                      </CardContent>
                      <CardFooter className="p-4 pt-0 flex justify-between items-center">
                        <div className="flex items-center text-sm text-muted-foreground">
                          <Clock className="mr-1 h-4 w-4" />
                          <span>{formatDate(doc.uploadedAt)}</span>
                        </div>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon">
                              <MoreVertical className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem>
                              <Eye className="mr-2 h-4 w-4" />
                              <span>View</span>
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Download className="mr-2 h-4 w-4" />
                              <span>Download</span>
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Share2 className="mr-2 h-4 w-4" />
                              <span>Share</span>
                            </DropdownMenuItem>
                            <DropdownMenuItem className="text-red-600">
                              <Trash2 className="mr-2 h-4 w-4" />
                              <span>Delete</span>
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </CardFooter>
                    </Card>
                  ))}
                </div>
              ) : (
                <div className="border rounded-md">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>Size</TableHead>
                        <TableHead>Uploaded</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredDocuments.map((doc) => (
                        <TableRow key={doc.id}>
                          <TableCell className="font-medium">
                            <Link to={`/documents/${doc.id}`} className="hover:underline">
                              {doc.name}
                            </Link>
                          </TableCell>
                          <TableCell>{doc.type}</TableCell>
                          <TableCell>{doc.size}</TableCell>
                          <TableCell>{formatDate(doc.uploadedAt)}</TableCell>
                          <TableCell>
                            <span
                              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                doc.status === 'processed' ? 'bg-green-100 text-green-800' :
                                doc.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                                'bg-red-100 text-red-800'
                              }`}
                            >
                              {doc.status.charAt(0).toUpperCase() + doc.status.slice(1)}
                            </span>
                          </TableCell>
                          <TableCell className="text-right">
                            <DropdownMenu>
                              <DropdownMenuTrigger asChild>
                                <Button variant="ghost" size="icon">
                                  <MoreVertical className="h-4 w-4" />
                                </Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent align="end">
                                <DropdownMenuItem>
                                  <Eye className="mr-2 h-4 w-4" />
                                  <span>View</span>
                                </DropdownMenuItem>
                                <DropdownMenuItem>
                                  <Download className="mr-2 h-4 w-4" />
                                  <span>Download</span>
                                </DropdownMenuItem>
                                <DropdownMenuItem>
                                  <Share2 className="mr-2 h-4 w-4" />
                                  <span>Share</span>
                                </DropdownMenuItem>
                                <DropdownMenuItem className="text-red-600">
                                  <Trash2 className="mr-2 h-4 w-4" />
                                  <span>Delete</span>
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
            
            {/* Other tab contents (processed, processing, failed) would be similar */}
            <TabsContent value="processed" className="mt-4">
              {/* Similar layout but filtered for processed documents */}
              <p className="text-center py-4">Processed documents view</p>
            </TabsContent>
            <TabsContent value="processing" className="mt-4">
              {/* Similar layout but filtered for processing documents */}
              <p className="text-center py-4">Processing documents view</p>
            </TabsContent>
            <TabsContent value="failed" className="mt-4">
              {/* Similar layout but filtered for failed documents */}
              <p className="text-center py-4">Failed documents view</p>
            </TabsContent>
          </Tabs>
        )}
      </div>
    </div>
  );
};

export default Documents;