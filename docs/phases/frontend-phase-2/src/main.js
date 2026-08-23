import { Button } from './components/Button.js';
import { Card } from './components/Card.js';
import { Badge } from './components/Badge.js';
import { Alert } from './components/Alert.js';
import { DocumentCard } from './components/DocumentCard.js';
import { ConsentCard } from './components/ConsentCard.js';
import { DigiInIDCard } from './components/DigiInIDCard.js';
import { VerificationTimeline } from './components/VerificationTimeline.js';
import { ShareVerificationCard } from './components/ShareVerificationCard.js';

const app = document.querySelector('#app');

const state = {
  menuOpen: false,
  lang: 'EN',
  currentStepIndex: 0,
};

const getPath = () => location.hash.replace('#', '') || '/';
const navigate = (p) => { location.hash = p; };

// Header Component
function Header() {
  return `
    <div class="gov-top-bar">
      <div class="container">
        <span>भारत सरकार • Government of India</span>
        <span>Digital India • UX4G 3.0 Standard</span>
      </div>
    </div>
    <header class="main-header ${state.menuOpen ? 'mobile-open' : ''}">
      <div class="container header-content">
        <a class="brand-link" href="#/">
          <div class="brand-logo">D</div>
          <div class="brand-text">
            <span>DigiIn</span>
            <small>Sovereign Credential Verification</small>
          </div>
        </a>

        <nav class="main-nav" aria-label="Main Navigation">
          <a class="nav-item ${getPath() === '/' ? 'active' : ''}" href="#/">Home</a>
          <a class="nav-item ${getPath() === '/dashboard' ? 'active' : ''}" href="#/dashboard">Dashboard</a>
          <a class="nav-item ${getPath() === '/verify' ? 'active' : ''}" href="#/verify">Verify</a>
          <a class="nav-item ${getPath() === '/how' ? 'active' : ''}" href="#/how">How It Works</a>
          <a class="nav-item ${getPath() === '/security' ? 'active' : ''}" href="#/security">Security</a>
        </nav>

        <div class="header-actions">
          <button id="lang-toggle" class="btn secondary" style="min-height: 36px; padding: 0.35rem 0.75rem; font-size: 0.8rem;">
            ${state.lang === 'EN' ? 'हिन्दी (HI)' : 'English (EN)'}
          </button>
          <a class="btn primary" href="#/sign-in" style="min-height: 36px; padding: 0.35rem 0.85rem; font-size: 0.85rem;">
            Sign in
          </a>
          <button id="mobile-menu-btn" class="mobile-menu-btn" aria-label="Toggle navigation menu">☰</button>
        </div>
      </div>
    </header>
  `;
}

// Footer Component
function Footer() {
  return `
    <footer class="gov-footer">
      <div class="container">
        <div class="grid-4" style="margin-bottom: 2rem;">
          <div>
            <strong style="color: var(--white); font-size: 1.1rem; display: block; margin-bottom: 0.5rem;">DigiIn</strong>
            <p style="font-size: 0.8rem; color: var(--slate-300); line-height: 1.5;">
              Sovereign credential and verification infrastructure adhering to UX4G 3.0 government standards.
            </p>
          </div>
          <div>
            <strong style="color: var(--white); font-size: 0.85rem; text-transform: uppercase; display: block; margin-bottom: 0.5rem;">Trust Framework</strong>
            <ul style="list-style: none; padding: 0; margin: 0; font-size: 0.8rem; line-height: 1.8;">
              <li>• Zero Document Retention</li>
              <li>• Ed25519 Cryptographic Proofs</li>
              <li>• Granular Purpose Consent</li>
            </ul>
          </div>
          <div>
            <strong style="color: var(--white); font-size: 0.85rem; text-transform: uppercase; display: block; margin-bottom: 0.5rem;">Issuers</strong>
            <ul style="list-style: none; padding: 0; margin: 0; font-size: 0.8rem; line-height: 1.8;">
              <li>• CBSE Education Board</li>
              <li>• UIDAI Aadhaar eKYC</li>
              <li>• State Revenue Registries</li>
            </ul>
          </div>
          <div>
            <strong style="color: var(--white); font-size: 0.85rem; text-transform: uppercase; display: block; margin-bottom: 0.5rem;">Compliance</strong>
            <p style="font-size: 0.8rem; color: var(--slate-300); line-height: 1.5;">
              DPDP Act 2023 & WCAG 2.1 Level AA Compliant.
            </p>
          </div>
        </div>

        <div style="padding-top: 1.5rem; border-top: 1px solid rgba(255, 255, 255, 0.1); display: flex; justify-content: space-between; flex-wrap: wrap; gap: 1rem; font-size: 0.78rem;">
          <span>© 2026 DigiIn • Digital Public Infrastructure</span>
          <div style="display: flex; gap: 1rem;">
            <a href="#/accessibility">Accessibility</a>
            <a href="#/privacy">Privacy Policy</a>
            <a href="#/terms">Terms of Service</a>
            <a href="#/help">Help</a>
          </div>
        </div>
      </div>
    </footer>
  `;
}

// Views
function HomeView() {
  return `
    <main id="main">
      <section class="hero-section">
        <div class="container hero-grid">
          <div>
            <span class="badge info">Government Service Journey</span>
            <h1 class="hero-title">Verify once.<br>Share securely.</h1>
            <p class="hero-subtitle">
              DigiIn enables citizens to share verified DigiLocker credentials with universities, employers, and government agencies with <strong>zero raw document transfers</strong>.
            </p>
            <div style="display: flex; gap: 0.75rem; margin-top: 1.75rem; flex-wrap: wrap;">
              ${Button({ text: 'Start Verification Journey →', variant: 'primary', href: '#/verify' })}
              ${Button({ text: 'Open Citizen Dashboard', variant: 'secondary', href: '#/dashboard' })}
            </div>
          </div>

          <div>
            ${Card({
              title: 'Consent-Led Verification',
              description: 'You control what is shared, with whom, and for what purpose.',
              variant: 'elevated',
              badge: Badge({ text: 'Sovereign', variant: 'success' }),
              content: `
                <ul style="list-style: none; padding: 0; margin: 0; display: grid; gap: 0.65rem; font-size: 0.85rem; color: var(--slate-700);">
                  <li><span style="color: var(--green-700); font-weight: 800;">✓</span> Requesting organization is verified</li>
                  <li><span style="color: var(--green-700); font-weight: 800;">✓</span> Granular attribute-level disclosure</li>
                  <li><span style="color: var(--green-700); font-weight: 800;">✓</span> Offline-verifiable cryptographic receipts</li>
                </ul>
              `,
            })}
          </div>
        </div>
      </section>

      <section style="padding: 3.5rem 0;">
        <div class="container">
          <div style="text-align: center; max-width: 600px; margin: 0 auto 2.5rem;">
            <h2 style="font-size: 1.8rem; color: var(--blue-900); margin-bottom: 0.5rem;">How DigiIn Works</h2>
            <p style="color: var(--slate-600); font-size: 0.95rem;">A simple 4-step workflow replacing paper file submissions.</p>
          </div>

          <div class="grid-4">
            ${Card({
              title: '1. Request',
              description: 'An accredited institution specifies required credentials.',
              variant: 'bordered',
              content: '<p style="font-size: 0.82rem; color: var(--slate-600); margin: 0;">Organization creates a purpose-bound query link or QR code.</p>',
            })}
            ${Card({
              title: '2. Consent',
              description: 'Citizen reviews and authorizes granular attributes.',
              variant: 'bordered',
              content: '<p style="font-size: 0.82rem; color: var(--slate-600); margin: 0;">Optionally choose Zero-Knowledge Predicates to prevent oversharing.</p>',
            })}
            ${Card({
              title: '3. Verify',
              description: 'Real-time validation directly against official registries.',
              variant: 'bordered',
              content: '<p style="font-size: 0.82rem; color: var(--slate-600); margin: 0;">Issuers (CBSE, UIDAI) validate records in real-time.</p>',
            })}
            ${Card({
              title: '4. Proof',
              description: 'Cryptographically signed JWS receipt generated.',
              variant: 'bordered',
              content: '<p style="font-size: 0.82rem; color: var(--slate-600); margin: 0;">Recipient verifies proof offline without retaining raw citizen files.</p>',
            })}
          </div>
        </div>
      </section>
    </main>
  `;
}

function SignInView() {
  return `
    <main id="main" class="page">
      <div class="container narrow-container">
        <a href="#/" style="font-size: 0.85rem; font-weight: 700;">← Back to Home</a>
        <div style="margin-top: 1rem;">
          <h1 style="color: var(--blue-900); font-size: 1.8rem; margin-bottom: 0.25rem;">Sign In to DigiIn</h1>
          <p style="color: var(--slate-600); font-size: 0.9rem;">Passwordless authentication via mobile OTP</p>

          <div class="card elevated" style="margin-top: 1.5rem;">
            ${Alert({
              type: 'info',
              title: 'Test Credentials Ready',
              message: 'Demo mode accepts any 10-digit number (e.g. 9876543210).',
            })}

            <form id="form-signin" style="margin-top: 1.25rem;">
              <div class="form-field">
                <label for="mobile-input">Registered Mobile Number</label>
                <input id="mobile-input" class="form-input" type="tel" maxlength="10" placeholder="10-digit mobile number" value="9876543210" required>
              </div>

              ${Button({ text: 'Send OTP & Sign In →', variant: 'primary', type: 'submit', className: 'block' })}
            </form>
          </div>
        </div>
      </div>
    </main>
  `;
}

function DashboardView() {
  return `
    <main id="main" class="page">
      <div class="container">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 1rem; margin-bottom: 2rem;">
          <div>
            <span class="badge info">Citizen Account</span>
            <h1 style="color: var(--blue-900); font-size: 2rem; margin: 0.25rem 0;">Welcome, Rahul Sharma</h1>
            <p style="color: var(--slate-600); font-size: 0.9rem; margin: 0;">Manage your verified credentials and active sharing permissions.</p>
          </div>
          <div>
            ${Button({ text: 'Start New Verification →', variant: 'primary', href: '#/verify' })}
          </div>
        </div>

        <div class="grid-3" style="margin-bottom: 2rem;">
          <div class="card">
            <span style="font-size: 0.8rem; color: var(--slate-600); font-weight: 700; text-transform: uppercase;">Total Credentials</span>
            <strong style="font-size: 2rem; color: var(--blue-900); display: block; margin-top: 0.25rem;">12</strong>
          </div>
          <div class="card">
            <span style="font-size: 0.8rem; color: var(--slate-600); font-weight: 700; text-transform: uppercase;">Verified at Source</span>
            <strong style="font-size: 2rem; color: var(--green-700); display: block; margin-top: 0.25rem;">9</strong>
          </div>
          <div class="card">
            <span style="font-size: 0.8rem; color: var(--slate-600); font-weight: 700; text-transform: uppercase;">Active Consent Grants</span>
            <strong style="font-size: 2rem; color: var(--blue-700); display: block; margin-top: 0.25rem;">2</strong>
          </div>
        </div>

        <div class="grid-2" style="margin-bottom: 2rem;">
          <div>
            ${DigiInIDCard({ idNumber: 'DIN-84K2-19Q7', holderName: 'Rahul Sharma' })}
          </div>
          <div>
            ${Card({
              title: 'Recent Activity',
              description: 'Audit log of verified exchanges',
              variant: 'elevated',
              content: `
                <div style="font-size: 0.85rem; line-height: 1.8;">
                  <div><strong>✓ Class 12 Verification Shared</strong><br><small style="color: var(--slate-500);">ABC University • Today at 10:15 IST</small></div>
                  <div style="margin-top: 0.5rem;"><strong>✓ Aadhaar eKYC Assertion Minted</strong><br><small style="color: var(--slate-500);">UIDAI Gateway • Yesterday</small></div>
                </div>
              `,
            })}
          </div>
        </div>

        ${Card({
          title: 'Your Verified Documents',
          description: 'Credentials synchronized with government issuing boards',
          variant: 'elevated',
          content: `
            ${DocumentCard({ title: 'Class XII Marksheet', issuer: 'CBSE', issueDate: '15 May 2025', status: 'VERIFIED', trustLevel: 4 })}
            ${DocumentCard({ title: 'Class X Passing Certificate', issuer: 'CBSE', issueDate: '20 May 2023', status: 'VERIFIED', trustLevel: 4 })}
            ${DocumentCard({ title: 'Aadhaar Identity Assertion', issuer: 'UIDAI', issueDate: 'Level 4 Matched', status: 'VERIFIED', trustLevel: 4 })}
          `,
        })}
      </div>
    </main>
  `;
}

function VerifyView() {
  return `
    <main id="main" class="page">
      <div class="container narrow-container">
        <span class="badge info">Verification Request</span>
        <h1 style="color: var(--blue-900); font-size: 1.8rem; margin: 0.25rem 0 0.5rem;">ABC University Admissions</h1>
        <p style="color: var(--slate-600); font-size: 0.9rem; margin-bottom: 1.5rem;">
          ABC University is requesting document verification for Undergraduate Admission 2026.
        </p>

        ${ConsentCard({
          requesterName: 'ABC University',
          purpose: 'Undergraduate Admissions Cut-off & Eligibility',
          documents: [
            { name: 'Class 10 Certificate', purpose: 'Age & Matriculation', authority: 'CBSE' },
            { name: 'Class 12 Marksheet', purpose: 'Cut-off Aggregate (>= 60%)', authority: 'CBSE' },
            { name: 'Aadhaar eKYC Assertion', purpose: 'Demographic Match Score', authority: 'UIDAI' },
          ],
        })}
      </div>
    </main>
  `;
}

function ProgressView() {
  return `
    <main id="main" class="page">
      <div class="container narrow-container">
        <div class="card elevated" style="text-align: center;">
          <div style="width: 44px; height: 44px; border: 4px solid var(--blue-700); border-top-color: transparent; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 1rem;"></div>
          <h2 style="color: var(--blue-900); font-size: 1.4rem; margin-bottom: 0.25rem;">Verifying your documents...</h2>
          <p style="color: var(--slate-600); font-size: 0.85rem;">Connecting to official government registries in real-time.</p>

          <div style="text-align: left; margin-top: 1.5rem;">
            ${VerificationTimeline({
              currentStepIndex: state.currentStepIndex,
              steps: [
                { title: 'Connecting to DigiLocker Secure Gateway', desc: 'UIDAI identity session bound.' },
                { title: 'Fetching CBSE Class 12 Verified Records', desc: 'Registry records matched.' },
                { title: 'Running Cut-off & Demographics Engine', desc: 'Validating eligibility predicates.' },
                { title: 'Minting Ed25519 Proof Receipt', desc: 'Signing verifiable JWS token.' },
              ],
            })}
          </div>
        </div>
      </div>
    </main>
  `;
}

function ResultView() {
  return `
    <main id="main" class="page">
      <div class="container narrow-container">
        ${ShareVerificationCard({
          verificationId: 'DIN-VRF-82A91',
          verifierName: 'ABC University Admissions',
          verifiedDate: '23 Aug 2026, 10:30 IST',
          documentsCount: '3 of 3',
        })}
      </div>
    </main>
  `;
}

function InfoView(title, subtitle, content) {
  return `
    <main id="main" class="page">
      <div class="container narrow-container">
        <a href="#/" style="font-size: 0.85rem; font-weight: 700;">← Back to Home</a>
        <h1 style="color: var(--blue-900); font-size: 1.8rem; margin: 0.75rem 0 0.25rem;">${title}</h1>
        <p style="color: var(--slate-600); font-size: 0.9rem; margin-bottom: 1.5rem;">${subtitle}</p>

        <div class="card elevated">
          ${content}
        </div>
      </div>
    </main>
  `;
}

// Router & State Binding
function render() {
  const p = getPath();
  let viewHtml = '';

  if (p === '/') viewHtml = HomeView();
  else if (p === '/sign-in') viewHtml = SignInView();
  else if (p === '/dashboard') viewHtml = DashboardView();
  else if (p === '/verify') viewHtml = VerifyView();
  else if (p === '/progress') viewHtml = ProgressView();
  else if (p === '/result') viewHtml = ResultView();
  else if (p === '/how') viewHtml = InfoView('How DigiIn Works', 'Informed consent & zero raw document sharing', '<p>An accredited organization issues a verification query. The citizen reviews the scope, authenticates via DigiLocker, and grants explicit consent. The system produces an Ed25519-signed verification token.</p>');
  else if (p === '/security') viewHtml = InfoView('Security & Privacy', 'Engineered for least-data disclosure', '<p>Under DPDP Act 2023, DigiIn strictly ensures that third-party requesters receive cryptographic proof assertions rather than unredacted PDF copies.</p>');
  else if (p === '/accessibility') viewHtml = InfoView('Accessibility Statement', 'WCAG 2.1 Level AA Compliance', '<p>DigiIn features high-contrast color tokens (>= 4.5:1), visible keyboard focus rings, semantic landmark elements, and polite ARIA status announcements.</p>');
  else if (p === '/privacy') viewHtml = InfoView('Privacy Policy', 'Sovereign data ownership', '<p>Zero document retention policy. All data remains in citizen-controlled vaults.</p>');
  else if (p === '/terms') viewHtml = InfoView('Terms of Service', 'Government digital public infrastructure', '<p>Governs verifiable credential exchanges between citizens, issuers, and requesting entities.</p>');
  else if (p === '/help') viewHtml = InfoView('Help & Support', 'Diagnostic references', '<p>Every verification generates an immutable diagnostic reference (e.g. <code>DIGIIN-PROD-2026-UX4G</code>) for instant resolution.</p>');
  else viewHtml = InfoView('Page Not Found', '404', '<p>The requested page does not exist. Return to <a href="#/">Home</a>.</p>');

  app.innerHTML = `
    <a class="skip-link" href="#main">Skip to main content</a>
    ${Header()}
    ${viewHtml}
    ${Footer()}
  `;

  bindEvents();
}

function bindEvents() {
  document.querySelector('#mobile-menu-btn')?.addEventListener('click', () => {
    state.menuOpen = !state.menuOpen;
    render();
  });

  document.querySelector('#lang-toggle')?.addEventListener('click', () => {
    state.lang = state.lang === 'EN' ? 'HI' : 'EN';
    render();
  });

  document.querySelector('#form-signin')?.addEventListener('submit', (e) => {
    e.preventDefault();
    navigate('/dashboard');
  });

  const consentCheck = document.querySelector('#consent-check');
  const consentProceed = document.querySelector('#btn-consent-proceed');
  consentCheck?.addEventListener('change', () => {
    if (consentProceed) consentProceed.disabled = !consentCheck.checked;
  });

  consentProceed?.addEventListener('click', () => {
    state.currentStepIndex = 0;
    navigate('/progress');
    
    // Animate timeline
    const t1 = setTimeout(() => { state.currentStepIndex = 1; render(); }, 800);
    const t2 = setTimeout(() => { state.currentStepIndex = 2; render(); }, 1600);
    const t3 = setTimeout(() => { state.currentStepIndex = 3; render(); }, 2400);
    const t4 = setTimeout(() => { navigate('/result'); }, 3200);
  });

  document.querySelector('#btn-copy-id')?.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText('DIN-84K2-19Q7');
      alert('DigiIn ID (DIN-84K2-19Q7) copied to clipboard!');
    } catch {
      alert('DigiIn ID: DIN-84K2-19Q7');
    }
  });

  document.querySelector('#btn-share-proof')?.addEventListener('click', async () => {
    const toast = document.querySelector('#share-toast');
    try {
      await navigator.clipboard.writeText('DigiIn Verification Receipt: DIN-VRF-82A91');
      if (toast) toast.textContent = '✓ Verification Proof Reference copied to clipboard!';
    } catch {
      if (toast) toast.textContent = 'Verification ID: DIN-VRF-82A91';
    }
  });
}

window.addEventListener('hashchange', () => {
  state.menuOpen = false;
  render();
});

render();
