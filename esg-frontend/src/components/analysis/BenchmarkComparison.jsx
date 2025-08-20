import React from 'react';
import { ArrowTrendingUpIcon, ArrowTrendingDownIcon } from '@heroicons/react/24/outline';

const BenchmarkComparison = ({ benchmarkData, companyScore }) => {
  const isAboveAverage = companyScore > benchmarkData.industryAverage;
  const difference = Math.abs(companyScore - benchmarkData.industryAverage);

  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold text-white mb-6">Industry Benchmark</h3>

      {/* Score Comparison */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <p className="text-sm text-dark-400">Company Score</p>
            <p className="text-2xl font-bold text-white">{companyScore.toFixed(1)}</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-dark-400">Industry Average</p>
            <p className="text-2xl font-bold text-dark-300">{benchmarkData.industryAverage.toFixed(1)}</p>
          </div>
        </div>

        <div className="relative">
          <div className="w-full bg-dark-700 rounded-full h-3">
            <div
              className="h-3 bg-primary-500 rounded-full transition-all duration-1000"
              style={{ width: `${(companyScore / 100) * 100}%` }}
            />
          </div>
          <div className="flex justify-between mt-2 text-xs text-dark-400">
            <span>0</span>
            <span>50</span>
            <span>100</span>
          </div>
        </div>
      </div>

      {/* Performance Indicator */}
      <div className={`p-4 rounded-lg mb-4 ${
        isAboveAverage ? 'bg-success-500/10 border border-success-500/20' : 'bg-warning-500/10 border border-warning-500/20'
      }`}>
        <div className="flex items-center space-x-3">
          {isAboveAverage ? (
            <ArrowTrendingUpIcon className="w-6 h-6 text-success-400" />
          ) : (
            <ArrowTrendingDownIcon className="w-6 h-6 text-warning-400" />
          )}
          <div>
            <p className={`font-medium ${isAboveAverage ? 'text-success-400' : 'text-warning-400'}`}>
              {difference.toFixed(1)} points {isAboveAverage ? 'above' : 'below'} industry average
            </p>
            <p className="text-sm text-dark-300">
              {benchmarkData.percentileRank}th percentile ranking
            </p>
          </div>
        </div>
      </div>

      {/* Peer Comparison */}
      <div>
        <h5 className="font-medium text-white mb-4">Peer Comparison</h5>
        <div className="space-y-3">
          {benchmarkData.peerComparison?.map((peer, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-dark-900 rounded-lg">
              <span className="text-sm text-dark-300">{peer.name}</span>
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium text-white">{peer.score.toFixed(1)}</span>
                <div className={`w-2 h-2 rounded-full ${
                  peer.score > companyScore ? 'bg-danger-500' : 'bg-success-500'
                }`} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Market Position */}
      <div className="mt-6 p-4 bg-dark-900 rounded-lg">
        <h6 className="font-medium text-white mb-2">Market Position</h6>
        <p className="text-sm text-dark-300">
          {isAboveAverage 
            ? `Strong ESG performance placing the company in the top ${100 - benchmarkData.percentileRank}% of industry peers.`
            : `ESG performance below industry average, presenting opportunities for improvement.`
          }
        </p>
      </div>
    </div>
  );
};

export default BenchmarkComparison;