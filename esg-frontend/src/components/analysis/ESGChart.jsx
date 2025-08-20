import React from 'react';
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

const ESGChart = ({ scores, type = 'doughnut' }) => {
  const doughnutData = {
    labels: ['Environmental', 'Social', 'Governance'],
    datasets: [
      {
        data: [scores.environmental, scores.social, scores.governance],
        backgroundColor: [
          '#22c55e', // Green for Environmental
          '#3b82f6', // Blue for Social
          '#8b5cf6', // Purple for Governance
        ],
        borderColor: [
          '#16a34a',
          '#2563eb',
          '#7c3aed',
        ],
        borderWidth: 2,
      },
    ],
  };

  const lineData = {
    labels: ['Q1', 'Q2', 'Q3', 'Q4'],
    datasets: [
      {
        label: 'Environmental',
        data: [85, 87, 88, scores.environmental],
        borderColor: '#22c55e',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.4,
      },
      {
        label: 'Social',
        data: [78, 80, 81, scores.social],
        borderColor: '#3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
      },
      {
        label: 'Governance',
        data: [82, 83, 84, scores.governance],
        borderColor: '#8b5cf6',
        backgroundColor: 'rgba(139, 92, 246, 0.1)',
        tension: 0.4,
      },
    ],
  };

  const options = {
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
    scales: type === 'line' ? {
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
        },
        min: 0,
        max: 100,
      },
    } : {},
  };

  return (
    <div className="h-80">
      {type === 'doughnut' ? (
        <Doughnut data={doughnutData} options={options} />
      ) : (
        <Line data={lineData} options={options} />
      )}
    </div>
  );
};

export default ESGChart;
