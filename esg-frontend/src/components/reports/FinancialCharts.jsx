import React, { useState } from 'react';
import { Line, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const FinancialCharts = ({ period }) => {
  const [chartType, setChartType] = useState('Pie Chart');

  // Mock financial data
  const lineChartData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    datasets: [
      {
        label: 'Income',
        data: [15000, 16000, 17500, 18000, 19750, 19750, 18500, 17000, 16500, 18000, 19000, 20000],
        borderColor: '#22c55e',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.4,
        fill: true,
      },
      {
        label: 'Expenses',
        data: [12000, 13000, 13650, 14000, 13650, 13650, 14500, 15000, 14000, 13500, 13000, 12500],
        borderColor: '#ef4444',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.4,
        fill: true,
      },
      {
        label: 'Profit',
        data: [3000, 3000, 3850, 4000, 6100, 6100, 4000, 2000, 2500, 4500, 6000, 7500],
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true,
      },
    ],
  };

  const doughnutData = {
    labels: ['Marketing', 'Operations', 'R&D', 'Sales', 'Admin', 'Other'],
    datasets: [
      {
        data: [17.8, 21.0, 8.5, 11.8, 14.4, 10.7],
        backgroundColor: [
          '#ef4444', // Red
          '#f97316', // Orange  
          '#eab308', // Yellow
          '#22c55e', // Green
          '#3b82f6', // Blue
          '#8b5cf6', // Purple
        ],
        borderColor: '#1f2937',
        borderWidth: 2,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          color: '#9ca3af',
          padding: 20,
        },
      },
      tooltip: {
        backgroundColor: '#1f2937',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: '#374151',
        borderWidth: 1,
      },
    },
    scales: {
      x: {
        grid: {
          color: '#374151',
        },
        ticks: {
          color: '#9ca3af',
        },
      },
      y: {
        grid: {
          color: '#374151',
        },
        ticks: {
          color: '#9ca3af',
          callback: function(value) {
            return '$' + value.toLocaleString();
          },
        },
      },
    },
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right',
        labels: {
          color: '#9ca3af',
          padding: 20,
          usePointStyle: true,
        },
      },
      tooltip: {
        backgroundColor: '#1f2937',
        titleColor: '#fff',
        bodyColor: '#fff',
        borderColor: '#374151',
        borderWidth: 1,
        callbacks: {
          label: function(context) {
            return context.label + ': ' + context.parsed + '%';
          },
        },
      },
    },
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Line Chart */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-6">
          <h4 className="font-semibold text-white">Financial Performance</h4>
          <div className="flex items-center space-x-2 text-sm">
            <span className="text-success-500">Income: $19,750.00</span>
            <span className="text-danger-500">Expenses: $13,650.00</span>
            <span className="text-primary-500">Profit: $6,100.00</span>
          </div>
        </div>
        <div className="h-80">
          <Line data={lineChartData} options={chartOptions} />
        </div>
      </div>

      {/* Doughnut Chart */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-6">
          <h4 className="font-semibold text-white">Expense Breakdown</h4>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setChartType('Bar Chart')}
              className={`px-3 py-1 rounded text-sm ${chartType === 'Bar Chart' ? 'bg-primary-600 text-white' : 'bg-dark-700 text-dark-300'}`}
            >
              Bar Chart
            </button>
          </div>
        </div>
        <div className="h-80">
          <Doughnut data={doughnutData} options={doughnutOptions} />
        </div>
      </div>
    </div>
  );
};

export default FinancialCharts;