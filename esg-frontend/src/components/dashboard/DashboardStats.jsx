import React from 'react';
import { 
  ChartBarIcon, 
  ArrowTrendingUpIcon, // Changed from TrendingUpIcon
  BuildingOfficeIcon, 
  CurrencyDollarIcon 
} from '@heroicons/react/24/outline';

const DashboardStats = () => {
  const stats = [
    {
      title: 'Total Analyses',
      value: '127',
      change: '+12.5% from last month',
      changeType: 'positive',
      icon: ChartBarIcon,
      iconBg: 'bg-blue-500',
      period: 'This Month'
    },
    {
      title: 'Avg ESG Score',
      value: '82.4',
      change: '+2.1 points this quarter',
      changeType: 'positive',
      icon: ArrowTrendingUpIcon, // Updated icon
      iconBg: 'bg-green-500',
      period: 'Portfolio Average'
    },
    {
      title: 'Companies Tracked',
      value: '45',
      change: '5 new this month',
      changeType: 'neutral',
      icon: BuildingOfficeIcon,
      iconBg: 'bg-purple-500',
      period: 'Active Portfolio'
    },
    {
      title: 'Portfolio Value',
      value: '$2.4M',
      change: '+8.3% from last quarter',
      changeType: 'positive',
      icon: CurrencyDollarIcon,
      iconBg: 'bg-orange-500',
      period: 'Current Value'
    }
  ];

  const getChangeColor = (type) => {
    switch (type) {
      case 'positive':
        return 'text-success-500';
      case 'negative':
        return 'text-danger-500';
      default:
        return 'text-dark-400';
    }
  };

  const getChangeIcon = (type) => {
    switch (type) {
      case 'positive':
        return '↗️';
      case 'negative':
        return '↘️';
      default:
        return '📊';
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat, index) => {
        const Icon = stat.icon;
        return (
          <div 
            key={index} 
            className="stat-card slide-up" 
            style={{ animationDelay: `${index * 100}ms` }}
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex-1">
                <p className="text-sm font-medium text-dark-400 mb-1">{stat.title}</p>
                <p className="text-3xl font-bold text-white">{stat.value}</p>
              </div>
              <div className={`w-14 h-14 ${stat.iconBg} rounded-xl flex items-center justify-center shadow-lg`}>
                <Icon className="w-7 h-7 text-white" />
              </div>
            </div>
            
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="text-lg">{getChangeIcon(stat.changeType)}</span>
                <p className={`text-sm font-medium ${getChangeColor(stat.changeType)}`}>
                  {stat.change}
                </p>
              </div>
            </div>
            
            <div className="mt-3 pt-3 border-t border-dark-700">
              <p className="text-xs text-dark-500 font-medium">{stat.period}</p>
            </div>

            {/* Mini progress indicator */}
            <div className="mt-2">
              <div className="w-full bg-dark-700 rounded-full h-1">
                <div 
                  className={`h-1 rounded-full transition-all duration-1000 ease-out ${
                    stat.changeType === 'positive' ? 'bg-success-500' : 
                    stat.changeType === 'negative' ? 'bg-danger-500' : 'bg-primary-500'
                  }`}
                  style={{ 
                    width: `${Math.random() * 40 + 40}%`,
                    transitionDelay: `${index * 200}ms`
                  }}
                />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default DashboardStats;