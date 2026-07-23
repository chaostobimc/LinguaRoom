import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';
import './styles.css';

// Note: we intentionally do NOT wrap in <React.StrictMode> because it double-
// invokes effects in development, which would open two WebSocket connections.
createRoot(document.getElementById('root')).render(<App />);
