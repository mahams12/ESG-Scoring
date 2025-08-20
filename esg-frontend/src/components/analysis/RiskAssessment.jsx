import React from 'react';
import { ExclamationTriangleIcon, ShieldCheckIcon, ArrowTrendingUpIcon } from '@heroicons/react/24/outline';
import { esgService } from '../../services/esgService';

const RiskAssessment = ({ riskLevel, scores }) => {
  const getRiskIcon = (level) => {
    switch (level?.toLowerCase()) {
      case 'low':
        return ShieldCheckIcon;
      case 'low-medium':
      case 'medium':
        return ExclamationTriangleIcon;
      case 'medium-high':
      case 'high':
        return ExclamationTriangleIcon;
      default:
        return ExclamationTriangleIcon;
    }
  };

  const getRiskDescription = (level) => {
    switch (level?.toLowerCase()) {
      case 'low':
        return 'Minimal ESG-related risks identified. Strong governance and compliance.';
      case 'low-medium':
        return 'Some areas for improvement but overall strong ESG performance.';
      case 'medium':
        return 'Moderate ESG risks requiring attention and monitoring.';
      case 'medium-high':
        return 'Several ESG concerns that could impact long-term performance.';
      case 'high':
        return 'Significant ESG risks requiring immediate attention.';
      default:
        return 'Risk assessment in progress.';
    }
  };

  const riskFactors = [
    {
      category: 'Environmental',
      risk: scores.environmental < 70 ? 'High' : scores.environmental < 85 ? 'Medium' : 'Low',
      description: 'Climate change adaptation and carbon footprint management'
    },
    {
      category: 'Social',
      risk: scores.social < 70 ? 'High' : scores.social < 85 ? 'Medium' : 'Low',
      description: 'Employee relations and community impact considerations'
    },
    {
      category: 'Governance',
      risk: scores.governance < 70 ? 'High' : scores.governance < 85 ? 'Medium' : 'Low',
      description: 'Board oversight and transparency in decision making'
    }
  ];

  const Icon = getRiskIcon(riskLevel);

  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold text-white mb-6">Risk Assessment</h3>

      {/* Overall Risk Level */}
      <div className="mb-6 p-4 bg-dark-900 rounded-lg">
        <div className="flex items-center space-x-3 mb-3">
          <Icon className={`w-8 h-8 ${esgService.getRiskColor(riskLevel)}`} />
          <div>
            <h4 className="font-medium text-white">Overall Risk Level</h4>
            <p className={`text-lg font-semibold ${esgService.getRiskColor(riskLevel)}`}>
              {riskLevel}
            </p>
          </div>
        </div>
        <p className="text-sm text-dark-300">
          {getRiskDescription(riskLevel)}
        </p>
      </div>

      {/* Risk Factors */}
      <div className="space-y-4">
        <h5 className="font-medium text-white">Risk Factors by Category</h5>
        {riskFactors.map((factor, index) => (
          <div key={index} className="flex items-start space-x-3 p-3 bg-dark-900 rounded-lg">
            <div className="flex-1">
              <div className="flex items-center justify-between mb-2">
                <h6 className="font-medium text-white">{factor.category}</h6>
                <span className={`text-sm font-medium px-2 py-1 rounded ${
                  factor.risk === 'Low' ? 'bg-success-500/20 text-success-400' :
                  factor.risk === 'Medium' ? 'bg-warning-500/20 text-warning-400' :
                  'bg-danger-500/20 text-danger-400'
                }`}>
                  {factor.risk} Risk
                </span>
              </div>
              <p className="text-xs text-dark-400">{factor.description}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Mitigation Strategies */}
      <div className="mt-6 p-4 bg-primary-600/10 border border-primary-600/20 rounded-lg">
        <div className="flex items-center space-x-2 mb-3">
          <ArrowTrendingUpIcon className="w-5 h-5 text-primary-400" />
          <h5 className="font-medium text-white">Recommended Actions</h5>
        </div>
        <ul className="text-sm text-primary-200 space-y-1">
          <li>• Enhance ESG reporting transparency</li>
          <li>• Implement comprehensive sustainability metrics</li>
          <li>• Regular stakeholder engagement programs</li>
          <li>• Continuous monitoring of ESG performance</li>
        </ul>
      </div>
    </div>
  );
};

export default RiskAssessment;