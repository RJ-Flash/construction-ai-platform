import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ChevronLeft, Download, Share2, Trash2, FileText, ArrowLeft, ArrowRight, ZoomIn, ZoomOut, Maximize, Layers, List, Eye, Edit, Clock, Clipboard } from 'lucide-react';

// UI Components
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from '@/components/ui/resizable';

// Mock service (replace with actual service later)
const fetchDocument = async (id: string) => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Mock data
  return {
    id,
    name: 'Office Building Floor Plan',
    type: 'PDF',
    uploadedAt: '2025-03-20T14:30:00Z',
    size: '4.2 MB',
    status: 'processed',
    thumbnailUrl: 'https://via.placeholder.com/800x600?text=Floor+Plan',
    processingData: {
      completed: true,
      progress: 100,
      startedAt: '2025-03-20T14:32:00Z',
      completedAt: '2025-03-20T14:35:00Z',
      elements: [
        { type: 'Wall', count: 42, area: '320 sqft' },
        { type: 'Door', count: 12, width: '36 inches' },
        { type: 'Window', count: 18, dimensions: '48x36 inches' },
        { type: 'Room', count: 8, totalArea: '2400 sqft' },
        { type: 'Staircase', count: 2, floors: 'connects 3 floors' },
        { type: 'HVAC', count: 4, type: 'Central air system' }
      ],
      materials: [
        { name: 'Drywall', quantity: '3200 sqft', unitCost: '$1.80/sqft', totalCost: '$5,760' },
        { name: 'Insulation', quantity: '3000 sqft', unitCost: '$1.20/sqft', totalCost: '$3,600' },
        { name: 'Door Frames', quantity: '12 units', unitCost: '$120/unit', totalCost: '$1,440' },
        { name: 'Window Frames', quantity: '18 units', unitCost: '$180/unit', totalCost: '$3,240' },
        { name: 'Electrical Wiring', quantity: '2400 linear ft', unitCost: '$2.50/ft', totalCost: '$6,000' },
        { name: 'Plumbing', quantity: '800 linear ft', unitCost: '$4.80/ft', totalCost: '$3,840' }
      ],
      estimatedTotal: '$145,600',
      annotations: [
        { id: 'a1', position: { x: 120, y: 150 }, text: 'Load-bearing wall - reinforcement needed', type: 'warning' },
        { id: 'a2', position: { x: 380, y: 220 }, text: 'Electrical panel location', type: 'info' },
        { id: 'a3', position: { x: 540, y: 320 }, text: 'Window size non-standard - custom order required', type: 'warning' }
      ]
    }
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

const DocumentViewer = () => {
  const { documentId } = useParams<{ documentId: string }>();
  const [zoomLevel, setZoomLevel] = useState(100);
  
  // Fetch document data
  const { data: document, isLoading, error } = useQuery({
    queryKey: ['document', documentId],
    queryFn: () => fetchDocument(documentId || '')
  });

  if (isLoading) {
    return (
      <div className="container mx-auto p-6 flex justify-center items-center h-96">
        <p>Loading document data...</p>
      </div>
    );
  }

  if (error || !document) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center mb-4">
          <Button variant="ghost" size="sm" asChild>
            <Link to="/documents">
              <ChevronLeft className="mr-2 h-4 w-4" />
              Back to Documents
            </Link>
          </Button>
        </div>
        <div className="flex justify-center items-center h-96">
          <p className="text-red-500">Error loading document</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <Button variant="ghost" size="sm" asChild>
            <Link to="/documents">
              <ChevronLeft className="mr-2 h-4 w-4" />
              Back to Documents
            </Link>
          </Button>
          <h1 className="text-2xl font-bold ml-4">{document.name}</h1>
          <Badge variant="outline" className="ml-2">
            {document.type}
          </Badge>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm">
            <Download className="mr-2 h-4 w-4" />
            Download
          </Button>
          <Button variant="outline" size="sm">
            <Share2 className="mr-2 h-4 w-4" />
            Share
          </Button>
          <Button variant="outline" size="sm" className="text-red-500 hover:text-red-700">
            <Trash2 className="mr-2 h-4 w-4" />
            Delete
          </Button>
        </div>
      </div>

      <ResizablePanelGroup direction="horizontal" className="min-h-[80vh] border rounded-lg">
        <ResizablePanel defaultSize={70}>
          <div className="h-full flex flex-col">
            <div className="border-b p-4 flex justify-between items-center bg-muted/30">
              <div className="flex items-center space-x-2">
                <Button variant="outline" size="sm">
                  <ArrowLeft className="h-4 w-4" />
                </Button>
                <Button variant="outline" size="sm">
                  <ArrowRight className="h-4 w-4" />
                </Button>
                <span className="text-sm">Page 1 of 1</span>
              </div>
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setZoomLevel(Math.max(50, zoomLevel - 10))}
                >
                  <ZoomOut className="h-4 w-4" />
                </Button>
                <span className="text-sm w-16 text-center">{zoomLevel}%</span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setZoomLevel(Math.min(200, zoomLevel + 10))}
                >
                  <ZoomIn className="h-4 w-4" />
                </Button>
                <Button variant="outline" size="sm">
                  <Maximize className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex items-center space-x-2">
                <Button variant="outline" size="sm">
                  <Layers className="mr-2 h-4 w-4" />
                  Layers
                </Button>
                <Button variant="outline" size="sm">
                  <Eye className="mr-2 h-4 w-4" />
                  Toggle Elements
                </Button>
              </div>
            </div>
            <div className="flex-1 overflow-auto p-4 flex justify-center items-start bg-muted/10">
              <div
                className="relative"
                style={{
                  transform: `scale(${zoomLevel / 100})`,
                  transformOrigin: 'top center',
                  transition: 'transform 0.2s ease'
                }}
              >
                <img 
                  src={document.thumbnailUrl} 
                  alt={document.name}
                  className="border shadow-md"
                />
                
                {/* Annotations */}
                {document.processingData.annotations.map(annotation => (
                  <div
                    key={annotation.id}
                    className={`absolute p-1 rounded-full cursor-pointer transform -translate-x-1/2 -translate-y-1/2 ${
                      annotation.type === 'warning' ? 'bg-amber-500' : 'bg-blue-500'
                    }`}
                    style={{
                      left: annotation.position.x,
                      top: annotation.position.y,
                    }}
                    title={annotation.text}
                  >
                    <div className="h-3 w-3 rounded-full bg-white" />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </ResizablePanel>
        
        <ResizableHandle />
        
        <ResizablePanel defaultSize={30}>
          <Tabs defaultValue="analysis">
            <TabsList className="w-full">
              <TabsTrigger value="analysis" className="flex-1">Analysis</TabsTrigger>
              <TabsTrigger value="elements" className="flex-1">Elements</TabsTrigger>
              <TabsTrigger value="materials" className="flex-1">Materials</TabsTrigger>
              <TabsTrigger value="notes" className="flex-1">Notes</TabsTrigger>
            </TabsList>
            
            <ScrollArea className="h-[calc(80vh-2.5rem)]">
              <TabsContent value="analysis" className="p-4">
                <Card>
                  <CardHeader>
                    <CardTitle>AI Analysis Results</CardTitle>
                    <CardDescription>
                      Processed on {formatDate(document.processingData.completedAt)}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span>Processing Status</span>
                          <span className="font-medium text-green-600">Complete</span>
                        </div>
                        <Progress value={100} className="h-2" />
                      </div>
                      
                      <div className="pt-2">
                        <h4 className="text-sm font-medium mb-2">Summary</h4>
                        <ul className="space-y-2 text-sm">
                          <li className="flex justify-between">
                            <span className="text-muted-foreground">Total Elements</span>
                            <span>{document.processingData.elements.reduce((sum, el) => sum + el.count, 0)}</span>
                          </li>
                          <li className="flex justify-between">
                            <span className="text-muted-foreground">Total Area</span>
                            <span>2,400 sqft</span>
                          </li>
                          <li className="flex justify-between">
                            <span className="text-muted-foreground">Estimated Cost</span>
                            <span className="font-bold">{document.processingData.estimatedTotal}</span>
                          </li>
                        </ul>
                      </div>
                      
                      <Separator />
                      
                      <div>
                        <div className="flex items-center justify-between">
                          <h4 className="text-sm font-medium">Key Insights</h4>
                          <Button variant="ghost" size="sm">
                            <Clipboard className="h-4 w-4 mr-2" />
                            Copy All
                          </Button>
                        </div>
                        <ul className="mt-2 space-y-2">
                          <li className="text-sm flex">
                            <Badge variant="outline" className="bg-amber-100 text-amber-800 hover:bg-amber-100 mr-2 mt-0.5">Warning</Badge>
                            <span>Load-bearing wall identified - requires reinforcement</span>
                          </li>
                          <li className="text-sm flex">
                            <Badge variant="outline" className="bg-amber-100 text-amber-800 hover:bg-amber-100 mr-2 mt-0.5">Warning</Badge>
                            <span>Non-standard window dimensions - custom order needed</span>
                          </li>
                          <li className="text-sm flex">
                            <Badge variant="outline" className="bg-blue-100 text-blue-800 hover:bg-blue-100 mr-2 mt-0.5">Info</Badge>
                            <span>HVAC system appears to be undersized for the space</span>
                          </li>
                          <li className="text-sm flex">
                            <Badge variant="outline" className="bg-green-100 text-green-800 hover:bg-green-100 mr-2 mt-0.5">Savings</Badge>
                            <span>Potential 12% cost reduction by standardizing door sizes</span>
                          </li>
                        </ul>
                      </div>
                      
                      <Button variant="outline" className="w-full">
                        <Edit className="mr-2 h-4 w-4" />
                        Edit Analysis
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
              
              <TabsContent value="elements" className="p-4">
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-medium">Detected Elements</h3>
                    <Button variant="outline" size="sm">
                      <Download className="mr-2 h-4 w-4" />
                      Export
                    </Button>
                  </div>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Type</TableHead>
                        <TableHead className="text-right">Count</TableHead>
                        <TableHead>Details</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {document.processingData.elements.map((element, index) => (
                        <TableRow key={index}>
                          <TableCell className="font-medium">{element.type}</TableCell>
                          <TableCell className="text-right">{element.count}</TableCell>
                          <TableCell>
                            {element.area || element.dimensions || element.width || element.totalArea || element.floors || element.type}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </TabsContent>
              
              <TabsContent value="materials" className="p-4">
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-medium">Material Estimates</h3>
                    <Button variant="outline" size="sm">
                      <Download className="mr-2 h-4 w-4" />
                      Export
                    </Button>
                  </div>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Material</TableHead>
                        <TableHead>Quantity</TableHead>
                        <TableHead>Unit Cost</TableHead>
                        <TableHead className="text-right">Total Cost</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {document.processingData.materials.map((material, index) => (
                        <TableRow key={index}>
                          <TableCell className="font-medium">{material.name}</TableCell>
                          <TableCell>{material.quantity}</TableCell>
                          <TableCell>{material.unitCost}</TableCell>
                          <TableCell className="text-right">{material.totalCost}</TableCell>
                        </TableRow>
                      ))}
                      <TableRow className="bg-muted/50">
                        <TableCell colSpan={3} className="font-medium">Total Estimated Cost</TableCell>
                        <TableCell className="text-right font-bold">{document.processingData.estimatedTotal}</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </div>
              </TabsContent>
              
              <TabsContent value="notes" className="p-4">
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-medium">Notes & Annotations</h3>
                    <Button size="sm">
                      <Edit className="mr-2 h-4 w-4" />
                      Add Note
                    </Button>
                  </div>
                  
                  <div className="space-y-3">
                    {document.processingData.annotations.map((annotation, index) => (
                      <Card key={index}>
                        <CardHeader className="py-3">
                          <CardTitle className="text-sm font-medium flex items-center">
                            <Badge variant="outline" className={`mr-2 ${
                              annotation.type === 'warning' 
                                ? 'bg-amber-100 text-amber-800 hover:bg-amber-100' 
                                : 'bg-blue-100 text-blue-800 hover:bg-blue-100'
                            }`}>
                              {annotation.type.charAt(0).toUpperCase() + annotation.type.slice(1)}
                            </Badge>
                            <span>Annotation {index + 1}</span>
                          </CardTitle>
                        </CardHeader>
                        <CardContent className="py-0">
                          <p className="text-sm">{annotation.text}</p>
                        </CardContent>
                        <CardFooter className="py-2 text-xs text-muted-foreground">
                          <div className="flex items-center">
                            <Clock className="mr-1 h-3 w-3" />
                            <span>Added on {formatDate(document.processingData.completedAt)}</span>
                          </div>
                        </CardFooter>
                      </Card>
                    ))}
                  </div>
                </div>
              </TabsContent>
            </ScrollArea>
          </Tabs>
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  );
};

export default DocumentViewer;