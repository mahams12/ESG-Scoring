import React from 'react';
import DashboardStats from '../components/dashboard/DashboardStats';
import QuickActions from '../components/dashboard/QuickActions';
import UpcomingTasks from '../components/dashboard/UpcomingTasks';
import RecentActivity from '../components/dashboard/RecentActivity';
import TaxInsights from '../components/dashboard/TaxInsights';

const Dashboard = () => {
  return (
    <div className="space-y-6 fade-in">
      {/* Welcome Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Welcome back, User!</h1>
        <p className="text-dark-300">Here's an overview of your ESG research activity for this month.</p>
      </div>

      {/* Dashboard Stats */}
      <DashboardStats />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - 2/3 width */}
        <div className="lg:col-span-2 space-y-6">
          <QuickActions />
          <RecentActivity />
        </div>

        {/* Right Column - 1/3 width */}
        <div className="space-y-6">
          <UpcomingTasks />
          <TaxInsights />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;