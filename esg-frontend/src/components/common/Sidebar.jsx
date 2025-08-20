import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  HomeIcon, 
  ChartBarIcon, 
  DocumentTextIcon, 
  PresentationChartLineIcon,
  CogIcon,
  PlusIcon,
  ChatBubbleLeftRightIcon,
  ArrowTrendingUpIcon, // Changed from TrendingUpIcon
  ShieldCheckIcon
} from '@heroicons/react/24/outline';

const Sidebar = () => {
  const location = useLocation();

  const menuItems = [
    { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
    { name: 'ESG Analysis', href: '/analysis', icon: ArrowTrendingUpIcon }, // Updated icon
    { name: 'Reports', href: '/reports', icon: DocumentTextIcon },
    { name: 'Analytics', href: '/analytics', icon: PresentationChartLineIcon },
  ];

  const quickActions = [
    { name: 'Add Analysis', icon: PlusIcon, action: 'add-analysis' },
    { name: 'Ask AI', icon: ChatBubbleLeftRightIcon, action: 'ask-ai' },
  ];

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <div className="w-64 bg-dark-900 border-r border-dark-700 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-dark-700">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
            <ShieldCheckIcon className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold text-white">ESG AI Bot</span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              to={item.href}
              className={`sidebar-item ${isActive(item.href) ? 'active' : ''}`}
            >
              <Icon className="w-5 h-5 mr-3" />
              {item.name}
            </Link>
          );
        })}
      </nav>

      {/* Quick Actions */}
      <div className="px-4 py-4 border-t border-dark-700">
        <p className="text-xs font-semibold text-dark-400 uppercase tracking-wider mb-3">
          Quick Actions
        </p>
        <div className="space-y-2">
          {quickActions.map((action) => {
            const Icon = action.icon;
            return (
              <button
                key={action.name}
                className="sidebar-item w-full justify-start"
                onClick={() => console.log(action.action)}
              >
                <Icon className="w-5 h-5 mr-3" />
                {action.name}
              </button>
            );
          })}
        </div>
      </div>

      {/* Settings */}
      <div className="px-4 py-4 border-t border-dark-700">
        <Link
          to="/settings"
          className={`sidebar-item ${isActive('/settings') ? 'active' : ''}`}
        >
          <CogIcon className="w-5 h-5 mr-3" />
          Settings
        </Link>
      </div>
    </div>
  );
};

export default Sidebar;