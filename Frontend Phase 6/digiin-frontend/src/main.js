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
  Stepper,
  VerificationTimeline,
  DocumentDetailCard,
  ProofEnvelopeCard
} from './components.js';
import { verificationService } from './services/verification/verificationService.js';

const app = document.querySelector('#app');
const state = {
  menu: false,
  lang: 'EN',
  user: { name: 'Rahul Sharma', digiinId: 'DIN-84K2-19Q7', mobile: '9876543210' },
  scenario: 'success', // 'success' | 'partial' | 'authority_unavailable' | 'mismatch'
  pipelineProgress: 0,
  pipelineStatusMessage: 'Initializing verification engine…',
  pipelineStages: [],
  result: null,
  selectedDocId: 'doc-12',
  request: {
    id: 'VR-82A91',
    organisation: 'ABC University',
    category: 'Central Higher Education Institution',
    purpose: 'Admission verification',
    documents: [
      { id: 'doc-10', title: 'Class 10 Certificate', issuer: 'CBSE', purpose: 'Eligibility verification', claims: ['DOB', 'Roll No'] },
      { id: 'doc-12', title: 'Class 12 Certificate', issuer: 'CBSE', purpose: 'Eligibility verification', claims: ['Passing Year', 'Percentage >= 60%'] }
    ]
  }
};

const path = () => location.hash.replace(/^#/, '') || '/';
const go = (p) => { location.hash = p; };

const Header = () => `
  <div class="top">
    <div class="container top-inner">
      <span>भारत सरकार • Government of India</span>
      <span>Digital India Initiative • Phase 6 Verification Engine</span>
    </div>
  </div>
  <header class="header">
    <div class="container head">
      <a class="brand" href="#/" aria-label="DigiIn home">
        <span class="mark">DI</span>
        <span>DigiIn<small>Phase 6 Document Verification Engine</small></span>
      </a>
      <nav class="nav" aria-label="Primary">
        <a href="#/">Home</a>
        <a href="#/verify/check">Start Verification</a>
        <a href="#/verify/proof">Proof Inspector</a>
        <a href="#/help">Help</a>
      </nav>
      <div class="actions">
        <button class="btn btn-secondary btn-small" id="lang" type="button" aria-label="Change language">
          ${state.lang === 'EN' ? 'हिन्दी (HI)' : 'English (EN)'}
        </button>
        <div class="user-pill">
          <span class="user-name">👤 ${state.user.name}</span>
          <a class="btn btn-primary btn-small" href="#/dashboard">Dashboard</a>
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
        <p class="muted">Verify once. Share securely.</p>
      </div>
      <div>
        <strong>Service</strong>
        <a href="#/verify/check">Start Verification</a>
        <a href="#/verify/proof">Proof Token Inspector</a>
        <a href="#/help">Help & Diagnostics</a>
      </div>
      <div>
        <strong>Trust & Standards</strong>
        <a href="#/security">Ed25519 Cryptographic Proofs</a>
        <a href="#/privacy">DPDP Act 2023</a>
        <a href="#/terms">Terms of Service</a>
      </div>
    </div>
    <div class="container footer-bottom">
      <small>Phase 6 Verification Engine • Zero Raw Document Storage Guarantee</small>
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
            <span class="eyebrow">Document Verification Engine</span>
            <h1>Documents Independently<br><span>Checked & Verified.</span></h1>
            <p>DigiIn verifies retrieved credentials through a multi-stage process: format integrity, issuing authority cryptographic checks, and demographic detail matching.</p>
            <div class="actions hero-actions">
              ${Button({ label: 'Start Verification', href: '#/verify/check', icon: '→' })}
              ${Button({ label: 'Inspect Proof Contract', href: '#/verify/proof', variant: 'secondary' })}
            </div>
            <div class="trust-row">
              <span>✓ Integrity Checked</span>
              <span>✓ Issuer Key Match</span>
              <span>✓ Explainable Details</span>
            </div>
          </div>
          ${Card({
            className: 'hero-card',
            children: `
              <div class="shield">🛡️</div>
              <h2>3-Layer Verification Architecture</h2>
              <p class="muted">Every credential is independently verified without black-box assumptions.</p>
              <ul class="list">
                <li>Layer 1: Document structure and SHA-256 digital seals.</li>
                <li>Layer 2: Issuing authority public key resolution (CBSE / UIDAI).</li>
                <li>Layer 3: Candidate name, roll number, and cutoff predicate matching.</li>
              </ul>
            `
          })}
        </div>
      </section>
      <section class="section section-alt">
        <div class="container">
          <span class="eyebrow">The Engine</span>
          <h2>The Phase 6 Verification Lifecycle</h2>
          ${Stepper({ steps: ['Check Request', 'Integrity', 'Authority', 'Details', 'Decision', 'Result'], current: 0 })}
        </div>
      </section>
    </main>
  `;
}

function Dashboard() {
  return Page({
    eyebrow: 'Citizen Account',
    title: `Welcome, ${state.user.name}`,
    description: 'Manage your verified documents, active institutional requests, and verification IDs.',
    children: `
      <div class="actions">
        <a class="btn btn-primary" href="#/verify/check">Start Verification Check <span aria-hidden="true">→</span></a>
      </div>
      <div class="stats">
        <div class="stat-card"><strong>12</strong><span>Vault Documents</span></div>
        <div class="stat-card"><strong>9</strong><span>Level 4 Verified</span></div>
        <div class="stat-card"><strong>1</strong><span>Active Request</span></div>
      </div>
      <div class="dashboard-grid">
        ${Card({
          children: `
            <div class="card-heading">
              <div><span class="eyebrow">Sovereign Account</span><h2>DigiIn ID</h2></div>
              ${Badge({ label: 'Active', tone: 'success', icon: '✓' })}
            </div>
            <div class="id-card">
              <small>DigiIn ID</small>
              <strong>${state.user.digiinId}</strong>
              <p class="muted">Share this identifier with verified services to initiate verification.</p>
              <button class="btn btn-secondary btn-small" id="copy-id" type="button">Copy ID</button>
            </div>
          `
        })}
        ${Card({
          children: `
            <div class="card-heading">
              <div><span class="eyebrow">Pending Request</span><h2>ABC University</h2></div>
            </div>
            <p class="muted">Admission verification request for Class 10 & Class 12 certificates.</p>
            <div class="actions" style="margin-top: 1rem;">
              <a class="btn btn-primary btn-small" href="#/verify/check">Ready to Verify →</a>
            </div>
          `
        })}
      </div>
    `
  });
}

function VerifyCheck() {
  const r = state.request;
  return Page({
    eyebrow: 'Step 1 of 4 • Ready to Verify',
    title: 'Ready to verify',
    description: 'These documents will now be checked against trusted verification data.',
    narrow: true,
    children: `
      ${Stepper({ steps: ['Ready', 'Integrity', 'Authority', 'Detail Match', 'Result'], current: 0 })}
      <div class="form-card">
        ${OrganisationIdentity({ name: r.organisation, category: r.category, requestId: r.id })}
        
        <div class="request-summary">
          <div><small>Organisation</small><strong>${r.organisation}</strong></div>
          <div><small>Purpose</small><strong>${r.purpose}</strong></div>
          <div><small>Request ID</small><strong>${r.id}</strong></div>
        </div>

        <div class="scenario-picker">
          <button class="scenario-btn ${state.scenario === 'success' ? 'selected' : ''}" data-scen="success" type="button">✓ All Verified</button>
          <button class="scenario-btn ${state.scenario === 'partial' ? 'selected' : ''}" data-scen="partial" type="button">! Partial Verification</button>
          <button class="scenario-btn ${state.scenario === 'authority_unavailable' ? 'selected' : ''}" data-scen="authority_unavailable" type="button">! Authority Unavailable</button>
          <button class="scenario-btn ${state.scenario === 'mismatch' ? 'selected' : ''}" data-scen="mismatch" type="button">✕ Detail Mismatch</button>
        </div>

        <h2>Documents</h2>
        <div class="requested-list">
          ${r.documents.map(d => RequestedDocumentCard({ title: d.title, issuer: d.issuer, purpose: d.purpose, claims: d.claims })).join('')}
        </div>

        ${Alert({
          title: 'Trust note',
          message: 'These documents will now be checked against trusted verification data. No raw files will be transferred.',
          tone: 'info'
        })}

        <button id="start-verification-btn" class="btn btn-primary block" style="margin-top: 1.5rem;" type="button">
          Start verification →
        </button>
      </div>
    `
  });
}

function VerifyProgress() {
  return Page({
    eyebrow: 'Step 2 of 4 • Verification in progress',
    title: 'Verification in progress',
    description: 'Please keep this page open while verification checks are executed.',
    narrow: true,
    children: `
      ${Stepper({ steps: ['Ready', 'Integrity', 'Authority', 'Detail Match', 'Result'], current: 2 })}
      <div class="form-card text-center">
        <div class="progress-ring" aria-hidden="true">⚡</div>
        <div id="pipeline-live-status" aria-live="polite">
          <h2>${state.pipelineStatusMessage}</h2>
          <p class="muted">Executing multi-layer cryptographic verification checks…</p>
        </div>

        ${VerificationTimeline({ stages: state.pipelineStages.length ? state.pipelineStages : [
          { title: 'Documents received', description: '2 digital credentials loaded into verification memory.', status: 'completed' },
          { title: 'Document integrity checked', description: 'Checking file structure and digital seals…', status: 'in_progress' },
          { title: 'Checking issuing authority', description: 'Validating against CBSE trusted registry…', status: 'pending' },
          { title: 'Matching document details', description: 'Matching candidate name and cutoff criteria…', status: 'pending' },
          { title: 'Preparing result', description: 'Evaluating decision and generating verification ID…', status: 'pending' }
        ]})}
      </div>
    `
  });
}

function VerifyResult() {
  const res = state.result;
  const isFailed = res?.status === 'FAILED';
  const isPartial = res?.status === 'PARTIALLY_VERIFIED';

  if (isFailed) {
    if (res?.errorType === 'AUTHORITY_UNAVAILABLE') {
      return Page({
        eyebrow: 'Verification Alert',
        title: 'Issuing authority unavailable',
        description: "We couldn't reach the issuing authority right now. Your documents have not been shared.",
        narrow: true,
        children: `
          <div class="form-card text-center">
            <div class="shield" style="background: #FFF0CC; color: #744B00; margin: 0 auto 16px;">!</div>
            <h2>Authority Check Incomplete</h2>
            <p class="muted">${res.message}</p>
            <div class="actions centered" style="margin-top: 24px;">
              <a class="btn btn-primary" href="#/verify/check">Retry verification</a>
              <a class="btn btn-secondary" href="#/dashboard">Return to dashboard</a>
            </div>
          </div>
        `
      });
    }

    return Page({
      eyebrow: 'Verification Failed',
      title: 'Verification failed',
      description: 'The certificate details could not be matched with the trusted source.',
      narrow: true,
      children: `
        <div class="form-card text-center">
          <div class="shield" style="background: #FDE8E8; color: #9B1C1C; margin: 0 auto 16px;">✕</div>
          <h2>Document Detail Mismatch</h2>
          <p class="muted">${res.message}</p>
          <div class="alert alert-error" style="text-align: left; margin: 16px 0;">
            <strong>Support Diagnostic Reference:</strong>
            <p><code>${res.supportCode}</code> • Flagged for Departmental Review Queue</p>
          </div>
          <div class="actions centered" style="margin-top: 24px;">
            <a class="btn btn-primary" href="#/verify/check">Try again</a>
            <a class="btn btn-secondary" href="#/dashboard">Return to dashboard</a>
          </div>
        </div>
      `
    });
  }

  return Page({
    eyebrow: 'Step 4 of 4 • Verification result',
    title: isPartial ? 'Partially verified' : 'Verification complete',
    description: `${isPartial ? '1 of 2' : '2 of 2'} requested documents were successfully verified.`,
    narrow: true,
    children: `
      ${Stepper({ steps: ['Ready', 'Integrity', 'Authority', 'Detail Match', 'Result'], current: 4 })}
      <div class="result-card">
        <div class="result-icon">${isPartial ? '!' : '✓'}</div>
        ${Badge({ label: isPartial ? 'Partially verified' : 'Verified', tone: isPartial ? 'warning' : 'success', icon: isPartial ? '!' : '✓' })}
        <div class="result-summary">
          <strong>${isPartial ? '1 of 2' : '2 of 2'}</strong>
          <span>documents verified</span>
        </div>

        <div class="verification-list">
          ${(res?.documents || []).map(d => `
            <div>
              ${Status({ status: d.status })}
              <span>${d.name}</span>
              <a href="#/verify/document/${d.id}" class="link-button" style="font-size: 0.8rem; text-decoration: underline;">View details →</a>
            </div>
          `).join('')}
        </div>

        <div class="verification-id">
          <small>Verification ID</small>
          <strong>${res?.id || 'DIN-VRF-82A91-K7'}</strong>
          <button id="copy-verif-id-btn" class="btn btn-secondary btn-small" type="button">Copy Verification ID</button>
        </div>
        <p id="verif-copy-msg" class="muted" aria-live="polite"></p>

        <div class="actions centered" style="margin-top: 20px;">
          <a class="btn btn-primary" href="#/dashboard">Go to dashboard</a>
          <a class="btn btn-secondary" href="#/verify/proof">Inspect proof token</a>
        </div>
      </div>
    `
  });
}

function DocumentDetail() {
  const hash = path();
  const docId = hash.split('/').pop() || 'doc-12';
  const docs = state.result?.documents || [
    {
      id: 'doc-12',
      name: 'Class 12 Certificate',
      issuer: 'CBSE',
      status: 'verified',
      verifiedAt: '23 Aug 2026',
      checks: [
        { label: 'Document integrity', status: 'passed', message: 'Document structure and digital seal are valid.' },
        { label: 'Issuing authority', status: 'passed', message: 'CBSE public signing key confirmed.' },
        { label: 'Certificate number', status: 'passed', message: 'CBSE-XII-2025-8812 matched.' },
        { label: 'Candidate details', status: 'passed', message: 'Name match 100%.' },
        { label: 'Issue year', status: 'passed', message: 'Year 2025 confirmed.' }
      ]
    }
  ];

  const doc = docs.find(d => d.id === docId) || docs[0];

  return Page({
    eyebrow: 'Verification Detail',
    title: doc.name,
    description: 'Detailed breakdown of independent verification checks performed on this credential.',
    narrow: true,
    children: `
      ${DocumentDetailCard({
        id: doc.id,
        name: doc.name,
        issuer: doc.issuer,
        status: doc.status,
        verifiedAt: doc.verifiedAt,
        checks: doc.checks
      })}

      <div class="actions" style="margin-top: 1.5rem;">
        <a class="btn btn-primary" href="#/verify/result">← Back to verification result</a>
        <a class="btn btn-secondary" href="#/dashboard">Go to dashboard</a>
      </div>
    `
  });
}

function ProofInspector() {
  return Page({
    eyebrow: 'Proof Contract',
    title: 'Verifiable Proof Receipt',
    description: 'Independent verification statement generated from approved consent and verified document checks.',
    narrow: true,
    children: `
      <div class="form-card">
        <div class="request-summary">
          <div><small>Verification ID</small><strong>${state.result?.id || 'DIN-VRF-82A91-K7'}</strong></div>
          <div><small>Status</small><strong class="text-success">✓ Verified</strong></div>
          <div><small>Documents</small><strong>2 / 2 Verified</strong></div>
        </div>

        ${ProofEnvelopeCard({
          proofId: state.result?.id || 'DIN-VRF-82A91-K7',
          algorithm: 'EdDSA (Ed25519)',
          keyId: 'digiin-ed25519-key-2026',
          status: state.result?.status || 'VERIFIED'
        })}

        ${Alert({
          title: 'Offline Independent Verification',
          message: 'Verifiers possessing the DigiIn gateway public key validate signatures and proof constraints locally without accessing raw documents.',
          tone: 'success'
        })}

        <div class="actions centered" style="margin-top: 20px;">
          <a class="btn btn-primary" href="#/dashboard">Return to Dashboard</a>
          <a class="btn btn-secondary" href="#/verify/check">Start New Verification</a>
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
    children: `<h2>${text[0]}</h2><p class="muted">${text[2] || 'Part of the DigiIn Phase 6 foundation build.'}</p>`
  })
});

const routes = {
  '/': Home,
  '/dashboard': Dashboard,
  '/verify/check': VerifyCheck,
  '/verify/progress': VerifyProgress,
  '/verify/result': VerifyResult,
  '/verify/proof': ProofInspector,
  '/help': () => Info('Help & Diagnostics', ['Verification Engine Support', 'Learn how digital signatures and Zero-Knowledge predicates are evaluated.']),
  '/security': () => Info('Cryptographic Proofs', ['Ed25519 Verifiable Proofs', 'DigiIn utilizes RFC 8037 asymmetric signatures for offline verifiability.']),
  '/privacy': () => Info('Privacy Protections', ['DPDP Act 2023 Compliance', 'Zero raw document storage guarantees complete citizen privacy.']),
  '/terms': () => Info('Terms of Verification', ['Terms of Service', 'Official terms governing the issuance and validation of proof tokens.'])
};

function render() {
  const p = path();
  if (p.startsWith('/verify/document/')) {
    app.innerHTML = `${Header()}${DocumentDetail()}${Footer()}`;
  } else {
    const view = routes[p] || routes['/'];
    app.innerHTML = `${Header()}${view()}${Footer()}`;
  }
  bindEvents();
}

function bindEvents() {
  // Scenario switcher buttons
  document.querySelectorAll('.scenario-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      state.scenario = e.target.dataset.scen;
      render();
    });
  });

  // Start verification button
  const startBtn = document.querySelector('#start-verification-btn');
  if (startBtn) {
    startBtn.addEventListener('click', async () => {
      go('/verify/progress');
      state.pipelineStatusMessage = 'Initiating verification engine…';

      state.result = await verificationService.runVerification(
        state.request.documents,
        state.scenario,
        (progress) => {
          state.pipelineStatusMessage = progress.message;
          state.pipelineStages = progress.stages;
          const liveStatus = document.querySelector('#pipeline-live-status');
          if (liveStatus) {
            liveStatus.innerHTML = `<h2>${progress.title}</h2><p class="muted">${progress.message}</p>`;
          }
        }
      );

      setTimeout(() => {
        go('/verify/result');
      }, 400);
    });
  }

  // Copy DigiIn ID
  const copyIdBtn = document.querySelector('#copy-id');
  if (copyIdBtn) {
    copyIdBtn.addEventListener('click', () => {
      navigator.clipboard?.writeText(state.user.digiinId);
      copyIdBtn.textContent = '✓ Copied!';
      setTimeout(() => { copyIdBtn.textContent = 'Copy ID'; }, 2000);
    });
  }

  // Copy Verification ID
  const copyVerifBtn = document.querySelector('#copy-verif-id-btn');
  if (copyVerifBtn) {
    copyVerifBtn.addEventListener('click', () => {
      navigator.clipboard?.writeText(state.result?.id || 'DIN-VRF-82A91-K7');
      const msg = document.querySelector('#verif-copy-msg');
      if (msg) msg.textContent = '✓ Verification ID copied to clipboard!';
    });
  }
}

window.addEventListener('hashchange', render);
render();
