export const Button = ({ label, href, variant = 'primary', size = 'normal', type = 'button', className = '', id = '', icon = '', disabled = false }) => {
  const cls = `btn btn-${variant} ${size === 'small' ? 'btn-small' : ''} ${size === 'lg' ? 'btn-lg' : ''} ${className}`.trim();
  const iconMarkup = icon ? ` <span aria-hidden="true">${icon}</span>` : '';
  if (href) {
    return `<a class="${cls}" href="${href}" ${id ? `id="${id}"` : ''}>${label}${iconMarkup}</a>`;
  }
  return `<button class="${cls}" type="${type}" ${id ? `id="${id}"` : ''} ${disabled ? 'disabled' : ''}>${label}${iconMarkup}</button>`;
};

export const Badge = ({ label, tone = 'default', icon = '' }) => {
  const iconMarkup = icon ? `<span aria-hidden="true">${icon}</span> ` : '';
  return `<span class="badge badge-${tone}">${iconMarkup}${label}</span>`;
};

export const Card = ({ title, children, className = '' }) => {
  return `<section class="card ${className}">${title ? `<h3 class="card-title">${title}</h3>` : ''}${children}</section>`;
};

export const Alert = ({ title, message, tone = 'info' }) => {
  return `<div class="alert alert-${tone}" role="alert"><strong>${title}</strong><p>${message}</p></div>`;
};

export const Field = ({ id, label, hint = '', type = 'text', value = '', placeholder = '', required = false, readonly = false }) => {
  return `<div class="field"><label for="${id}">${label}</label>${hint ? `<span class="hint">${hint}</span>` : ''}<input id="${id}" type="${type}" value="${value}" placeholder="${placeholder}" ${required ? 'required' : ''} ${readonly ? 'readonly' : ''} /></div>`;
};

export const Status = ({ status }) => {
  const map = {
    verified: { label: 'Verified', tone: 'success', icon: '✓' },
    pending: { label: 'Pending', tone: 'warning', icon: '•' },
    retrieving: { label: 'Ready', tone: 'info', icon: '↓' },
    failed: { label: 'Failed', tone: 'danger', icon: '✕' },
    partial: { label: 'Partially verified', tone: 'warning', icon: '!' }
  };
  const s = map[status] || map.pending;
  return `<span class="status-pill status-${s.tone}"><span class="status-icon" aria-hidden="true">${s.icon}</span> ${s.label}</span>`;
};

export const DocumentCard = ({ title, issuer, detail, status = 'verified' }) => {
  return `<article class="document-card"><div class="document-card-header"><div><h4>${title}</h4><span class="muted">${issuer}</span></div>${Status({ status })}</div>${detail ? `<p class="document-card-detail">${detail}</p>` : ''}</article>`;
};

export const OrganisationIdentity = ({ name, category = 'Verified Organisation', requestId = 'VR-82A91' }) => {
  return `<div class="requester"><div class="org-mark">${name.split(' ').map(w => w[0]).slice(0,2).join('')}</div><div class="org-info"><strong>${name}</strong><span>${category}</span><small class="request-id-badge">Request ID: ${requestId}</small></div><span class="verified-org">✓ Verified</span></div>`;
};

export const RequestedDocumentCard = ({ title, issuer, purpose, required = true, claims = [] }) => {
  return `<div class="requested requested-rich"><div class="document-mini-icon" aria-hidden="true">▤</div><div class="requested-body"><strong>${title}</strong><span class="muted">Issued by ${issuer}</span><small class="purpose-tag">Purpose: ${purpose}</small>${claims.length ? `<div class="claims-preview">${claims.map(c => `<code>${c}</code>`).join(' ')}</div>` : ''}</div><span class="required-label ${required ? 'req-true' : 'req-opt'}">${required ? 'Required' : 'Optional'}</span></div>`;
};

export const Stepper = ({ steps, current }) => {
  return `<ol class="stepper" aria-label="Progress">${steps.map((s, i) => `<li class="${i === current ? 'current' : i < current ? 'complete' : ''}" aria-current="${i === current ? 'step' : 'false'}"><span class="step-num">${i < current ? '✓' : i + 1}</span><span>${s}</span></li>`).join('')}</ol>`;
};

export const VerificationTimeline = ({ stages = [] }) => {
  return `
    <div class="timeline-card">
      <ul class="timeline-list">
        ${stages.map((st, i) => `
          <li class="timeline-item ${st.status === 'completed' ? 'done' : st.status === 'in_progress' ? 'active' : st.status === 'failed' ? 'failed' : ''}">
            <div class="timeline-icon">${st.status === 'completed' ? '✓' : st.status === 'failed' ? '✕' : i + 1}</div>
            <div class="timeline-content">
              <strong>${st.title}</strong>
              <p>${st.description}</p>
            </div>
          </li>
        `).join('')}
      </ul>
    </div>
  `;
};

export const DocumentDetailCard = ({ id, name, issuer, status, verifiedAt, checks = [] }) => {
  return `
    <div class="card" style="margin-bottom: 1rem;">
      <div class="document-card-header">
        <div>
          <h4>${name}</h4>
          <span class="muted">Issued by ${issuer}</span>
        </div>
        ${Status({ status })}
      </div>
      
      <div style="margin-top: 1rem; border-top: 1px solid var(--color-border-subtle); padding-top: 0.75rem;">
        <strong style="font-size: 0.85rem; text-transform: uppercase; color: var(--color-text-muted); letter-spacing: 0.05em;">Verification Checks</strong>
        <ul style="list-style: none; padding: 0; margin: 0.5rem 0 0; display: grid; gap: 0.5rem;">
          ${checks.map(c => `
            <li style="display: flex; align-items: start; gap: 0.5rem; font-size: 0.85rem;">
              <span style="color: ${c.status === 'passed' ? 'var(--color-success-700)' : c.status === 'warning' ? 'var(--color-warning-700)' : 'var(--color-error-700)'}; font-weight: 800;">
                ${c.status === 'passed' ? '✓' : c.status === 'warning' ? '!' : '✕'}
              </span>
              <div>
                <strong>${c.label}</strong>
                <p class="muted" style="margin: 0; font-size: 0.78rem;">${c.message}</p>
              </div>
            </li>
          `).join('')}
        </ul>
      </div>
      <div style="margin-top: 0.75rem; font-size: 0.78rem; color: var(--color-text-muted);">
        Verified on <strong>${verifiedAt || '23 Aug 2026'}</strong>
      </div>
    </div>
  `;
};

export const ProofEnvelopeCard = ({ proofId, algorithm = 'EdDSA', keyId = 'digiin-ed25519-key-2026', status = 'VERIFIED' }) => {
  return `
    <div class="proof-envelope">
      <div class="proof-envelope-header">
        <span>🔐 RFC 7515/7519 Verifiable Credential Proof</span>
        <span>Algorithm: ${algorithm}</span>
      </div>
      <pre>{
  "proof_id": "${proofId}",
  "type": "Ed25519SignedAssertion",
  "issuer": "DigiLocker X Sovereign Gateway",
  "audience": "ABC University (AY 2026-27)",
  "key_id": "${keyId}",
  "status": "${status}",
  "claims": {
    "candidate_name": "Rahul Sharma",
    "class_x_verified": true,
    "class_xii_verified": true,
    "predicate_percentage_gte_60": true,
    "raw_documents_stored": false
  }
}</pre>
    </div>
  `;
};
