import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Check, FileText, Upload, X, FileWarning, Image, File } from 'lucide-react';

// UI Components
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

// Mock service (replace with actual service when available)
const uploadDocument = async (file: File, metadata: any) => {
  // Simulate upload delay
  await new Promise(resolve => setTimeout(resolve, 3000));
  
  // Mock successful upload
  return {
    id: 'doc-' + Math.random().toString(36).substring(2, 9),
    name: file.name,
    status: 'processing',
    uploadedAt: new Date().toISOString()
  };
};

interface DocumentUploadFormProps {
  onSuccess?: () => void;
}

type UploadStatus = 'idle' | 'uploading' | 'success' | 'error';

const DocumentUploadForm = ({ onSuccess }: DocumentUploadFormProps) => {
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>('idle');
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [documentName, setDocumentName] = useState('');
  const [documentType, setDocumentType] = useState('plan');
  const [description, setDescription] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  
  // Determine file icon based on file type
  const getFileIcon = (file: File) => {
    const extension = file.name.split('.').pop()?.toLowerCase();
    
    if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff'].includes(extension || '')) {
      return <Image className="h-10 w-10 text-blue-500" />;
    } else if (['pdf'].includes(extension || '')) {
      return <FileText className="h-10 w-10 text-red-500" />;
    } else if (['dwg', 'dxf'].includes(extension || '')) {
      return <FileText className="h-10 w-10 text-green-500" />;
    } else {
      return <File className="h-10 w-10 text-gray-500" />;
    }
  };

  // Configure dropzone
  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'image/*': ['.jpg', '.jpeg', '.png', '.tiff'],
      'application/dxf': ['.dxf'],
      'application/dwg': ['.dwg'],
      'application/octet-stream': ['.dwg', '.dxf', '.rvt'],
    },
    maxFiles: 1,
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        setSelectedFile(acceptedFiles[0]);
        if (!documentName) {
          // Set document name from file name without extension
          const fileName = acceptedFiles[0].name;
          const nameWithoutExtension = fileName.substring(0, fileName.lastIndexOf('.')) || fileName;
          setDocumentName(nameWithoutExtension);
        }
      }
    },
  });

  // Reset the form
  const resetForm = () => {
    setSelectedFile(null);
    setDocumentName('');
    setDocumentType('plan');
    setDescription('');
    setUploadStatus('idle');
    setUploadProgress(0);
    setUploadError(null);
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedFile) {
      setUploadError('Please select a file to upload');
      return;
    }

    try {
      setUploadStatus('uploading');
      setUploadError(null);
      
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          const newProgress = prev + Math.random() * 10;
          return newProgress >= 95 ? 95 : newProgress;
        });
      }, 300);
      
      // Upload the document
      const metadata = {
        name: documentName.trim() || selectedFile.name,
        type: documentType,
        description,
      };
      
      await uploadDocument(selectedFile, metadata);
      
      // Complete the upload
      clearInterval(progressInterval);
      setUploadProgress(100);
      setUploadStatus('success');
      
      // Notify parent component
      if (onSuccess) {
        setTimeout(() => {
          onSuccess();
        }, 1500);
      }
    } catch (error) {
      setUploadStatus('error');
      setUploadError('Failed to upload document. Please try again.');
      console.error('Upload error:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {uploadStatus === 'idle' && (
        <>
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
              ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'}
              ${isDragReject ? 'border-red-500 bg-red-50' : ''}
            `}
          >
            <input {...getInputProps()} />
            
            {selectedFile ? (
              <div className="flex flex-col items-center">
                {getFileIcon(selectedFile)}
                <p className="mt-2 font-medium">{selectedFile.name}</p>
                <p className="text-sm text-muted-foreground">
                  {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                </p>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="mt-4"
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedFile(null);
                  }}
                >
                  <X className="mr-2 h-4 w-4" />
                  Remove File
                </Button>
              </div>
            ) : (
              <div className="flex flex-col items-center">
                <Upload className="mx-auto h-12 w-12 text-muted-foreground" />
                <h3 className="mt-2 font-medium">Drop your file here or click to browse</h3>
                <p className="mt-1 text-sm text-muted-foreground">
                  Support for PDF, CAD (DWG, DXF), and image files
                </p>
                <Button
                  type="button"
                  variant="outline"
                  className="mt-4"
                >
                  Select File
                </Button>
              </div>
            )}
          </div>
          
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="document-name">Document Name</Label>
                <Input
                  id="document-name"
                  value={documentName}
                  onChange={(e) => setDocumentName(e.target.value)}
                  placeholder="Enter document name"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="document-type">Document Type</Label>
                <Select
                  value={documentType}
                  onValueChange={setDocumentType}
                >
                  <SelectTrigger id="document-type">
                    <SelectValue placeholder="Select document type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="plan">Floor Plan</SelectItem>
                    <SelectItem value="elevation">Elevation</SelectItem>
                    <SelectItem value="section">Section</SelectItem>
                    <SelectItem value="detail">Detail</SelectItem>
                    <SelectItem value="mep">MEP</SelectItem>
                    <SelectItem value="structural">Structural</SelectItem>
                    <SelectItem value="site">Site Plan</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="description">Description (Optional)</Label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Add additional details about this document..."
                rows={3}
              />
            </div>

            <div className="space-y-2">
              <Label>AI Processing Options</Label>
              <RadioGroup defaultValue="standard" className="grid grid-cols-3 gap-4 pt-2">
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="standard" id="processing-standard" />
                  <Label htmlFor="processing-standard" className="cursor-pointer">
                    Standard
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="detailed" id="processing-detailed" />
                  <Label htmlFor="processing-detailed" className="cursor-pointer">
                    Detailed
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="comprehensive" id="processing-comprehensive" />
                  <Label htmlFor="processing-comprehensive" className="cursor-pointer">
                    Comprehensive
                  </Label>
                </div>
              </RadioGroup>
              <p className="text-sm text-muted-foreground">
                Processing detail affects analysis time and cost estimation accuracy
              </p>
            </div>
          </div>
        </>
      )}

      {uploadStatus === 'uploading' && (
        <div className="space-y-4">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 flex-shrink-0">
              {getFileIcon(selectedFile!)}
            </div>
            <div className="flex-grow">
              <h4 className="font-medium">{selectedFile?.name}</h4>
              <Progress value={uploadProgress} className="h-2 mt-2" />
              <p className="text-sm text-muted-foreground mt-1">
                Uploading... {Math.round(uploadProgress)}%
              </p>
            </div>
          </div>
        </div>
      )}

      {uploadStatus === 'success' && (
        <div className="space-y-4">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 flex items-center justify-center rounded-full bg-green-100">
              <Check className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <h4 className="font-medium">Upload Complete</h4>
              <p className="text-sm text-muted-foreground">
                Your document has been uploaded and is now being processed.
              </p>
            </div>
          </div>
        </div>
      )}

      {uploadStatus === 'error' && (
        <div className="space-y-4">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 flex items-center justify-center rounded-full bg-red-100">
              <FileWarning className="h-6 w-6 text-red-600" />
            </div>
            <div>
              <h4 className="font-medium">Upload Failed</h4>
              <p className="text-sm text-red-600">{uploadError}</p>
            </div>
          </div>
          <Button
            type="button"
            variant="outline"
            onClick={() => {
              setUploadStatus('idle');
              setUploadError(null);
              setUploadProgress(0);
            }}
          >
            Try Again
          </Button>
        </div>
      )}

      {uploadStatus === 'idle' && (
        <div className="flex justify-end space-x-4">
          <Button
            type="button"
            variant="outline"
            onClick={resetForm}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            disabled={!selectedFile}
          >
            Upload Document
          </Button>
        </div>
      )}
    </form>
  );
};

export default DocumentUploadForm;