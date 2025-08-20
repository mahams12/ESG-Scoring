import React, { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import LoadingSpinner from './components/common/LoadingSpinner';
import ErrorBoundary from './components/common/ErrorBoundary';

// Lazy load pages for better performance
const Dashboard = lazy(() => import('./pages/Dashboard'));
const ESGAnalysis = lazy(() => import('./pages/ESGAnalysis'));

// Loading fallback component
const PageLoadingFallback = () => (
  <div className="flex items-center justify-center min-h-screen">
    <LoadingSpinner size="large" message="Loading page..." />
  </div>
);

// Route wrapper with error boundary
const RouteWrapper = ({ children }) => (
  <ErrorBoundary>
    <Suspense fallback={<PageLoadingFallback />}>
      {children}
    </Suspense>
  </ErrorBoundary>
);

// Protected route component (for future authentication if needed)
const ProtectedRoute = ({ children, requireAuth = false }) => {
  // For now, no authentication required - pure ESG analysis tool
  const isAuthenticated = true;
  
  if (requireAuth && !isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }
  
  return <RouteWrapper>{children}</RouteWrapper>;
};

// Main routes configuration
const AppRoutes = () => {
  return (
    <Routes>
      {/* Default redirect */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      
      {/* Dashboard - ESG metrics overview */}
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } 
      />
      
      {/* ESG Analysis - Main functionality */}
      <Route 
        path="/analysis" 
        element={
          <ProtectedRoute>
            <ESGAnalysis />
          </ProtectedRoute>
        } 
      />
      
      {/* ESG Analysis with specific company ticker */}
      <Route 
        path="/analysis/:ticker" 
        element={
          <ProtectedRoute>
            <ESGAnalysis />
          </ProtectedRoute>
        } 
      />
      
      {/* API documentation route (development only) */}
      {process.env.NODE_ENV === 'development' && (
        <Route 
          path="/api-docs" 
          element={
            <div className="p-8 bg-dark-900 min-h-screen">
              <h1 className="text-2xl font-bold text-white mb-4">ESG API Documentation</h1>
              <div className="space-y-4 text-dark-300">
                <p>Available endpoints:</p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li><code className="bg-dark-800 px-2 py-1 rounded">/api/v1/health</code> - Health checks</li>
                  <li><code className="bg-dark-800 px-2 py-1 rounded">/api/v1/company</code> - Company validation</li>
                  <li><code className="bg-dark-800 px-2 py-1 rounded">/api/v1/analysis</code> - ESG analysis</li>
                </ul>
                <p className="mt-4">
                  <a 
                    href={`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/docs`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:text-blue-300 underline"
                  >
                    View Full API Documentation →
                  </a>
                </p>
              </div>
            </div>
          } 
        />
      )}
      
      {/* 404 Not Found */}
      <Route 
        path="*" 
        element={
          <div className="min-h-screen bg-dark-950 flex items-center justify-center p-6">
            <div className="text-center">
              <div className="w-24 h-24 bg-dark-800 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-4xl">🌱</span>
              </div>
              <h1 className="text-6xl font-bold text-white mb-4">404</h1>
              <h2 className="text-2xl font-semibold text-dark-300 mb-4">Page Not Found</h2>
              <p className="text-dark-400 mb-8 max-w-md">
                The page you're looking for doesn't exist. Let's get you back to ESG analysis.
              </p>
              <div className="space-x-4">
                <button 
                  onClick={() => window.history.back()}
                  className="btn-secondary"
                >
                  Go Back
                </button>
                <button 
                  onClick={() => window.location.href = '/dashboard'}
                  className="btn-primary"
                >
                  Go to Dashboard
                </button>
              </div>
            </div>
          </div>
        } 
      />
    </Routes>
  );
};

// Route configuration for external use
export const routeConfig = {
  dashboard: '/dashboard',
  analysis: '/analysis'
};

// Navigation helper functions
export const navigationHelpers = {
  goToDashboard: () => '/dashboard',
  goToAnalysis: (ticker) => ticker ? `/analysis/${ticker}` : '/analysis',
  // Helper for ESG report downloads (will be handled within components)
  downloadESGReport: (ticker, format = 'pdf') => {
    // This will be implemented in the ESG analysis components
    // Returns download URL or triggers download
    return `/api/v1/analysis/${ticker}/download?format=${format}`;
  }
};

export default AppRoutes;