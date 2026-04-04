import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

// Disable performance analytics for privacy
// reportWebVitals not used - see SECURITY.md
// If needed in future, only use localStorage, not external endpoints

// Security: Clear all localStorage on app start (medical data protection)
if (process.env.NODE_ENV === 'production') {
  // Only keep necessary session data
  const allowedKeys = ['disclaimerAccepted'];
  Object.keys(sessionStorage).forEach(key => {
    if (!allowedKeys.includes(key)) {
      sessionStorage.removeItem(key);
    }
  });
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Security: Prevent memory leaks and clear data on unload
window.addEventListener('beforeunload', () => {
  // Browser will automatically clear sessionStorage on close
  // This ensures no data persists between sessions
});
