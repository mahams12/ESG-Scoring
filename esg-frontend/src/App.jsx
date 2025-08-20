// src/App.jsx
import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { NotificationContextProvider } from './context/NotificationContext';
import { ESGContextProvider } from './context/ESGContext';
import Sidebar from './components/common/Sidebar';
import Header from './components/common/Header';
import NotificationToast from './components/common/NotificationToast';
import ErrorBoundary from './components/common/ErrorBoundary';
import AppRoutes from './routes';
import './styles/globals.css';

function App() {
  return (
    <ErrorBoundary>
      <NotificationContextProvider>
        <ESGContextProvider>
          <Router>
            <div className="flex h-screen bg-dark-950 overflow-hidden">
              {/* Sidebar */}
              <Sidebar />
              
              {/* Main Content Area */}
              <div className="flex-1 flex flex-col overflow-hidden">
                {/* Header */}
                <Header />
                
                {/* Main Content */}
                <main className="flex-1 overflow-y-auto bg-dark-900 p-6">
                  <div className="max-w-7xl mx-auto">
                    <AppRoutes />
                  </div>
                </main>
              </div>
              
              {/* Notification Toast */}
              <NotificationToast />
            </div>
          </Router>
        </ESGContextProvider>
      </NotificationContextProvider>
    </ErrorBoundary>
  );
}

// Development tools
if (process.env.NODE_ENV === 'development') {
  App.displayName = 'ESGApp';
  
  if (module.hot) {
    module.hot.accept();
  }
}

export default App;