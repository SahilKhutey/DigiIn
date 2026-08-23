const proofs = new Map();

const now = () => new Date();
const iso = (d) => d.toISOString();

export const proofService = {
  async createProof(verification, request) {
    const existing = [...proofs.values()].find(p => p.verificationId === verification.id && p.status === 'active');
    if (existing) return existing;
    const issued = now();
    const expires = new Date(issued.getTime() + 24 * 60 * 60 * 1000);
    const proof = {
      proofId: `DIN-PRF-${Math.random().toString(36).slice(2, 6).toUpperCase()}-${Math.random().toString(36).slice(2, 4).toUpperCase()}`,
      verificationId: verification.id,
      status: 'active',
      organisation: request.organisation,
      purpose: request.purpose,
      verifiedDocuments: verification.documents.filter(d => d.status === 'verified').map(d => ({ id: d.id, title: d.title, issuer: d.issuer })),
      issuedAt: iso(issued),
      expiresAt: iso(expires),
      revokedAt: null,
      version: 1,
      audit: [{ type: 'PROOF_CREATED', timestamp: iso(issued) }]
    };
    proofs.set(proof.proofId, proof);
    return proof;
  },
  async getProof(id) {
    const p = proofs.get(id);
    if (!p) return null;
    if (p.status === 'active' && new Date(p.expiresAt) <= now()) {
      p.status = 'expired';
      p.audit.push({ type: 'PROOF_EXPIRED', timestamp: iso(now()) });
    }
    return p;
  },
  async validateProof(id) {
    const p = await this.getProof(id);
    if (!p) return { status: 'invalid', message: 'This proof is not recognised by DigiIn.' };
    p.audit.push({ type: 'PROOF_VALIDATED', timestamp: iso(now()) });
    return { status: p.status, proof: p };
  },
  async revokeProof(id) {
    const p = await this.getProof(id);
    if (!p || p.status !== 'active') return p;
    p.status = 'revoked';
    p.revokedAt = iso(now());
    p.audit.push({ type: 'PROOF_REVOKED', timestamp: p.revokedAt });
    return p;
  },
  getShareUrl(id) { return `${location.origin}${location.pathname}#/verify-proof?id=${encodeURIComponent(id)}`; },
  async history() { return [...proofs.values()]; }
};
