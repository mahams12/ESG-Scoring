import React, { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import LoadingSpinner from './components/common/LoadingSpinner';
import ErrorBoundary from './components/common/ErrorBoundary';

// Lazy load pages for better performance
const Dashboard = lazy(() => import('./pages/Dashboard'));
const ESGAnalysis = lazy(() => import('./pages/ESGAnalysis'));
const Reports = lazy(() => import('./pages/Reports'));
const Analytics = lazy(() => import('./pages/Analytics'));
const Settings = lazy(() => import('./pages/Settings'));

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

// Protected route component (for future authentication)
const ProtectedRoute = ({ children, requireAuth = false }) => {
  // TODO: Implement authentication logic
  const isAuthenticated = true; // Replace with actual auth check
  
  if (requireAuth && !isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <RouteWrapper>{children}</RouteWrapper>;
};

// Main routes configuration
const AppRoutes = () => {
  return (
    <Routes>
      {/* Default redirect */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      
      {/* Main application routes */}
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/analysis" 
        element={
          <ProtectedRoute>
            <ESGAnalysis />
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/analysis/:ticker" 
        element={
          <ProtectedRoute>
            <ESGAnalysis />
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/reports" 
        element={
          <ProtectedRoute>
            <Reports />
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/reports/:type" 
        element={
          <ProtectedRoute>
            <Reports />
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/analytics" 
        element={
          <ProtectedRoute>
            <Analytics />
          </ProtectedRoute>
        } 
      />
      
      <Route 
        path="/settings" 
        element={
          <ProtectedRoute>
            <Settings />
          </ProtectedRoute>
        } 
      />
      
      {/* Future authentication routes */}
      {/* 
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password/:token" element={<ResetPassword />} />
      */}
      
      {/* API documentation route (development only) */}
      {process.env.NODE_ENV === 'development' && (
        <Route 
          path="/api-docs" 
          element={
            <div className="p-8 bg-dark-900 min-h-screen">
              <h1 className="text-2xl font-bold text-white mb-4">API Documentation</h1>
              <p className="text-dark-300">
                API documentation will be available here in development mode.
              </p>
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
                <span className="text-4xl">🔍</span>
              </div>
              <h1 className="text-6xl font-bold text-white mb-4">404</h1>
              <h2 className="text-2xl font-semibold text-dark-300 mb-4">Page Not Found</h2>
              <p className="text-dark-400 mb-8 max-w-md">
                The page you're looking for doesn't exist or has been moved.
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
  analysis: '/analysis',
  reports: '/reports',
  analytics: '/analytics',
  settings: '/settings'
};

// Navigation helper functions
export const navigationHelpers = {
  goToDashboard: () => '/dashboard',
  goToAnalysis: (ticker) => ticker ? `/analysis/${ticker}` : '/analysis',
  goToReports: (type) => type ? `/reports/${type}` : '/reports',
  goToAnalytics: () => '/analytics',
  goToSettings: () => '/settings'
};

export default AppRoutes;