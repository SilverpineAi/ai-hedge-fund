import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Plus, MoreHorizontal, FolderOpen, Users, Calendar } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '../components/ui/dropdown-menu';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { projectsApi, Project } from '../services/api';

export function Projects() {
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [newProject, setNewProject] = useState({
    name: '',
    description: '',
  });

  const queryClient = useQueryClient();

  // Fetch projects
  const { data: projects, isLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: () => projectsApi.getAll(),
  });

  // Create project mutation
  const createProjectMutation = useMutation({
    mutationFn: (data: Partial<Project>) => projectsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      setCreateDialogOpen(false);
      setNewProject({ name: '', description: '' });
    },
  });

  // Delete project mutation
  const deleteProjectMutation = useMutation({
    mutationFn: (id: number) => projectsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });

  const handleCreateProject = (e: React.FormEvent) => {
    e.preventDefault();
    if (newProject.name.trim()) {
      createProjectMutation.mutate(newProject);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'paused':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'completed':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'archived':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200';
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Projects</h1>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded"></div>
                  <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-5/6"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Projects
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Manage your sales intelligence projects and campaigns
          </p>
        </div>
        
        <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              New Project
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create New Project</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreateProject} className="space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Project Name
                </label>
                <Input
                  value={newProject.name}
                  onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                  placeholder="Enter project name"
                  required
                />
              </div>
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Description
                </label>
                <Textarea
                  value={newProject.description}
                  onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                  placeholder="Enter project description"
                  rows={3}
                />
              </div>
              <div className="flex justify-end space-x-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setCreateDialogOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={createProjectMutation.isPending}
                >
                  {createProjectMutation.isPending ? 'Creating...' : 'Create Project'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Projects Grid */}
      {projects?.data && projects.data.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.data.map((project: Project) => (
            <Card key={project.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div className="flex items-center space-x-2">
                    <FolderOpen className="h-5 w-5 text-blue-600" />
                    <CardTitle className="text-lg">
                      <Link 
                        to={`/projects/${project.id}`}
                        className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                      >
                        {project.name}
                      </Link>
                    </CardTitle>
                  </div>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="sm">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem asChild>
                        <Link to={`/projects/${project.id}`}>
                          View Details
                        </Link>
                      </DropdownMenuItem>
                      <DropdownMenuItem>
                        Edit Project
                      </DropdownMenuItem>
                      <DropdownMenuItem 
                        className="text-red-600"
                        onClick={() => {
                          if (confirm('Are you sure you want to delete this project?')) {
                            deleteProjectMutation.mutate(project.id);
                          }
                        }}
                      >
                        Delete Project
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
                <CardDescription>
                  {project.description || 'No description provided'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Status Badge */}
                  <div className="flex items-center justify-between">
                    <Badge className={getStatusColor(project.status)}>
                      {project.status.charAt(0).toUpperCase() + project.status.slice(1)}
                    </Badge>
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      ID: {project.id}
                    </span>
                  </div>

                  {/* Project Stats */}
                  <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                    <div className="flex items-center space-x-2">
                      <Users className="h-4 w-4 text-gray-400" />
                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Contacts</p>
                        <p className="text-sm font-medium text-gray-900 dark:text-white">-</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Calendar className="h-4 w-4 text-gray-400" />
                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Created</p>
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {new Date(project.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Quick Actions */}
                  <div className="flex space-x-2 pt-2">
                    <Button size="sm" variant="outline" asChild className="flex-1">
                      <Link to={`/contacts?project_id=${project.id}`}>
                        View Contacts
                      </Link>
                    </Button>
                    <Button size="sm" variant="outline" asChild className="flex-1">
                      <Link to={`/upload?project_id=${project.id}`}>
                        Upload
                      </Link>
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        // Empty State
        <Card className="p-12">
          <div className="text-center">
            <FolderOpen className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-4 text-lg font-medium text-gray-900 dark:text-white">
              No projects yet
            </h3>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              Get started by creating your first sales intelligence project.
            </p>
            <Button className="mt-6" onClick={() => setCreateDialogOpen(true)}>
              <Plus className="mr-2 h-4 w-4" />
              Create Your First Project
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
}