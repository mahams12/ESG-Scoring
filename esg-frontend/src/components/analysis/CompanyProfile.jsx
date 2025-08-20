import React from 'react';
import { BuildingOfficeIcon, UsersIcon, MapPinIcon, CalendarIcon } from '@heroicons/react/24/outline';

const CompanyProfile = ({ company }) => {
  const formatMarketCap = (value) => {
    if (value >= 1e12) return `$${(value / 1e12).toFixed(1)}T`;
    if (value >= 1e9) return `$${(value / 1e9).toFixed(1)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
    return `$${value}`;
  };

  const formatEmployees = (count) => {
    if (count >= 1000) return `${(count / 1000).toFixed(0)}K`;
    return count?.toLocaleString();
  };

  return (
    <div className="card p-6">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h3 className="text-2xl font-bold text-white mb-2">{company.name}</h3>
          <p className="text-primary-400 font-medium text-lg">{company.ticker}</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-dark-400">Market Cap</p>
          <p className="text-xl font-bold text-white">{formatMarketCap(company.marketCap)}</p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        <div className="flex items-center space-x-3">
          <BuildingOfficeIcon className="w-8 h-8 text-blue-500" />
          <div>
            <p className="text-xs text-dark-400 uppercase tracking-wide">Sector</p>
            <p className="font-medium text-white">{company.sector}</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <UsersIcon className="w-8 h-8 text-green-500" />
          <div>
            <p className="text-xs text-dark-400 uppercase tracking-wide">Employees</p>
            <p className="font-medium text-white">{formatEmployees(company.employees)}</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <CalendarIcon className="w-8 h-8 text-purple-500" />
          <div>
            <p className="text-xs text-dark-400 uppercase tracking-wide">Founded</p>
            <p className="font-medium text-white">{company.founded}</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <MapPinIcon className="w-8 h-8 text-orange-500" />
          <div>
            <p className="text-xs text-dark-400 uppercase tracking-wide">Headquarters</p>
            <p className="font-medium text-white">{company.headquarters}</p>
          </div>
        </div>
      </div>

      <div className="mt-6 p-4 bg-dark-900 rounded-lg">
        <h4 className="font-medium text-white mb-2">Company Overview</h4>
        <p className="text-sm text-dark-300 leading-relaxed">
          {company.name} is a leading company in the {company.sector} sector, 
          operating with {formatEmployees(company.employees)} employees worldwide. 
          Founded in {company.founded}, the company has established itself as a major player 
          in the market with a current market capitalization of {formatMarketCap(company.marketCap)}.
        </p>
      </div>
    </div>
  );
};

export default CompanyProfile;