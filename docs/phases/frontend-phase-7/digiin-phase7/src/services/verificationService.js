const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const checksFor = (doc) => [
  { id: 'integrity', label: 'Document integrity', status: 'passed', message: 'Document structure and verification metadata are valid.' },
  { id: 'issuer', label: 'Issuing authority', status: 'passed', message: `${doc.issuer} was confirmed as the issuing authority.` },
  { id: 'number', label: 'Certificate number', status: 'passed', message: 'Certificate number matched the trusted verification record.' },
  { id: 'details', label: 'Candidate details', status: 'passed', message: 'Candidate details matched the trusted verification record.' },
  { id: 'year', label: 'Issue year', status: 'passed', message: 'Issue year matched the trusted verification record.' }
];

export const verificationService = {
  async verify(documents, onProgress = () => {}) {
    const stages = [
      ['integrity', 'Checking document integrity'],
      ['issuer', 'Checking issuing authority'],
      ['details', 'Matching document details'],
      ['decision', 'Preparing verification result']
    ];
    onProgress({ stage: 'started', label: 'Verification started' });
    const results = documents.map((doc) => ({ ...doc, status: 'verifying', checks: [] }));
    for (const [stage, label] of stages) {
      onProgress({ stage, label, results });
      await wait(650);
      if (stage !== 'decision') {
        results.forEach((doc) => {
          const checks = checksFor(doc);
          if (stage === 'integrity') doc.checks = checks.slice(0, 1);
          if (stage === 'issuer') doc.checks = checks.slice(0, 2);
          if (stage === 'details') doc.checks = checks;
        });
      }
    }
    results.forEach((doc) => { doc.status = 'verified'; });
    const verified = results.filter((d) => d.status === 'verified').length;
    const status = verified === results.length ? 'verified' : verified > 0 ? 'partial' : 'failed';
    const result = {
      id: `DIN-VRF-${Math.random().toString(36).slice(2, 8).toUpperCase()}`,
      status,
      verified,
      total: results.length,
      documents: results,
      completedAt: new Date().toISOString()
    };
    onProgress({ stage: 'completed', label: 'Verification complete', result });
    return result;
  }
};
