import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { 
  Users, 
  Building2, 
  TrendingUp, 
  CheckSquare,
  Upload,
  Activity,
  Target,
  Zap
} from 'lucide-react';
import { dashboardApi, contactsApi, signalsApi, tasksApi } from '../services/api';

export function Dashboard() {
  // Fetch dashboard overview data
  const { data: overview } = useQuery({
    queryKey: ['dashboard', 'overview'],
    queryFn: () => dashboardApi.getOverview(),
  });

  // Fetch recent activity
  const { data: recentActivity } = useQuery({
    queryKey: ['dashboard', 'activity'],
    queryFn: () => dashboardApi.getRecentActivity({ limit: 10 }),
  });

  // Fetch top prospects
  const { data: topProspects } = useQuery({
    queryKey: ['dashboard', 'prospects'],
    queryFn: () => dashboardApi.getProspectLeaderboard({ limit: 5 }),
  });

  // Fetch recent signals
  const { data: recentSignals } = useQuery({
    queryKey: ['dashboard', 'signals'],
    queryFn: () => signalsApi.getRecentHighImpact({ limit: 5 }),
  });

  // Fetch today's tasks
  const { data: todaysTasks } = useQuery({
    queryKey: ['dashboard', 'tasks', 'today'],
    queryFn: () => tasksApi.getTodaysTasks(),
  });

  const stats = [
    {
      title: 'Total Contacts',
      value: overview?.data?.contacts?.total || 0,
      change: '+12%',
      icon: Users,
      color: 'blue',
    },
    {
      title: 'A-Grade Prospects',
      value: overview?.data?.contacts?.a_grade_count || 0,
      change: '+8%',
      icon: Target,
      color: 'green',
    },
    {
      title: 'Recent Signals',
      value: overview?.data?.signals?.total_recent || 0,
      change: '+23%',
      icon: TrendingUp,
      color: 'orange',
    },
    {
      title: 'Pending Tasks',
      value: overview?.data?.tasks?.pending || 0,
      change: '-5%',
      icon: CheckSquare,
      color: 'purple',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Dashboard
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Welcome back! Here's what's happening with your sales intelligence.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <Card key={index}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600 dark:text-gray-400">
                {stat.title}
              </CardTitle>
              <stat.icon className={`h-4 w-4 text-${stat.color}-600`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {stat.value.toLocaleString()}
              </div>
              <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                <span className={`text-${stat.change.startsWith('+') ? 'green' : 'red'}-600`}>
                  {stat.change}
                </span>{' '}
                from last month
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - 2/3 width */}
        <div className="lg:col-span-2 space-y-6">
          {/* Top Prospects */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5 text-green-600" />
                Top Prospects
              </CardTitle>
              <CardDescription>
                Your highest-scoring prospects this week
              </CardDescription>
            </CardHeader>
            <CardContent>
              {topProspects?.data ? (
                <div className="space-y-4">
                  {topProspects.data.slice(0, 5).map((prospect: any, index: number) => (
                    <div key={prospect.contact.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div className="flex-shrink-0">
                          <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                            <span className="text-sm font-medium text-blue-600 dark:text-blue-300">
                              #{index + 1}
                            </span>
                          </div>
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-900 dark:text-white">
                            {prospect.contact.full_name}
                          </p>
                          <p className="text-xs text-gray-600 dark:text-gray-400">
                            {prospect.contact.title} at {prospect.contact.company_name}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant={prospect.contact_grade === 'A' ? 'default' : 'secondary'}>
                          Grade {prospect.contact_grade}
                        </Badge>
                        <span className="text-sm font-medium text-gray-900 dark:text-white">
                          {Math.round(prospect.prospect_score)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                  No prospects data available
                </div>
              )}
            </CardContent>
          </Card>

          {/* Recent Signals */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-orange-600" />
                Recent High-Impact Signals
              </CardTitle>
              <CardDescription>
                Growth signals detected in the last 7 days
              </CardDescription>
            </CardHeader>
            <CardContent>
              {recentSignals?.data ? (
                <div className="space-y-4">
                  {recentSignals.data.slice(0, 5).map((signal: any) => (
                    <div key={signal.id} className="flex items-start space-x-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <div className="flex-shrink-0">
                        <div className="w-2 h-2 bg-orange-500 rounded-full mt-2"></div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {signal.title}
                        </p>
                        <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                          {signal.company?.name} • {signal.source}
                        </p>
                        <div className="flex items-center space-x-2 mt-2">
                          <Badge variant="outline" className="text-xs">
                            {signal.signal_type.replace('_', ' ')}
                          </Badge>
                          <span className="text-xs text-gray-500">
                            Impact: {Math.round(signal.impact_score)}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                  No recent signals
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Column - 1/3 width */}
        <div className="space-y-6">
          {/* Today's Tasks */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckSquare className="h-5 w-5 text-purple-600" />
                Today's Tasks
              </CardTitle>
              <CardDescription>
                {todaysTasks?.data?.length || 0} tasks scheduled for today
              </CardDescription>
            </CardHeader>
            <CardContent>
              {todaysTasks?.data ? (
                <div className="space-y-3">
                  {todaysTasks.data.slice(0, 5).map((task: any) => (
                    <div key={task.id} className="flex items-center space-x-3 p-2 bg-gray-50 dark:bg-gray-800 rounded">
                      <div className="flex-shrink-0">
                        <div className={`w-3 h-3 rounded-full ${
                          task.priority >= 4 ? 'bg-red-500' : 
                          task.priority >= 3 ? 'bg-orange-500' : 'bg-green-500'
                        }`}></div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {task.title}
                        </p>
                        <p className="text-xs text-gray-600 dark:text-gray-400">
                          {task.contact?.full_name} • {task.channel}
                        </p>
                      </div>
                    </div>
                  ))}
                  {todaysTasks.data.length === 0 && (
                    <div className="text-center py-4 text-gray-500 dark:text-gray-400 text-sm">
                      No tasks for today
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-4 text-gray-500 dark:text-gray-400 text-sm">
                  Loading tasks...
                </div>
              )}
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5 text-blue-600" />
                Recent Activity
              </CardTitle>
            </CardHeader>
            <CardContent>
              {recentActivity?.data ? (
                <div className="space-y-3">
                  {recentActivity.data.slice(0, 5).map((activity: any, index: number) => (
                    <div key={index} className="flex items-start space-x-3">
                      <div className="flex-shrink-0">
                        <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-xs text-gray-900 dark:text-white">
                          {activity.description}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          {new Date(activity.timestamp).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  ))}
                  {recentActivity.data.length === 0 && (
                    <div className="text-center py-4 text-gray-500 dark:text-gray-400 text-xs">
                      No recent activity
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-4 text-gray-500 dark:text-gray-400 text-xs">
                  Loading activity...
                </div>
              )}
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button className="w-full justify-start" variant="outline">
                <Upload className="mr-2 h-4 w-4" />
                Upload Contacts
              </Button>
              <Button className="w-full justify-start" variant="outline">
                <Building2 className="mr-2 h-4 w-4" />
                Add Company
              </Button>
              <Button className="w-full justify-start" variant="outline">
                <TrendingUp className="mr-2 h-4 w-4" />
                Detect Signals
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}