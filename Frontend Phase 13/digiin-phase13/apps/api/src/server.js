const http = require('http');

const mockVerification = {
  id: 'VRF-7K2P-91MX',
  publicId: 'VRF-7K2P-91MX',
  documentId: 'DOC-82K7',
  status: 'VERIFIED',
  engineVersion: '1.0.0',
  rulesetVersion: '1.0',
  decision: 'VERIFIED',
  confidence: 'HIGH',
  reasonCode: 'VERIFIED',
  summary: 'All required source, integrity, and issuer checks passed.',
  evidence: [
    { type: 'DOCUMENT_SOURCE', source: 'DIGILOCKER', result: 'PASS' },
    { type: 'DOCUMENT_CHECKSUM', source: 'SHA-256', result: 'PASS' },
    { type: 'ISSUER_AUTHENTICITY', source: 'CBSE', result: 'PASS' },
    { type: 'DOCUMENT_TYPE', source: 'CLASS_12_CERTIFICATE', result: 'PASS' }
  ],
  rules: [
    { ruleId: 'DOCUMENT_SOURCE_VALID', status: 'PASS', version: '1.0' },
    { ruleId: 'DOCUMENT_CHECKSUM_VALID', status: 'PASS', version: '1.0' },
    { ruleId: 'ISSUER_PRESENT', status: 'PASS', version: '1.0' },
    { ruleId: 'DOCUMENT_TYPE_VALID', status: 'PASS', version: '1.0' },
    { ruleId: 'DOCUMENT_NOT_EXPIRED', status: 'PASS', version: '1.0' }
  ]
};

const mockProof = {
  id: 'PRF-7K2P-91MX',
  proofId: 'PRF-7K2P-91MX',
  verificationId: 'VRF-7K2P-91MX',
  subjectId: 'DIN-7K4P-92M8',
  claimType: 'EDUCATION_VERIFIED',
  claim: {
    type: 'EDUCATION_VERIFIED',
    qualification: 'Class 12 Certificate',
    issuer: 'CBSE'
  },
  issuer: 'DigiIn',
  status: 'ACTIVE',
  version: '1.0',
  keyId: 'KEY-2026-01',
  signature: 'ed25519_sig_dGhpc19pc19hX3ZhbGlkX3NpZ25hdHVyZV90ZXN0X3ZlY3Rvcg',
  issuedAt: '2026-08-23T10:00:00Z',
  expiresAt: '2027-08-23T10:00:00Z'
};

const routes = {
  '/health': () => ({ status: 'ok', version: '1.3.0', phase: 13 }),
  '/ready': () => ({ status: 'ready', dependencies: { database: 'ok', redis: 'ok', proof_signer: 'ok' } }),
  '/version': () => ({ version: '1.3.0', phase: 13, service: 'DigiIn Verification Engine & Proof Signer' }),
  '/v1/verifications/VRF-7K2P-91MX': () => mockVerification,
  '/v1/verifications/VRF-7K2P-91MX/evidence': () => ({ count: mockVerification.evidence.length, evidence: mockVerification.evidence }),
  '/v1/verifications/VRF-7K2P-91MX/result': () => ({
    decision: mockVerification.decision,
    confidence: mockVerification.confidence,
    reasonCode: mockVerification.reasonCode,
    summary: mockVerification.summary,
    rulesPassed: 5,
    rulesFailed: 0,
    rulesReviewed: 0
  }),
  '/v1/proofs': () => ({ count: 1, proofs: [mockProof] }),
  '/v1/proofs/PRF-7K2P-91MX': () => mockProof,
  '/v1/public/proofs/PRF-7K2P-91MX/verify': () => ({
    valid: true,
    status: 'ACTIVE',
    claim: mockProof.claim,
    issuer: mockProof.issuer,
    keyId: mockProof.keyId,
    issuedAt: mockProof.issuedAt,
    expiresAt: mockProof.expiresAt
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

  if (url === '/v1/proofs/PRF-7K2P-91MX/revoke' && req.method === 'POST') {
    res.statusCode = 200;
    return res.end(JSON.stringify({
      proofId: 'PRF-7K2P-91MX',
      status: 'REVOKED',
      revokedAt: new Date().toISOString(),
      reason: 'USER_REQUESTED'
    }));
  }

  if (url.startsWith('/v1/documents/') && url.endsWith('/verify') && req.method === 'POST') {
    res.statusCode = 202;
    return res.end(JSON.stringify({
      verificationId: 'VRF-7K2P-91MX',
      status: 'QUEUED',
      message: 'Deterministic verification engine job initiated.'
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
  console.log(`DigiIn Phase 13 Verification Engine listening on http://localhost:${PORT}`);
});
