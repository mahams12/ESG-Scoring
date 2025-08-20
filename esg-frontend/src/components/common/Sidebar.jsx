import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  HomeIcon, 
  GlobeAltIcon, 
  DocumentChartBarIcon, 
  PresentationChartLineIcon,
  CogIcon,
  SparklesIcon,
  ChartBarSquareIcon,
  BeakerIcon,
  UsersIcon
} from '@heroicons/react/24/outline';

const Sidebar = () => {
  const location = useLocation();

  const navigationSections = [
    {
      title: "Main",
      items: [
        { 
          name: 'Dashboard', 
          href: '/dashboard', 
          icon: HomeIcon,
          description: 'ESG overview & metrics'
        },
        { 
          name: 'Analysis', 
          href: '/analysis', 
          icon: GlobeAltIcon,
          description: 'Company sustainability scoring'
        },
        { 
          name: 'Reports', 
          href: '/reports', 
          icon: DocumentChartBarIcon,
          description: 'Impact & performance reports'
        },
        { 
          name: 'Analytics', 
          href: '/analytics', 
          icon: PresentationChartLineIcon,
          description: 'Market intelligence & trends'
        },
      ]
    },
    {
      title: "Tools",
      items: [
        { 
          name: 'AI Insights', 
          href: '/ai-insights', 
          icon: SparklesIcon,
          description: 'Smart recommendations'
        },
        { 
          name: 'Carbon Tracker', 
          href: '/carbon-tracker', 
          icon: BeakerIcon,
          description: 'Emissions monitoring'
        },
        { 
          name: 'Social Impact', 
          href: '/social-impact', 
          icon: UsersIcon,
          description: 'DEI & community metrics'
        },
        { 
          name: 'Benchmarking', 
          href: '/benchmarking', 
          icon: ChartBarSquareIcon,
          description: 'Industry comparisons'
        },
      ]
    }
  ];

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <div className="w-80 h-screen bg-gradient-to-b from-dark-950/95 to-dark-900/98 backdrop-blur-xl border-r border-primary-500/20 flex flex-col">
      {/* Logo Section */}
      <div className="p-6 border-b border-primary-500/20">
        <div className="flex items-center space-x-4">
          <div className="floating-icon bg-gradient-to-br from-primary-500 to-primary-600 shadow-lg">
            <GlobeAltIcon className="w-7 h-7 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-white to-primary-300 bg-clip-text text-transparent">
              ESG Platform
            </h1>
            <p className="text-xs text-text-muted">Sustainable Investment Analytics</p>
          </div>
        </div>
      </div>

      {/* Navigation Sections */}
      <div className="flex-1 overflow-y-auto py-6">
        {navigationSections.map((section, sectionIndex) => (
          <div key={section.title} className="mb-8">
            <h3 className="text-xs font-semibold text-text-muted uppercase tracking-wider px-6 mb-4">
              {section.title}
            </h3>
            <nav className="space-y-2">
              {section.items.map((item, itemIndex) => {
                const Icon = item.icon;
                const active = isActive(item.href);
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`nav-item stagger-item ${active ? 'active' : ''}`}
                    style={{ animationDelay: `${(sectionIndex * 4 + itemIndex) * 100}ms` }}
                  >
                    <div className="floating-icon w-10 h-10 bg-gradient-to-br from-primary-500/20 to-primary-600/10 mr-4">
                      <Icon className="w-5 h-5" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-sm truncate">{item.name}</div>
                      <div className="text-xs text-text-muted truncate">{item.description}</div>
                    </div>
                    {active && (
                      <div className="w-2 h-2 bg-primary-400 rounded-full pulse-ring flex-shrink-0" />
                    )}
                  </Link>
                );
              })}
            </nav>
          </div>
        ))}
      </div>

      {/* Portfolio ESG Score */}
      <div className="p-6 border-t border-primary-500/20">
        <div className="metric-card">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-medium text-text-secondary">Portfolio Score</span>
            <span className="text-2xl font-bold text-primary-400">85.2</span>
          </div>
          <div className="w-full bg-dark-800/50 rounded-full h-2 mb-3">
            <div 
              className="h-2 bg-gradient-to-r from-primary-500 to-primary-400 rounded-full transition-all duration-1000" 
              style={{ width: '85%' }}
            />
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-text-muted">Excellent</span>
            <span className="text-primary-400 font-medium">Top 15%</span>
          </div>
        </div>
      </div>

      {/* Settings */}
      <div className="p-6 border-t border-primary-500/20">
        <Link
          to="/settings"
          className={`nav-item ${isActive('/settings') ? 'active' : ''}`}
        >
          <div className="floating-icon w-10 h-10 bg-gradient-to-br from-primary-500/20 to-primary-600/10 mr-4">
            <CogIcon className="w-5 h-5" />
          </div>
          <div className="flex-1">
            <div className="font-medium text-sm">Settings</div>
            <div className="text-xs text-text-muted">Preferences & config</div>
          </div>
        </Link>
      </div>
    </div>
  );
};

export default Sidebar;