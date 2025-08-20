import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  PlusIcon, 
  ChatBubbleLeftRightIcon, 
  ChartBarIcon, 
  EyeIcon 
} from '@heroicons/react/24/outline';

const QuickActions = () => {
  const navigate = useNavigate();

  const actions = [
    {
      title: 'Add Analysis',
      description: 'Analyze a new company',
      icon: PlusIcon,
      iconBg: 'bg-blue-500',
      onClick: () => navigate('/analysis')
    },
    {
      title: 'Chat with AI',
      description: 'Ask ESG questions or get help',
      icon: ChatBubbleLeftRightIcon,
      iconBg: 'bg-purple-500',
      onClick: () => console.log('Open AI Chat')
    },
    {
      title: 'Generate Report',
      description: 'Create ESG reports',
      icon: ChartBarIcon,
      iconBg: 'bg-green-500',
      onClick: () => navigate('/reports')
    },
    {
      title: 'View Analytics',
      description: 'Analyze trends and patterns',
      icon: EyeIcon,
      iconBg: 'bg-orange-500',
      onClick: () => navigate('/analytics')
    }
  ];

  return (
    <div className="card p-6">
      <h3 className="text-lg font-semibold text-white mb-6">Quick Actions</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {actions.map((action, index) => {
          const Icon = action.icon;
          return (
            <div
              key={index}
              className="quick-action-card group"
              onClick={action.onClick}
            >
              <div className="flex items-center space-x-4">
                <div className={`w-12 h-12 ${action.iconBg} rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform duration-200`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-white group-hover:text-primary-400 transition-colors duration-200">
                    {action.title}
                  </h4>
                  <p className="text-sm text-dark-400 mt-1">{action.description}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default QuickActions;