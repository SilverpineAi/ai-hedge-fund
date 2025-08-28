import { Link, useLocation } from 'react-router-dom';
import { cn } from '../../lib/utils';
import {
  LayoutDashboard,
  FolderOpen,
  Users,
  Building2,
  TrendingUp,
  CheckSquare,
  Upload,
  Settings,
} from 'lucide-react';

interface SidebarProps {
  open: boolean;
  onToggle: () => void;
}

const navigation = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    name: 'Projects',
    href: '/projects',
    icon: FolderOpen,
  },
  {
    name: 'Contacts',
    href: '/contacts',
    icon: Users,
  },
  {
    name: 'Companies',
    href: '/companies',
    icon: Building2,
  },
  {
    name: 'Signals',
    href: '/signals',
    icon: TrendingUp,
  },
  {
    name: 'Tasks',
    href: '/tasks',
    icon: CheckSquare,
  },
  {
    name: 'Upload',
    href: '/upload',
    icon: Upload,
  },
];

export function Sidebar({ open, onToggle }: SidebarProps) {
  const location = useLocation();

  return (
    <>
      {/* Overlay for mobile */}
      {open && (
        <div
          className="fixed inset-0 bg-gray-600 bg-opacity-75 lg:hidden z-20"
          onClick={onToggle}
        />
      )}

      {/* Sidebar */}
      <div
        className={cn(
          'fixed inset-y-0 left-0 z-30 w-64 bg-white dark:bg-gray-800 shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0',
          open ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex items-center justify-center h-16 px-4 bg-blue-600 dark:bg-blue-700">
          <h1 className="text-xl font-bold text-white">
            Sales Intelligence
          </h1>
        </div>

        <nav className="mt-8 px-4">
          <div className="space-y-2">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={cn(
                    'group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors',
                    isActive
                      ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-200'
                      : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
                  )}
                >
                  <item.icon
                    className={cn(
                      'mr-3 h-5 w-5',
                      isActive
                        ? 'text-blue-500 dark:text-blue-300'
                        : 'text-gray-400 group-hover:text-gray-500 dark:group-hover:text-gray-300'
                    )}
                  />
                  {item.name}
                </Link>
              );
            })}
          </div>

          <div className="mt-8 pt-8 border-t border-gray-200 dark:border-gray-700">
            <Link
              to="/settings"
              className="group flex items-center px-3 py-2 text-sm font-medium text-gray-700 rounded-md hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 transition-colors"
            >
              <Settings className="mr-3 h-5 w-5 text-gray-400 group-hover:text-gray-500 dark:group-hover:text-gray-300" />
              Settings
            </Link>
          </div>
        </nav>

        {/* Footer */}
        <div className="absolute bottom-0 w-full p-4 border-t border-gray-200 dark:border-gray-700">
          <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
            Sales Intelligence Platform v1.0
          </div>
        </div>
      </div>
    </>
  );
}