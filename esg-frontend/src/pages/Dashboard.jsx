import React, { useState, useEffect } from 'react';
import DashboardStats from '../components/dashboard/DashboardStats';
import QuickActions from '../components/dashboard/QuickActions';
import RecentActivity from '../components/dashboard/RecentActivity';
import LoadingSpinner from '../components/common/LoadingSpinner';

const Dashboard = () => {
  const [esgData, setEsgData] = useState({});
  const [recentCompanies, setRecentCompanies] = useState([]);
  const [activities, setActivities] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        
        // In a real app, these would be API calls
        // For now, using mock data
        const mockEsgData = {
          totalAnalyzed: 247,
          newAnalysesThisWeek: 15,
          averageScore: 67,
          scoreImprovement: 3,
          highRiskCount: 12,
          riskChange: -2,
          reportsGenerated: 89,
          reportsThisWeek: 8
        };

        const mockRecentCompanies = [
          { ticker: 'MSFT', name: 'Microsoft Corporation', esgScore: 85, riskLevel: 'Low', lastAnalyzed: '2 hours ago' },
          { ticker: 'AAPL', name: 'Apple Inc.', esgScore: 78, riskLevel: 'Low', lastAnalyzed: '1 day ago' },
          { ticker: 'TSLA', name: 'Tesla Inc.', esgScore: 62, riskLevel: 'Medium', lastAnalyzed: '2 days ago' },
          { ticker: 'GOOGL', name: 'Alphabet Inc.', esgScore: 73, riskLevel: 'Low', lastAnalyzed: '3 days ago' },
          { ticker: 'AMZN', name: 'Amazon.com Inc.', esgScore: 58, riskLevel: 'Medium', lastAnalyzed: '1 week ago' }
        ];

        setEsgData(mockEsgData);
        setRecentCompanies(mockRecentCompanies);
        
        // Activities would come from your backend
        setActivities([]);
        
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-dark-950 flex items-center justify-center">
        <LoadingSpinner size="large" message="Loading dashboard..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-dark-950 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">ESG Analysis Dashboard</h1>
          <p className="text-dark-400">
            Monitor ESG performance and generate comprehensive sustainability reports
          </p>
        </div>

        {/* Stats */}
        <DashboardStats esgData={esgData} />

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Quick Actions - 2/3 width */}
          <div className="lg:col-span-2">
            <QuickActions 
              recentCompanies={recentCompanies}
              onCompanySearch={(ticker) => {
                // Navigate to analysis page
                window.location.href = `/analysis/${ticker}`;
              }}
            />
          </div>

          {/* Recent Activity - 1/3 width */}
          <div className="lg:col-span-1">
            <RecentActivity activities={activities} />
          </div>
        </div>

        {/* Recent Companies Table */}
        {recentCompanies.length > 0 && (
          <div className="bg-dark-800 border border-dark-700 rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-white">Recently Analyzed Companies</h3>
              <button 
                onClick={() => window.location.href = '/analysis'}
                className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
              >
                Analyze New Company →
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-dark-700">
                    <th className="text-left py-3 px-4 text-dark-400 font-medium">Company</th>
                    <th className="text-left py-3 px-4 text-dark-400 font-medium">ESG Score</th>
                    <th className="text-left py-3 px-4 text-dark-400 font-medium">Risk Level</th>
                    <th className="text-left py-3 px-4 text-dark-400 font-medium">Last Analyzed</th>
                    <th className="text-left py-3 px-4 text-dark-400 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {recentCompanies.map((company, index) => (
                    <tr 
                      key={index}
                      className="border-b border-dark-800 hover:bg-dark-700/50 transition-colors"
                    >
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 bg-dark-700 rounded-full flex items-center justify-center">
                            <span className="text-xs font-bold text-white">
                              {company.ticker.charAt(0)}
                            </span>
                          </div>
                          <div>
                            <div className="font-medium text-white">{company.name}</div>
                            <div className="text-sm text-dark-400">{company.ticker}</div>
                          </div>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-2">
                          <span className={`font-bold ${
                            company.esgScore >= 70 ? 'text-green-400' : 
                            company.esgScore >= 50 ? 'text-yellow-400' : 'text-red-400'
                          }`}>
                            {company.esgScore}
                          </span>
                          <span className="text-dark-400">/100</span>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${
                          company.riskLevel === 'Low' ? 'bg-green-500/20 text-green-400' :
                          company.riskLevel === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-red-500/20 text-red-400'
                        }`}>
                          {company.riskLevel} Risk
                        </span>
                      </td>
                      <td className="py-3 px-4 text-dark-300">
                        {company.lastAnalyzed}
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={() => window.location.href = `/analysis/${company.ticker}`}
                            className="text-blue-400 hover:text-blue-300 text-sm transition-colors"
                          >
                            View
                          </button>
                          <span className="text-dark-600">|</span>
                          <button className="text-green-400 hover:text-green-300 text-sm transition-colors">
                            Download
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;