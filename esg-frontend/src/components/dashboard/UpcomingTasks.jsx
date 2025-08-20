import React from 'react';
import { ClockIcon, CheckCircleIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';

const UpcomingTasks = () => {
  const tasks = [
    {
      title: 'Quarterly ESG Filing',
      dueDate: '2024-04-15',
      status: 'urgent',
      icon: ExclamationTriangleIcon
    },
    {
      title: 'ESG Report Review',
      dueDate: '2024-09-20',
      status: 'warning',
      icon: ClockIcon
    },
    {
      title: 'Sustainability Assessment',
      dueDate: '2024-03-18',
      status: 'completed',
      icon: CheckCircleIcon
    }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'urgent':
        return 'text-danger-500';
      case 'warning':
        return 'text-warning-500';
      case 'completed':
        return 'text-success-500';
      default:
        return 'text-dark-400';
    }
  };

  const getStatusBg = (status) => {
    switch (status) {
      case 'urgent':
        return 'bg-danger-500';
      case 'warning':
        return 'bg-warning-500';
      case 'completed':
        return 'bg-success-500';
      default:
        return 'bg-dark-500';
    }
  };

  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold text-white mb-6">Upcoming Tasks</h3>
      <div className="space-y-4">
        {tasks.map((task, index) => {
          const Icon = task.icon;
          return (
            <div key={index} className="flex items-center space-x-4 p-3 rounded-lg hover:bg-dark-750 transition-colors duration-200">
              <div className={`w-8 h-8 ${getStatusBg(task.status)} rounded-full flex items-center justify-center`}>
                <Icon className="w-4 h-4 text-white" />
              </div>
              <div className="flex-1">
                <h4 className="font-medium text-white">{task.title}</h4>
                <p className="text-sm text-dark-400">Due: {task.dueDate}</p>
              </div>
              <div className={`w-2 h-2 rounded-full ${getStatusBg(task.status)}`}></div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default UpcomingTasks;