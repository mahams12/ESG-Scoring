import React from 'react';
import { Clock, TrendingUp, Download, AlertTriangle, CheckCircle } from 'lucide-react';

const RecentActivity = ({ activities = [] }) => {
  const getActivityIcon = (type) => {
    switch (type) {
      case 'analysis': return <TrendingUp className="w-4 h-4" />;
      case 'download': return <Download className="w-4 h-4" />;
      case 'alert': return <AlertTriangle className="w-4 h-4" />;
      case 'completed': return <CheckCircle className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  const getActivityColor = (type) => {
    switch (type) {
      case 'analysis': return 'text-blue-400';
      case 'download': return 'text-green-400';
      case 'alert': return 'text-yellow-400';
      case 'completed': return 'text-green-400';
      default: return 'text-dark-400';
    }
  };

  const defaultActivities = [
    {
      id: 1,
      type: 'analysis',
      title: 'ESG analysis completed',
      description: 'Microsoft Corporation (MSFT)',
      timestamp: '2 minutes ago',
      score: 85
    },
    {
      id: 2,
      type: 'download',
      title: 'Report downloaded',
      description: 'Apple Inc. ESG Report (PDF)',
      timestamp: '15 minutes ago'
    },
    {
      id: 3,
      type: 'alert',
      title: 'Risk level changed',
      description: 'Tesla Inc. (TSLA) - Medium to High risk',
      timestamp: '1 hour ago'
    },
    {
      id: 4,
      type: 'analysis',
      title: 'Bulk analysis started',
      description: '15 companies in Technology sector',
      timestamp: '3 hours ago'
    },
    {
      id: 5,
      type: 'completed',
      title: 'Benchmark comparison ready',
      description: 'S&P 500 ESG performance analysis',
      timestamp: '1 day ago'
    }
  ];

  const displayActivities = activities.length > 0 ? activities : defaultActivities;

  return (
    <div className="bg-dark-800 border border-dark-700 rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-white">Recent Activity</h3>
        <button className="text-sm text-blue-400 hover:text-blue-300 transition-colors">
          View All
        </button>
      </div>

      <div className="space-y-4">
        {displayActivities.slice(0, 5).map((activity) => (
          <div key={activity.id} className="flex items-start space-x-3 group">
            <div className={`p-2 rounded-lg bg-dark-700 ${getActivityColor(activity.type)}`}>
              {getActivityIcon(activity.type)}
            </div>
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <p className="font-medium text-white group-hover:text-blue-400 transition-colors">
                  {activity.title}
                </p>
                {activity.score && (
                  <span className={`text-sm font-medium px-2 py-1 rounded ${
                    activity.score >= 70 ? 'bg-green-500/20 text-green-400' :
                    activity.score >= 50 ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-red-500/20 text-red-400'
                  }`}>
                    {activity.score}/100
                  </span>
                )}
              </div>
              <p className="text-sm text-dark-400 mt-1">
                {activity.description}
              </p>
              <p className="text-xs text-dark-500 mt-1">
                {activity.timestamp}
              </p>
            </div>
          </div>
        ))}
      </div>

      {displayActivities.length === 0 && (
        <div className="text-center py-8">
          <Clock className="w-12 h-12 text-dark-600 mx-auto mb-3" />
          <p className="text-dark-400">No recent activity</p>
          <p className="text-sm text-dark-500 mt-1">
            Start by analyzing a company to see activity here
          </p>
        </div>
      )}
    </div>
  );
};

export default RecentActivity;