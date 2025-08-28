import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Users, Building2, TrendingUp, CheckSquare, Calendar, BarChart3 } from 'lucide-react';
import { projectsApi, dashboardApi } from '../services/api';

export function ProjectDetail() {
  const { projectId } = useParams<{ projectId: string }>();
  const id = parseInt(projectId!);

  // Fetch project details
  const { data: project } = useQuery({
    queryKey: ['projects', id],
    queryFn: () => projectsApi.getById(id),
  });

  // Fetch project dashboard data
  const { data: dashboard } = useQuery({
    queryKey: ['dashboard', 'project', id],
    queryFn: () => dashboardApi.getProjectDashboard(id),
    enabled: !!id,
  });

  if (!project?.data) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/4 mb-4"></div>
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
        </div>
      </div>
    );
  }

  const projectData = project.data;
  const stats = dashboard?.data?.contact_stats;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            {projectData.name}
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            {projectData.description || 'No description provided'}
          </p>
          <div className="flex items-center space-x-4 mt-4">
            <Badge className={
              projectData.status === 'active' 
                ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200'
            }>
              {projectData.status.charAt(0).toUpperCase() + projectData.status.slice(1)}
            </Badge>
            <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
              <Calendar className="h-4 w-4 mr-1" />
              Created {new Date(projectData.created_at).toLocaleDateString()}
            </div>
          </div>
        </div>
        
        <div className="flex space-x-2">
          <Button variant="outline">Edit Project</Button>
          <Button>Upload Contacts</Button>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Total Contacts
              </CardTitle>
              <Users className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {stats.total_contacts.toLocaleString()}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Graded Contacts
              </CardTitle>
              <BarChart3 className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {stats.graded_contacts.toLocaleString()}
              </div>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                {stats.total_contacts > 0 
                  ? Math.round((stats.graded_contacts / stats.total_contacts) * 100)
                  : 0
                }% of total
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Avg Prospect Score
              </CardTitle>
              <TrendingUp className="h-4 w-4 text-orange-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {stats.average_prospect_score 
                  ? Math.round(stats.average_prospect_score)
                  : '-'
                }
              </div>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                Out of 100
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                Enriched Contacts
              </CardTitle>
              <CheckSquare className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {stats.enriched_contacts || 0}
              </div>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                {stats.total_contacts > 0 
                  ? Math.round(((stats.enriched_contacts || 0) / stats.total_contacts) * 100)
                  : 0
                }% of total
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content Tabs */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="contacts">Contacts</TabsTrigger>
          <TabsTrigger value="signals">Signals</TabsTrigger>
          <TabsTrigger value="tasks">Tasks</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Grade Distribution */}
            {stats?.grade_distribution && (
              <Card>
                <CardHeader>
                  <CardTitle>Contact Grade Distribution</CardTitle>
                  <CardDescription>
                    Breakdown of contact grades in this project
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {Object.entries(stats.grade_distribution).map(([grade, count]) => (
                      <div key={grade} className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <Badge variant={grade === 'A' ? 'default' : 'secondary'}>
                            Grade {grade}
                          </Badge>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-medium">{count}</span>
                          <div className="w-16 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full"
                              style={{
                                width: `${stats.total_contacts > 0 ? (count / stats.total_contacts) * 100 : 0}%`
                              }}
                            />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
                <CardDescription>
                  Latest updates in this project
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                  No recent activity
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="contacts">
          <Card>
            <CardHeader>
              <CardTitle>Project Contacts</CardTitle>
              <CardDescription>
                Manage contacts in this project
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Users className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-4 text-lg font-medium text-gray-900 dark:text-white">
                  Contact management coming soon
                </h3>
                <p className="mt-2 text-gray-600 dark:text-gray-400">
                  Advanced contact filtering and management features will be available here.
                </p>
                <Button className="mt-4">
                  View All Contacts
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="signals">
          <Card>
            <CardHeader>
              <CardTitle>Growth Signals</CardTitle>
              <CardDescription>
                Signals detected for companies in this project
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <TrendingUp className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-4 text-lg font-medium text-gray-900 dark:text-white">
                  Signal tracking coming soon
                </h3>
                <p className="mt-2 text-gray-600 dark:text-gray-400">
                  Real-time growth signals and market intelligence will be displayed here.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tasks">
          <Card>
            <CardHeader>
              <CardTitle>Project Tasks</CardTitle>
              <CardDescription>
                Outreach tasks for contacts in this project
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <CheckSquare className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-4 text-lg font-medium text-gray-900 dark:text-white">
                  Task management coming soon
                </h3>
                <p className="mt-2 text-gray-600 dark:text-gray-400">
                  AI-generated outreach tasks and scheduling will be available here.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}