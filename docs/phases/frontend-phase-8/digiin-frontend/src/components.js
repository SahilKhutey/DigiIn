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

export const Status = ({ status }) => {
  const map = {
    COMPLETED: { label: 'Verified', tone: 'success', icon: '✓' },
    VERIFIED: { label: 'Verified', tone: 'success', icon: '✓' },
    AWAITING_CONSENT: { label: 'Waiting for citizen', tone: 'warning', icon: '•' },
    PENDING: { label: 'Pending', tone: 'warning', icon: '•' },
    DOCUMENT_RETRIEVING: { label: 'Retrieving', tone: 'info', icon: '↓' },
    VERIFYING: { label: 'Verifying', tone: 'info', icon: '⚡' },
    EXPIRED: { label: 'Expired', tone: 'danger', icon: '!' },
    CANCELLED: { label: 'Cancelled', tone: 'neutral', icon: '✕' },
    DECLINED: { label: 'Declined', tone: 'danger', icon: '✕' }
  };
  const s = map[status] || { label: status, tone: 'neutral', icon: '•' };
  return `<span class="status-pill status-${s.tone}"><span class="status-icon" aria-hidden="true">${s.icon}</span> ${s.label}</span>`;
};

export const Stepper = ({ steps, current }) => {
  return `<ol class="stepper" aria-label="Progress">${steps.map((s, i) => `<li class="${i === current ? 'current' : i < current ? 'complete' : ''}" aria-current="${i === current ? 'step' : 'false'}"><span class="step-num">${i < current ? '✓' : i + 1}</span><span>${s}</span></li>`).join('')}</ol>`;
};

export const OrganisationSidebar = ({ currentRoute = '/organisation/dashboard' }) => {
  const links = [
    { label: '📊 Dashboard', href: '#/organisation/dashboard', id: '/organisation/dashboard' },
    { label: '📋 Requests', href: '#/organisation/requests', id: '/organisation/requests' },
    { label: '➕ Create Request', href: '#/organisation/requests/new', id: '/organisation/requests/new' },
    { label: '🛡️ Verify Proof', href: '#/organisation/verify-proof', id: '/organisation/verify-proof' },
    { label: '📜 History', href: '#/organisation/history', id: '/organisation/history' },
    { label: '🏢 Profile', href: '#/organisation/profile', id: '/organisation/profile' }
  ];

  return `
    <aside class="portal-sidebar">
      <nav aria-label="Organisation Menu">
        <ul class="sidebar-nav">
          ${links.map(l => `
            <li>
              <a href="${l.href}" class="${currentRoute === l.id || (l.id !== '/organisation/dashboard' && currentRoute.startsWith(l.id)) ? 'active' : ''}">${l.label}</a>
            </li>
          `).join('')}
        </ul>
      </nav>
      <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid var(--color-border-subtle);">
        <a href="#/organisation/sign-in" class="btn btn-secondary btn-small block" style="color: var(--color-error-700);">Sign out</a>
      </div>
    </aside>
  `;
};

export const MetricCard = ({ label, value, subtext, tone = 'default' }) => {
  return `
    <div class="stat-card">
      <small style="color: var(--color-text-muted); font-weight: 700; text-transform: uppercase; font-size: 0.72rem;">${label}</small>
      <strong>${value}</strong>
      ${subtext ? `<span>${subtext}</span>` : ''}
    </div>
  `;
};

export const RequestTable = ({ requests = [] }) => {
  if (!requests.length) {
    return `<div class="card text-center muted" style="padding: 2rem;">No verification requests found for this filter.</div>`;
  }

  return `
    <div class="data-table-card">
      <table class="data-table" aria-label="Verification Requests Table">
        <thead>
          <tr>
            <th>Request ID</th>
            <th>Citizen</th>
            <th>Purpose</th>
            <th>Status</th>
            <th>Created</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          ${requests.map(r => `
            <tr>
              <td><strong style="font-family: var(--font-mono); color: var(--color-primary-900);">${r.id}</strong></td>
              <td>${r.citizenName || r.citizenId}</td>
              <td>${r.purpose}</td>
              <td>${Status({ status: r.status })}</td>
              <td><small class="muted">${r.createdAt}</small></td>
              <td>
                <a class="btn btn-secondary btn-small" href="#/organisation/requests/${r.id}">View</a>
              </td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
};

export const RequestDetailCard = ({ req }) => {
  return `
    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: start; border-bottom: 1px solid var(--color-border-subtle); padding-bottom: 1rem;">
        <div>
          <span class="eyebrow">Verification Request</span>
          <h2 style="margin: 0.35rem 0 0; font-family: var(--font-mono);">${req.id}</h2>
        </div>
        ${Status({ status: req.status })}
      </div>

      <div class="request-summary" style="margin: 1.5rem 0;">
        <div><small>Citizen Account</small><strong style="font-family: var(--font-mono);">${req.citizenId}</strong></div>
        <div><small>Purpose</small><strong>${req.purpose}</strong></div>
        <div><small>Created on</small><strong>${req.createdAt}</strong></div>
        <div><small>Expires on</small><strong>${req.expiresAt}</strong></div>
      </div>

      <h3>Requested documents</h3>
      <div class="verification-list" style="margin-bottom: 1.5rem;">
        ${req.documents.map(d => `
          <div>
            <span class="badge badge-info">Requested</span>
            <div>
              <strong>${d.title}</strong>
              <div style="font-size: 0.78rem; color: var(--color-text-muted);">${d.reason}</div>
            </div>
            <small>${d.required ? 'Required' : 'Optional'}</small>
          </div>
        `).join('')}
      </div>

      <h3>Consent Status</h3>
      <div class="card" style="background: var(--color-surface-alt); margin-bottom: 1.5rem;">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
          <strong style="color: ${req.consent.granted ? 'var(--color-success-700)' : 'var(--color-warning-700)'};">
            ${req.consent.granted ? '✓ Explicit Consent Granted' : '• Awaiting Citizen Consent'}
          </strong>
        </div>
        <p class="muted" style="margin: 0.35rem 0 0; font-size: 0.85rem;">
          ${req.consent.granted ? `Scope: ${req.consent.scope} (Granted at ${req.consent.grantedAt})` : 'The citizen has not yet authorized document retrieval.'}
        </p>
      </div>

      ${req.verificationResult ? `
        <h3>Verification Outcome</h3>
        <div class="card" style="border: 2px solid var(--color-success-700); margin-bottom: 1.5rem;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
              <span class="badge badge-success">✓ Level 4 Verified</span>
              <h4 style="margin: 0.25rem 0 0;">${req.verificationResult.verifiedCount} / ${req.verificationResult.totalCount} Documents Verified</h4>
            </div>
            <strong style="font-family: var(--font-mono);">${req.verificationResult.verificationId}</strong>
          </div>
          <p class="muted" style="font-size: 0.85rem; margin-top: 0.5rem;">
            Verifiable Credential proof minted under RFC 7515/7519.
          </p>
          <div class="actions" style="margin-top: 1rem;">
            <a class="btn btn-primary btn-small" href="#/proof/${req.verificationResult.proofId}">View verification proof →</a>
          </div>
        </div>
      ` : ''}

      <div class="actions" style="margin-top: 1.5rem;">
        <a class="btn btn-secondary" href="#/organisation/requests">← Back to requests</a>
        ${(req.status === 'AWAITING_CONSENT' || req.status === 'CREATED') ? `
          <button id="cancel-req-btn" class="btn btn-secondary text-danger" style="color: var(--color-error-700);" type="button">Cancel request</button>
        ` : ''}
      </div>
    </div>
  `;
};
