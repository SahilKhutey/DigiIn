import {
  Button,
  Badge,
  Card,
  Alert,
  Status,
  VerificationProofCard,
  ProofDetails,
  ShareProof,
  QRCodePanel,
  ProofValidationResult,
  VerificationHistory,
  Stepper
} from './components.js';
import { proofService } from './services/proof/proofService.js';
import { organisationService } from './services/organisation/organisationService.js';

const app = document.querySelector('#app');
const state = {
  menu: false,
  lang: 'EN',
  user: { name: 'Rahul Sharma', digiinId: 'DIN-7K4P-92M8', mobile: '9876543210' },
  activeProofId: 'DIN-PRF-51Q8-X2',
  validationResult: null,
  allProofs: []
};

const path = () => location.hash.replace(/^#/, '') || '/';
const go = (p) => { location.hash = p; };

const Header = () => `
  <div class="top">
    <div class="container top-inner">
      <span>भारत सरकार • Government of India</span>
      <span>Digital India Initiative • Phase 7 Digital Proof & Sharing</span>
    </div>
  </div>
  <header class="header">
    <div class="container head">
      <a class="brand" href="#/" aria-label="DigiIn home">
        <span class="mark">DI</span>
        <span>DigiIn<small>Digital Verification Proof & Sharing Layer</small></span>
      </a>
      <nav class="nav" aria-label="Primary">
        <a href="#/">Home</a>
        <a href="#/proof/DIN-PRF-51Q8-X2">Verification Proof</a>
        <a href="#/proof/DIN-PRF-51Q8-X2/share">Share Proof</a>
        <a href="#/verify-proof">Organisation Portal</a>
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
        <strong>Proof & Sharing</strong>
        <a href="#/proof/DIN-PRF-51Q8-X2">Verification Proof</a>
        <a href="#/proof/DIN-PRF-51Q8-X2/share">Share Verification</a>
        <a href="#/verify-proof">Organisation Portal</a>
      </div>
      <div>
        <strong>Trust & Standards</strong>
        <a href="#/security">Data Minimisation Principle</a>
        <a href="#/privacy">DPDP Act 2023 Compliance</a>
        <a href="#/terms">Terms of Verification</a>
      </div>
    </div>
    <div class="container footer-bottom">
      <small>Phase 7 Complete • Data Minimisation • Zero Raw Document Transfer</small>
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
            <span class="eyebrow">Phase 7 • Sovereign Proofs</span>
            <h1>Digital Verification Proof<br><span>& Secure Sharing.</span></h1>
            <p>A verified result can be shared and independently checked without sharing the citizen's underlying documents.</p>
            <div class="actions hero-actions">
              ${Button({ label: 'View Active Proof', href: '#/proof/DIN-PRF-51Q8-X2', icon: '→' })}
              ${Button({ label: 'Organisation Verification Portal', href: '#/verify-proof', variant: 'secondary' })}
            </div>
            <div class="trust-row">
              <span>✓ Data Minimisation</span>
              <span>✓ QR Verification</span>
              <span>✓ Citizen-Controlled Revocation</span>
            </div>
          </div>
          ${Card({
            className: 'hero-card',
            children: `
              <div class="shield">🛡️</div>
              <h2>Data Minimisation Architecture</h2>
              <p class="muted">Organisations verify authenticity without receiving unredacted certificates.</p>
              <ul class="list">
                <li>Proof ID (DIN-PRF-51Q8-X2) linked to Verification ID (DIN-VRF-82A91-K7).</li>
                <li>Secure share URL with endpoint reference.</li>
                <li>Citizen-controlled instant revocation.</li>
              </ul>
            `
          })}
        </div>
      </section>
    </main>
  `;
}

async function Dashboard() {
  state.allProofs = await proofService.getProofHistory();
  const auditEvents = proofService.getAuditEvents();

  return Page({
    eyebrow: 'Citizen Account',
    title: `Welcome, ${state.user.name}`,
    description: 'Manage your verified documents, active verification proofs, and privacy controls.',
    children: `
      <div class="actions">
        <a class="btn btn-primary" href="#/proof/DIN-PRF-51Q8-X2/share">Share Active Proof <span aria-hidden="true">→</span></a>
        <a class="btn btn-secondary" href="#/verify-proof">Organisation Portal</a>
      </div>
      <div class="stats">
        <div class="stat-card"><strong>12</strong><span>Vault Documents</span></div>
        <div class="stat-card"><strong>${state.allProofs.filter(p => p.status === 'ACTIVE').length}</strong><span>Active Proofs</span></div>
        <div class="stat-card"><strong>${state.allProofs.filter(p => p.status === 'REVOKED').length}</strong><span>Revoked Proofs</span></div>
      </div>
      <div class="dashboard-grid">
        ${Card({
          children: `
            <div class="card-heading">
              <div><span class="eyebrow">Proof History</span><h2>Verification Proofs</h2></div>
            </div>
            <p class="muted">Active, expired, and revoked verification proofs created from your verified documents.</p>
            ${VerificationHistory({ proofs: state.allProofs })}
          `
        })}
        <div>
          ${Card({
            children: `
              <div class="card-heading">
                <div><span class="eyebrow">Account Identifier</span><h2>DigiIn ID</h2></div>
              </div>
              <div class="id-card">
                <small>DigiIn ID (Account)</small>
                <strong>${state.user.digiinId}</strong>
                <p class="muted">Identifies your sovereign account. Cannot be used by third parties to view your documents.</p>
                <button class="btn btn-secondary btn-small" id="copy-id" type="button">Copy ID</button>
              </div>
            `
          })}
          ${Card({
            className: 'feature-card',
            children: `
              <span class="eyebrow" style="margin-bottom: 0.5rem;">Audit Trail</span>
              <h3 style="margin: 0.3rem 0 0.75rem;">Recent Proof Activity</h3>
              <ul style="list-style: none; padding: 0; margin: 0; font-size: 0.85rem; display: grid; gap: 0.5rem;">
                ${auditEvents.map(e => `
                  <li style="border-bottom: 1px solid var(--color-border-subtle); padding-bottom: 0.4rem;">
                    <strong>${e.label}</strong>
                    <div style="font-size: 0.75rem; color: var(--color-text-muted);">${e.timestamp} • ${e.proofId}</div>
                  </li>
                `).join('')}
              </ul>
            `
          })}
        </div>
      </div>
    `
  });
}

function VerifyResultWithCreateProof() {
  return Page({
    eyebrow: 'Phase 6 Result • Complete',
    title: 'Verification complete',
    description: '2 of 2 requested credentials independently verified.',
    narrow: true,
    children: `
      <div class="result-card">
        <div class="result-icon">✓</div>
        ${Badge({ label: 'Verified', tone: 'success', icon: '✓' })}
        <div class="result-summary">
          <strong>2 of 2</strong>
          <span>documents verified</span>
        </div>

        <div class="verification-list">
          <div>
            <span class="status-pill status-success"><span class="status-icon">✓</span> Verified</span>
            <span>Class 10 Certificate</span>
            <small>CBSE</small>
          </div>
          <div>
            <span class="status-pill status-success"><span class="status-icon">✓</span> Verified</span>
            <span>Class 12 Certificate</span>
            <small>CBSE</small>
          </div>
        </div>

        <div class="verification-id">
          <small>Verification ID</small>
          <strong>DIN-VRF-82A91-K7</strong>
        </div>

        <div class="actions centered" style="margin-top: 24px;">
          <button id="create-proof-action-btn" class="btn btn-primary" type="button">
            Create verification proof →
          </button>
          <a class="btn btn-secondary" href="#/dashboard">Go to dashboard</a>
        </div>
      </div>
    `
  });
}

async function ProofResultView(proofId = 'DIN-PRF-51Q8-X2') {
  const p = await proofService.getProof(proofId) || {
    proofId,
    verificationId: 'DIN-VRF-82A91-K7',
    status: 'ACTIVE',
    organisation: 'ABC University',
    purpose: 'Admission verification',
    verifiedDocuments: ['Class 10 Certificate', 'Class 12 Certificate'],
    issuedAt: '23 Aug 2026',
    expiresAt: '24 Aug 2026'
  };

  return Page({
    eyebrow: 'Phase 7 • Verification Proof',
    title: 'Verification proof',
    description: 'Your verification proof is active and ready for ABC University.',
    narrow: true,
    children: `
      ${ProofDetails({ proof: p })}
    `
  });
}

async function ShareProofView(proofId = 'DIN-PRF-51Q8-X2') {
  const p = await proofService.getProof(proofId) || {
    proofId,
    expiresAt: '24 Aug 2026'
  };
  const shareUrl = proofService.getShareUrl(proofId);

  return Page({
    eyebrow: 'Phase 7 • Secure Share',
    title: 'Share this verification',
    description: 'Provide ABC University with the secure proof reference or link.',
    narrow: true,
    children: `
      ${ShareProof({
        proofId: p.proofId,
        shareUrl,
        expiresAt: p.expiresAt
      })}

      ${Alert({
        title: 'Privacy Note',
        message: 'The share URL contains only a non-secret proof reference. Organisations verify validity without accessing your document vault.',
        tone: 'info'
      })}

      <div class="actions centered" style="margin-top: 1.5rem;">
        <a class="btn btn-secondary" href="#/dashboard">Return to Citizen Dashboard</a>
      </div>
    `
  });
}

function QrView(proofId = 'DIN-PRF-51Q8-X2') {
  return Page({
    eyebrow: 'Phase 7 • QR Verification',
    title: 'Scan to verify this DigiIn proof',
    description: 'Present this QR code for instant verification by relying organisations.',
    narrow: true,
    children: `
      ${QRCodePanel({
        proofId,
        qrSvg: proofService.getQrSvg(proofId)
      })}
    `
  });
}

async function RevokeProofView(proofId = 'DIN-PRF-51Q8-X2') {
  const p = await proofService.getProof(proofId);

  return Page({
    eyebrow: 'Citizen Revocation Control',
    title: 'Revoke this verification?',
    description: 'You have full sovereign control over your issued verification proofs.',
    narrow: true,
    children: `
      <div class="form-card">
        <div class="request-summary">
          <div><small>Proof ID</small><strong style="font-family: var(--font-mono);">${proofId}</strong></div>
          <div><small>Organisation</small><strong>${p?.organisation || 'ABC University'}</strong></div>
          <div><small>Purpose</small><strong>${p?.purpose || 'Admission verification'}</strong></div>
        </div>

        <div class="alert alert-error" style="margin: 1.5rem 0;">
          <strong>Warning:</strong>
          <p>After revocation, this proof can no longer be validated as active. The original verification result remains part of the historical record; only the shareable proof becomes invalid.</p>
        </div>

        <div class="actions" style="justify-content: flex-end;">
          <a class="btn btn-secondary" href="#/proof/${proofId}">Cancel</a>
          <button id="confirm-revoke-btn" class="btn btn-primary" style="background: var(--color-error-700); border-color: var(--color-error-700);" type="button">Revoke proof</button>
        </div>
      </div>
    `
  });
}

function OrganisationPortalView() {
  const params = new URLSearchParams(window.location.hash.split('?')[1] || '');
  const prefillId = params.get('id') || state.activeProofId;

  return Page({
    eyebrow: 'Organisation Verification Portal',
    title: 'Verify DigiIn proof',
    description: 'Enter a verification ID or scan a QR code to validate a citizen’s verification proof.',
    narrow: true,
    children: `
      <div class="form-card">
        <div class="field">
          <label for="input-proof-id">Enter Verification ID</label>
          <input id="input-proof-id" type="text" placeholder="e.g. DIN-PRF-51Q8-X2" value="${prefillId}" />
        </div>

        <div style="margin: 1rem 0;">
          <small class="muted" style="display: block; margin-bottom: 0.35rem; font-weight: 700;">Test Validation Scenarios:</small>
          <div class="scenario-picker">
            <button class="scenario-btn selected" data-test="DIN-PRF-51Q8-X2" type="button">✓ Valid (ABC Univ)</button>
            <button class="scenario-btn" data-test="DIN-PRF-73K1-P9" type="button">! Expired Proof</button>
            <button class="scenario-btn" data-test="DIN-PRF-REV-88" type="button">✕ Revoked Proof</button>
            <button class="scenario-btn" data-test="INVALID-PROOF-99" type="button">✕ Invalid ID</button>
            <button class="scenario-btn" data-test="SERVICE_UNAVAILABLE" type="button">⚡ Unavailable</button>
          </div>
        </div>

        <div class="actions" style="margin-top: 1.5rem;">
          <button id="portal-verify-btn" class="btn btn-primary block" type="button">Verify proof →</button>
        </div>
      </div>
    `
  });
}

function OrganisationResultView() {
  const res = state.validationResult || {
    status: 'VALID',
    message: 'DigiIn has confirmed this verification proof.',
    proof: {
      proofId: 'DIN-PRF-51Q8-X2',
      verificationId: 'DIN-VRF-82A91-K7',
      organisation: 'ABC University',
      purpose: 'Admission verification',
      verifiedDocuments: ['Class 10 Certificate', 'Class 12 Certificate'],
      issuedAt: '23 Aug 2026',
      expiresAt: '24 Aug 2026'
    }
  };

  return Page({
    eyebrow: 'Organisation Validation Result',
    title: res.status === 'VALID' ? 'Verification Confirmed' : 'Verification Status',
    description: 'DigiIn Sovereign Gateway verification outcome.',
    narrow: true,
    children: `
      ${ProofValidationResult({ result: res })}
    `
  });
}

const Info = (title, text, eyebrow = 'Information') => Page({
  eyebrow,
  title,
  description: text[1],
  narrow: true,
  children: Card({
    children: `<h2>${text[0]}</h2><p class="muted">${text[2] || 'Part of the DigiIn Phase 7 foundation build.'}</p>`
  })
});

const routes = {
  '/': Home,
  '/dashboard': Dashboard,
  '/verify/result': VerifyResultWithCreateProof,
  '/verify-proof': OrganisationPortalView,
  '/verify-proof/result': OrganisationResultView,
  '/help': () => Info('Help & Verifier Guide', ['Verifying Digital Proofs', 'Learn how organisations validate proofs online and offline.']),
  '/security': () => Info('Data Minimisation Principle', ['Zero Document Transfer', 'Organisations verify assertions without acquiring citizen document copies.']),
  '/privacy': () => Info('Privacy Notice', ['DPDP Act 2023 Compliance', 'Sovereign citizen control and instant revocation guarantee privacy.']),
  '/terms': () => Info('Terms of Service', ['Terms of Verification', 'Official terms governing verifiable proof tokens.'])
};

async function render() {
  const p = path().split('?')[0];

  if (p.startsWith('/proof/') && p.endsWith('/share')) {
    const proofId = p.split('/')[2];
    const html = await ShareProofView(proofId);
    app.innerHTML = `${Header()}${html}${Footer()}`;
  } else if (p.startsWith('/proof/') && p.endsWith('/qr')) {
    const proofId = p.split('/')[2];
    app.innerHTML = `${Header()}${QrView(proofId)}${Footer()}`;
  } else if (p.startsWith('/proof/') && p.endsWith('/revoke')) {
    const proofId = p.split('/')[2];
    const html = await RevokeProofView(proofId);
    app.innerHTML = `${Header()}${html}${Footer()}`;
  } else if (p.startsWith('/proof/')) {
    const proofId = p.split('/')[2];
    const html = await ProofResultView(proofId);
    app.innerHTML = `${Header()}${html}${Footer()}`;
  } else if (p === '/dashboard') {
    const html = await Dashboard();
    app.innerHTML = `${Header()}${html}${Footer()}`;
  } else {
    const view = routes[p] || routes['/'];
    app.innerHTML = `${Header()}${view()}${Footer()}`;
  }
  bindEvents();
}

function bindEvents() {
  // Create proof action from Phase 6 result
  const createProofBtn = document.querySelector('#create-proof-action-btn');
  if (createProofBtn) {
    createProofBtn.addEventListener('click', async () => {
      const proof = await proofService.createProof('DIN-VRF-82A91-K7');
      go(`/proof/${proof.proofId}`);
    });
  }

  // Scenario buttons in Verifier Portal
  document.querySelectorAll('.scenario-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('.scenario-btn').forEach(b => b.classList.remove('selected'));
      e.target.classList.add('selected');
      const input = document.querySelector('#input-proof-id');
      if (input) input.value = e.target.dataset.test;
    });
  });

  // Verify button in organisation portal
  const verifyBtn = document.querySelector('#portal-verify-btn');
  if (verifyBtn) {
    verifyBtn.addEventListener('click', async () => {
      const input = document.querySelector('#input-proof-id');
      const id = input?.value || 'DIN-PRF-51Q8-X2';
      state.validationResult = await organisationService.verifyProof(id);
      go('/verify-proof/result');
    });
  }

  // Copy share link
  const copyLinkBtn = document.querySelector('#copy-share-link');
  if (copyLinkBtn) {
    copyLinkBtn.addEventListener('click', () => {
      const input = document.querySelector('#share-link-input');
      if (input) {
        navigator.clipboard?.writeText(input.value);
        const toast = document.querySelector('#share-toast');
        if (toast) toast.textContent = '✓ Secure Share Link copied to clipboard!';
      }
    });
  }

  // Native share button fallback
  const shareBtn = document.querySelector('#native-share-btn');
  if (shareBtn) {
    shareBtn.addEventListener('click', () => {
      const input = document.querySelector('#share-link-input');
      if (navigator.share && input) {
        navigator.share({ title: 'DigiIn Verification Proof', url: input.value });
      } else if (input) {
        navigator.clipboard?.writeText(input.value);
        const toast = document.querySelector('#share-toast');
        if (toast) toast.textContent = '✓ Link copied to clipboard!';
      }
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

  // Confirm Revoke Button
  const revokeBtn = document.querySelector('#confirm-revoke-btn');
  if (revokeBtn) {
    revokeBtn.addEventListener('click', async () => {
      const p = path();
      const proofId = p.split('/')[2] || 'DIN-PRF-51Q8-X2';
      await proofService.revokeProof(proofId);
      alert('✓ Verification proof revoked successfully. Organisations will no longer be able to validate this proof.');
      go('/dashboard');
    });
  }
}

window.addEventListener('hashchange', () => render());
render();
