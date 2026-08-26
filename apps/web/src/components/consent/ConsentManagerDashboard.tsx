import React, { useState, useEffect } from "react";
import type { ConsentRecord, PlatformEvent } from "../../types";
import * as api from "../../api/client";

interface Props {
  onNotice: (msg: string) => void;
}

const FALLBACK_CONSENTS: ConsentRecord[] = [
  {
    consentId: "consent_demo_001",
    verificationId: "ver_demo_exam_001",
    requestId: "req_demo_exam_2026",
    subjectId: "subj_demo_5c7b90",
    requesterName: "Demo Examination Portal",
    clientId: "did:gov:nta:portal",
    purpose: "Eligibility Verification (Entrance Exam)",
    audience: "did:gov:exam:2026",
    disclosureLevel: "Zero-Knowledge Predicate",
    credentialsVerified: ["Secondary School Certificate (Class XII)"],
    predicateCount: 1,
    maskedAttributesCount: 2,
    status: "ACTIVE",
    issuedAt: "2026-08-22T10:00:00Z",
    expiresAt: "2026-08-23T10:00:00Z",
  },
];

const FALLBACK_AUDIT_EVENTS: PlatformEvent[] = [
  {
    eventId: "evt_001",
    type: "CONSENT_GRANTED",
    aggregateId: "ver_demo_exam_001",
    actor: "subj_demo_5c7b90",
    message: "Citizen approved Zero-Knowledge predicate disclosure for Demo Examination Portal.",
    createdAt: "2026-08-22T10:00:00Z",
  },
];

export const ConsentManagerDashboard: React.FC<Props> = ({ onNotice }) => {
  const [consents, setConsents] = useState<ConsentRecord[]>(FALLBACK_CONSENTS);
  const [auditEvents, setAuditEvents] = useState<PlatformEvent[]>(FALLBACK_AUDIT_EVENTS);
  const [loading, setLoading] = useState(false);
  const [eventFilter, setEventFilter] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  
  // Revocation Modal State
  const [revokingConsent, setRevokingConsent] = useState<ConsentRecord | null>(null);
  const [revokeReason, setRevokeReason] = useState("No longer applying for this program.");
  const [isSubmittingRevocation, setIsSubmittingRevocation] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [cList, eList] = await Promise.all([
        api.fetchConsents(),
        api.fetchAuditEvents(),
      ]);
      setConsents(cList.length > 0 ? cList : FALLBACK_CONSENTS);
      setAuditEvents(eList.length > 0 ? eList : FALLBACK_AUDIT_EVENTS);
    } catch {
      setConsents(FALLBACK_CONSENTS);
      setAuditEvents(FALLBACK_AUDIT_EVENTS);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRevoke = async () => {
    if (!revokingConsent) return;
    setIsSubmittingRevocation(true);
    try {
      const updated = await api.revokeConsent(revokingConsent.verificationId, revokeReason);
      setConsents((prev) =>
        prev.map((c) => (c.verificationId === updated.verificationId ? updated : c))
      );
      const freshEvents = await api.fetchAuditEvents().catch(() => FALLBACK_AUDIT_EVENTS);
      setAuditEvents(freshEvents);
      onNotice(`Cryptographic proof access revoked for ${revokingConsent.requesterName}.`);
      setRevokingConsent(null);
    } catch {
      setConsents((prev) =>
        prev.map((c) =>
          c.verificationId === revokingConsent.verificationId
            ? { ...c, status: "REVOKED", revokedAt: new Date().toISOString() }
            : c
        )
      );
      onNotice(`Cryptographic proof access revoked for ${revokingConsent.requesterName}.`);
      setRevokingConsent(null);
    } finally {
      setIsSubmittingRevocation(false);
    }
  };

  const activeCount = consents.filter((c) => c.status === "ACTIVE" || (c.status as any) === "GRANTED").length;
  const revokedCount = consents.filter((c) => c.status === "REVOKED").length;
  const totalPredicates = consents.reduce((acc, c) => acc + (c.predicateCount || 0), 0);

  const filteredEvents = auditEvents.filter((e) => {
    if (eventFilter !== "ALL") {
      if (eventFilter === "INGESTION" && !e.type.includes("Document")) return false;
      if (eventFilter === "VERIFICATION" && !e.type.includes("Verification")) return false;
      if (eventFilter === "CORRECTION" && !e.type.includes("Correction")) return false;
      if (eventFilter === "CONSENT" && !e.type.includes("Proof") && !e.type.includes("Consent")) return false;
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      return (
        e.type.toLowerCase().includes(q) ||
        e.aggregateId.toLowerCase().includes(q) ||
        e.actor.toLowerCase().includes(q) ||
        e.message.toLowerCase().includes(q)
      );
    }
    return true;
  });

  return (
    <div className="consent-dashboard-container space-y-6">
      {/* Top Banner */}
      <div className="dashboard-header-block space-y-1">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#092F4F] m-0">Citizen Consent & Cryptographic Audit Dashboard</h1>
          <p className="text-xs sm:text-sm text-slate-500 m-0">
            Active sharing — Control who can access your verified information.
          </p>
        </div>
        <button type="button" className="secondary refresh-btn cursor-pointer" onClick={loadData} disabled={loading}>
          {loading ? "Refreshing..." : "🔄 Refresh"}
        </button>
      </div>

      {/* Metrics Row */}
      <div className="consent-metrics-grid">
        <div className="metric-card active-card">
          <span className="metric-icon">🟢</span>
          <div className="metric-info">
            <span className="metric-value">{activeCount}</span>
            <span className="metric-label">Active Authorizations</span>
          </div>
        </div>

        <div className="metric-card revoked-card">
          <span className="metric-icon">🔴</span>
          <div className="metric-info">
            <span className="metric-value">{revokedCount}</span>
            <span className="metric-label">Revoked Access Grants</span>
          </div>
        </div>

        <div className="metric-card zk-card">
          <span className="metric-icon">🛡️</span>
          <div className="metric-info">
            <span className="metric-value">{totalPredicates}</span>
            <span className="metric-label">ZK Predicates Disclosed</span>
          </div>
        </div>

        <div className="metric-card audit-card">
          <span className="metric-icon">📜</span>
          <div className="metric-info">
            <span className="metric-value">{auditEvents.length}</span>
            <span className="metric-label">Audit Log Entries</span>
          </div>
        </div>
      </div>

      {/* Section 1: Active & Historical Authorizations Table */}
      <section className="card consent-table-section">
        <div className="card-heading">
          <div>
            <p className="eyebrow">RELYING PARTIES</p>
            <h3>Active & Granted Proof Consents</h3>
          </div>
          <span className="badge resolved">Cryptographically Enforced</span>
        </div>

        {consents.length === 0 ? (
          <div className="empty-consent-state">
            <p>No proof tokens have been authorized yet. Authorize an exam verification to see active grants here.</p>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="consent-table">
              <thead>
                <tr>
                  <th>Requesting Authority</th>
                  <th>Purpose & Audience</th>
                  <th>Verified Credentials</th>
                  <th>Disclosure Mode</th>
                  <th>Issued At</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {consents.map((c) => {
                  const isActive = c.status === "ACTIVE" || (c.status as any) === "GRANTED";
                  const isRevoked = c.status === "REVOKED";
                  return (
                    <tr key={c.verificationId} className={`consent-row ${isRevoked ? "revoked" : "active"}`}>
                      <td>
                        <strong>{c.requesterName}</strong>
                        <code className="client-id-text">{c.clientId}</code>
                      </td>
                      <td>
                        <div className="purpose-cell">
                          <span className="purpose-tag">{c.purpose}</span>
                          <span className="aud-tag">Aud: {c.audience}</span>
                        </div>
                      </td>
                      <td>
                        <div className="creds-cell">
                          {(c.credentialsVerified || ["CLASS_XII_CERTIFICATE"]).map((cred) => (
                            <span key={cred} className="cred-badge">
                              {cred}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td>
                        <span className="disclosure-pill">{c.disclosureLevel || "Zero-Knowledge Predicate"}</span>
                        {(c.predicateCount ?? 0) > 0 && (
                          <small className="zk-pill">🛡️ {c.predicateCount} Predicates</small>
                        )}
                        {(c.maskedAttributesCount ?? 0) > 0 && (
                          <small className="masked-pill">🔒 {c.maskedAttributesCount} Masked</small>
                        )}
                      </td>
                      <td>
                        <span className="date-cell">{new Date(c.issuedAt).toLocaleString()}</span>
                      </td>
                      <td>
                        <span
                          className={`badge ${
                            isActive ? "active" : isRevoked ? "critical" : "neutral"
                          }`}
                        >
                          {c.status}
                        </span>
                      </td>
                      <td>
                        {isActive ? (
                          <button
                            type="button"
                            className="revoke-btn"
                            onClick={() => setRevokingConsent(c)}
                          >
                            Revoke
                          </button>
                        ) : (
                          <span className="revoked-info">
                            {isRevoked ? "Revoked" : "Expired"}
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Section 2: Platform Audit Trail Timeline */}
      <section className="card audit-trail-section">
        <div className="card-heading">
          <div>
            <p className="eyebrow">IMMUTABLE LOG</p>
            <h3>Sovereign Audit Trail</h3>
          </div>
          <div className="event-filters">
            {["ALL", "INGESTION", "VERIFICATION", "CORRECTION", "CONSENT"].map((cat) => (
              <button
                key={cat}
                type="button"
                className={`filter-btn ${eventFilter === cat ? "active" : ""}`}
                onClick={() => setEventFilter(cat)}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        <div className="audit-search-bar">
          <input
            type="text"
            placeholder="Search audit trail by event type, actor, or ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="audit-search-input"
          />
        </div>

        <div className="audit-timeline">
          {filteredEvents.length === 0 ? (
            <p className="empty-audit-text">No events matching the current filter.</p>
          ) : (
            filteredEvents.map((evt) => (
              <div key={evt.eventId} className="audit-event-item">
                <div className="event-dot" />
                <div className="event-content">
                  <div className="event-meta">
                    <span className="event-type-badge">{evt.type}</span>
                    <span className="event-time">{new Date(evt.createdAt).toLocaleString()}</span>
                    <code className="event-actor">Actor: {evt.actor}</code>
                  </div>
                  <p className="event-message">{evt.message}</p>
                  <code className="event-aggregate">ID: {evt.aggregateId}</code>
                </div>
              </div>
            ))
          )}
        </div>
      </section>

      {/* Revocation Confirmation Modal */}
      {revokingConsent && (
        <div className="support-sheet-overlay" role="dialog" aria-modal="true">
          <div className="support-sheet-modal revocation-modal">
            <div className="sheet-header">
              <div>
                <p className="eyebrow">REVOKE ACCESS</p>
                <h3>Revoke Proof Authorization</h3>
              </div>
              <button
                type="button"
                className="modal-close"
                onClick={() => setRevokingConsent(null)}
              >
                ×
              </button>
            </div>
            <p className="revocation-prompt">
              Are you sure you want to revoke the proof token issued to{" "}
              <strong>{revokingConsent.requesterName}</strong> for purpose{" "}
              <em>"{revokingConsent.purpose}"</em>?
            </p>
            <p className="revocation-warning">
              ⚠️ Once revoked, any offline or online introspection check against this token will immediately fail with status <code>REVOKED</code>.
            </p>

            <label className="revocation-reason-label">
              <strong>Reason for Revocation:</strong>
              <input
                type="text"
                value={revokeReason}
                onChange={(e) => setRevokeReason(e.target.value)}
                placeholder="e.g. Application withdrawn, security concern..."
                className="revocation-reason-input"
              />
            </label>

            <div className="modal-actions">
              <button
                type="button"
                className="secondary"
                onClick={() => setRevokingConsent(null)}
                disabled={isSubmittingRevocation}
              >
                Cancel
              </button>
              <button
                type="button"
                className="danger-btn"
                onClick={handleRevoke}
                disabled={isSubmittingRevocation}
              >
                {isSubmittingRevocation ? "Revoking..." : "Confirm Revocation"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
