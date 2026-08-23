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
    failed: { label: 'Action needed', tone: 'danger', icon: '✕' },
    partial: { label: 'Partial', tone: 'warning', icon: '!' }
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

export const ExternalServiceCard = ({ name = 'DigiLocker', logo = 'DL', description, securityPoints = [] }) => {
  return `<div class="external-card"><div class="external-service-logo">${logo}</div><h2>Connect to ${name}</h2><p class="muted">${description || 'You will authenticate directly with the external provider.'}</p><div class="security-points">${securityPoints.map(p => `<div>✓ ${p}</div>`).join('')}</div></div>`;
};

export const Stepper = ({ steps, current }) => {
  return `<ol class="stepper" aria-label="Progress">${steps.map((s, i) => `<li class="${i === current ? 'current' : i < current ? 'complete' : ''}" aria-current="${i === current ? 'step' : 'false'}"><span class="step-num">${i < current ? '✓' : i + 1}</span><span>${s}</span></li>`).join('')}</ol>`;
};
