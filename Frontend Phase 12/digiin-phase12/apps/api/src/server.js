const http = require('http');

const mockDigiLockerDocs = [
  { id: 'dl-doc-10', title: 'Class 10 Certificate', type: 'CLASS_10_CERTIFICATE', issuer: 'CBSE', issuedAt: '2024-05-15', status: 'AVAILABLE' },
  { id: 'dl-doc-12', title: 'Class 12 Certificate', type: 'CLASS_12_CERTIFICATE', issuer: 'CBSE', issuedAt: '2026-05-20', status: 'AVAILABLE' },
  { id: 'dl-doc-deg', title: 'Degree Certificate', type: 'DEGREE_CERTIFICATE', issuer: 'Delhi University', issuedAt: '2026-06-30', status: 'AVAILABLE' },
  { id: 'dl-doc-dl', title: 'Driving Licence', type: 'DRIVING_LICENCE', issuer: 'Ministry of Road Transport', issuedAt: '2025-01-10', status: 'AVAILABLE' },
  { id: 'dl-doc-pan', title: 'PAN Verification Record', type: 'IDENTITY', issuer: 'Income Tax Department', issuedAt: '2023-11-12', status: 'AVAILABLE' },
  { id: 'dl-doc-addr', title: 'Domicile Certificate', type: 'ADDRESS', issuer: 'State Revenue Department', issuedAt: '2024-08-01', status: 'AVAILABLE' }
];

const mockDocuments = [
  {
    id: 'DOC-82K7',
    citizenId: 'DIN-7K4P-92M8',
    type: 'CLASS_10_CERTIFICATE',
    title: 'Class 10 Certificate',
    source: 'DIGILOCKER',
    checksum: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    checksumAlgorithm: 'SHA-256',
    status: 'AVAILABLE',
    retrievedAt: '23 Aug 2026 10:32',
    provenance: {
      source: 'DigiLocker',
      issuer: 'CBSE',
      retrievedAt: '23 Aug 2026 10:32',
      checksum: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    }
  },
  {
    id: 'DOC-91M4',
    citizenId: 'DIN-7K4P-92M8',
    type: 'CLASS_12_CERTIFICATE',
    title: 'Class 12 Certificate',
    source: 'DIGILOCKER',
    checksum: 'a8b1c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852c966',
    checksumAlgorithm: 'SHA-256',
    status: 'AVAILABLE',
    retrievedAt: '23 Aug 2026 10:32',
    provenance: {
      source: 'DigiLocker',
      issuer: 'CBSE',
      retrievedAt: '23 Aug 2026 10:32',
      checksum: 'a8b1c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852c966'
    }
  }
];

const routes = {
  '/health': () => ({ status: 'ok', version: '1.2.0', phase: 12 }),
  '/ready': () => ({ status: 'ready', dependencies: { database: 'ok', redis: 'ok', digilocker: 'ok' } }),
  '/version': () => ({ version: '1.2.0', phase: 12, service: 'DigiIn Document Pipeline' }),
  '/v1/digilocker/status': () => ({
    connected: true,
    provider: 'DIGILOCKER',
    connectedAt: '23 Aug 2026',
    documentsCount: mockDigiLockerDocs.length,
    scopes: ['read:documents']
  }),
  '/v1/digilocker/documents': () => ({
    count: mockDigiLockerDocs.length,
    documents: mockDigiLockerDocs
  }),
  '/v1/documents': () => ({
    count: mockDocuments.length,
    documents: mockDocuments
  })
};

const server = http.createServer((req, res) => {
  res.setHeader('content-type', 'application/json');
  res.setHeader('X-Request-ID', `REQ-${Math.floor(1000 + Math.random() * 9000)}-${Date.now().toString(36).toUpperCase()}`);

  const url = req.url.split('?')[0];

  if (routes[url]) {
    res.statusCode = 200;
    return res.end(JSON.stringify(routes[url]()));
  }

  if (url.startsWith('/v1/documents/') && req.method === 'GET') {
    const docId = url.split('/')[3];
    const doc = mockDocuments.find(d => d.id === docId) || mockDocuments[0];
    res.statusCode = 200;
    return res.end(JSON.stringify(doc));
  }

  if (url.startsWith('/v1/digilocker/documents/') && url.endsWith('/retrieve') && req.method === 'POST') {
    res.statusCode = 202;
    return res.end(JSON.stringify({
      jobId: `JOB-${Date.now()}`,
      status: 'QUEUED',
      message: 'Document retrieval background job initiated.'
    }));
  }

  if (url.startsWith('/v1/documents/') && url.endsWith('/verify') && req.method === 'POST') {
    res.statusCode = 202;
    return res.end(JSON.stringify({
      verificationId: 'DIN-VRF-82A91-K7',
      status: 'QUEUED',
      message: 'Verification background worker job queued.'
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
  console.log(`DigiIn Phase 12 Document API listening on http://localhost:${PORT}`);
});
