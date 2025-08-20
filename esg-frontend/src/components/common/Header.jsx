// src/components/common/Header.jsx
import React, { useState } from 'react';
import { Search, Bell, Settings, User, TrendingUp, Leaf, Users, Shield } from 'lucide-react';
import { useNotification } from '../../context/NotificationContext';
import { useESGContext } from '../../context/ESGContext'; // We'll create this

const Header = () => {
  const [showNotifications, setShowNotifications] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const { showNotification } = useNotification();
  const { latestAnalysis } = useESGContext(); // Get latest analysis data

  // Use real ESG scores from latest analysis, or default values
  const esgScores = latestAnalysis ? {
    environmental: latestAnalysis.esg_scores?.environmental_score || 0,
    social: latestAnalysis.esg_scores?.social_score || 0,
    governance: latestAnalysis.esg_scores?.governance_score || 0,
    company: latestAnalysis.company_info?.ticker || null
  } : {
    environmental: 67.5, // Default when no analysis
    social: 72.3,
    governance: 74.7,
    company: null
  };

  const handleNewAnalysis = () => {
    showNotification('Starting new ESG analysis...');
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    if (score >= 40) return 'text-orange-400';
    return 'text-red-400';
  };

  const getScoreIcon = (type) => {
    switch (type) {
      case 'environmental': return <Leaf className="w-4 h-4" />;
      case 'social': return <Users className="w-4 h-4" />;
      case 'governance': return <Shield className="w-4 h-4" />;
      default: return <TrendingUp className="w-4 h-4" />;
    }
  };

  return (
    <header className="bg-dark-800 border-b border-dark-700 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Left: Search */}
        <div className="flex items-center space-x-4">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-4 w-4 text-dark-400" />
            </div>
            <input
              type="text"
              placeholder="Search companies..."
              className="
                pl-9 pr-4 py-2 bg-dark-700 border border-dark-600 rounded-lg
                text-white placeholder-dark-400 text-sm
                focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                w-64
              "
            />
            <kbd className="absolute right-2 top-1/2 transform -translate-y-1/2 text-xs text-dark-500">
              ⌘K
            </kbd>
          </div>
        </div>

        {/* Center: ESG Scores */}
        <div className="flex items-center space-x-6">
          {/* Environmental Score */}
          <div className="flex items-center space-x-2">
            <div className={`flex items-center space-x-1 ${getScoreColor(esgScores.environmental)}`}>
              {getScoreIcon('environmental')}
              <span className="text-xs font-medium text-dark-400">ENV</span>
            </div>
            <span className={`font-bold ${getScoreColor(esgScores.environmental)}`}>
              {esgScores.environmental.toFixed(1)}
            </span>
          </div>

          {/* Social Score */}
          <div className="flex items-center space-x-2">
            <div className={`flex items-center space-x-1 ${getScoreColor(esgScores.social)}`}>
              {getScoreIcon('social')}
              <span className="text-xs font-medium text-dark-400">SOC</span>
            </div>
            <span className={`font-bold ${getScoreColor(esgScores.social)}`}>
              {esgScores.social.toFixed(1)}
            </span>
          </div>

          {/* Governance Score */}
          <div className="flex items-center space-x-2">
            <div className={`flex items-center space-x-1 ${getScoreColor(esgScores.governance)}`}>
              {getScoreIcon('governance')}
              <span className="text-xs font-medium text-dark-400">GOV</span>
            </div>
            <span className={`font-bold ${getScoreColor(esgScores.governance)}`}>
              {esgScores.governance.toFixed(1)}
            </span>
          </div>

          {/* Company Indicator */}
          {esgScores.company && (
            <div className="ml-4 px-3 py-1 bg-blue-500/20 border border-blue-500/30 rounded-full">
              <span className="text-xs font-medium text-blue-400">
                {esgScores.company}
              </span>
            </div>
          )}
        </div>

        {/* Right: Actions */}
        <div className="flex items-center space-x-4">
          {/* New Analysis Button */}
          <button
            onClick={handleNewAnalysis}
            className="btn-primary text-sm"
          >
            New Analysis
          </button>

          {/* Notifications */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="p-2 text-dark-400 hover:text-white rounded-lg hover:bg-dark-700 transition-colors relative"
            >
              <Bell className="w-5 h-5" />
              <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>
          </div>

          {/* Settings */}
          <button className="p-2 text-dark-400 hover:text-white rounded-lg hover:bg-dark-700 transition-colors">
            <Settings className="w-5 h-5" />
          </button>

          {/* Profile */}
          <div className="relative">
            <button
              onClick={() => setShowProfile(!showProfile)}
              className="flex items-center space-x-2 p-2 text-dark-400 hover:text-white rounded-lg hover:bg-dark-700 transition-colors"
            >
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-green-500 rounded-full flex items-center justify-center">
                <User className="w-4 h-4 text-white" />
              </div>
              <div className="text-left hidden md:block">
                <div className="text-sm font-medium text-white">Sarah Mitchell</div>
                <div className="text-xs text-dark-400">ESG Research Lead</div>
              </div>
            </button>
          </div>
        </div>
      </div>

      {/* Score Details Tooltip */}
      {esgScores.company && (
        <div className="mt-2 text-center">
          <p className="text-xs text-dark-500">
            Latest analysis for {esgScores.company} • 
            Overall Score: {((esgScores.environmental + esgScores.social + esgScores.governance) / 3).toFixed(1)}/100
          </p>
        </div>
      )}
    </header>
  );
};

export default Header;