import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Building2 } from 'lucide-react';

export function Companies() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Companies
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Explore company intelligence and growth signals
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="h-5 w-5" />
            Company Intelligence
          </CardTitle>
          <CardDescription>
            Company profiles, enrichment data, and growth tracking
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12">
            <Building2 className="mx-auto h-16 w-16 text-gray-400" />
            <h3 className="mt-4 text-xl font-medium text-gray-900 dark:text-white">
              Coming Soon
            </h3>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              Company intelligence features are being developed
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}