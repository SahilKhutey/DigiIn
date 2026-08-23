const http = require('http');

let inMemoryRequests = [
  {
    id: 'VRQ-7K2P-91MX',
    publicId: 'VRQ-7K2P-91MX',
    organisationId: 'ORG-84K2-19Q7',
    organisationName: 'ABC University',
    verifiedOrganisation: true,
    citizenId: 'DIN-7K4P-92M8',
    purpose: 'UNIVERSITY_ADMISSION',
    description: 'Verify Class 12 qualification for university admission processing.',
    status: 'COMPLETED',
    claims: [
      { claimType: 'EDUCATION_VERIFIED', required: true, status: 'VERIFIED' }
    ],
    proofId: 'PRF-7K2P-91MX',
    expiresAt: '2026-08-31T00:00:00Z',
    createdAt: '23 Aug 2026'
  },
  {
    id: 'VRQ-83M9-22PX',
    publicId: 'VRQ-83M9-22PX',
    organisationId: 'ORG-84K2-19Q7',
    organisationName: 'ABC University',
    verifiedOrganisation: true,
    citizenId: 'DIN-7K4P-92M8',
    purpose: 'SCHOLARSHIP',
    description: 'Verify income and qualification for academic scholarship.',
    status: 'PENDING',
    claims: [
      { claimType: 'EDUCATION_VERIFIED', required: true, status: 'PENDING' },
      { claimType: 'ADDRESS_VERIFIED', required: false, status: 'PENDING' }
    ],
    proofId: null,
    expiresAt: '2026-08-31T00:00:00Z',
    createdAt: '23 Aug 2026'
  }
];

const inMemoryConsents = [
  {
    id: 'CNS-7K2P-91MX',
    requestId: 'VRQ-7K2P-91MX',
    citizenId: 'DIN-7K4P-92M8',
    organisationName: 'ABC University',
    status: 'GRANTED',
    scope: ['EDUCATION_VERIFIED'],
    purpose: 'UNIVERSITY_ADMISSION',
    grantedAt: '23 Aug 2026',
    expiresAt: '31 Aug 2026'
  }
];

const routes = {
  '/health': () => ({ status: 'ok', version: '1.4.0', phase: 14 }),
  '/ready': () => ({ status: 'ready', dependencies: { database: 'ok', redis: 'ok', consent_engine: 'ok' } }),
  '/version': () => ({ version: '1.4.0', phase: 14, service: 'DigiIn Two-Sided Verification & Consent Engine' }),
  '/v1/organisation/requests': () => ({ count: inMemoryRequests.length, requests: inMemoryRequests }),
  '/v1/requests': () => ({ count: inMemoryRequests.length, requests: inMemoryRequests }),
  '/v1/consents': () => ({ count: inMemoryConsents.length, consents: inMemoryConsents })
};

const server = http.createServer((req, res) => {
  res.setHeader('content-type', 'application/json');
  res.setHeader('X-Request-ID', `REQ-${Math.floor(1000 + Math.random() * 9000)}-${Date.now().toString(36).toUpperCase()}`);

  const url = req.url.split('?')[0];

  if (routes[url]) {
    res.statusCode = 200;
    return res.end(JSON.stringify(routes[url]()));
  }

  if (url === '/v1/organisation/requests' && req.method === 'POST') {
    res.statusCode = 201;
    const newReqId = `VRQ-${Math.floor(1000 + Math.random() * 9000)}-${Date.now().toString(36).substring(0, 4).toUpperCase()}`;
    return res.end(JSON.stringify({
      requestId: newReqId,
      status: 'PENDING',
      expiresAt: '2026-08-31T00:00:00Z',
      message: 'Verification request created and dispatched to citizen inbox.'
    }));
  }

  if (url.startsWith('/v1/requests/') && url.endsWith('/consent') && req.method === 'POST') {
    res.statusCode = 200;
    return res.end(JSON.stringify({
      status: 'CONSENTED',
      proofId: 'PRF-7K2P-91MX',
      message: 'Consent granted. Verification orchestrated and proof minted.'
    }));
  }

  if (url.startsWith('/v1/requests/') && url.endsWith('/decline') && req.method === 'POST') {
    res.statusCode = 200;
    return res.end(JSON.stringify({
      status: 'DECLINED',
      message: 'Verification request declined.'
    }));
  }

  if (url.startsWith('/v1/consents/') && url.endsWith('/revoke') && req.method === 'POST') {
    res.statusCode = 200;
    return res.end(JSON.stringify({
      status: 'REVOKED',
      revokedAt: new Date().toISOString(),
      message: 'Consent successfully revoked.'
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
  console.log(`DigiIn Phase 14 Two-Sided Platform listening on http://localhost:${PORT}`);
});
