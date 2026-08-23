import {
  Button,
  Badge,
  Card,
  Alert,
  Field,
  Status,
  DocumentCard,
  OrganisationIdentity,
  RequestedDocumentCard,
  ExternalServiceCard,
  Stepper
} from './components.js';
import { digiLockerService } from './services/digilocker/digilockerService.js';

const app = document.querySelector('#app');
const state = {
  menu: false,
  lang: 'EN',
  user: { name: 'Rahul Sharma', digiinId: 'DIN-84K2-19Q7', mobile: '9876543210' },
  consent: false,
  zkpMode: true,
  consentDuration: 24,
  consentDeclined: false,
  verification: 'idle',
  retrievalScenario: 'success', // 'success' | 'partial' | 'failure'
  request: {
    id: 'VR-82A91',
    organisation: 'ABC University',
    category: 'Central Higher Education Institution',
    purpose: 'Admission eligibility verification (AY 2026-27)',
    documents: [
      { id: 'doc-10', title: 'Class 10 Certificate', issuer: 'CBSE', purpose: 'Date of birth and secondary passing', claims: ['DOB', 'Roll No'] },
      { id: 'doc-12', title: 'Class 12 Certificate', issuer: 'CBSE', purpose: 'Higher secondary aggregate >= 60.0%', claims: ['Year', 'Percentage >= 60%'] }
    ],
    expiresInHours: 24
  },
  connectionState: 'NOT_CONNECTED',
  retrieved: [],
  consentRecord: null
};

const path = () => location.hash.replace(/^#/, '') || '/';
const go = (p) => { location.hash = p; };
const currentRequest = () => state.request;

const Header = () => `
  <div class="top">
    <div class="container top-inner">
      <span>भारत सरकार • Government of India</span>
      <span>Digital India Initiative • UX4G 3.0</span>
    </div>
  </div>
  <header class="header">
    <div class="container head">
      <a class="brand" href="#/" aria-label="DigiIn home">
        <span class="mark">DI</span>
        <span>DigiIn<small>Digital document verification</small></span>
      </a>
      <nav class="nav" aria-label="Primary">
        <a href="#/">Home</a>
        <a href="#/how">How it works</a>
        <a href="#/security">Security</a>
        <a href="#/help">Help</a>
      </nav>
      <div class="actions">
        <button class="btn btn-secondary btn-small" id="lang" type="button" aria-label="Change language">
          ${state.lang === 'EN' ? 'हिन्दी (HI)' : 'English (EN)'}
        </button>
        ${state.user ? `
          <div class="user-pill">
            <span class="user-name">👤 ${state.user.name}</span>
            <a class="btn btn-primary btn-small" href="#/dashboard">Dashboard</a>
          </div>
        ` : `
          <a class="btn btn-primary btn-small" href="#/sign-in">Sign in</a>
        `}
        <button class="menu" id="menu" type="button" aria-label="Open menu" aria-expanded="${state.menu}">☰</button>
      </div>
    </div>
    ${state.menu ? `
      <nav class="mobile-nav" aria-label="Mobile navigation">
        <a href="#/">Home</a>
        <a href="#/how">How it works</a>
        <a href="#/security">Security</a>
        <a href="#/help">Help</a>
        ${state.user ? '<a href="#/dashboard">Dashboard</a>' : '<a href="#/sign-in">Sign in</a>'}
      </nav>
    ` : ''}
  </header>
`;

const Footer = () => `
  <footer class="footer">
    <div class="container footer-grid">
      <div>
        <strong>DigiIn</strong>
        <p class="muted">Verify once. Share securely.</p>
      </div>
      <div>
        <strong>Service</strong>
        <a href="#/how">How it works</a>
        <a href="#/security">Security</a>
        <a href="#/help">Help & FAQ</a>
      </div>
      <div>
        <strong>Trust & Standards</strong>
        <a href="#/accessibility">Accessibility</a>
        <a href="#/privacy">Privacy Notice</a>
        <a href="#/terms">Terms of Service</a>
      </div>
    </div>
    <div class="container footer-bottom">
      <small>Phase 5 Prototype • Zero raw document storage guarantee • DPDP Act 2023 compliant</small>
    </div>
  </footer>
`;

const Page = ({ eyebrow, title, description, children, narrow = false }) => `
  <main id="main" class="page">
    <div class="container ${narrow ? 'narrow' : ''}">
      ${eyebrow ? `<span class="eyebrow">${eyebrow}</span>` : ''}
      <h1>${title}</h1>
      ${description ? `<p class="lead muted">${description}</p>` : ''}
      ${children}
    </div>
  </main>
`;

function Home() {
  return `
    <main id="main">
      <section class="hero">
        <div class="container hero-grid">
          <div>
            <span class="eyebrow">Digital Public Infrastructure</span>
            <h1>Verify once.<br><span>Share securely.</span></h1>
            <p>DigiIn enables sovereign document verification without transferring unredacted documents. Consent-led, privacy-preserving, and compliant with UX4G 3.0.</p>
            <div class="actions hero-actions">
              ${Button({ label: 'Start verification', href: '#/verify/request', icon: '→' })}
              ${Button({ label: 'How DigiIn works', href: '#/how', variant: 'secondary' })}
            </div>
            <div class="trust-row">
              <span>✓ Consent-led</span>
              <span>✓ Zero Raw Storage</span>
              <span>✓ Ed25519 Signed</span>
            </div>
          </div>
          ${Card({
            className: 'hero-card',
            children: `
              <div class="shield">🛡️</div>
              <h2>Consent-led by design</h2>
              <p class="muted">You stay in control of what is shared, with whom, and for what purpose.</p>
              <ul class="list">
                <li>Requesting organisation is verified.</li>
                <li>Only requested documents are queried.</li>
                <li>Cryptographic proof generated without raw storage.</li>
              </ul>
            `
          })}
        </div>
      </section>
      <section class="section section-alt">
        <div class="container">
          <span class="eyebrow">The journey</span>
          <h2>How Phase 5 Verification Works</h2>
          ${Stepper({ steps: ['Request Review', 'DigiLocker Auth', 'Consent', 'Retrieve', 'Proof'], current: 0 })}
        </div>
      </section>
    </main>
  `;
}

function Dashboard() {
  return Page({
    eyebrow: 'Citizen account',
    title: `Welcome, ${state.user?.name || 'Citizen'}`,
    description: 'Manage your verified documents, active institutional requests, and consent logs.',
    children: `
      <div class="actions">
        <a class="btn btn-primary" href="#/verify/request">New verification request <span aria-hidden="true">→</span></a>
      </div>
      <div class="stats">
        <div class="stat-card"><strong>12</strong><span>Documents</span></div>
        <div class="stat-card"><strong>9</strong><span>Verified</span></div>
        <div class="stat-card"><strong>2</strong><span>Pending</span></div>
      </div>
      <div class="dashboard-grid">
        ${Card({
          children: `
            <div class="card-heading">
              <div><span class="eyebrow">Your sovereign identity</span><h2>DigiIn ID</h2></div>
              ${Badge({ label: 'Active', tone: 'success', icon: '✓' })}
            </div>
            <div class="id-card">
              <small>DigiIn ID (Account Identifier)</small>
              <strong>${state.user?.digiinId || 'DIN-84K2-19Q7'}</strong>
              <p class="muted">Share this ID with authorised services to initiate consent-bound verification.</p>
              <button class="btn btn-secondary btn-small" id="copy-id" type="button">Copy ID</button>
            </div>
          `
        })}
        ${Card({
          children: `
            <div class="card-heading">
              <div><span class="eyebrow">Activity</span><h2>Recent verification requests</h2></div>
            </div>
            <ul class="activity">
              <li>
                <span class="activity-dot info"></span>
                <div>
                  <strong>ABC University Request</strong>
                  <small>Pending review • VR-82A91</small>
                </div>
                <a class="btn btn-secondary btn-small" href="#/verify/request">Review</a>
              </li>
            </ul>
          `
        })}
      </div>
      <section class="documents-section">
        <div class="section-heading">
          <div><span class="eyebrow">Document vault</span><h2>Your documents</h2></div>
        </div>
        <div class="document-grid">
          ${DocumentCard({ title: 'Class 12 Certificate', issuer: 'CBSE', detail: 'Issued 15 May 2025 • Level 4 Verified', status: 'verified' })}
          ${DocumentCard({ title: 'Class 10 Certificate', issuer: 'CBSE', detail: 'Issued 20 May 2023 • Level 4 Verified', status: 'verified' })}
          ${DocumentCard({ title: 'Aadhaar Identity Card', issuer: 'UIDAI', detail: 'Demographics verified via eKYC', status: 'verified' })}
        </div>
      </section>
    `
  });
}

function VerifyRequest() {
  const r = currentRequest();
  return Page({
    eyebrow: 'Step 1 of 5 • Request Context',
    title: 'Verification Request',
    description: 'Understand who is requesting your credentials and why before connecting any external document source.',
    narrow: true,
    children: `
      ${Stepper({ steps: ['Request', 'Review', 'Connect', 'Consent', 'Retrieve', 'Verify'], current: 0 })}
      <div class="form-card request-card">
        ${OrganisationIdentity({ name: r.organisation, category: r.category, requestId: r.id })}
        <div class="request-summary">
          <div><small>Stated Purpose</small><strong>${r.purpose}</strong></div>
          <div><small>Request ID</small><strong>${r.id}</strong></div>
          <div><small>Consent Validity</small><strong>${r.expiresInHours} hours</strong></div>
        </div>
        <h2>Documents requested</h2>
        <div class="requested-list">
          ${r.documents.map(d => RequestedDocumentCard({ title: d.title, issuer: d.issuer, purpose: d.purpose, claims: d.claims })).join('')}
        </div>
        ${Alert({
          title: 'You stay in control.',
          message: 'DigiIn will not query unrelated documents. You will review exact permissions before anything is retrieved.',
          tone: 'info'
        })}
        <div class="actions request-actions">
          <a class="btn btn-primary" href="#/verify/review">Review and continue <span aria-hidden="true">→</span></a>
          <a class="btn btn-secondary" href="#/dashboard">Cancel</a>
        </div>
      </div>
    `
  });
}

function VerifyReview() {
  const r = currentRequest();
  return Page({
    eyebrow: 'Step 2 of 5 • Review Before Connection',
    title: 'Review what will be shared',
    description: 'This verification request is strictly limited to the credentials and claims shown below.',
    narrow: true,
    children: `
      ${Stepper({ steps: ['Request', 'Review', 'Connect', 'Consent', 'Retrieve', 'Verify'], current: 1 })}
      <div class="form-card">
        ${OrganisationIdentity({ name: r.organisation, category: r.category, requestId: r.id })}
        <div class="review-block">
          <span class="eyebrow">Purpose of verification</span>
          <h2>${r.purpose}</h2>
          <p class="muted">ABC University will use the verification proof only for undergraduate admission eligibility verification.</p>
        </div>
        <h2>Requested documents (2)</h2>
        <div class="requested-list">
          ${r.documents.map(d => RequestedDocumentCard({ title: d.title, issuer: d.issuer, purpose: d.purpose, claims: d.claims })).join('')}
        </div>
        ${Alert({
          title: 'What happens next?',
          message: 'You will connect to DigiLocker, authenticate your account, and then provide explicit purpose-bound consent.',
          tone: 'info'
        })}
        <a class="btn btn-primary block" href="#/verify/digilocker">Continue to DigiLocker <span aria-hidden="true">→</span></a>
        <a class="text-action" href="#/verify/request">← Back to request overview</a>
      </div>
    `
  });
}

function DigiLockerConnect() {
  return Page({
    eyebrow: 'Step 3 of 5 • External Provider',
    title: 'Connect DigiLocker',
    description: 'DigiIn needs access to your DigiLocker documents to verify this admission request.',
    narrow: true,
    children: `
      ${Stepper({ steps: ['Request', 'Review', 'Connect', 'Consent', 'Retrieve', 'Verify'], current: 2 })}
      <div class="form-card external-card">
        <div class="external-service-logo">DL</div>
        <h2>Connect to DigiLocker</h2>
        <p class="muted">You will authenticate securely with DigiLocker. DigiIn does not ask for or store your DigiLocker PIN or password.</p>
        <div class="security-points">
          <div>✓ Authentication occurs directly with DigiLocker</div>
          <div>✓ Only this admission request is in scope</div>
          <div>✓ Nothing is shared without your explicit consent</div>
        </div>
        <div id="connection-status" aria-live="polite"></div>
        <button id="connect-digilocker" class="btn btn-primary block" type="button">
          Authenticate with DigiLocker <span aria-hidden="true">→</span>
        </button>
        <a class="text-action" href="#/verify/review">← Back to review</a>
      </div>
    `
  });
}

function Consent() {
  const r = currentRequest();
  return Page({
    eyebrow: 'Step 4 of 5 • Informed Consent',
    title: 'Review and give consent',
    description: 'Grant permission only if the request matches what you intend to verify.',
    narrow: true,
    children: `
      ${Stepper({ steps: ['Request', 'Review', 'Connect', 'Consent', 'Retrieve', 'Verify'], current: 3 })}
      <div class="form-card consent-card">
        ${OrganisationIdentity({ name: r.organisation, category: r.category, requestId: r.id })}
        
        <div class="consent-section">
          <span class="eyebrow">Requested documents</span>
          <div class="requested-list">
            ${r.documents.map(d => RequestedDocumentCard({ title: d.title, issuer: d.issuer, purpose: d.purpose, claims: d.claims })).join('')}
          </div>
        </div>

        <div class="consent-section">
          <span class="eyebrow">Zero-Knowledge Assertion</span>
          <label class="check-field" style="margin-top: 8px;">
            <input id="zkp-toggle" type="checkbox" ${state.zkpMode ? 'checked' : ''}>
            <span><strong>Enable Zero-Knowledge Predicate Mode (Recommended)</strong><br><small class="muted">Confirms percentage >= 60.0% without transferring raw scores or marksheet copies.</small></span>
          </label>
        </div>

        <div class="consent-grid">
          <div class="consent-box positive">
            <strong>What will happen:</strong>
            <p>Your approved documents will be checked against CBSE registries to generate a signed mathematical proof.</p>
          </div>
          <div class="consent-box negative">
            <strong>What will not happen:</strong>
            <p>Unrelated documents in your DigiLocker account will not be retrieved, stored, or exposed.</p>
          </div>
        </div>

        <div class="consent-expiry">
          <strong>Consent validity:</strong>
          <span>This verification request expires after ${r.expiresInHours} hours.</span>
        </div>

        <label class="check-field consent-check">
          <input id="consent" type="checkbox" ${state.consent ? 'checked' : ''}>
          <span>I understand and give explicit, purpose-limited consent to retrieve and verify these documents under DPDP Act 2023 protections.</span>
        </label>

        <div class="actions" style="margin-top: 16px;">
          <button id="give-consent" class="btn btn-primary block" type="button" ${state.consent ? '' : 'disabled'}>
            Give consent and retrieve documents <span aria-hidden="true">→</span>
          </button>
          <button id="decline-consent" class="btn btn-secondary block" type="button">
            Decline request
          </button>
        </div>
      </div>
    `
  });
}

function ConsentDeclined() {
  return Page({
    eyebrow: 'Consent declined',
    title: 'You declined this verification request',
    description: 'No documents were retrieved, and no personal data was shared with ABC University.',
    narrow: true,
    children: `
      <div class="form-card text-center">
        <div class="shield" style="background: #FEE2E2; color: #991B1B; margin: 0 auto 16px;">✕</div>
        <h2>Request Safely Terminated</h2>
        <p class="muted">Your decision has been respected. Under DPDP Act 2023, your documents remain private in your DigiLocker vault.</p>
        <div class="actions centered" style="margin-top: 24px;">
          <a class="btn btn-primary" href="#/dashboard">Return to dashboard</a>
          <a class="btn btn-secondary" href="#/verify/request">Review again</a>
        </div>
      </div>
    `
  });
}

function Retrieving() {
  return Page({
    eyebrow: 'Step 5 of 5 • Document Retrieval',
    title: 'Retrieving your documents',
    description: 'Connecting to official government registries to fetch certified digital credential claims.',
    narrow: true,
    children: `
      ${Stepper({ steps: ['Request', 'Review', 'Connect', 'Consent', 'Retrieve', 'Verify'], current: 4 })}
      <div class="form-card retrieval-card text-center">
        <div class="progress-ring" aria-hidden="true">⬇️</div>
        <div id="retrieval-status" aria-live="polite">
          <h2>Connecting securely…</h2>
          <p class="muted">Establishing TLS session with DigiLocker registry gateway.</p>
        </div>
        <ol class="process-list" style="text-align: left; margin-top: 24px;">
          <li class="active" id="step-1"><span>1</span><div><strong>Consent authorized</strong><small>Digital consent token registered.</small></div></li>
          <li id="step-2"><span>2</span><div><strong>Query CBSE source registry</strong><small>Fetching Class 10 & Class 12 certificates.</small></div></li>
          <li id="step-3"><span>3</span><div><strong>Validate digital signatures</strong><small>Confirming issuer public keys.</small></div></li>
        </ol>
      </div>
    `
  });
}

function DocumentsReady() {
  const isPartial = state.retrievalScenario === 'partial' || state.retrieved.length < 2;
  return Page({
    eyebrow: 'Documents Ready',
    title: isPartial ? '1 of 2 documents retrieved' : 'Documents retrieved successfully',
    description: `${state.retrieved.length} requested credential(s) are ready for verification.`,
    narrow: true,
    children: `
      ${Stepper({ steps: ['Request', 'Review', 'Connect', 'Consent', 'Retrieve', 'Verify'], current: 5 })}
      <div class="form-card">
        <div class="ready-summary">
          <span class="ready-icon">✓</span>
          <div>
            <h2>${isPartial ? 'Partial credentials available' : 'Ready for verification'}</h2>
            <p class="muted">Only documents approved under your consent scope are available to the verification engine.</p>
          </div>
        </div>

        <div class="document-grid single">
          ${state.retrieved.map((d) => DocumentCard({
            title: d.title,
            issuer: d.issuer,
            detail: 'Retrieved from DigiLocker • Level 4 Verified Credential',
            status: 'verified'
          })).join('')}
          ${isPartial ? `
            <div class="alert alert-warning" style="margin-top: 8px;">
              <strong>Class 10 Certificate unavailable</strong>
              <p>The secondary registry was unreachable during this retrieval attempt.</p>
            </div>
          ` : ''}
        </div>

        ${Alert({
          title: 'Zero raw document retention',
          message: 'DigiIn does not store unredacted files. The verification engine will issue a signed Ed25519 assertion.',
          tone: 'info'
        })}

        <div class="actions" style="margin-top: 16px;">
          <button id="start-verification" class="btn btn-primary block" type="button">
            Generate signed proof & complete →
          </button>
          <a class="btn btn-secondary block" href="#/verify/audit">View consent audit trail</a>
        </div>
      </div>
    `
  });
}

function Result() {
  return Page({
    eyebrow: 'Verification Complete',
    title: 'Proof Token Issued',
    description: '2 of 2 requested documents were successfully verified at the source registry.',
    narrow: true,
    children: `
      <div class="result-card">
        <div class="result-icon">✓</div>
        ${Badge({ label: 'Level 4 Verified', tone: 'success', icon: '✓' })}
        <div class="result-summary">
          <strong>2 of 2</strong>
          <span>credentials cryptographically verified</span>
        </div>
        <div class="verification-list">
          <div>${Status({ status: 'verified' })}<span>Class 10 Certificate</span><small>CBSE</small></div>
          <div>${Status({ status: 'verified' })}<span>Class 12 Certificate</span><small>CBSE (ZKP >= 60%)</small></div>
        </div>
        <div class="verification-id">
          <small>Signed Proof ID</small>
          <strong>DIN-VRF-82A91</strong>
          <button id="share" class="btn btn-secondary btn-small" type="button">Copy Proof ID</button>
        </div>
        <p id="sharemsg" class="muted" aria-live="polite"></p>
        <div class="actions centered">
          <a class="btn btn-primary" href="#/dashboard">Go to dashboard</a>
          <a class="btn btn-secondary" href="#/verify/audit">Audit log</a>
        </div>
      </div>
    `
  });
}

function AuditLog() {
  const r = currentRequest();
  return Page({
    eyebrow: 'Consent & Audit Trail',
    title: 'Verification Transaction Record',
    description: 'Immutable log of consent grants and verification transactions under DPDP Act 2023.',
    narrow: true,
    children: `
      <div class="form-card">
        ${OrganisationIdentity({ name: r.organisation, category: r.category, requestId: r.id })}
        <div class="request-summary" style="margin-top: 16px;">
          <div><small>Transaction Status</small><strong class="text-success">✓ Verified Proof Generated</strong></div>
          <div><small>Verification ID</small><strong>DIN-VRF-82A91</strong></div>
          <div><small>Consent Timestamp</small><strong>${new Date().toLocaleDateString()}</strong></div>
          <div><small>Consent Expiry</small><strong>${new Date(Date.now() + 24*3600*1000).toLocaleDateString()}</strong></div>
        </div>
        <h2>Documents in scope</h2>
        <div class="requested-list">
          ${r.documents.map(d => RequestedDocumentCard({ title: d.title, issuer: d.issuer, purpose: d.purpose, claims: d.claims })).join('')}
        </div>
        <div class="actions centered" style="margin-top: 20px;">
          <a class="btn btn-primary" href="#/dashboard">Return to dashboard</a>
        </div>
      </div>
    `
  });
}

const Info = (title, text, eyebrow = 'Information') => Page({
  eyebrow,
  title,
  description: text[1],
  narrow: true,
  children: Card({
    children: `<h2>${text[0]}</h2><p class="muted">${text[2] || 'This information is part of the DigiIn foundation build.'}</p>`
  })
});

const routes = {
  '/': Home,
  '/dashboard': Dashboard,
  '/verify/request': VerifyRequest,
  '/verify/review': VerifyReview,
  '/verify/digilocker': DigiLockerConnect,
  '/verify/consent': Consent,
  '/verify/declined': ConsentDeclined,
  '/verify/retrieving': Retrieving,
  '/verify/documents': DocumentsReady,
  '/verify/result': Result,
  '/verify/audit': AuditLog,
  '/how': () => Info('How DigiIn Works', ['Three simple steps', 'Learn how DigiIn makes digital document verification simple, consent-led and accessible.', 'Citizens review requests, connect trusted sources, and generate mathematical proof tokens.']),
  '/security': () => Info('Security & Privacy', ['Built for trust', 'Understand the privacy safeguards, consent management, and data protections behind DigiIn.', 'We never store raw documents or share data without explicit consent.']),
  '/accessibility': () => Info('Accessibility Statement', ['Accessible by design', 'DigiIn complies with WCAG 2.1 Level AA and UX4G 3.0 accessibility standards.']),
  '/help': () => Info('Help & Support', ['Frequently asked questions', 'Find answers to common questions about document verification and DigiLocker connection.']),
  '/privacy': () => Info('Privacy Notice', ['Your privacy rights', 'DigiIn adheres to DPDP Act 2023 regulations and sovereign citizen data ownership.']),
  '/terms': () => Info('Terms of Service', ['Terms & Conditions', 'Official terms governing the use of DigiIn verification services.'])
};

function render() {
  const p = path();
  const view = routes[p] || routes['/'];
  app.innerHTML = `${Header()}${view()}${Footer()}`;
  bindEvents();
}

function bindEvents() {
  // Mobile menu toggle
  const menuBtn = document.querySelector('#menu');
  if (menuBtn) {
    menuBtn.addEventListener('click', () => {
      state.menu = !state.menu;
      render();
    });
  }

  // Language switch
  const langBtn = document.querySelector('#lang');
  if (langBtn) {
    langBtn.addEventListener('click', () => {
      state.lang = state.lang === 'EN' ? 'HI' : 'EN';
      render();
    });
  }

  // Copy DigiIn ID
  const copyBtn = document.querySelector('#copy-id');
  if (copyBtn) {
    copyBtn.addEventListener('click', () => {
      navigator.clipboard?.writeText(state.user?.digiinId || 'DIN-84K2-19Q7');
      copyBtn.textContent = '✓ Copied!';
      setTimeout(() => { copyBtn.textContent = 'Copy ID'; }, 2000);
    });
  }

  // Copy Verification Share ID
  const shareBtn = document.querySelector('#share');
  if (shareBtn) {
    shareBtn.addEventListener('click', () => {
      navigator.clipboard?.writeText('DIN-VRF-82A91');
      const msg = document.querySelector('#sharemsg');
      if (msg) msg.textContent = '✓ Verification Proof ID copied to clipboard!';
    });
  }

  // DigiLocker Connection & Auth
  const dlBtn = document.querySelector('#connect-digilocker');
  if (dlBtn) {
    dlBtn.addEventListener('click', async () => {
      const statusEl = document.querySelector('#connection-status');
      if (statusEl) statusEl.innerHTML = '<p class="muted">Connecting to DigiLocker gateway…</p>';
      dlBtn.disabled = true;

      await digiLockerService.connect();
      if (statusEl) statusEl.innerHTML = '<p class="muted">Authenticating credentials…</p>';
      await digiLockerService.authenticate();

      go('/verify/consent');
    });
  }

  // Consent checkbox handling
  const consentBox = document.querySelector('#consent');
  const giveConsentBtn = document.querySelector('#give-consent');
  if (consentBox && giveConsentBtn) {
    consentBox.addEventListener('change', () => {
      state.consent = consentBox.checked;
      giveConsentBtn.disabled = !state.consent;
    });
  }

  // Decline consent
  const declineBtn = document.querySelector('#decline-consent');
  if (declineBtn) {
    declineBtn.addEventListener('click', () => {
      state.consent = false;
      go('/verify/declined');
    });
  }

  // Give consent & retrieve
  if (giveConsentBtn) {
    giveConsentBtn.addEventListener('click', async () => {
      state.consentRecord = await digiLockerService.authorizeConsent(state.request.id, {
        zkpMode: state.zkpMode,
        durationHours: state.consentDuration
      });
      go('/verify/retrieving');
    });
  }

  // Asynchronous Retrieval Simulation
  if (path() === '/verify/retrieving') {
    const statusEl = document.querySelector('#retrieval-status');
    const step2 = document.querySelector('#step-2');
    const step3 = document.querySelector('#step-3');

    setTimeout(() => {
      if (statusEl) statusEl.innerHTML = '<h2>Querying CBSE Registry…</h2><p class="muted">Retrieving Class 10 & Class 12 digital records.</p>';
      if (step2) step2.classList.add('active');
    }, 600);

    setTimeout(() => {
      if (statusEl) statusEl.innerHTML = '<h2>Validating Signatures…</h2><p class="muted">Checking cryptographic public keys.</p>';
      if (step3) step3.classList.add('active');
    }, 1200);

    setTimeout(async () => {
      state.retrieved = await digiLockerService.getDocuments(state.retrievalScenario);
      go('/verify/documents');
    }, 1800);
  }

  // Start verification from ready documents
  const startVerifBtn = document.querySelector('#start-verification');
  if (startVerifBtn) {
    startVerifBtn.addEventListener('click', () => {
      go('/verify/result');
    });
  }
}

window.addEventListener('hashchange', render);
render();
