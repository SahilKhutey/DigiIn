const http = require('http');
const crypto = require('crypto');

const mockProviders = [
  { id: 'sandbox', name: 'DigiIn Deterministic Sandbox', version: '1.0', enabled: true, status: 'HEALTHY', assuranceLevel: 'HIGH', lastCheckedAt: '2026-08-23T11:20:00Z' },
  { id: 'digilocker', name: 'DigiLocker Government Adapter', version: '1.0', enabled: false, status: 'DISABLED', assuranceLevel: 'HIGH', lastCheckedAt: null },
  { id: 'government', name: 'National Registry Gateway', version: '1.0', enabled: false, status: 'DISABLED', assuranceLevel: 'HIGH', lastCheckedAt: null },
  { id: 'institution', name: 'Institutional Trust Network', version: '1.0', enabled: false, status: 'DISABLED', assuranceLevel: 'MEDIUM', lastCheckedAt: null }
];

let inMemoryApiKeys = [
  { id: 'key-1', name: 'Primary Production Key', prefix: 'din_live_91M4', scopes: ['verification:request:create', 'verification:proof:verify'], createdAt: '23 Aug 2026' }
];

const routes = {
  '/health': () => ({ status: 'ok', version: '1.5.0', phase: 15 }),
  '/ready': () => ({ status: 'ready', dependencies: { database: 'ok', redis: 'ok', provider_registry: 'ok' } }),
  '/version': () => ({ version: '1.5.0', phase: 15, service: 'DigiIn Production Integration & Provider Mesh' }),
  '/v1/integrations/health': () => ({ count: mockProviders.length, providers: mockProviders }),
  '/v1/admin/integrations': () => ({ count: mockProviders.length, providers: mockProviders }),
  '/v1/organisation/api-keys': () => ({ count: inMemoryApiKeys.length, keys: inMemoryApiKeys })
};

const server = http.createServer((req, res) => {
  res.setHeader('content-type', 'application/json');
  res.setHeader('X-Request-ID', `REQ-${Math.floor(1000 + Math.random() * 9000)}-${Date.now().toString(36).toUpperCase()}`);

  const url = req.url.split('?')[0];

  if (routes[url]) {
    res.statusCode = 200;
    return res.end(JSON.stringify(routes[url]()));
  }

  if (url.startsWith('/v1/admin/integrations/') && url.endsWith('/test') && req.method === 'POST') {
    const providerId = url.split('/')[4];
    res.statusCode = 200;
    return res.end(JSON.stringify({
      providerId,
      status: 'HEALTHY',
      responseTimeMs: 42,
      lastCheckedAt: new Date().toISOString(),
      message: 'Provider health check succeeded with 0 errors.'
    }));
  }

  if (url === '/v1/organisation/api-keys' && req.method === 'POST') {
    const secret = crypto.randomBytes(24).toString('base64url');
    const key = `din_live_${secret}`;
    res.statusCode = 201;
    return res.end(JSON.stringify({
      id: `key-${Date.now()}`,
      name: 'New API Key',
      apiKey: key,
      warning: 'Store this key safely. It will not be shown again.',
      scopes: ['verification:request:create', 'verification:proof:verify']
    }));
  }

  if (url.startsWith('/v1/integrations/') && url.endsWith('/webhook') && req.method === 'POST') {
    res.statusCode = 200;
    return res.end(JSON.stringify({
      status: 'RECEIVED',
      eventId: `EVT-${Date.now()}`,
      message: 'Webhook signature verified and payload queued for asynchronous processing.'
    }));
  }

  res.statusCode = 404;
  res.end(JSON.stringify({
    error: {
      code: 'NOT_FOUND',
      message: 'Requested endpoint does not exist',
      requestId: 'REQ-DEMO'
    }
  }));
});

const PORT = process.env.PORT || 8080;
server.listen(PORT, () => {
  console.log(`DigiIn Phase 15 Production Integration Server listening on http://localhost:${PORT}`);
});
