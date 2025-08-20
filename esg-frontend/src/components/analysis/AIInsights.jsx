import React, { useState } from 'react';
import { Brain, TrendingUp, AlertTriangle, CheckCircle, Download, Eye } from 'lucide-react';
import ESGReportDownload from './ESGReportDownload';

const AIInsights = ({ 
  insights = {}, 
  ticker, 
  companyName,
  isLoading = false 
}) => {
  const [expandedInsight, setExpandedInsight] = useState(null);

  const insightCategories = [
    {
      title: 'Key Strengths',
      icon: CheckCircle,
      color: 'green',
      items: insights.strengths || [
        'Strong environmental compliance record',
        'Diverse and inclusive workforce policies',
        'Transparent governance structure'
      ]
    },
    {
      title: 'Areas of Concern',
      icon: AlertTriangle,
      color: 'yellow',
      items: insights.concerns || [
        'Limited renewable energy adoption',
        'Board diversity could be improved'
      ]
    },
    {
      title: 'Growth Opportunities',
      icon: TrendingUp,
      color: 'blue',
      items: insights.opportunities || [
        'Potential for carbon footprint reduction',
        'Enhanced stakeholder engagement programs'
      ]
    }
  ];

  const getColorClasses = (color) => {
    const colors = {
      green: 'bg-green-500/10 border-green-500/20 text-green-400',
      yellow: 'bg-yellow-500/10 border-yellow-500/20 text-yellow-400',
      blue: 'bg-blue-500/10 border-blue-500/20 text-blue-400'
    };
    return colors[color] || colors.blue;
  };

  if (isLoading) {
    return (
      <div className="bg-dark-800 border border-dark-700 rounded-xl p-6">
        <div className="flex items-center space-x-3 mb-6">
          <Brain className="w-6 h-6 text-blue-400 animate-pulse" />
          <h3 className="text-lg font-semibold text-white">AI Analysis</h3>
        </div>
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="h-4 bg-dark-700 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-dark-700 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-dark-800 border border-dark-700 rounded-xl p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <Brain className="w-6 h-6 text-blue-400" />
          <h3 className="text-lg font-semibold text-white">AI Analysis Insights</h3>
        </div>
        
        {/* Download Options */}
        <div className="flex items-center space-x-2">
          <button className="p-2 text-dark-400 hover:text-white rounded-lg hover:bg-dark-700 transition-colors">
            <Eye className="w-4 h-4" />
          </button>
          <ESGReportDownload 
            ticker={ticker}
            companyName={companyName}
            className="scale-90"
          />
        </div>
      </div>

      {/* Overall AI Summary */}
      {insights.summary && (
        <div className="mb-6 p-4 bg-dark-700 border border-dark-600 rounded-lg">
          <h4 className="font-medium text-white mb-2">Executive Summary</h4>
          <p className="text-dark-300 text-sm leading-relaxed">
            {insights.summary}
          </p>
        </div>
      )}

      {/* Insight Categories */}
      <div className="space-y-4">
        {insightCategories.map((category, categoryIndex) => {
          const Icon = category.icon;
          
          return (
            <div
              key={categoryIndex}
              className={`border rounded-lg ${getColorClasses(category.color)}`}
            >
              <div className="p-4">
                <div className="flex items-center space-x-3 mb-3">
                  <Icon className="w-5 h-5" />
                  <h4 className="font-medium text-white">{category.title}</h4>
                  <span className="text-sm text-dark-400">
                    ({category.items.length})
                  </span>
                </div>
                
                <div className="space-y-2">
                  {category.items.map((item, itemIndex) => (
                    <div
                      key={itemIndex}
                      className="flex items-start space-x-2 text-sm"
                    >
                      <span className="text-current mt-1">•</span>
                      <span className="text-dark-300 flex-1">{item}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* AI Confidence Score */}
      <div className="mt-6 pt-4 border-t border-dark-700">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-dark-400">AI Analysis Confidence</p>
            <div className="flex items-center space-x-2 mt-1">
              <div className="w-24 h-2 bg-dark-700 rounded-full">
                <div 
                  className="h-2 bg-blue-500 rounded-full"
                  style={{ width: `${insights.confidence || 85}%` }}
                />
              </div>
              <span className="text-sm font-medium text-white">
                {insights.confidence || 85}%
              </span>
            </div>
          </div>
          
          <div className="text-right">
            <p className="text-xs text-dark-500">
              Based on {insights.dataPoints || 147} data points
            </p>
            <p className="text-xs text-dark-500">
              Last updated: {new Date().toLocaleDateString()}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIInsights;