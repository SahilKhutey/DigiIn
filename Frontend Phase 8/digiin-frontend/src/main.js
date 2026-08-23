import {
  Button,
  Badge,
  Card,
  Alert,
  Status,
  Stepper,
  OrganisationSidebar,
  MetricCard,
  RequestTable,
  RequestDetailCard
} from './components.js';
import { organisationService } from './services/organisation/organisationService.js';
import { requestService } from './services/requests/requestService.js';
import { proofService } from './services/proof/proofService.js';

const app = document.querySelector('#app');
const state = {
  menu: false,
  lang: 'EN',
  org: null,
  requestsFilter: 'ALL',
  wizard: {
    step: 1,
    citizenId: 'DIN-7K4P-92M8',
    purpose: 'Admission',
    customPurpose: '',
    documents: [
      { id: 'doc-10', title: 'Class 10 Certificate', selected: true, required: true, reason: 'Confirm educational qualification' },
      { id: 'doc-12', title: 'Class 12 Certificate', selected: true, required: true, reason: 'Confirm eligibility cutoff' },
      { id: 'doc-deg', title: 'Degree Certificate', selected: false, required: false, reason: 'Higher qualification verification' },
      { id: 'doc-id', title: 'Identity Document', selected: false, required: false, reason: 'Confirm identity' },
      { id: 'doc-addr', title: 'Address Proof', selected: false, required: false, reason: 'Confirm state domicile' }
    ],
    validityHours: 24
  },
  validationResult: null
};

const path = () => location.hash.replace(/^#/, '') || '/organisation/dashboard';
const go = (p) => { location.hash = p; };

const Header = () => `
  <div class="top">
    <div class="container top-inner">
      <span>भारत सरकार • Government of India</span>
      <span>Digital India Initiative • Phase 8 Organisation Portal</span>
    </div>
  </div>
  <header class="header">
    <div class="container head">
      <a class="brand" href="#/organisation/dashboard" aria-label="DigiIn organisation home">
        <span class="mark">DI</span>
        <span>DigiIn<small>Organisation Verifier Workspace</small></span>
      </a>
      <nav class="nav" aria-label="Primary">
        <a href="#/organisation/dashboard">Dashboard</a>
        <a href="#/organisation/requests">Requests</a>
        <a href="#/organisation/requests/new">+ Create Request</a>
        <a href="#/organisation/verify-proof">Verify Proof</a>
      </nav>
      <div class="actions">
        <div class="user-pill" style="background: var(--color-primary-100); color: var(--color-primary-900);">
          <span>🏢 ABC University (ORG-84K2)</span>
        </div>
      </div>
    </div>
  </header>
`;

const Footer = () => `
  <footer class="footer">
    <div class="container footer-grid">
      <div>
        <strong>DigiIn Sovereign Gateway</strong>
        <p class="muted">Two-Sided Sovereign Verification Network.</p>
      </div>
      <div>
        <strong>Organisation Portal</strong>
        <a href="#/organisation/dashboard">Dashboard</a>
        <a href="#/organisation/requests">Requests</a>
        <a href="#/organisation/requests/new">Create Request</a>
        <a href="#/organisation/verify-proof">Verify Proof</a>
      </div>
      <div>
        <strong>Standards & Privacy</strong>
        <a href="#/security">Data Minimisation</a>
        <a href="#/privacy">DPDP Act 2023</a>
        <a href="#/terms">Terms of Verification</a>
      </div>
    </div>
    <div class="container footer-bottom">
      <small>Phase 8 • Organisation Portal & Request Management • Complete Two-Sided Trust Network</small>
    </div>
  </footer>
`;

const PageLayout = ({ title, eyebrow, description, currentRoute, children }) => `
  <main id="main" class="page container">
    ${eyebrow ? `<span class="eyebrow">${eyebrow}</span>` : ''}
    <h1>${title}</h1>
    ${description ? `<p class="lead muted">${description}</p>` : ''}
    
    <div class="portal-layout">
      ${OrganisationSidebar({ currentRoute })}
      <div class="portal-content">
        ${children}
      </div>
    </div>
  </main>
`;

function SignInView() {
  return `
    <main id="main" class="page container narrow" style="padding-top: 3rem;">
      <div class="form-card">
        <div class="text-center" style="margin-bottom: 1.5rem;">
          <div class="mark" style="margin: 0 auto 0.75rem;">DI</div>
          <span class="eyebrow">Verifier Workspace</span>
          <h2>Organisation Sign in</h2>
          <p class="muted">Access institutional verification request management.</p>
        </div>

        <form id="org-signin-form">
          <div class="field">
            <label for="org-id">Organisation ID</label>
            <input id="org-id" type="text" value="ORG-84K2-19Q7" required />
          </div>

          <div class="field">
            <label for="org-email">Email</label>
            <input id="org-email" type="email" value="verifier@abcuniversity.example" required />
          </div>

          <div class="field">
            <label for="org-password">Password</label>
            <input id="org-password" type="password" value="•••••••••••" required />
          </div>

          <button class="btn btn-primary block" style="margin-top: 1.5rem;" type="submit">Sign in →</button>
        </form>

        ${Alert({
          title: 'Authorised Access Only',
          message: 'Organisation access is restricted to verified institutions. Demo authentication mode is active.',
          tone: 'info'
        })}
      </div>
    </main>
  `;
}

async function DashboardView() {
  const org = await organisationService.getOrganisation();
  const requests = await requestService.listRequests('ALL');

  return PageLayout({
    eyebrow: 'Organisation Workspace',
    title: `Welcome, ${org.name}`,
    description: 'Manage educational credentials, issue purpose-bound requests, and inspect verification proofs.',
    currentRoute: '/organisation/dashboard',
    children: `
      <div class="actions" style="margin-bottom: 1rem;">
        <a class="btn btn-primary" href="#/organisation/requests/new">+ Create verification request</a>
        <a class="btn btn-secondary" href="#/organisation/verify-proof">Verify DigiIn proof</a>
      </div>

      <div class="stats-grid">
        ${MetricCard({ label: 'Total Requests', value: org.stats.totalRequests, subtext: 'Lifetime issued' })}
        ${MetricCard({ label: 'Verified', value: org.stats.verified, subtext: 'Completed proofs', tone: 'success' })}
        ${MetricCard({ label: 'Pending', value: org.stats.pending, subtext: 'Awaiting citizen' })}
        ${MetricCard({ label: 'Expired', value: org.stats.expired, subtext: 'Exceeded validity' })}
      </div>

      <div style="display: flex; justify-content: space-between; align-items: center; margin: 2rem 0 1rem;">
        <h3 style="margin: 0;">Recent Verification Requests</h3>
        <a href="#/organisation/requests" class="link-button" style="font-size: 0.85rem; font-weight: 700;">View all requests →</a>
      </div>

      ${RequestTable({ requests: requests.slice(0, 5) })}
    `
  });
}

async function RequestsListView() {
  const requests = await requestService.listRequests(state.requestsFilter);

  return PageLayout({
    eyebrow: 'Request Management',
    title: 'Verification Requests',
    description: 'Track, inspect, and manage issued document verification requests.',
    currentRoute: '/organisation/requests',
    children: `
      <div class="tab-filter-row">
        <button class="tab-filter-btn ${state.requestsFilter === 'ALL' ? 'selected' : ''}" data-filter="ALL" type="button">All Requests</button>
        <button class="tab-filter-btn ${state.requestsFilter === 'PENDING' ? 'selected' : ''}" data-filter="PENDING" type="button">Pending</button>
        <button class="tab-filter-btn ${state.requestsFilter === 'VERIFIED' ? 'selected' : ''}" data-filter="VERIFIED" type="button">Verified</button>
        <button class="tab-filter-btn ${state.requestsFilter === 'EXPIRED' ? 'selected' : ''}" data-filter="EXPIRED" type="button">Expired</button>
        <button class="tab-filter-btn ${state.requestsFilter === 'CANCELLED' ? 'selected' : ''}" data-filter="CANCELLED" type="button">Cancelled</button>
      </div>

      ${RequestTable({ requests })}
    `
  });
}

async function RequestDetailView(requestId) {
  const req = await requestService.getRequest(requestId);
  if (!req) {
    return PageLayout({
      title: 'Request Not Found',
      currentRoute: '/organisation/requests',
      children: `<div class="card text-center"><p class="muted">Verification request ${requestId} was not found.</p><a class="btn btn-primary" href="#/organisation/requests">Back to Requests</a></div>`
    });
  }

  return PageLayout({
    eyebrow: 'Request Detail',
    title: `Request ${req.id}`,
    description: `Issued for ${req.purpose} to citizen ${req.citizenId}.`,
    currentRoute: '/organisation/requests',
    children: `
      ${RequestDetailCard({ req })}
    `
  });
}

function NewRequestWizardView() {
  const wiz = state.wizard;

  return PageLayout({
    eyebrow: `Step ${wiz.step} of 5 • New Request`,
    title: 'Create verification request',
    description: 'Specify the citizen target, purpose, and required credentials without collecting unnecessary data.',
    currentRoute: '/organisation/requests/new',
    children: `
      ${Stepper({
        steps: ['Citizen ID', 'Purpose', 'Documents', 'Validity', 'Review'],
        current: wiz.step - 1
      })}

      <div class="form-card" style="margin-top: 1.5rem;">
        ${wiz.step === 1 ? `
          <h3>Step 1 — Citizen Identification</h3>
          <p class="muted">The organisation must specify the citizen target without asking for unnecessary personal data.</p>
          
          <div class="field">
            <label for="wiz-citizen-id">Citizen DigiIn ID</label>
            <input id="wiz-citizen-id" type="text" value="${wiz.citizenId}" placeholder="e.g. DIN-7K4P-92M8" required />
          </div>

          ${Alert({
            title: 'Security & Privacy Rule',
            message: 'A DigiIn ID identifies the citizen account. It does not provide access to the citizen’s documents without explicit consent.',
            tone: 'info'
          })}

          <div class="actions" style="margin-top: 1.5rem; justify-content: flex-end;">
            <button id="wiz-next-1" class="btn btn-primary" type="button">Next: Specify Purpose →</button>
          </div>
        ` : ''}

        ${wiz.step === 2 ? `
          <h3>Step 2 — Verification Purpose</h3>
          <p class="muted">Purpose must be explicitly declared and bound to the verification transaction.</p>
          
          <div class="field">
            <label for="wiz-purpose-select">Select Purpose</label>
            <select id="wiz-purpose-select">
              <option value="Admission" ${wiz.purpose === 'Admission' ? 'selected' : ''}>Admission verification</option>
              <option value="Employment" ${wiz.purpose === 'Employment' ? 'selected' : ''}>Employment verification</option>
              <option value="Scholarship" ${wiz.purpose === 'Scholarship' ? 'selected' : ''}>Scholarship eligibility</option>
              <option value="Government service" ${wiz.purpose === 'Government service' ? 'selected' : ''}>Government service onboarding</option>
              <option value="Financial service" ${wiz.purpose === 'Financial service' ? 'selected' : ''}>Financial service KYC</option>
              <option value="Other" ${wiz.purpose === 'Other' ? 'selected' : ''}>Other purpose</option>
            </select>
          </div>

          ${wiz.purpose === 'Other' ? `
            <div class="field">
              <label for="wiz-custom-purpose">Describe Purpose</label>
              <input id="wiz-custom-purpose" type="text" value="${wiz.customPurpose}" placeholder="Specific purpose description" required />
            </div>
          ` : ''}

          <div class="actions" style="margin-top: 1.5rem; justify-content: space-between;">
            <button id="wiz-back-2" class="btn btn-secondary" type="button">← Back</button>
            <button id="wiz-next-2" class="btn btn-primary" type="button">Next: Select Documents →</button>
          </div>
        ` : ''}

        ${wiz.step === 3 ? `
          <h3>Step 3 — Documents Requested</h3>
          <p class="muted">The organisation should only request credentials necessary for the declared purpose.</p>
          
          <div style="display: grid; gap: 0.75rem; margin: 1rem 0;">
            ${wiz.documents.map((d, idx) => `
              <label style="display: flex; align-items: start; gap: 0.75rem; padding: 0.75rem; border: 1px solid var(--color-border-subtle); border-radius: var(--radius-md); background: ${d.selected ? 'var(--color-primary-100)' : '#fff'}; cursor: pointer;">
                <input type="checkbox" class="wiz-doc-check" data-idx="${idx}" ${d.selected ? 'checked' : ''} style="margin-top: 0.25rem;" />
                <div>
                  <strong>${d.title}</strong>
                  <div style="font-size: 0.8rem; color: var(--color-text-muted);">${d.reason}</div>
                </div>
              </label>
            `).join('')}
          </div>

          <div class="actions" style="margin-top: 1.5rem; justify-content: space-between;">
            <button id="wiz-back-3" class="btn btn-secondary" type="button">← Back</button>
            <button id="wiz-next-3" class="btn btn-primary" type="button">Next: Select Validity →</button>
          </div>
        ` : ''}

        ${wiz.step === 4 ? `
          <h3>Step 4 — Request Validity</h3>
          <p class="muted">This request automatically expires after the selected period if consent is not provided.</p>
          
          <div style="display: grid; gap: 0.5rem; margin: 1rem 0;">
            ${[
              { hours: 1, label: '1 hour' },
              { hours: 6, label: '6 hours' },
              { hours: 24, label: '24 hours (Standard)' },
              { hours: 72, label: '3 days' },
              { hours: 168, label: '7 days' }
            ].map(v => `
              <label style="display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem; border: 1px solid var(--color-border-subtle); border-radius: var(--radius-md); background: ${wiz.validityHours === v.hours ? 'var(--color-primary-100)' : '#fff'}; cursor: pointer;">
                <input type="radio" name="wiz-validity" class="wiz-validity-radio" value="${v.hours}" ${wiz.validityHours === v.hours ? 'checked' : ''} />
                <strong>${v.label}</strong>
              </label>
            `).join('')}
          </div>

          <div class="actions" style="margin-top: 1.5rem; justify-content: space-between;">
            <button id="wiz-back-4" class="btn btn-secondary" type="button">← Back</button>
            <button id="wiz-next-4" class="btn btn-primary" type="button">Next: Review Request →</button>
          </div>
        ` : ''}

        ${wiz.step === 5 ? `
          <h3>Step 5 — Review Verification Request</h3>
          <p class="muted">Confirm request details before issuing to the citizen.</p>
          
          <div class="request-summary">
            <div><small>Citizen Account</small><strong style="font-family: var(--font-mono);">${wiz.citizenId}</strong></div>
            <div><small>Purpose</small><strong>${wiz.purpose === 'Other' ? wiz.customPurpose : wiz.purpose}</strong></div>
            <div><small>Validity</small><strong>${wiz.validityHours} hours</strong></div>
          </div>

          <h4>Requested Credentials:</h4>
          <ul class="list" style="margin: 0.5rem 0 1.5rem;">
            ${wiz.documents.filter(d => d.selected).map(d => `
              <li>${d.title} <small class="muted">(${d.reason})</small></li>
            `).join('')}
          </ul>

          ${Alert({
            title: 'Informed Citizen Consent Required',
            message: 'The citizen must explicitly consent in their DigiIn wallet before any documents are retrieved or verified.',
            tone: 'info'
          })}

          <div class="actions" style="margin-top: 1.5rem; justify-content: space-between;">
            <button id="wiz-back-5" class="btn btn-secondary" type="button">← Back</button>
            <button id="wiz-submit-btn" class="btn btn-primary" type="button">Create verification request →</button>
          </div>
        ` : ''}
      </div>
    `
  });
}

function OrganisationVerifyProofView() {
  return PageLayout({
    eyebrow: 'Verifier Portal',
    title: 'Verify DigiIn proof',
    description: 'Enter a verification ID or scan a QR code to validate a citizen’s verification proof.',
    currentRoute: '/organisation/verify-proof',
    children: `
      <div class="form-card">
        <div class="field">
          <label for="proof-search-input">Verification Proof ID</label>
          <input id="proof-search-input" type="text" placeholder="e.g. DIN-PRF-51Q8-X2" value="DIN-PRF-51Q8-X2" />
        </div>

        <div style="margin: 1rem 0;">
          <small class="muted" style="display: block; margin-bottom: 0.35rem; font-weight: 700;">Test Quick Presets:</small>
          <div class="tab-filter-row">
            <button class="tab-filter-btn selected" data-test="DIN-PRF-51Q8-X2" type="button">✓ Valid (ABC Univ)</button>
            <button class="tab-filter-btn" data-test="DIN-PRF-73K1-P9" type="button">! Expired</button>
            <button class="tab-filter-btn" data-test="DIN-PRF-REV-88" type="button">✕ Revoked</button>
            <button class="tab-filter-btn" data-test="INVALID-PROOF" type="button">✕ Invalid ID</button>
          </div>
        </div>

        <button id="org-verify-proof-btn" class="btn btn-primary block" style="margin-top: 1.5rem;" type="button">Verify proof →</button>
      </div>

      <div id="proof-result-mount" style="margin-top: 1.5rem;"></div>
    `
  });
}

async function OrganisationHistoryView() {
  const auditEvents = requestService.getAuditEvents();

  return PageLayout({
    eyebrow: 'Audit & Compliance',
    title: 'Verification History',
    description: 'Immutable timeline of verification transactions and proof lookups.',
    currentRoute: '/organisation/history',
    children: `
      <div class="card">
        <h3 style="margin-top: 0;">Institutional Audit Log</h3>
        <ul style="list-style: none; padding: 0; margin: 1rem 0; display: grid; gap: 0.75rem;">
          ${auditEvents.map(e => `
            <li style="border-bottom: 1px solid var(--color-border-subtle); padding-bottom: 0.75rem;">
              <div style="display: flex; justify-content: space-between; align-items: start;">
                <strong>${e.event}</strong>
                <small style="font-family: var(--font-mono); color: var(--color-primary-700);">${e.requestId}</small>
              </div>
              <small class="muted">${e.timestamp}</small>
            </li>
          `).join('')}
        </ul>
      </div>
    `
  });
}

async function OrganisationProfileView() {
  const org = await organisationService.getOrganisation();

  return PageLayout({
    eyebrow: 'Institutional Identity',
    title: 'Organisation Profile',
    description: 'Registered verified organisation information and access settings.',
    currentRoute: '/organisation/profile',
    children: `
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--color-border-subtle); padding-bottom: 1rem;">
          <div>
            <h2 style="margin: 0;">${org.name}</h2>
            <span class="muted">${org.type}</span>
          </div>
          ${Badge({ label: 'Verified Organisation', tone: 'success', icon: '✓' })}
        </div>

        <div class="request-summary" style="margin: 1.5rem 0;">
          <div><small>Organisation ID</small><strong style="font-family: var(--font-mono);">${org.id}</strong></div>
          <div><small>Account Status</small><strong style="color: var(--color-success-700);">${org.status}</strong></div>
          <div><small>Authorised Users</small><strong>${org.users} Active Users</strong></div>
          <div><small>Registered Email</small><strong>${org.email}</strong></div>
          <div><small>Member Since</small><strong>${org.createdAt}</strong></div>
        </div>

        ${Alert({
          title: 'Public Trust Guarantee',
          message: 'This organisation’s public key and identity are registered with the Digital India sovereign registry.',
          tone: 'info'
        })}
      </div>
    `
  });
}

const routes = {
  '/organisation/sign-in': SignInView,
  '/organisation/dashboard': DashboardView,
  '/organisation/requests': RequestsListView,
  '/organisation/requests/new': NewRequestWizardView,
  '/organisation/verify-proof': OrganisationVerifyProofView,
  '/organisation/history': OrganisationHistoryView,
  '/organisation/profile': OrganisationProfileView
};

async function render() {
  const p = path().split('?')[0];

  if (p === '/organisation/sign-in') {
    app.innerHTML = `${Header()}${SignInView()}${Footer()}`;
  } else if (p.startsWith('/organisation/requests/') && p !== '/organisation/requests/new') {
    const reqId = p.split('/')[3];
    const html = await RequestDetailView(reqId);
    app.innerHTML = `${Header()}${html}${Footer()}`;
  } else if (routes[p]) {
    const viewFn = routes[p];
    const html = await viewFn();
    app.innerHTML = `${Header()}${html}${Footer()}`;
  } else {
    const html = await DashboardView();
    app.innerHTML = `${Header()}${html}${Footer()}`;
  }

  bindEvents();
}

function bindEvents() {
  // Sign in form
  const signinForm = document.querySelector('#org-signin-form');
  if (signinForm) {
    signinForm.addEventListener('submit', (e) => {
      e.preventDefault();
      go('/organisation/dashboard');
    });
  }

  // Requests filter tabs
  document.querySelectorAll('.tab-filter-btn[data-filter]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      state.requestsFilter = e.target.dataset.filter;
      render();
    });
  });

  // Wizard Step 1 -> 2
  const next1 = document.querySelector('#wiz-next-1');
  if (next1) {
    next1.addEventListener('click', () => {
      const input = document.querySelector('#wiz-citizen-id');
      if (input) state.wizard.citizenId = input.value;
      state.wizard.step = 2;
      render();
    });
  }

  // Wizard Step 2
  const next2 = document.querySelector('#wiz-next-2');
  if (next2) {
    next2.addEventListener('click', () => {
      const sel = document.querySelector('#wiz-purpose-select');
      if (sel) state.wizard.purpose = sel.value;
      const custom = document.querySelector('#wiz-custom-purpose');
      if (custom) state.wizard.customPurpose = custom.value;
      state.wizard.step = 3;
      render();
    });
  }
  const back2 = document.querySelector('#wiz-back-2');
  if (back2) back2.addEventListener('click', () => { state.wizard.step = 1; render(); });

  const purpSelect = document.querySelector('#wiz-purpose-select');
  if (purpSelect) {
    purpSelect.addEventListener('change', (e) => {
      state.wizard.purpose = e.target.value;
      render();
    });
  }

  // Wizard Step 3
  const next3 = document.querySelector('#wiz-next-3');
  if (next3) {
    next3.addEventListener('click', () => {
      state.wizard.step = 4;
      render();
    });
  }
  const back3 = document.querySelector('#wiz-back-3');
  if (back3) back3.addEventListener('click', () => { state.wizard.step = 2; render(); });

  document.querySelectorAll('.wiz-doc-check').forEach(chk => {
    chk.addEventListener('change', (e) => {
      const idx = parseInt(e.target.dataset.idx, 10);
      state.wizard.documents[idx].selected = e.target.checked;
    });
  });

  // Wizard Step 4
  const next4 = document.querySelector('#wiz-next-4');
  if (next4) {
    next4.addEventListener('click', () => {
      state.wizard.step = 5;
      render();
    });
  }
  const back4 = document.querySelector('#wiz-back-4');
  if (back4) back4.addEventListener('click', () => { state.wizard.step = 3; render(); });

  document.querySelectorAll('.wiz-validity-radio').forEach(r => {
    r.addEventListener('change', (e) => {
      state.wizard.validityHours = parseInt(e.target.value, 10);
      render();
    });
  });

  // Wizard Submit (Step 5)
  const submitReqBtn = document.querySelector('#wiz-submit-btn');
  if (submitReqBtn) {
    submitReqBtn.addEventListener('click', async () => {
      const selectedDocs = state.wizard.documents.filter(d => d.selected);
      const newReq = await requestService.createRequest({
        citizenId: state.wizard.citizenId,
        purpose: state.wizard.purpose === 'Other' ? state.wizard.customPurpose : state.wizard.purpose,
        documents: selectedDocs,
        validityHours: state.wizard.validityHours
      });
      alert(`✓ Verification request ${newReq.id} created successfully! Waiting for citizen consent.`);
      state.wizard.step = 1;
      go(`/organisation/requests/${newReq.id}`);
    });
  }
  const back5 = document.querySelector('#wiz-back-5');
  if (back5) back5.addEventListener('click', () => { state.wizard.step = 4; render(); });

  // Cancel request in detail view
  const cancelReqBtn = document.querySelector('#cancel-req-btn');
  if (cancelReqBtn) {
    cancelReqBtn.addEventListener('click', async () => {
      const p = path();
      const reqId = p.split('/')[3];
      await requestService.cancelRequest(reqId);
      alert(`✓ Request ${reqId} has been cancelled.`);
      render();
    });
  }

  // Organisation proof verifier test pills
  document.querySelectorAll('.tab-filter-btn[data-test]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('.tab-filter-btn[data-test]').forEach(b => b.classList.remove('selected'));
      e.target.classList.add('selected');
      const input = document.querySelector('#proof-search-input');
      if (input) input.value = e.target.dataset.test;
    });
  });

  // Verify Proof Button in portal
  const verifyProofBtn = document.querySelector('#org-verify-proof-btn');
  if (verifyProofBtn) {
    verifyProofBtn.addEventListener('click', async () => {
      const input = document.querySelector('#proof-search-input');
      const id = input?.value || 'DIN-PRF-51Q8-X2';
      const res = await proofService.validateProof(id);
      const mount = document.querySelector('#proof-result-mount');
      if (mount) {
        if (res.status === 'VALID') {
          mount.innerHTML = `
            <div class="card" style="border: 2px solid var(--color-success-700);">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span class="badge badge-success">✓ Verification Confirmed</span>
                <strong style="font-family: var(--font-mono);">${res.proof.proofId}</strong>
              </div>
              <h3 style="margin: 0.5rem 0 0.25rem;">Authentic Verification Proof</h3>
              <p class="muted">Issued for ${res.proof.organisation} • Purpose: ${res.proof.purpose}</p>
              <div class="verification-list" style="margin: 1rem 0;">
                ${res.proof.verifiedDocuments.map(d => `<div><span class="status-pill status-success">✓ Verified</span><span>${d}</span></div>`).join('')}
              </div>
              <small class="muted">Valid until ${res.proof.expiresAt}</small>
            </div>
          `;
        } else {
          mount.innerHTML = `
            <div class="card" style="border: 2px solid var(--color-error-700);">
              <span class="badge badge-danger">✕ Verification Could Not Be Confirmed</span>
              <h3 style="margin: 0.5rem 0 0.25rem;">Proof Not Recognized</h3>
              <p class="muted">${res.message}</p>
            </div>
          `;
        }
      }
    });
  }
}

window.addEventListener('hashchange', () => render());
render();
