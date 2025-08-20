ESG-Scoring – AI-Powered ESG Investment Research System

A modern React application for ESG (Environmental, Social, Governance) investment research with AI-powered analysis.

## Features

- 🎨 Modern dark UI with Tailwind CSS
- 📱 Responsive design for all devices
- 🔄 Real-time ESG analysis
- 📊 Interactive charts and visualizations
- 🤖 AI-powered insights and recommendations
- 📈 Comprehensive reporting system
- ⚡ Fast and optimized performance

## Tech Stack

- React 18
- Tailwind CSS
- React Router
- Chart.js & Recharts
- Axios for API calls
- Heroicons for icons

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

## Environment Variables

Create a `.env` file in the root directory:

```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_APP_NAME=ESG AI Bot
```

## Project Structure

- `/src/components` - Reusable React components
- `/src/pages` - Main application pages
- `/src/services` - API service layer
- `/src/hooks` - Custom React hooks
- `/src/utils` - Utility functions
- `/src/context` - React context providers

## API Integration

The frontend is designed to integrate with the ESG backend API. Update the API endpoints in `/src/services/api.js` to match your backend deployment.

## Development

The application includes mock data for development purposes. Switch to real API calls by updating the service files when your backend is ready.

## License

Private - ESG Investment Research System