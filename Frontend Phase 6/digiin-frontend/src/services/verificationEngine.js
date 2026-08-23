const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export const verificationEngine = {
  async runPipeline(documents = [], scenario = 'success', onProgress) {
    onProgress?.({
      stage: 'INTEGRITY_CHECK',
      percent: 25,
      title: '1. Checking Document Integrity',
      message: 'Validating SHA-256 integrity digests across 2 retrieved digital certificates…',
      stages: [
        { title: 'Document Integrity Check', description: 'Validating SHA-256 hashes and digital seal tamper-resistance.', status: 'in_progress' },
        { title: 'Issuer Key Resolution', description: 'Fetching official registry public signing keys from CBSE & UIDAI.', status: 'pending' },
        { title: 'Demographics & Predicates', description: 'Evaluating candidate eligibility and Zero-Knowledge assertions (>=60%).', status: 'pending' },
        { title: 'Proof Token Minting', description: 'Signing verifiable Ed25519 assertion proof token.', status: 'pending' }
      ]
    });
    await delay(600);

    onProgress?.({
      stage: 'ISSUER_MATCH',
      percent: 50,
      title: '2. Matching Issuing Authority Keys',
      message: 'Resolving cryptographic public keys for Central Board of Secondary Education…',
      stages: [
        { title: 'Document Integrity Check', description: 'SHA-256 cryptographic hashes matched successfully.', status: 'completed' },
        { title: 'Issuer Key Resolution', description: 'Resolving public key digiin-ed25519-key-2026 for CBSE.', status: 'in_progress' },
        { title: 'Demographics & Predicates', description: 'Evaluating candidate eligibility and Zero-Knowledge assertions (>=60%).', status: 'pending' },
        { title: 'Proof Token Minting', description: 'Signing verifiable Ed25519 assertion proof token.', status: 'pending' }
      ]
    });
    await delay(600);

    if (scenario === 'mismatch') {
      onProgress?.({
        stage: 'FAILED',
        percent: 75,
        title: '3. Demographics Discrepancy Detected',
        message: 'Name spelling mismatch detected between secondary school record and admission application.',
        stages: [
          { title: 'Document Integrity Check', description: 'SHA-256 cryptographic hashes matched successfully.', status: 'completed' },
          { title: 'Issuer Key Resolution', description: 'CBSE issuing authority validated.', status: 'completed' },
          { title: 'Demographics & Predicates', description: 'Mismatch: Name on record does not meet 90% phonetic threshold.', status: 'failed' },
          { title: 'Proof Token Minting', description: 'Halted due to validation failure.', status: 'pending' }
        ]
      });
      await delay(300);
      return {
        status: 'FAILED',
        reason: 'NAME_MISMATCH',
        message: 'Candidate name on record ("Rahul Kumar Sharma") differs from application ("Rahul Sharma").',
        supportCode: 'ERR-NAME-DISCREPANCY-901'
      };
    }

    onProgress?.({
      stage: 'DETAIL_CHECK',
      percent: 75,
      title: '3. Checking Document Details & Predicates',
      message: 'Evaluating passing year (2025) and aggregate percentage criteria (>= 60.0%)…',
      stages: [
        { title: 'Document Integrity Check', description: 'SHA-256 cryptographic hashes matched successfully.', status: 'completed' },
        { title: 'Issuer Key Resolution', description: 'CBSE issuing authority validated.', status: 'completed' },
        { title: 'Demographics & Predicates', description: 'Candidate verified. Predicate: percentage >= 60.0% satisfied (84.5%).', status: 'in_progress' },
        { title: 'Proof Token Minting', description: 'Signing verifiable Ed25519 assertion proof token.', status: 'pending' }
      ]
    });
    await delay(600);

    onProgress?.({
      stage: 'PROOF_MINTING',
      percent: 100,
      title: '4. Minting Signed Verifiable Proof Receipt',
      message: 'Generating RFC 7515/7519 Ed25519 cryptographic token proof…',
      stages: [
        { title: 'Document Integrity Check', description: 'SHA-256 cryptographic hashes matched successfully.', status: 'completed' },
        { title: 'Issuer Key Resolution', description: 'CBSE issuing authority validated.', status: 'completed' },
        { title: 'Demographics & Predicates', description: 'Candidate verified. Predicate: percentage >= 60.0% satisfied (84.5%).', status: 'completed' },
        { title: 'Proof Token Minting', description: 'Signed Ed25519 token issued with key ID digiin-ed25519-key-2026.', status: 'completed' }
      ]
    });
    await delay(400);

    const isPartial = scenario === 'partial';
    return {
      status: isPartial ? 'PARTIALLY_VERIFIED' : 'VERIFIED',
      verificationId: 'DIN-VRF-82A91',
      algorithm: 'EdDSA',
      keyId: 'digiin-ed25519-key-2026',
      issuedAt: new Date().toISOString(),
      expiresAt: new Date(Date.now() + 24 * 3600 * 1000).toISOString(),
      disclosedClaims: {
        candidate_name: 'Rahul Sharma',
        class_x_status: isPartial ? 'UNAVAILABLE' : 'PASSED (2023)',
        class_xii_status: 'PASSED (2025)',
        aggregate_predicate: 'percentage >= 60.0% -> SATISFIED (TRUE)',
        zero_knowledge_mode: true,
        raw_documents_stored: false
      },
      documents: [
        { id: 'doc-10', title: 'Class 10 Certificate', issuer: 'CBSE', status: isPartial ? 'failed' : 'verified', detail: isPartial ? 'Registry lookup timeout' : 'Date of birth verified • Roll No match 100%' },
        { id: 'doc-12', title: 'Class 12 Certificate', issuer: 'CBSE', status: 'verified', detail: 'Passing year verified • Aggregate >= 60.0% satisfied' }
      ]
    };
  }
};
