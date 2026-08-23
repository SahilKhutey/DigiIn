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
    OPERATIONAL: { label: 'Operational', tone: 'success', icon: '✓' },
    DEGRADED: { label: 'Degraded', tone: 'warning', icon: '!' },
    OUTAGE: { label: 'Outage', tone: 'danger', icon: '✕' },
    DELIVERED: { label: 'Delivered (200 OK)', tone: 'success', icon: '✓' },
    FAILED: { label: 'Failed (500)', tone: 'danger', icon: '✕' },
    RETRYING: { label: 'Retrying', tone: 'warning', icon: '↻' },
    ACTIVE: { label: 'Active', tone: 'success', icon: '✓' },
    VERIFIED: { label: 'Verified', tone: 'success', icon: '✓' },
    EXPIRED: { label: 'Expired', tone: 'danger', icon: '!' },
    CONNECTED: { label: 'Connected', tone: 'success', icon: '✓' }
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
    { label: '🔔 Notifications', href: '#/organisation/notifications', id: '/organisation/notifications' },
    { label: '📈 API Analytics', href: '#/organisation/developer/usage', id: '/organisation/developer/usage' },
    { label: '🔌 Integrations', href: '#/organisation/integrations', id: '/organisation/integrations' },
    { label: '⚡ Dev Webhooks', href: '#/organisation/developer/webhooks', id: '/organisation/developer/webhooks' },
    { label: '🏢 Profile', href: '#/organisation/profile', id: '/organisation/profile' }
  ];

  return `
    <aside class="portal-sidebar">
      <nav aria-label="Organisation Navigation">
        <ul class="sidebar-nav">
          ${links.map(l => `
            <li>
              <a href="${l.href}" class="${currentRoute === l.id || (l.id !== '/organisation/dashboard' && currentRoute.startsWith(l.id)) ? 'active' : ''}">${l.label}</a>
            </li>
          `).join('')}
        </ul>
      </nav>
      <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid var(--color-border-subtle);">
        <a href="#/status" class="btn btn-secondary btn-small block" style="font-size: 0.8rem;">🌐 Service Status</a>
      </div>
    </aside>
  `;
};

export const NotificationItem = ({ notif }) => {
  return `
    <div class="card" style="padding: 1rem; margin-bottom: 0.75rem; border-left: 4px solid ${notif.read ? 'var(--color-border)' : 'var(--color-primary-700)'};">
      <div style="display: flex; justify-content: space-between; align-items: start;">
        <div style="display: flex; gap: 0.5rem; align-items: center;">
          <span style="font-size: 1.1rem;">${notif.read ? '○' : '●'}</span>
          <strong>${notif.title}</strong>
        </div>
        <small class="muted">${notif.createdAt}</small>
      </div>
      <p class="muted" style="margin: 0.35rem 0 0.5rem 1.6rem; font-size: 0.88rem;">${notif.message}</p>
      ${notif.actionUrl ? `
        <div style="margin-left: 1.6rem;">
          <a class="link-button" href="${notif.actionUrl}" style="font-size: 0.82rem; font-weight: 700; text-decoration: underline;">View action →</a>
        </div>
      ` : ''}
    </div>
  `;
};

export const HealthStatusGrid = ({ services = [] }) => {
  return `
    <div style="display: grid; gap: 0.75rem; margin-top: 1rem;">
      ${services.map(s => `
        <div class="card" style="display: flex; justify-content: space-between; align-items: center; padding: 0.85rem 1.2rem;">
          <div>
            <strong>${s.service}</strong>
            <div class="muted" style="font-size: 0.78rem;">Latency: ${s.latency} • Version: ${s.version}</div>
          </div>
          ${Status({ status: s.status })}
        </div>
      `).join('')}
    </div>
  `;
};

export const PublicStatusBanner = ({ allOperational = true, lastUpdated = 'Now' }) => {
  return `
    <div class="card text-center" style="background: ${allOperational ? 'var(--color-success-100)' : 'var(--color-warning-100)'}; border-color: ${allOperational ? '#b9e5cb' : '#f1d88d'}; padding: 2rem;">
      <div class="result-icon" style="background: ${allOperational ? 'var(--color-success-700)' : 'var(--color-warning-700)'}; color: #fff; width: 64px; height: 64px; font-size: 1.8rem;">
        ${allOperational ? '✓' : '!'}
      </div>
      <h2 style="margin: 0.5rem 0 0.25rem; color: var(--color-text);">${allOperational ? 'All Systems Operational' : 'Partial Service Degradation'}</h2>
      <p class="muted" style="margin: 0;">DigiIn verification services, DigiLocker integration, and proof portals are running smoothly.</p>
      <small class="muted" style="display: block; margin-top: 0.75rem;">Last checked: ${lastUpdated}</small>
    </div>
  `;
};

export const RateLimitCard = ({ limit = 1000, remaining = 742, resetIn = '42 minutes' }) => {
  return `
    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
          <span class="eyebrow">API Rate Limit</span>
          <h4 style="margin: 0.25rem 0 0;">Hourly Request Allocation</h4>
        </div>
        ${Badge({ label: `${remaining} / ${limit} Remaining`, tone: 'info' })}
      </div>
      <div style="margin-top: 1rem; background: var(--color-surface-alt); border-radius: var(--radius-full); height: 10px; overflow: hidden;">
        <div style="background: var(--color-primary-700); height: 100%; width: ${(remaining / limit) * 100}%;"></div>
      </div>
      <small class="muted" style="display: block; margin-top: 0.5rem;">Resets in ${resetIn}. Rate limit enforced by RFC 6585 gateway standards.</small>
    </div>
  `;
};

export const IntegrationGrid = ({ integrations = [] }) => {
  return `
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; margin-top: 1rem;">
      ${integrations.map(it => `
        <div class="card">
          <div style="display: flex; justify-content: space-between; align-items: start;">
            <div>
              <strong style="font-size: 1.05rem;">${it.name}</strong>
              <div class="muted" style="font-size: 0.78rem;">${it.type} • v${it.version}</div>
            </div>
            ${Status({ status: it.status })}
          </div>
          <p class="muted" style="margin: 0.75rem 0; font-size: 0.82rem;">${it.description || 'Enterprise sovereign connector.'}</p>
          <small class="muted">Last sync: ${it.lastSync}</small>
        </div>
      `).join('')}
    </div>
  `;
};
