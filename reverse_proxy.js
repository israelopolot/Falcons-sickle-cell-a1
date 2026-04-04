/**
 * Simple reverse proxy to serve frontend and backend together
 * Allows ngrok to tunnel a single port that handles both frontend + API
 */
const http = require('http');
const httpProxy = require('http-proxy');
const fs = require('fs');
const path = require('path');

// Create proxy instances
const apiProxy = httpProxy.createProxyServer({
  target: 'http://localhost:8000',
  changeOrigin: true,
});

const frontendProxy = httpProxy.createProxyServer({
  target: 'http://localhost:3000',
  changeOrigin: true,
});

// Handle proxy errors
apiProxy.on('error', (err, req, res) => {
  console.error('API Proxy Error:', err);
  res.writeHead(503, { 'Content-Type': 'text/plain' });
  res.end('Backend service unavailable');
});

frontendProxy.on('error', (err, req, res) => {
  console.error('Frontend Proxy Error:', err);
  res.writeHead(503, { 'Content-Type': 'text/plain' });
  res.end('Frontend service unavailable');
});

// Create server
const server = http.createServer((req, res) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    res.writeHead(200, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      'Access-Control-Max-Age': '3600',
    });
    res.end();
    return;
  }

  // API calls go to backend
  if (req.url.startsWith('/predict') || 
      req.url.startsWith('/analyze-lab-values') || 
      req.url.startsWith('/health') ||
      req.url.startsWith('/docs') ||
      req.url.startsWith('/openapi.json')) {
    console.log(`[API] ${req.method} ${req.url}`);
    apiProxy.web(req, res);
  } else {
    // Everything else goes to frontend
    console.log(`[FRONTEND] ${req.method} ${req.url}`);
    frontendProxy.web(req, res);
  }
});

const PORT = process.env.PORT || 9000;
server.listen(PORT, '0.0.0.0', () => {
  console.log(`\n✅ Reverse Proxy Running on port ${PORT}`);
  console.log(`   Frontend: http://localhost:${PORT}`);
  console.log(`   Backend: Proxied to http://localhost:8000\n`);
});
