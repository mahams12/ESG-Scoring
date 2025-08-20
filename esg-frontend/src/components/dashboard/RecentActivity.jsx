import React from 'react';
import { 
  BuildingOfficeIcon, 
  DocumentTextIcon,
  ChartBarIcon,
  UserIcon
} from '@heroicons/react/24/outline';

const RecentActivity = () => {
  const activities = [
    {
      title: 'Apple Inc. ESG analysis completed',
      time: '2 hours ago',
      amount: '$150.00',
      type: 'analysis',
      icon: BuildingOfficeIcon
    },
    {
      title: 'Monthly ESG report generated',
      time: '1 day ago',
      type: 'report',
      icon: DocumentTextIcon
    },
    {
      title: 'Quarterly benchmarking updated',
      time: '2 days ago',
      type: 'benchmark',
      icon: ChartBarIcon
    },
    {
      title: 'New user joined ESG team',
      time: '3 days ago',
      type: 'user',
      icon: UserIcon
    }
  ];

  const getActivityColor = (type) => {
    switch (type) {
      case 'analysis':
        return 'bg-green-500';
      case 'report':
        return 'bg-blue-500';
      case 'benchmark':
        return 'bg-purple-500';
      case 'user':
        return 'bg-orange-500';
      default:
        return 'bg-dark-500';
    }
  };

  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold text-white mb-6">Recent Activity</h3>
      <div className="space-y-4">
        {activities.map((activity, index) => {
          const Icon = activity.icon;
          return (
            <div key={index} className="flex items-center space-x-4 p-3 rounded-lg hover:bg-dark-750 transition-colors duration-200">
              <div className={`w-10 h-10 ${getActivityColor(activity.type)} rounded-lg flex items-center justify-center`}>
                <Icon className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1">
                <h4 className="font-medium text-white">{activity.title}</h4>
                <p className="text-sm text-dark-400">{activity.time}</p>
              </div>
              {activity.amount && (
                <span className="font-medium text-white">{activity.amount}</span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default RecentActivity;