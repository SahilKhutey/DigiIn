import {
  Button,
  Badge,
  Card,
  Alert,
  Status,
  Stepper,
  OrganisationSidebar,
  NotificationItem,
  HealthStatusGrid,
  PublicStatusBanner,
  RateLimitCard,
  IntegrationGrid
} from './components.js';

import { notificationService } from './services/notifications/notificationService.js';
import { webhookDeliveryService } from './services/webhooks/webhookDeliveryService.js';
import { usageService } from './services/analytics/usageService.js';
import { healthService } from './services/health/healthService.js';
import { statusService } from './services/status/statusService.js';
import { integrationService } from './services/integrations/integrationService.js';
import { eventService } from './services/events/eventService.js';

const app = document.querySelector('#app');
const path = () => location.hash.replace(/^#/, '') || '/status';
const go = (p) => { location.hash = p; };

const Header = () => `
  <div class="top">
    <div class="container top-inner">
      <span>भारत सरकार • Government of India</span>
      <span>Digital India Initiative • Phase 10 Platform Operations</span>
    </div>
  </div>
  <header class="header">
    <div class="container head">
      <a class="brand" href="#/status" aria-label="DigiIn Platform Home">
        <span class="mark">DI</span>
        <span>DigiIn<small>Platform Integration & Observability</small></span>
      </a>
      <nav class="nav" aria-label="Primary">
        <a href="#/notifications">Citizen Alerts</a>
        <a href="#/organisation/dashboard">Organisation Portal</a>
        <a href="#/organisation/developer/usage">API Analytics</a>
        <a href="#/organisation/integrations">Integrations</a>
        <a href="#/admin/system">System Health</a>
        <a href="#/status">Public Status</a>
      </nav>
      <div class="actions">
        <a href="#/notifications" class="badge badge-info" style="text-decoration: none; padding: 0.4rem 0.75rem;">🔔 3 Alerts</a>
      </div>
    </div>
  </header>
`;

const Footer = () => `
  <footer class="footer">
    <div class="container footer-grid">
      <div>
        <strong>DigiIn Platform Mesh</strong>
        <p class="muted">Production-ready sovereign verification integration layer.</p>
      </div>
      <div>
        <strong>Platform Navigation</strong>
        <a href="#/status">Service Status</a>
        <a href="#/notifications">Notification Center</a>
        <a href="#/organisation/developer/usage">Usage Analytics</a>
        <a href="#/admin/system">Ops Health Console</a>
      </div>
      <div>
        <strong>Standards & Compliance</strong>
        <a href="#/security">Security Center</a>
        <a href="#/privacy">DPDP Act 2023</a>
        <a href="#/settings/notifications">Notification Settings</a>
      </div>
    </div>
    <div class="container footer-bottom">
      <small>Phase 10 • Integration, Webhooks, Notifications & Platform Observability</small>
    </div>
  </footer>
`;

const PageLayout = ({ title, eyebrow, description, children, sidebar = false, currentRoute = '' }) => `
  <main id="main" class="page container">
    ${eyebrow ? `<span class="eyebrow">${eyebrow}</span>` : ''}
    <h1>${title}</h1>
    ${description ? `<p class="lead muted">${description}</p>` : ''}
    
    ${sidebar ? `
      <div class="portal-layout">
        ${OrganisationSidebar({ currentRoute })}
        <div class="portal-content">
          ${children}
        </div>
      </div>
    ` : `
      <div style="margin-top: 1.5rem;">
        ${children}
      </div>
    `}
  </main>
`;

async function CitizenNotificationsView() {
  const notifs = await notificationService.getCitizenNotifications();

  return PageLayout({
    eyebrow: 'Citizen Workspace',
    title: 'Notifications',
    description: 'Real-time actionable alerts regarding verification requests, consent, and security.',
    children: `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
        <div class="tab-filter-row" style="margin: 0;">
          <button class="tab-filter-btn selected" type="button">All Alerts</button>
          <button class="tab-filter-btn" type="button">Unread</button>
          <button class="tab-filter-btn" type="button">Requests</button>
        </div>
        <a href="#/settings/notifications" class="link-button" style="font-size: 0.85rem; font-weight: 700;">⚙️ Notification preferences</a>
      </div>

      <div>
        ${notifs.map(n => NotificationItem({ notif: n })).join('')}
      </div>
    `
  });
}

function NotificationPreferencesView() {
  return PageLayout({
    eyebrow: 'Citizen Settings',
    title: 'Notification Preferences',
    description: 'Control multi-channel delivery options for verification transactions and alerts.',
    children: `
      <div class="card" style="max-width: 680px;">
        <h3>Channel Selection</h3>
        <p class="muted">Select where you receive notices. Security alerts cannot be disabled.</p>

        <div style="display: grid; gap: 1rem; margin: 1.5rem 0;">
          <div style="border-bottom: 1px solid var(--color-border-subtle); padding-bottom: 1rem;">
            <strong>Verification Requests</strong>
            <div style="display: flex; gap: 1.5rem; margin-top: 0.5rem;">
              <label><input type="checkbox" checked /> In-app</label>
              <label><input type="checkbox" checked /> Email</label>
              <label><input type="checkbox" /> SMS</label>
            </div>
          </div>

          <div style="border-bottom: 1px solid var(--color-border-subtle); padding-bottom: 1rem;">
            <strong>Verification Completed</strong>
            <div style="display: flex; gap: 1.5rem; margin-top: 0.5rem;">
              <label><input type="checkbox" checked /> In-app</label>
              <label><input type="checkbox" checked /> Email</label>
              <label><input type="checkbox" /> SMS</label>
            </div>
          </div>

          <div style="border-bottom: 1px solid var(--color-border-subtle); padding-bottom: 1rem;">
            <strong>Security & Access Alerts</strong>
            <div style="display: flex; gap: 1.5rem; margin-top: 0.5rem;">
              <label><input type="checkbox" checked disabled /> In-app (Mandatory)</label>
              <label><input type="checkbox" checked /> Email</label>
              <label><input type="checkbox" checked /> SMS</label>
            </div>
          </div>
        </div>

        <div class="actions">
          <button class="btn btn-primary" type="button" onclick="alert('Notification preferences saved.')">Save preferences</button>
          <a class="btn btn-secondary" href="#/notifications">Back to alerts</a>
        </div>
      </div>
    `
  });
}

async function OrganisationNotificationsView() {
  const notifs = await notificationService.getOrganisationNotifications();

  return PageLayout({
    eyebrow: 'Organisation Operations',
    title: 'Organisation Notifications',
    description: 'System and transaction updates for institutional verifiers.',
    sidebar: true,
    currentRoute: '/organisation/notifications',
    children: `
      <div>
        ${notifs.map(n => NotificationItem({ notif: n })).join('')}
      </div>
    `
  });
}

async function OrganisationUsageView() {
  const usage = await usageService.getDailyUsage();

  return PageLayout({
    eyebrow: 'Observability & Metrics',
    title: 'API Usage Analytics',
    description: 'Traffic volume, latency percentiles, and rate-limiting enforcement metrics.',
    sidebar: true,
    currentRoute: '/organisation/developer/usage',
    children: `
      <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.5rem;">
        <div class="stat-card">
          <small class="muted" style="font-weight: 700; text-transform: uppercase; font-size: 0.72rem;">Requests Today</small>
          <strong>${usage.totalRequests.toLocaleString()}</strong>
          <span class="muted">Lifetime: 48.2k</span>
        </div>
        <div class="stat-card">
          <small class="muted" style="font-weight: 700; text-transform: uppercase; font-size: 0.72rem;">Success Rate</small>
          <strong style="color: var(--color-success-700);">${usage.successRate}%</strong>
          <span class="muted">${usage.successfulRequests} successful</span>
        </div>
        <div class="stat-card">
          <small class="muted" style="font-weight: 700; text-transform: uppercase; font-size: 0.72rem;">Errors</small>
          <strong style="color: var(--color-error-700);">${usage.failedRequests}</strong>
          <span class="muted">0.3% rate limited</span>
        </div>
        <div class="stat-card">
          <small class="muted" style="font-weight: 700; text-transform: uppercase; font-size: 0.72rem;">Avg Latency</small>
          <strong>${usage.avgLatency}</strong>
          <span class="muted">p95: 142ms</span>
        </div>
      </div>

      ${RateLimitCard({ limit: 1000, remaining: 742, resetIn: '42 minutes' })}

      <div class="card" style="margin-top: 1.5rem;">
        <h3>Endpoint Traffic Breakdown</h3>
        <table class="data-table" style="margin-top: 1rem;">
          <thead>
            <tr>
              <th>Endpoint</th>
              <th>Method</th>
              <th>Calls Today</th>
              <th>Success Rate</th>
              <th>Avg Latency</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><code>/v1/verification-requests</code></td>
              <td><span class="badge badge-info">POST</span></td>
              <td>842</td>
              <td>99.4%</td>
              <td>82 ms</td>
            </tr>
            <tr>
              <td><code>/v1/verification-requests/:id</code></td>
              <td><span class="badge badge-info">GET</span></td>
              <td>268</td>
              <td>99.8%</td>
              <td>34 ms</td>
            </tr>
            <tr>
              <td><code>/v1/proofs/validate</code></td>
              <td><span class="badge badge-info">POST</span></td>
              <td>174</td>
              <td>100.0%</td>
              <td>48 ms</td>
            </tr>
          </tbody>
        </table>
      </div>
    `
  });
}

async function WebhookDeliveriesView() {
  const deliveries = await webhookDeliveryService.getRecentDeliveries();

  return PageLayout({
    eyebrow: 'Event Dispatcher',
    title: 'Webhook Deliveries',
    description: 'Inspect event dispatches, payload deliveries, and retry simulations.',
    sidebar: true,
    currentRoute: '/organisation/developer/webhooks',
    children: `
      <div class="card" style="margin-bottom: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div>
            <strong style="font-size: 1.1rem;">https://example.org/digiin/webhook</strong>
            <div class="muted" style="font-size: 0.8rem;">Subscribed to: <code>verification.created</code>, <code>verification.completed</code>, <code>proof.created</code></div>
          </div>
          ${Status({ status: 'ACTIVE' })}
        </div>
      </div>

      <h3>Recent Delivery Logs</h3>
      <div style="display: grid; gap: 0.75rem; margin-top: 1rem;">
        ${deliveries.map(d => `
          <div class="card" style="padding: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <div>
                <strong>Event: <code>${d.event}</code></strong>
                <div class="muted" style="font-size: 0.78rem;">Attempt ${d.attempt} • Response: ${d.latency} • Time: ${d.timestamp}</div>
              </div>
              ${Status({ status: d.status })}
            </div>
            <div style="margin-top: 0.5rem; background: var(--color-surface-alt); padding: 0.5rem; border-radius: var(--radius-sm); font-family: var(--font-mono); font-size: 0.75rem;">
              Payload: { "eventId": "${d.id}", "transactionId": "${d.transactionId}", "type": "${d.event}" }
            </div>
          </div>
        `).join('')}
      </div>
    `
  });
}

async function IntegrationsDashboardView() {
  const integrations = await integrationService.listIntegrations();

  return PageLayout({
    eyebrow: 'Ecosystem Connectors',
    title: 'Platform Integrations',
    description: 'Active connectors linking DigiIn with sovereign registries and messaging gateways.',
    sidebar: true,
    currentRoute: '/organisation/integrations',
    children: `
      ${IntegrationGrid({ integrations })}
    `
  });
}

async function SystemHealthView() {
  const services = await healthService.getServiceHealth();

  return PageLayout({
    eyebrow: 'Operations & SRE Console',
    title: 'System Health',
    description: 'Real-time uptime monitoring and latency telemetry for DigiIn platform microservices.',
    children: `
      <div class="card" style="background: var(--color-primary-900); color: #fff; margin-bottom: 1.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div>
            <span class="eyebrow" style="background: rgba(255,255,255,0.15); color: #fff;">SRE Observability</span>
            <h3 style="margin: 0.4rem 0 0; color: #fff;">DigiIn Sovereign Gateway Health</h3>
          </div>
          <span class="badge badge-success">✓ 99.99% Uptime SLA</span>
        </div>
      </div>

      ${HealthStatusGrid({ services })}
    `
  });
}

async function PublicStatusView() {
  const statusData = await statusService.getStatus();

  return PageLayout({
    eyebrow: 'DigiIn Status Gateway',
    title: 'System Status',
    description: 'Public health status and operational telemetry for all citizen and institutional services.',
    children: `
      ${PublicStatusBanner({ allOperational: statusData.allOperational, lastUpdated: statusData.lastUpdated })}

      <div style="margin-top: 2rem;">
        <h3>Operational Components</h3>
        ${HealthStatusGrid({ services: statusData.components })}
      </div>
    `
  });
}

const routes = {
  '/notifications': CitizenNotificationsView,
  '/settings/notifications': NotificationPreferencesView,
  '/organisation/notifications': OrganisationNotificationsView,
  '/organisation/developer/usage': OrganisationUsageView,
  '/organisation/developer/webhooks': WebhookDeliveriesView,
  '/organisation/integrations': IntegrationsDashboardView,
  '/admin/system': SystemHealthView,
  '/status': PublicStatusView
};

async function render() {
  const p = path().split('?')[0];
  const viewFn = routes[p] || PublicStatusView;
  const content = await viewFn();
  app.innerHTML = `${Header()}${content}${Footer()}`;
}

window.addEventListener('hashchange', () => render());
render();
