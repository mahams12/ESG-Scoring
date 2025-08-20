import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './styles/globals.css';

// Get the root container
const container = document.getElementById('root');
const root = createRoot(container);

// Render the app
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Service Worker registration for PWA (optional)
if ('serviceWorker' in navigator && process.env.NODE_ENV === 'production') {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('SW registered: ', registration);
      })
      .catch((registrationError) => {
        console.log('SW registration failed: ', registrationError);
      });
  });
}

// Error boundary for unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
});

// Global error handler
window.addEventListener('error', (event) => {
  console.error('Global error:', event.error);
});

// Development helpers
if (process.env.NODE_ENV === 'development') {
  // React DevTools detection
  if (window.__REACT_DEVTOOLS_GLOBAL_HOOK__) {
    console.log('React DevTools detected');
  }
  
  // Hot module replacement support
  if (module.hot) {
    module.hot.accept('./App', () => {
      root.render(
        <React.StrictMode>
          <App />
        </React.StrictMode>
      );
    });
  }
  
  // Development-only console styling
  console.log(
    '%c🚀 ESG AI Bot - Development Mode',
    'background: #3b82f6; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;'
  );
  
  console.log(
    '%cAPI URL: ' + (process.env.REACT_APP_API_URL || 'http://localhost:8000'),
    'color: #10b981; font-weight: bold;'
  );
}