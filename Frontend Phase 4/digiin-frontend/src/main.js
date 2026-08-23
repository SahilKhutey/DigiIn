import { Button, Badge, Card, Alert, Field, Status, DocumentCard, Stepper } from './components.js';

const app = document.querySelector('#app');

// Authentication & Session State
const state = {
  mobile: '',
  otp: '',
  otpTimer: 30,
  timerInterval: null,
  otpAttempts: 3,
  otpError: '',
  user: null, // { name: 'Rahul Sharma', mobile: '9876543210', digiinId: 'DIN-84K2-19Q7', ekycVerified: true }
  menu: false,
};

const path = () => location.hash.replace(/^#/, '') || '/';
const go = (p) => location.hash = p;

const Header = () => `
  <div class="top">
    <div class="container top-inner">
      <span>Government of India • भारत सरकार</span>
      <span>UX4G 3.0 Citizen Identity Standard</span>
    </div>
  </div>
  <header class="header">
    <div class="container head">
      <a class="brand" href="#/" aria-label="DigiIn Home">
        <span class="mark">DI</span>
        <span>DigiIn<small>Sovereign Document Verification</small></span>
      </a>
      <nav class="nav" aria-label="Primary">
        <a href="#/about">About</a>
        <a href="#/how">How it works</a>
        <a href="#/citizens">For citizens</a>
        <a href="#/organisations">For organisations</a>
        <a href="#/security">Security</a>
        <a href="#/help">Help</a>
      </nav>
      <div class="actions">
        ${state.user ? `
          <div class="user-badge">
            <span>👤 ${state.user.name}</span>
            <code>${state.user.digiinId}</code>
          </div>
          <button class="btn btn-secondary btn-small" id="btn-logout" type="button">Sign Out</button>
        ` : `
          <a class="btn btn-primary btn-small" href="#/sign-in">Sign In</a>
        `}
      </div>
    </div>
  </header>
`;

const Footer = () => `
  <footer class="footer">
    <div class="container footer-grid">
      <div>
        <strong>DigiIn</strong>
        <p class="muted" style="margin-top:0.5rem">Verify once. Share securely anywhere.</p>
        <p class="muted" style="font-size:0.75rem;margin-top:0.5rem">Built on UX4G 3.0 and DPDP Act 2023 principles.</p>
      </div>
      <div>
        <strong>Service</strong>
        <a href="#/about">About DigiIn</a>
        <a href="#/how">How it works</a>
        <a href="#/citizens">For citizens</a>
        <a href="#/organisations">For organisations</a>
      </div>
      <div>
        <strong>Security & Help</strong>
        <a href="#/security">Security & privacy</a>
        <a href="#/accessibility">Accessibility</a>
        <a href="#/help">Help & FAQ</a>
        <a href="#/contact">Contact Desk</a>
      </div>
    </div>
    <div class="container footer-bottom">
      <span>Digital Personal Data Protection (DPDP) Act 2023 Compliant</span>
      <span><a href="#/privacy">Privacy Policy</a> · <a href="#/terms">Terms of Service</a></span>
    </div>
  </footer>
`;

const Page = ({ eyebrow, title, description, children, narrow = false }) => `
  <main id="main" class="page">
    <div class="container ${narrow ? 'narrow' : ''}">
      ${eyebrow ? `<span class="eyebrow">${eyebrow}</span>` : ''}
      <h1>${title}</h1>
      ${description ? `<p class="lead">${description}</p>` : ''}
      ${children}
    </div>
  </main>
`;

// 1. Mobile Number Entry
function SignIn() {
  return Page({
    eyebrow: 'Citizen Authentication • Step 1 of 2',
    title: 'Sign In with Mobile OTP',
    description: 'Enter your 10-digit mobile number to access your sovereign DigiIn ID and document vault.',
    narrow: true,
    children: `
      ${Alert({
        title: 'Demo Test Account',
        message: 'Enter any valid 10-digit number (e.g. 9876543210). Standard test OTP is 123456.',
        tone: 'info',
      })}
      <form id="form-mobile" class="card form-card">
        ${Field({
          id: 'mobile',
          label: 'Mobile Number',
          prefix: '+91',
          hint: 'We will send a 6-digit one-time password (OTP) via SMS.',
          type: 'tel',
          placeholder: '98765 43210',
          value: state.mobile,
          required: true,
        })}
        ${Button({
          label: 'Get Verification OTP →',
          type: 'submit',
          className: 'block',
          id: 'btn-submit-mobile',
        })}
        <p style="font-size:0.75rem;color:#64748B;margin-top:1rem;text-align:center">
          By signing in, you agree to the DigiIn <a href="#/terms">Terms</a> and <a href="#/privacy">Privacy Notice</a>.
        </p>
      </form>
    `
  });
}

// 2. 6-Digit OTP Verification Screen
function OtpVerification() {
  if (!state.mobile) {
    go('/sign-in');
    return '';
  }

  return Page({
    eyebrow: 'Citizen Authentication • Step 2 of 2',
    title: 'Verify One-Time Password',
    description: `Enter the 6-digit code sent to <strong>+91 ${state.mobile}</strong>.`,
    narrow: true,
    children: `
      <form id="form-otp" class="card form-card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem">
          <span style="font-size:0.8rem;color:#475569">Sending to +91 ${state.mobile}</span>
          <a href="#/sign-in" style="font-size:0.8rem;font-weight:700">Change number</a>
        </div>

        ${state.otpError ? Alert({ title: 'Verification Failed', message: state.otpError, tone: 'error' }) : ''}

        <div class="field">
          <label for="otp-code">Enter 6-Digit OTP</label>
          <div class="field-hint">Test demo code: <code>123456</code></div>
          <input id="otp-code" type="text" maxlength="6" pattern="[0-9]{6}" placeholder="123456" style="font-family:var(--font-mono);font-size:1.5rem;text-align:center;letter-spacing:0.3em;font-weight:800" required autofocus>
        </div>

        <div class="timer-box">
          <span>Resend Code:</span>
          ${state.otpTimer > 0 ? `
            <strong style="color:var(--color-primary)">Wait ${state.otpTimer}s</strong>
          ` : `
            <button id="btn-resend-otp" class="btn btn-secondary btn-small" type="button">Resend OTP</button>
          `}
        </div>

        ${Button({
          label: 'Verify and Continue →',
          type: 'submit',
          className: 'block',
          id: 'btn-verify-otp',
        })}
      </form>
    `
  });
}

// 3. First-Time Citizen Onboarding
function Onboarding() {
  return Page({
    eyebrow: 'Citizen Profile Setup',
    title: 'Welcome to DigiIn',
    description: 'Set up your citizen profile to mint your sovereign DigiIn ID.',
    narrow: true,
    children: `
      <form id="form-onboarding" class="card form-card">
        ${Alert({
          title: 'Identity Linkage',
          message: 'Your mobile number will be linked to your DigiLocker identity under DPDP Act safeguards.',
          tone: 'info',
        })}

        ${Field({
          id: 'full-name',
          label: 'Full Legal Name (as per Aadhaar)',
          placeholder: 'e.g. Rahul Sharma',
          value: 'Rahul Sharma',
          required: true,
        })}

        <div style="padding:1rem;background:#F8FAFC;border:1px solid #CBD5E1;border-radius:10px;margin-bottom:1.5rem">
          <div style="font-size:0.8rem;font-weight:700;color:#092F4F;margin-bottom:0.25rem">Assigned DigiIn ID</div>
          <div style="font-family:var(--font-mono);font-size:1.1rem;font-weight:800;color:#0B5D9B">DIN-84K2-19Q7</div>
          <div style="font-size:0.75rem;color:#64748B;margin-top:0.25rem">Your universal sovereign verification identifier.</div>
        </div>

        ${Button({
          label: 'Complete Setup & Open Dashboard →',
          type: 'submit',
          className: 'block',
          id: 'btn-complete-onboarding',
        })}
      </form>
    `
  });
}

// 4. Authenticated Citizen Dashboard
function Dashboard() {
  if (!state.user) {
    go('/sign-in');
    return '';
  }

  return Page({
    eyebrow: 'Citizen Vault & Identity',
    title: `Welcome back, ${state.user.name}`,
    description: 'Manage your verified sovereign credentials and active institution verifications.',
    children: `
      <div style="display:flex;gap:1rem;margin-bottom:2rem;flex-wrap:wrap">
        <a class="btn btn-primary" href="#/verify">Start Document Verification →</a>
        <button class="btn btn-secondary" id="btn-copy-din" type="button">Copy DigiIn ID (${state.user.digiinId})</button>
      </div>

      <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(300px, 1fr));gap:1.5rem;margin-bottom:2rem">
        <div class="id-card">
          <small>Sovereign Citizen Identifier</small>
          <strong>${state.user.digiinId}</strong>
          <p style="font-size:0.8rem;color:#E2E8F0;margin-bottom:1rem">Share this ID with universities or employers to authorize verification requests.</p>
          <span class="badge badge-success">✓ Aadhaar eKYC Verified</span>
        </div>

        ${Card({
          children: `
            <h3 style="font-size:1rem;font-weight:700;margin-bottom:1rem">Verification Posture</h3>
            <div style="display:flex;justify-content:space-around;text-align:center">
              <div><strong style="font-size:1.5rem;color:#0B5D9B">12</strong><div style="font-size:0.75rem;color:#64748B">Total Docs</div></div>
              <div><strong style="font-size:1.5rem;color:#14743F">9</strong><div style="font-size:0.75rem;color:#64748B">Verified</div></div>
              <div><strong style="font-size:1.5rem;color:#744B00">2</strong><div style="font-size:0.75rem;color:#64748B">Pending</div></div>
            </div>
          `
        })}
      </div>

      <div style="margin-top:2rem">
        <h2 style="font-size:1.25rem;font-weight:800;margin-bottom:1rem">Your Verified Document Vault</h2>
        <div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(280px, 1fr));gap:1rem">
          ${DocumentCard({ title: 'Class 12 Passing Certificate', issuer: 'CBSE', detail: 'Issued 15 May 2025', status: 'verified' })}
          ${DocumentCard({ title: 'Class 10 Passing Certificate', issuer: 'CBSE', detail: 'Issued 20 May 2023', status: 'verified' })}
          ${DocumentCard({ title: 'Aadhaar Identity eKYC', issuer: 'UIDAI', detail: 'Verified at Source', status: 'verified' })}
          ${DocumentCard({ title: 'Driving Licence', issuer: 'MoRTH', detail: 'Awaiting Renewal Verification', status: 'pending' })}
        </div>
      </div>
    `
  });
}

// 5. Verification Flow
function Verify() {
  return Page({
    eyebrow: 'Institutional Verification Request',
    title: 'Verify Documents for ABC University',
    description: 'ABC University has requested admission verification for Class 10 & Class 12 credentials.',
    narrow: true,
    children: `
      ${Stepper({ steps: ['Request', 'Consent', 'Verify', 'Result'], current: 1 })}
      <div class="card">
        <h3 style="font-size:1.1rem;font-weight:700;margin-bottom:0.5rem">Requested Attributes</h3>
        <p style="font-size:0.8rem;color:#475569;margin-bottom:1rem">Only required claims will be shared under zero-knowledge assertion rules.</p>
        <ul style="font-size:0.85rem;color:#092F4F;margin-bottom:1.5rem;list-style:none;padding:0">
          <li style="padding:0.4rem 0;border-bottom:1px solid #E2E8F0">✓ Class 10 Passing Status & Roll Number (CBSE)</li>
          <li style="padding:0.4rem 0;border-bottom:1px solid #E2E8F0">✓ Class 12 Aggregate Percentage &gt;= 60.0% (CBSE)</li>
        </ul>
        <button class="btn btn-primary block" id="btn-grant-consent" type="button">Authorize & Verify Records →</button>
      </div>
    `
  });
}

function Result() {
  return Page({
    eyebrow: 'Verification Result',
    title: 'Documents Verified Successfully',
    description: 'Cryptographic proof token generated and delivered to ABC University.',
    narrow: true,
    children: `
      <div class="card" style="text-align:center">
        <div style="width:3rem;height:3rem;background:#DFF6E8;color:#14743F;border-radius:50%;display:grid;place-items:center;font-size:1.5rem;font-weight:800;margin:0 auto 1rem">✓</div>
        <h3 style="font-size:1.2rem;font-weight:800;color:#092F4F;margin-bottom:0.25rem">Proof Token Issued</h3>
        <p style="font-size:0.8rem;color:#64748B;margin-bottom:1rem">Token Ref: <code>DLV-8F72-A92C</code></p>
        <div class="badge badge-success">✓ 100% Cryptographic Integrity</div>
        <div style="margin-top:1.5rem;display:flex;gap:0.5rem;justify-content:center">
          <a class="btn btn-primary" href="#/dashboard">Go to Dashboard</a>
          <a class="btn btn-secondary" href="#/verify">Start Another</a>
        </div>
      </div>
    `
  });
}

function startOtpTimer() {
  if (state.timerInterval) clearInterval(state.timerInterval);
  state.otpTimer = 30;
  state.timerInterval = setInterval(() => {
    state.otpTimer -= 1;
    if (state.otpTimer <= 0) {
      clearInterval(state.timerInterval);
    }
    const timerElem = document.querySelector('.timer-box strong');
    if (timerElem) {
      if (state.otpTimer > 0) {
        timerElem.textContent = `Wait ${state.otpTimer}s`;
      } else {
        const timerBox = document.querySelector('.timer-box');
        if (timerBox) {
          timerBox.innerHTML = `<span>Resend Code:</span><button id="btn-resend-otp" class="btn btn-secondary btn-small" type="button">Resend OTP</button>`;
          bindEvents();
        }
      }
    }
  }, 1000);
}

function render() {
  const p = path();
  let content = '';

  switch (p) {
    case '/':
    case '/about':
    case '/how':
    case '/citizens':
    case '/organisations':
    case '/security':
    case '/accessibility':
    case '/help':
    case '/contact':
    case '/privacy':
    case '/terms':
      if (p === '/') {
        content = Page({
          eyebrow: 'Digital Public Infrastructure',
          title: 'Verify Once. Share Securely Anywhere.',
          description: 'DigiIn enables sovereign document verification for Indian public services with zero raw document transfers.',
          children: `
            <div style="display:flex;gap:1rem;margin-top:1rem">
              <a class="btn btn-primary" href="#/sign-in">Sign In to Citizen Vault →</a>
              <a class="btn btn-secondary" href="#/verify">Try Verification Flow</a>
            </div>
          `
        });
      } else {
        content = Page({
          eyebrow: 'DigiIn Public Portal',
          title: p.replace('/', '').toUpperCase(),
          description: 'Public service information.',
          children: `<a class="btn btn-primary" href="#/sign-in">Sign In to Citizen Account</a>`
        });
      }
      break;
    case '/sign-in': content = SignIn(); break;
    case '/otp': content = OtpVerification(); break;
    case '/onboarding': content = Onboarding(); break;
    case '/dashboard': content = Dashboard(); break;
    case '/verify': content = Verify(); break;
    case '/result': content = Result(); break;
    default: content = SignIn(); break;
  }

  app.innerHTML = Header() + content + Footer();
  bindEvents();
}

function bindEvents() {
  // Mobile form submission
  const formMobile = document.querySelector('#form-mobile');
  if (formMobile) {
    formMobile.addEventListener('submit', (e) => {
      e.preventDefault();
      const mobileInput = document.querySelector('#mobile');
      const val = mobileInput ? mobileInput.value.replace(/\D/g, '') : '';
      if (val.length === 10) {
        state.mobile = val;
        state.otpError = '';
        startOtpTimer();
        go('/otp');
      } else {
        alert('Please enter a valid 10-digit mobile number.');
      }
    });
  }

  // OTP form submission
  const formOtp = document.querySelector('#form-otp');
  if (formOtp) {
    formOtp.addEventListener('submit', (e) => {
      e.preventDefault();
      const otpInput = document.querySelector('#otp-code');
      const val = otpInput ? otpInput.value.trim() : '';
      if (val === '123456' || val.length === 6) {
        state.otpError = '';
        if (!state.user) {
          go('/onboarding');
        } else {
          go('/dashboard');
        }
      } else {
        state.otpError = 'Invalid OTP code. Please enter 123456 for demo authorization.';
        render();
      }
    });
  }

  // Resend OTP button
  const btnResend = document.querySelector('#btn-resend-otp');
  if (btnResend) {
    btnResend.addEventListener('click', () => {
      startOtpTimer();
      render();
    });
  }

  // Onboarding form submission
  const formOnboarding = document.querySelector('#form-onboarding');
  if (formOnboarding) {
    formOnboarding.addEventListener('submit', (e) => {
      e.preventDefault();
      const nameInput = document.querySelector('#full-name');
      state.user = {
        name: nameInput ? nameInput.value.trim() : 'Rahul Sharma',
        mobile: state.mobile,
        digiinId: 'DIN-84K2-19Q7',
        ekycVerified: true,
      };
      go('/dashboard');
    });
  }

  // Copy DIN button
  const btnCopyDin = document.querySelector('#btn-copy-din');
  if (btnCopyDin) {
    btnCopyDin.addEventListener('click', () => {
      if (state.user && navigator.clipboard) {
        navigator.clipboard.writeText(state.user.digiinId);
        alert('DigiIn ID copied to clipboard: ' + state.user.digiinId);
      }
    });
  }

  // Logout button
  const btnLogout = document.querySelector('#btn-logout');
  if (btnLogout) {
    btnLogout.addEventListener('click', () => {
      state.user = null;
      state.mobile = '';
      state.otp = '';
      go('/sign-in');
    });
  }

  // Grant Consent in Verify flow
  const btnGrantConsent = document.querySelector('#btn-grant-consent');
  if (btnGrantConsent) {
    btnGrantConsent.addEventListener('click', () => {
      btnGrantConsent.textContent = 'Verifying with CBSE Registry...';
      btnGrantConsent.disabled = true;
      setTimeout(() => {
        go('/result');
      }, 1200);
    });
  }
}

window.addEventListener('hashchange', render);
window.addEventListener('load', render);
