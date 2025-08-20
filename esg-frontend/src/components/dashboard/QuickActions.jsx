import React from 'react';
import { Search, TrendingUp, Download, BookOpen, Zap } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const QuickActions = ({ onCompanySearch, recentCompanies = [] }) => {
  const navigate = useNavigate();

  const primaryActions = [
    {
      title: 'Analyze Company',
      description: 'Get comprehensive ESG analysis',
      icon: Search,
      color: 'blue',
      action: () => navigate('/analysis')
    },
    {
      title: 'Market Trends',
      description: 'View ESG market insights',
      icon: TrendingUp,
      color: 'green',
      action: () => navigate('/analysis?view=trends')
    },
    {
      title: 'Bulk Analysis',
      description: 'Analyze multiple companies',
      icon: Zap,
      color: 'purple',
      action: () => navigate('/analysis?mode=bulk')
    },
    {
      title: 'ESG Guide',
      description: 'Learn about ESG metrics',
      icon: BookOpen,
      color: 'orange',
      action: () => navigate('/analysis?view=guide')
    }
  ];

  const getColorClasses = (color) => {
    const colors = {
      blue: 'bg-blue-500/10 hover:bg-blue-500/20 border-blue-500/20 text-blue-400',
      green: 'bg-green-500/10 hover:bg-green-500/20 border-green-500/20 text-green-400',
      purple: 'bg-purple-500/10 hover:bg-purple-500/20 border-purple-500/20 text-purple-400',
      orange: 'bg-orange-500/10 hover:bg-orange-500/20 border-orange-500/20 text-orange-400'
    };
    return colors[color] || colors.blue;
  };

  return (
    <div className="space-y-6">
      {/* Primary Actions */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {primaryActions.map((action, index) => {
            const Icon = action.icon;
            
            return (
              <button
                key={index}
                onClick={action.action}
                className={`
                  p-4 rounded-xl border transition-all text-left group
                  ${getColorClasses(action.color)}
                `}
              >
                <div className="flex items-start space-x-3">
                  <div className="p-2 rounded-lg bg-current bg-opacity-20">
                    <Icon className="w-5 h-5" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-white group-hover:text-current transition-colors">
                      {action.title}
                    </h4>
                    <p className="text-sm text-dark-400 mt-1">
                      {action.description}
                    </p>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Recent Companies */}
      {recentCompanies.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-white mb-4">Recently Analyzed</h3>
          <div className="space-y-2">
            {recentCompanies.slice(0, 5).map((company, index) => (
              <button
                key={index}
                onClick={() => navigate(`/analysis/${company.ticker}`)}
                className="w-full flex items-center justify-between p-3 bg-dark-800 hover:bg-dark-700 border border-dark-700 hover:border-dark-600 rounded-lg transition-all group"
              >
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-dark-700 rounded-full flex items-center justify-center">
                    <span className="text-xs font-bold text-white">
                      {company.ticker.charAt(0)}
                    </span>
                  </div>
                  <div className="text-left">
                    <div className="font-medium text-white group-hover:text-blue-400 transition-colors">
                      {company.name}
                    </div>
                    <div className="text-sm text-dark-400">
                      {company.ticker} • Score: {company.esgScore}/100
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className={`text-sm font-medium ${
                    company.esgScore >= 70 ? 'text-green-400' : 
                    company.esgScore >= 50 ? 'text-yellow-400' : 'text-red-400'
                  }`}>
                    {company.riskLevel}
                  </div>
                  <div className="text-xs text-dark-500">
                    {company.lastAnalyzed}
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default QuickActions;