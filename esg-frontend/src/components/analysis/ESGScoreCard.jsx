import React from 'react';
import { GlobeAltIcon, UsersIcon, ShieldCheckIcon } from '@heroicons/react/24/outline';
import { esgService } from '../../services/esgService';

const ESGScoreCard = ({ scores }) => {
  const categories = [
    {
      name: 'Environmental',
      score: scores.environmental,
      icon: GlobeAltIcon, // Changed from LeafIcon
      color: 'bg-green-500',
      description: 'Climate impact, resource usage, waste management'
    },
    {
      name: 'Social',
      score: scores.social,
      icon: UsersIcon,
      color: 'bg-blue-500',
      description: 'Employee relations, community impact, human rights'
    },
    {
      name: 'Governance',
      score: scores.governance,
      icon: ShieldCheckIcon,
      color: 'bg-purple-500',
      description: 'Board structure, executive compensation, transparency'
    }
  ];

  // Rest of the component remains the same...
  const CircularProgress = ({ score, size = 120 }) => {
    const radius = size / 2 - 10;
    const circumference = 2 * Math.PI * radius;
    const strokeDasharray = circumference;
    const strokeDashoffset = circumference - (score / 100) * circumference;

    return (
      <div className="relative" style={{ width: size, height: size }}>
        <svg
          className="transform -rotate-90"
          width={size}
          height={size}
        >
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth="8"
            fill="transparent"
            className="text-dark-700"
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth="8"
            fill="transparent"
            strokeDasharray={strokeDasharray}
            strokeDashoffset={strokeDashoffset}
            className={esgService.getScoreColor(score)}
            strokeLinecap="round"
            style={{
              transition: 'stroke-dashoffset 1s ease-in-out'
            }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-bold text-white">
            {esgService.formatScore(score)}
          </span>
          <span className="text-xs text-dark-400">Score</span>
        </div>
      </div>
    );
  };

  return (
    <div className="card p-6">
      <h3 className="text-xl font-semibold text-white mb-6">ESG Scorecard</h3>
      
      {/* Overall Score */}
      <div className="flex items-center justify-between mb-8 p-6 bg-dark-900 rounded-xl">
        <div className="flex-1">
          <h4 className="text-lg font-medium text-white mb-2">Overall ESG Score</h4>
          <div className="flex items-center space-x-4">
            <span className={`text-3xl font-bold ${esgService.getScoreColor(scores.overall)}`}>
              {esgService.formatScore(scores.overall)}
            </span>
            <span className={`text-xl font-semibold px-3 py-1 rounded-lg border ${esgService.getScoreColor(scores.overall)}`}>
              {esgService.getScoreGrade(scores.overall)}
            </span>
          </div>
          <p className="text-sm text-dark-400 mt-2">
            Excellent ESG performance - top quartile in industry
          </p>
        </div>
        <CircularProgress score={scores.overall} />
      </div>

      {/* Individual Categories */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {categories.map((category, index) => {
          const Icon = category.icon;
          return (
            <div 
              key={category.name} 
              className="bg-dark-900 rounded-xl p-6 hover:bg-dark-850 transition-colors duration-200"
              style={{ animationDelay: `${index * 150}ms` }}
            >
              <div className="flex items-center space-x-3 mb-4">
                <div className={`w-10 h-10 ${category.color} rounded-lg flex items-center justify-center`}>
                  <Icon className="w-5 h-5 text-white" />
                </div>
                <h5 className="font-medium text-white">{category.name}</h5>
              </div>
              
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className={`text-2xl font-bold ${esgService.getScoreColor(category.score)}`}>
                    {esgService.formatScore(category.score)}
                  </span>
                  <span className="text-sm text-dark-400">
                    {esgService.getScoreGrade(category.score)}
                  </span>
                </div>
                
                {/* Progress Bar */}
                <div className="w-full bg-dark-700 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-1000 ease-out ${
                      category.score >= 85 ? 'bg-success-500' :
                      category.score >= 70 ? 'bg-success-600' :
                      category.score >= 50 ? 'bg-warning-500' : 'bg-danger-500'
                    }`}
                    style={{ 
                      width: `${category.score}%`,
                      transitionDelay: `${index * 200}ms`
                    }}
                  />
                </div>
              </div>
              
              <p className="text-xs text-dark-400 leading-relaxed">
                {category.description}
              </p>
            </div>
          );
        })}
      </div>

      {/* Score Breakdown */}
      <div className="mt-8 p-4 bg-dark-900 rounded-xl">
        <h6 className="font-medium text-white mb-3">Score Breakdown</h6>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="flex justify-between">
            <span className="text-dark-400">Environmental Weight:</span>
            <span className="text-white">35%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-dark-400">Social Weight:</span>
            <span className="text-white">35%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-dark-400">Governance Weight:</span>
            <span className="text-white">30%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-dark-400">Last Updated:</span>
            <span className="text-white">Real-time</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ESGScoreCard;