import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { CheckSquare } from 'lucide-react';

export function Tasks() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Tasks
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Manage your outreach tasks and follow-ups
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckSquare className="h-5 w-5" />
            Task Management
          </CardTitle>
          <CardDescription>
            AI-generated outreach recommendations and task scheduling
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <CheckSquare className="mx-auto h-16 w-16 text-gray-400" />
            <h3 className="mt-4 text-xl font-medium text-gray-900 dark:text-white">
              Coming Soon
            </h3>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              Task management features are being developed
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}