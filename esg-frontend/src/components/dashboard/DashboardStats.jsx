import React from 'react';
import { TrendingUp, Leaf, Shield, Users, BarChart3, Download } from 'lucide-react';

const DashboardStats = ({ esgData = {} }) => {
  const stats = [
    {
      title: 'Companies Analyzed',
      value: esgData.totalAnalyzed || 0,
      change: esgData.newAnalysesThisWeek || 0,
      changeType: 'increase',
      icon: BarChart3,
      color: 'blue'
    },
    {
      title: 'Avg ESG Score',
      value: esgData.averageScore || 0,
      change: esgData.scoreImprovement || 0,
      changeType: esgData.scoreImprovement > 0 ? 'increase' : 'decrease',
      icon: Leaf,
      color: 'green',
      suffix: '/100'
    },
    {
      title: 'High Risk Companies',
      value: esgData.highRiskCount || 0,
      change: esgData.riskChange || 0,
      changeType: esgData.riskChange > 0 ? 'decrease' : 'increase', // Reversed because less risk is good
      icon: Shield,
      color: 'red'
    },
    {
      title: 'Reports Generated',
      value: esgData.reportsGenerated || 0,
      change: esgData.reportsThisWeek || 0,
      changeType: 'increase',
      icon: Download,
      color: 'purple'
    }
  ];

  const getColorClasses = (color) => {
    const colors = {
      blue: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
      green: 'bg-green-500/10 text-green-400 border-green-500/20',
      red: 'bg-red-500/10 text-red-400 border-red-500/20',
      purple: 'bg-purple-500/10 text-purple-400 border-purple-500/20'
    };
    return colors[color] || colors.blue;
  };

  const getChangeIcon = (changeType) => {
    return changeType === 'increase' ? '↗️' : '↘️';
  };

  const getChangeColor = (changeType) => {
    return changeType === 'increase' ? 'text-green-400' : 'text-red-400';
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat, index) => {
        const Icon = stat.icon;
        
        return (
          <div
            key={index}
            className="bg-dark-800 border border-dark-700 rounded-xl p-6 hover:border-dark-600 transition-all"
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-dark-400 text-sm font-medium mb-1">
                  {stat.title}
                </p>
                <div className="flex items-baseline space-x-1">
                  <h3 className="text-2xl font-bold text-white">
                    {stat.value.toLocaleString()}
                  </h3>
                  {stat.suffix && (
                    <span className="text-dark-400 text-sm">{stat.suffix}</span>
                  )}
                </div>
                
                {stat.change !== 0 && (
                  <div className={`flex items-center space-x-1 mt-2 ${getChangeColor(stat.changeType)}`}>
                    <span className="text-xs">
                      {getChangeIcon(stat.changeType)}
                    </span>
                    <span className="text-xs font-medium">
                      {Math.abs(stat.change)} this week
                    </span>
                  </div>
                )}
              </div>
              
              <div className={`p-3 rounded-lg border ${getColorClasses(stat.color)}`}>
                <Icon className="w-6 h-6" />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default DashboardStats;
