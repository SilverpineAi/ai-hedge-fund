import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
import { Upload as UploadIcon, FileText, AlertCircle, CheckCircle, X } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Progress } from '../components/ui/progress';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import { projectsApi, uploadApi } from '../services/api';

interface UploadResult {
  upload_batch_id: number;
  filename: string;
  total_records: number;
  preview_records: any[];
  validation_errors: string[];
  warnings: string[];
}

export function Upload() {
  const [searchParams] = useSearchParams();
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(
    searchParams.get('project_id') ? parseInt(searchParams.get('project_id')!) : null
  );
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const queryClient = useQueryClient();

  // Fetch projects for selection
  const { data: projects } = useQuery({
    queryKey: ['projects'],
    queryFn: () => projectsApi.getAll(),
  });

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: ({ file, projectId }: { file: File; projectId: number }) =>
      uploadApi.uploadCsv(file, projectId),
    onSuccess: (response) => {
      setUploadResult(response.data);
      setUploadError(null);
      queryClient.invalidateQueries({ queryKey: ['contacts'] });
      queryClient.invalidateQueries({ queryKey: ['upload-batches'] });
    },
    onError: (error: any) => {
      setUploadError(error.response?.data?.detail || 'Upload failed');
      setUploadResult(null);
    },
  });

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (!selectedProjectId) {
      setUploadError('Please select a project first');
      return;
    }

    const file = acceptedFiles[0];
    if (file) {
      // Validate file type
      if (!file.name.toLowerCase().endsWith('.csv')) {
        setUploadError('Please upload a CSV file');
        return;
      }

      // Validate file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        setUploadError('File size must be less than 10MB');
        return;
      }

      uploadMutation.mutate({ file, projectId: selectedProjectId });
    }
  }, [selectedProjectId, uploadMutation]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
    },
    maxFiles: 1,
  });

  const resetUpload = () => {
    setUploadResult(null);
    setUploadError(null);
  };

  return (
    <div className="space-y-6 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Upload Contacts
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Upload CSV files to import contacts into your projects
        </p>
      </div>

      {/* Project Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Select Project</CardTitle>
          <CardDescription>
            Choose the project where you want to import the contacts
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Select
            value={selectedProjectId?.toString() || ''}
            onValueChange={(value) => setSelectedProjectId(parseInt(value))}
          >
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select a project" />
            </SelectTrigger>
            <SelectContent>
              {projects?.data?.map((project) => (
                <SelectItem key={project.id} value={project.id.toString()}>
                  {project.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      {/* Upload Area */}
      <Card>
        <CardHeader>
          <CardTitle>Upload CSV File</CardTitle>
          <CardDescription>
            Drag and drop your CSV file or click to browse
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!uploadResult ? (
            <div
              {...getRootProps()}
              className={`
                border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
                ${isDragActive
                  ? 'border-blue-400 bg-blue-50 dark:bg-blue-900/20'
                  : 'border-gray-300 dark:border-gray-600 hover:border-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20'
                }
                ${!selectedProjectId ? 'opacity-50 cursor-not-allowed' : ''}
              `}
            >
              <input {...getInputProps()} disabled={!selectedProjectId} />
              
              <UploadIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              
              {uploadMutation.isPending ? (
                <div className="space-y-4">
                  <p className="text-lg font-medium text-gray-900 dark:text-white">
                    Uploading and processing...
                  </p>
                  <Progress value={50} className="w-full max-w-xs mx-auto" />
                </div>
              ) : (
                <div>
                  <p className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                    {isDragActive
                      ? 'Drop the CSV file here'
                      : selectedProjectId
                      ? 'Drag and drop a CSV file here, or click to select'
                      : 'Please select a project first'
                    }
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Maximum file size: 10MB • Maximum records: 10,000
                  </p>
                </div>
              )}
            </div>
          ) : (
            // Upload Success
            <div className="space-y-6">
              <Alert>
                <CheckCircle className="h-4 w-4" />
                <AlertDescription>
                  File uploaded successfully! {uploadResult.total_records} contacts processed.
                </AlertDescription>
              </Alert>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                  <CardContent className="p-4">
                    <div className="text-2xl font-bold text-green-600">
                      {uploadResult.total_records}
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Total Records
                    </p>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardContent className="p-4">
                    <div className="text-2xl font-bold text-blue-600">
                      {uploadResult.preview_records.length}
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Preview Records
                    </p>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardContent className="p-4">
                    <div className="text-2xl font-bold text-orange-600">
                      {uploadResult.validation_errors.length + uploadResult.warnings.length}
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Issues Found
                    </p>
                  </CardContent>
                </Card>
              </div>

              {/* Warnings and Errors */}
              {uploadResult.warnings.length > 0 && (
                <Alert>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    <strong>Warnings:</strong>
                    <ul className="mt-2 list-disc list-inside">
                      {uploadResult.warnings.map((warning, index) => (
                        <li key={index} className="text-sm">{warning}</li>
                      ))}
                    </ul>
                  </AlertDescription>
                </Alert>
              )}

              {uploadResult.validation_errors.length > 0 && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    <strong>Errors:</strong>
                    <ul className="mt-2 list-disc list-inside">
                      {uploadResult.validation_errors.map((error, index) => (
                        <li key={index} className="text-sm">{error}</li>
                      ))}
                    </ul>
                  </AlertDescription>
                </Alert>
              )}

              {/* Preview Table */}
              {uploadResult.preview_records.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Data Preview</CardTitle>
                    <CardDescription>
                      First {uploadResult.preview_records.length} records from your upload
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b border-gray-200 dark:border-gray-700">
                            <th className="text-left p-2 font-medium">Name</th>
                            <th className="text-left p-2 font-medium">Email</th>
                            <th className="text-left p-2 font-medium">Title</th>
                            <th className="text-left p-2 font-medium">Company</th>
                          </tr>
                        </thead>
                        <tbody>
                          {uploadResult.preview_records.map((record, index) => (
                            <tr key={index} className="border-b border-gray-100 dark:border-gray-800">
                              <td className="p-2">{record.full_name || '-'}</td>
                              <td className="p-2">{record.email || '-'}</td>
                              <td className="p-2">{record.title || '-'}</td>
                              <td className="p-2">{record.company_name || '-'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>
              )}

              <div className="flex space-x-4">
                <Button onClick={resetUpload} variant="outline">
                  Upload Another File
                </Button>
                <Button asChild>
                  <a href={`/contacts?project_id=${selectedProjectId}`}>
                    View Contacts
                  </a>
                </Button>
              </div>
            </div>
          )}

          {/* Upload Error */}
          {uploadError && (
            <Alert variant="destructive" className="mt-4">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{uploadError}</AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* CSV Format Instructions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            CSV Format Requirements
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h4 className="font-medium mb-2">Required Columns:</h4>
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline">full_name</Badge>
            </div>
          </div>
          
          <div>
            <h4 className="font-medium mb-2">Optional Columns:</h4>
            <div className="flex flex-wrap gap-2">
              <Badge variant="secondary">first_name</Badge>
              <Badge variant="secondary">last_name</Badge>
              <Badge variant="secondary">email</Badge>
              <Badge variant="secondary">phone</Badge>
              <Badge variant="secondary">title</Badge>
              <Badge variant="secondary">company_name</Badge>
              <Badge variant="secondary">company_domain</Badge>
              <Badge variant="secondary">location</Badge>
              <Badge variant="secondary">linkedin_url</Badge>
              <Badge variant="secondary">department</Badge>
              <Badge variant="secondary">seniority_level</Badge>
            </div>
          </div>

          <div className="text-sm text-gray-600 dark:text-gray-400">
            <p><strong>Tips:</strong></p>
            <ul className="list-disc list-inside mt-1 space-y-1">
              <li>Ensure your CSV file has headers in the first row</li>
              <li>Use UTF-8 encoding for special characters</li>
              <li>Email addresses will be validated automatically</li>
              <li>Phone numbers will be cleaned and formatted</li>
              <li>LinkedIn URLs will be validated</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}