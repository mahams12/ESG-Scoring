import React from 'react';
import { TrendingUp, TrendingDown, Minus, Leaf, Users, Shield } from 'lucide-react';
import ESGReportDownload from './ESGReportDownload';

const ESGScoreCard = ({ 
  company, 
  esgData, 
  industryBenchmark = {}, 
  className = '' 
}) => {
  const getScoreColor = (score) => {
    if (score >= 70) return 'text-green-400';
    if (score >= 50) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getScoreBackground = (score) => {
    if (score >= 70) return 'bg-green-500/10 border-green-500/20';
    if (score >= 50) return 'bg-yellow-500/10 border-yellow-500/20';
    return 'bg-red-500/10 border-red-500/20';
  };

  const getTrendIcon = (current, benchmark) => {
    if (current > benchmark + 5) return <TrendingUp className="w-4 h-4 text-green-400" />;
    if (current < benchmark - 5) return <TrendingDown className="w-4 h-4 text-red-400" />;
    return <Minus className="w-4 h-4 text-yellow-400" />;
  };

  const categories = [
    {
      name: 'Environmental',
      icon: Leaf,
      score: esgData?.environmental || 0,
      benchmark: industryBenchmark?.environmental || 0,
      description: 'Climate impact, resource use, pollution'
    },
    {
      name: 'Social',
      icon: Users,
      score: esgData?.social || 0,
      benchmark: industryBenchmark?.social || 0,
      description: 'Labor practices, community relations, diversity'
    },
    {
      name: 'Governance',
      icon: Shield,
      score: esgData?.governance || 0,
      benchmark: industryBenchmark?.governance || 0,
      description: 'Board structure, ethics, transparency'
    }
  ];

  const overallScore = esgData?.overall_score || 0;
  const overallBenchmark = industryBenchmark?.overall || 0;

  return (
    <div className={`bg-dark-800 border border-dark-700 rounded-xl p-6 ${className}`}>
      {/* Header with Company Info and Download */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-white mb-2">ESG Score Analysis</h2>
          <p className="text-dark-400">
            {company?.name} ({company?.ticker}) • {company?.industry}
          </p>
        </div>
        
        {/* Download Button */}
        <ESGReportDownload 
          ticker={company?.ticker}
          companyName={company?.name}
        />
      </div>

      {/* Overall Score */}
      <div className={`p-6 rounded-xl border mb-6 ${getScoreBackground(overallScore)}`}>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-white mb-1">Overall ESG Score</h3>
            <div className="flex items-center space-x-2">
              <span className={`text-3xl font-bold ${getScoreColor(overallScore)}`}>
                {overallScore}
              </span>
              <span className="text-dark-400">/100</span>
              {getTrendIcon(overallScore, overallBenchmark)}
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-dark-400">Industry Average</p>
            <p className="text-xl font-semibold text-dark-300">{overallBenchmark}</p>
          </div>
        </div>
        
        {/* Risk Level */}
        <div className="mt-4">
          <span className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${
            overallScore >= 70 ? 'bg-green-500/20 text-green-400' :
            overallScore >= 50 ? 'bg-yellow-500/20 text-yellow-400' :
            'bg-red-500/20 text-red-400'
          }`}>
            {overallScore >= 70 ? 'Low Risk' : overallScore >= 50 ? 'Medium Risk' : 'High Risk'}
          </span>
        </div>
      </div>

      {/* Category Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {categories.map((category) => {
          const Icon = category.icon;
          
          return (
            <div
              key={category.name}
              className="bg-dark-700 border border-dark-600 rounded-lg p-4 hover:border-dark-500 transition-colors"
            >
              <div className="flex items-center space-x-3 mb-3">
                <div className={`p-2 rounded-lg ${getScoreBackground(category.score)}`}>
                  <Icon className="w-5 h-5" />
                </div>
                <h4 className="font-medium text-white">{category.name}</h4>
              </div>
              
              <div className="flex items-center justify-between mb-2">
                <span className={`text-2xl font-bold ${getScoreColor(category.score)}`}>
                  {category.score}
                </span>
                <div className="flex items-center space-x-1">
                  {getTrendIcon(category.score, category.benchmark)}
                  <span className="text-sm text-dark-400">vs {category.benchmark}</span>
                </div>
              </div>
              
              <p className="text-xs text-dark-500">
                {category.description}
              </p>
              
              {/* Progress Bar */}
              <div className="mt-3 w-full bg-dark-600 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all ${
                    category.score >= 70 ? 'bg-green-500' :
                    category.score >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${category.score}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div className="mt-6 pt-6 border-t border-dark-700">
        <div className="flex items-center justify-between">
          <div className="text-sm text-dark-400">
            Last updated: {new Date().toLocaleDateString()}
          </div>
          <div className="flex space-x-2">
            <button className="btn-secondary text-sm">
              View Details
            </button>
            <button className="btn-primary text-sm">
              Compare with Peers
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ESGScoreCard;