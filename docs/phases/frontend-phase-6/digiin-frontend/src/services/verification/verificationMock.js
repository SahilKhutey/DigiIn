const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export const verificationMock = {
  async runPipeline(documents = [], scenario = 'success', onProgress) {
    // Stage 1: Received
    onProgress?.({
      stage: 'STARTED',
      percent: 20,
      title: '1. Documents Received',
      message: '2 retrieved digital credentials loaded into secure verification memory.',
      stages: [
        { title: 'Documents Received', description: '2 digital credentials loaded from DigiLocker session.', status: 'completed' },
        { title: 'Document Integrity Check', description: 'Checking file format, metadata, and digital seal.', status: 'in_progress' },
        { title: 'Checking Issuing Authority', description: 'Validating against CBSE & UIDAI trusted authority registry.', status: 'pending' },
        { title: 'Matching Document Details', description: 'Matching candidate name, certificate numbers, and year.', status: 'pending' },
        { title: 'Preparing Verification Result', description: 'Evaluating rules and issuing proof token.', status: 'pending' }
      ]
    });
    await delay(500);

    // Stage 2: Integrity Check
    onProgress?.({
      stage: 'INTEGRITY_CHECK',
      percent: 40,
      title: '2. Checking Document Integrity',
      message: 'Validating SHA-256 digests and digital seal tamper-resistance…',
      stages: [
        { title: 'Documents Received', description: '2 digital credentials loaded from DigiLocker session.', status: 'completed' },
        { title: 'Document Integrity Check', description: 'Structure, metadata, and digital seals valid.', status: 'completed' },
        { title: 'Checking Issuing Authority', description: 'Connecting to CBSE & UIDAI trusted authority registry…', status: 'in_progress' },
        { title: 'Matching Document Details', description: 'Matching candidate name, certificate numbers, and year.', status: 'pending' },
        { title: 'Preparing Verification Result', description: 'Evaluating rules and issuing proof token.', status: 'pending' }
      ]
    });
    await delay(500);

    // Stage 3: Authority Check
    if (scenario === 'authority_unavailable') {
      onProgress?.({
        stage: 'AUTHORITY_UNAVAILABLE',
        percent: 60,
        title: '3. Issuing Authority Unavailable',
        message: 'Could not connect to CBSE registry gateway. Timeout encountered.',
        stages: [
          { title: 'Documents Received', description: '2 digital credentials loaded from DigiLocker session.', status: 'completed' },
          { title: 'Document Integrity Check', description: 'Structure, metadata, and digital seals valid.', status: 'completed' },
          { title: 'Checking Issuing Authority', description: 'CBSE registry gateway unreachable (Timeout).', status: 'failed' },
          { title: 'Matching Document Details', description: 'Halted due to authority unavailability.', status: 'pending' },
          { title: 'Preparing Verification Result', description: 'Pending retry.', status: 'pending' }
        ]
      });
      await delay(300);
      return {
        id: 'DIN-VRF-82A91-FAIL',
        status: 'FAILED',
        errorType: 'AUTHORITY_UNAVAILABLE',
        message: "We couldn't reach the issuing authority right now.",
        canRetry: true
      };
    }

    onProgress?.({
      stage: 'AUTHORITY_CHECK',
      percent: 60,
      title: '3. Issuing Authority Confirmed',
      message: 'Cryptographic public key digiin-ed25519-key-2026 confirmed for CBSE.',
      stages: [
        { title: 'Documents Received', description: '2 digital credentials loaded from DigiLocker session.', status: 'completed' },
        { title: 'Document Integrity Check', description: 'Structure, metadata, and digital seals valid.', status: 'completed' },
        { title: 'Checking Issuing Authority', description: 'Issuing authority CBSE confirmed.', status: 'completed' },
        { title: 'Matching Document Details', description: 'Matching candidate name, roll number, and cutoff criteria…', status: 'in_progress' },
        { title: 'Preparing Verification Result', description: 'Evaluating rules and issuing proof token.', status: 'pending' }
      ]
    });
    await delay(500);

    // Stage 4: Detail Match
    if (scenario === 'mismatch') {
      onProgress?.({
        stage: 'DETAIL_MISMATCH',
        percent: 80,
        title: '4. Demographic Mismatch Detected',
        message: 'Name spelling mismatch detected between school certificate and admission entry.',
        stages: [
          { title: 'Documents Received', description: '2 digital credentials loaded from DigiLocker session.', status: 'completed' },
          { title: 'Document Integrity Check', description: 'Structure, metadata, and digital seals valid.', status: 'completed' },
          { title: 'Checking Issuing Authority', description: 'Issuing authority CBSE confirmed.', status: 'completed' },
          { title: 'Matching Document Details', description: 'Candidate name on record differs from application.', status: 'failed' },
          { title: 'Preparing Verification Result', description: 'Verification failed.', status: 'pending' }
        ]
      });
      await delay(300);
      return {
        id: 'DIN-VRF-82A91-FAIL',
        status: 'FAILED',
        errorType: 'DETAIL_MISMATCH',
        message: "Document details don't match the trusted source.",
        supportCode: 'ERR-NAME-DISCREPANCY-901',
        canRetry: false
      };
    }

    onProgress?.({
      stage: 'DETAIL_MATCH',
      percent: 80,
      title: '4. Document Details Matched',
      message: 'Candidate name, roll number, passing year, and percentage criteria (>= 60.0%) verified.',
      stages: [
        { title: 'Documents Received', description: '2 digital credentials loaded from DigiLocker session.', status: 'completed' },
        { title: 'Document Integrity Check', description: 'Structure, metadata, and digital seals valid.', status: 'completed' },
        { title: 'Checking Issuing Authority', description: 'Issuing authority CBSE confirmed.', status: 'completed' },
        { title: 'Matching Document Details', description: 'All candidate details and ZKP predicates matched.', status: 'completed' },
        { title: 'Preparing Verification Result', description: 'Minting signed verification proof token…', status: 'in_progress' }
      ]
    });
    await delay(500);

    // Stage 5: Preparing Result
    onProgress?.({
      stage: 'DECISION',
      percent: 100,
      title: '5. Verification Complete',
      message: 'Signed proof token DIN-VRF-82A91-K7 minted successfully.',
      stages: [
        { title: 'Documents Received', description: '2 digital credentials loaded from DigiLocker session.', status: 'completed' },
        { title: 'Document Integrity Check', description: 'Structure, metadata, and digital seals valid.', status: 'completed' },
        { title: 'Checking Issuing Authority', description: 'Issuing authority CBSE confirmed.', status: 'completed' },
        { title: 'Matching Document Details', description: 'All candidate details and ZKP predicates matched.', status: 'completed' },
        { title: 'Preparing Verification Result', description: 'Proof token DIN-VRF-82A91-K7 ready.', status: 'completed' }
      ]
    });
    await delay(300);

    const isPartial = scenario === 'partial';
    return {
      id: 'DIN-VRF-82A91-K7',
      status: isPartial ? 'PARTIALLY_VERIFIED' : 'VERIFIED',
      completedAt: new Date().toISOString(),
      documents: [
        {
          id: 'doc-10',
          type: 'CLASS_X_CERTIFICATE',
          name: 'Class 10 Certificate',
          issuer: 'CBSE',
          status: isPartial ? 'partial' : 'verified',
          verifiedAt: '23 Aug 2026',
          checks: [
            { type: 'integrity', label: 'Document integrity', status: 'passed', message: 'Document structure and verification information are valid.' },
            { type: 'authority', label: 'Issuing authority', status: isPartial ? 'warning' : 'passed', message: isPartial ? 'Issuing authority could not be reached.' : 'CBSE public signing key confirmed.' },
            { type: 'cert_no', label: 'Certificate number', status: isPartial ? 'warning' : 'passed', message: 'CBSE-X-2023-9941 matched.' },
            { type: 'candidate', label: 'Candidate details', status: 'passed', message: 'Name and date of birth match 100%.' },
            { type: 'year', label: 'Issue year', status: 'passed', message: 'Year 2023 confirmed.' }
          ]
        },
        {
          id: 'doc-12',
          type: 'CLASS_XII_CERTIFICATE',
          name: 'Class 12 Certificate',
          issuer: 'CBSE',
          status: 'verified',
          verifiedAt: '23 Aug 2026',
          checks: [
            { type: 'integrity', label: 'Document integrity', status: 'passed', message: 'Document structure and verification information are valid.' },
            { type: 'authority', label: 'Issuing authority', status: 'passed', message: 'CBSE public signing key confirmed.' },
            { type: 'cert_no', label: 'Certificate number', status: 'passed', message: 'CBSE-XII-2025-8812 matched.' },
            { type: 'candidate', label: 'Candidate details', status: 'passed', message: 'Name match 100%.' },
            { type: 'year', label: 'Issue year', status: 'passed', message: 'Year 2025 confirmed.' },
            { type: 'predicate', label: 'Eligibility predicate', status: 'passed', message: 'Aggregate percentage >= 60.0% satisfied (84.5%).' }
          ]
        }
      ]
    };
  }
};
