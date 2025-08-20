import React, { useState } from 'react';
import { MagnifyingGlassIcon, BellIcon, UserCircleIcon, PlusIcon } from '@heroicons/react/24/outline';
import { useNotification } from '../../context/NotificationContext';

const Header = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const { showNotification } = useNotification();

  const handleAddExpense = () => {
    showNotification('Add analysis functionality coming soon!', 'info');
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      showNotification(`Searching for: ${searchQuery}`, 'info');
      setSearchQuery('');
    }
  };

  return (
    <header className="bg-dark-800 border-b border-dark-700 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Search Bar */}
        <div className="flex-1 max-w-lg">
          <form onSubmit={handleSearch} className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-dark-400" />
            <input
              type="text"
              placeholder="Search companies, reports, or ask AI..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white placeholder-dark-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200"
            />
          </form>
        </div>

        {/* Right Side Actions */}
        <div className="flex items-center space-x-4">
          {/* Add Analysis Button */}
          <button
            onClick={handleAddExpense}
            className="btn-primary flex items-center space-x-2"
          >
            <PlusIcon className="w-4 h-4" />
            <span>Add Analysis</span>
          </button>

          {/* Notifications */}
          <button className="relative p-2 text-dark-400 hover:text-white transition-colors duration-200">
            <BellIcon className="w-6 h-6" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-primary-500 rounded-full"></span>
          </button>

          {/* User Profile */}
          <div className="flex items-center space-x-3">
            <div className="text-right">
              <p className="text-sm font-medium text-white">User</p>
              <p className="text-xs text-dark-400">ESG Analyst</p>
            </div>
            <button className="p-1">
              <UserCircleIcon className="w-8 h-8 text-dark-400 hover:text-white transition-colors duration-200" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;