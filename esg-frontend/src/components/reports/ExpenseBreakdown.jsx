import React from 'react';

const ExpenseBreakdown = () => {
  const expenses = [
    { category: 'Marketing', amount: 2500, percentage: 17.8, color: 'bg-red-500' },
    { category: 'Operations', amount: 2950, percentage: 21.0, color: 'bg-orange-500' },
    { category: 'R&D', amount: 1200, percentage: 8.5, color: 'bg-yellow-500' },
    { category: 'Sales', amount: 1650, percentage: 11.8, color: 'bg-green-500' },
    { category: 'Admin', amount: 2025, percentage: 14.4, color: 'bg-blue-500' },
    { category: 'Other', amount: 1500, percentage: 10.7, color: 'bg-purple-500' },
  ];

  return (
    <div className="card p-6">
      <h4 className="font-semibold text-white mb-6">Expense Categories</h4>
      
      <div className="space-y-4">
        {expenses.map((expense, index) => (
          <div key={index} className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className={`w-3 h-3 rounded-full ${expense.color}`} />
              <span className="text-sm text-white font-medium">{expense.category}</span>
            </div>
            <div className="text-right">
              <div className="text-sm font-semibold text-white">
                ${expense.amount.toLocaleString()}
              </div>
              <div className="text-xs text-dark-400">
                {expense.percentage}%
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 pt-4 border-t border-dark-700">
        <div className="flex justify-between items-center">
          <span className="font-medium text-white">Total Expenses</span>
          <span className="font-bold text-white">$11,825</span>
        </div>
      </div>
    </div>
  );
};

export default ExpenseBreakdown;