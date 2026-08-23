import { Button, Badge, Card, Alert, Field, Status, DocumentCard, Stepper } from './components.js';
import { digiLockerService } from './services/digilocker/digilockerService.js';
import { verificationService } from './services/verificationService.js';

const app = document.querySelector('#app');
const state = {
  menu: false,
  lang: 'EN',
  user: null,
  consent: false,
  verification: 'idle',
  request: {
    id: 'VR-82A91',
    organisation: 'ABC University',
    purpose: 'Admission verification',
    documents: [
      { id: 'doc-10', title: 'Class 10 Certificate', issuer: 'CBSE', purpose: 'Eligibility verification' },
      { id: 'doc-12', title: 'Class 12 Certificate', issuer: 'CBSE', purpose: 'Eligibility verification' }
    ],
    expiresInHours: 24
  },
  connection: 'not_connected',
  retrieved: [],
  verificationResult: null,
  verificationProgress: { stage: 'ready', label: 'Ready for verification' }
};

const path = () => location.hash.replace(/^#/, '') || '/';
const go = (p) => { location.hash = p; };
const currentRequest = () => state.request;

const Header = () => `<div class="top"><div class="container top-inner"><span>Government service experience foundation</span><span>Accessible • Secure • Citizen-first</span></div></div><header class="header"><div class="container head"><a class="brand" href="#/" aria-label="DigiIn home"><span class="mark">DI</span><span>DigiIn<small>Digital document verification</small></span></a><nav class="nav" aria-label="Primary"><a href="#/">Home</a><a href="#/how">How it works</a><a href="#/security">Security</a><a href="#/help">Help</a></nav><div class="actions"><button class="btn btn-secondary btn-small" id="lang" type="button" aria-label="Change language">${state.lang === 'EN' ? 'हिन्दी' : 'English'}</button>${state.user ? '<a class="btn btn-primary btn-small" href="#/dashboard">Dashboard</a>' : '<a class="btn btn-primary btn-small" href="#/sign-in">Sign in</a>'}<button class="menu" id="menu" type="button" aria-label="Open menu" aria-expanded="${state.menu}">☰</button></div></div>${state.menu ? `<nav class="mobile-nav" aria-label="Mobile navigation"><a href="#/">Home</a><a href="#/how">How it works</a><a href="#/security">Security</a><a href="#/help">Help</a>${state.user ? '<a href="#/dashboard">Dashboard</a>' : '<a href="#/sign-in">Sign in</a>'}</nav>` : ''}</header>`;

const Footer = () => `<footer class="footer"><div class="container footer-grid"><div><strong>DigiIn</strong><p class="muted">Verify once. Share securely.</p></div><div><strong>Service</strong><a href="#/how">How it works</a><a href="#/security">Security</a><a href="#/help">Help</a></div><div><strong>Information</strong><a href="#/accessibility">Accessibility</a><a href="#/privacy">Privacy</a><a href="#/terms">Terms</a></div></div><div class="container footer-bottom"><small>Prototype foundation • No real documents are processed in demo mode.</small></div></footer>`;

const Page = ({ eyebrow, title, description, children, narrow = false }) => `<main id="main" class="page"><div class="container ${narrow ? 'narrow' : ''}">${eyebrow ? `<span class="eyebrow">${eyebrow}</span>` : ''}<h1>${title}</h1>${description ? `<p class="lead muted">${description}</p>` : ''}${children}</div></main>`;

function Home() { return `<main id="main"><section class="hero"><div class="container hero-grid"><div><span class="eyebrow">Secure document verification</span><h1>Verify once.<br><span>Share securely.</span></h1><p>DigiIn helps citizens use verified digital documents across government and trusted services without repeatedly submitting the same documents.</p><div class="actions hero-actions">${Button({ label: 'Start verification', href: '#/verify/request', icon: '→' })}${Button({ label: 'How DigiIn works', href: '#/how', variant: 'secondary' })}</div><div class="trust-row"><span>✓ Consent-led</span><span>✓ Accessible</span><span>✓ Privacy-first</span></div></div>${Card({ className: 'hero-card', children: `<div class="shield">✓</div><h2>Consent-led by design</h2><p class="muted">You stay in control of what is shared, with whom, and for what purpose.</p><ul class="list"><li>Requesting organisation is clearly identified.</li><li>Only requested documents are shared.</li><li>Every verification has a clear status.</li></ul>` })}</div></section><section class="section"><div class="container"><div class="section-heading"><div><span class="eyebrow">Simple by design</span><h2>A simpler verification journey</h2></div><p class="muted">Designed around the citizen, not the paperwork.</p></div><div class="grid3">${['Connect once', 'Give clear consent', 'Share proof'].map((x, i) => Card({ className: 'feature-card', children: `<div class="icon">0${i + 1}</div><h3>${x}</h3><p class="muted">${['Keep trusted digital documents available in one place.', 'See who needs what and why before anything is shared.', 'Share a verification result instead of repeated document copies.'][i]}</p>` })).join('')}</div></div></section><section class="section section-alt"><div class="container"><span class="eyebrow">The journey</span><h2>How verification works</h2>${Stepper({ steps: ['Request', 'Consent', 'Verify', 'Result'], current: 3 })}</div></section></main>`; }

function SignIn() { return Page({ eyebrow: 'Citizen account', title: 'Sign in to DigiIn', description: 'Use your registered mobile number to continue.', narrow: true, children: `${Alert({ title: 'Demo mode', message: 'Any valid 10-digit mobile number is accepted. No real identity data is processed.', tone: 'info' })}<form id="signin" class="form-card">${Field({ id: 'mobile', label: 'Mobile number', hint: 'Enter the 10-digit number registered with your account.', type: 'tel', placeholder: '10-digit mobile number', required: true })}${Button({ label: 'Continue', type: 'submit', className: 'block' })}<p class="form-footer">By continuing, you agree to the DigiIn <a href="#/terms">terms</a> and <a href="#/privacy">privacy notice</a>.</p></form>` }); }

function Dashboard() { return Page({ eyebrow: 'Citizen account', title: 'Welcome back', description: 'Manage your verified documents and active requests.', children: `<div class="actions"><a class="btn btn-primary" href="#/verify/request">New verification <span aria-hidden="true">→</span></a></div><div class="stats"><div class="stat-card"><strong>12</strong><span>Documents</span></div><div class="stat-card"><strong>9</strong><span>Verified</span></div><div class="stat-card"><strong>2</strong><span>Pending</span></div></div><div class="dashboard-grid">${Card({ children: `<div class="card-heading"><div><span class="eyebrow">Your identity</span><h2>DigiIn ID</h2></div>${Badge({ label: 'Active', tone: 'success', icon: '✓' })}</div><div class="id-card"><small>DigiIn ID</small><strong>DIN-84K2-19Q7</strong><p>Use this ID with authorised services to start a verification request.</p><button class="btn btn-secondary btn-small" id="copy-id" type="button">Copy ID</button></div>` })}${Card({ children: `<div class="card-heading"><div><span class="eyebrow">Activity</span><h2>Recent activity</h2></div></div><ul class="activity"><li><span class="activity-dot success"></span><div><strong>Class 12 verified</strong><small>Today • CBSE</small></div></li><li><span class="activity-dot info"></span><div><strong>University request received</strong><small>Yesterday</small></div></li></ul>` })}</div><section class="documents-section"><div class="section-heading"><div><span class="eyebrow">Document vault</span><h2>Your documents</h2></div></div><div class="document-grid">${DocumentCard({ title: 'Class 12 Certificate', issuer: 'CBSE', detail: 'Issued 15 May 2025', status: 'verified' })}${DocumentCard({ title: 'Class 10 Certificate', issuer: 'CBSE', detail: 'Issued 20 May 2023', status: 'verified' })}${DocumentCard({ title: 'Identity document', issuer: 'Connected source', detail: 'Awaiting verification', status: 'pending' })}</div></section>` }); }

function OrganisationCard() { const r = currentRequest(); return `<div class="requester"><div class="org-mark">AU</div><div><strong>${r.organisation}</strong><span>Verified organisation • ${r.purpose}</span></div><span class="verified-org">✓ Verified</span></div>`; }

function RequestedDocuments() { return `<div class="requested-list">${currentRequest().documents.map((d) => `<div class="requested requested-rich"><div class="document-mini-icon" aria-hidden="true">▤</div><div><strong>${d.title}</strong><small>Issued by ${d.issuer} • ${d.purpose}</small></div><span class="required-label">Required</span></div>`).join('')}</div>`; }

function VerifyRequest() { return Page({ eyebrow: 'Verification request', title: 'Review the request', description: 'Before connecting a trusted document source, understand who is requesting your information and why.', narrow: true, children: `${Stepper({ steps: ['Request', 'Consent', 'Verify', 'Result'], current: 0 })}<div class="form-card request-card">${OrganisationCard()}<div class="request-summary"><div><small>Purpose</small><strong>${currentRequest().purpose}</strong></div><div><small>Request ID</small><strong>${currentRequest().id}</strong></div><div><small>Consent validity</small><strong>${currentRequest().expiresInHours} hours</strong></div></div><h2>Documents requested</h2>${RequestedDocuments()}${Alert({ title: 'You stay in control.', message: 'DigiIn will not request unrelated documents. You can review the exact consent terms before anything is shared.', tone: 'info' })}<div class="actions request-actions"><a class="btn btn-primary" href="#/verify/review">Review and continue <span aria-hidden="true">→</span></a><a class="btn btn-secondary" href="#/dashboard">Cancel</a></div></div>` }); }

function VerifyReview() { return Page({ eyebrow: 'Step 1 of 4 • Review', title: 'Review what will be shared', description: 'This request is limited to the documents and purpose shown below.', narrow: true, children: `${Stepper({ steps: ['Request', 'Consent', 'Verify', 'Result'], current: 0 })}<div class="form-card">${OrganisationCard()}<div class="review-block"><span class="eyebrow">Purpose</span><h2>${currentRequest().purpose}</h2><p class="muted">The organisation will use the verification result only for this stated purpose.</p></div><h2>Requested documents</h2>${RequestedDocuments()}${Alert({ title: 'What will happen next?', message: 'You will connect to DigiLocker, authenticate there, and then return to DigiIn to review and give explicit consent.', tone: 'info' })}<a class="btn btn-primary block" href="#/verify/digilocker">Continue to DigiLocker <span aria-hidden="true">→</span></a><a class="text-action" href="#/verify/request">← Back to request</a></div>` }); }

function DigiLockerConnect() { return Page({ eyebrow: 'Step 2 of 4 • Trusted source', title: 'Connect DigiLocker', description: 'DigiIn needs access to the requested documents from your DigiLocker account.', narrow: true, children: `${Stepper({ steps: ['Request', 'Consent', 'Verify', 'Result'], current: 1 })}<div class="form-card external-card"><div class="external-service-logo">DL</div><h2>Connect to DigiLocker</h2><p class="muted">You will be redirected to DigiLocker to authenticate. DigiIn does not ask for or store your DigiLocker password.</p><div class="security-points"><div>✓ Authentication happens with DigiLocker</div><div>✓ Only this verification request is in scope</div><div>✓ Nothing is shared without your consent</div></div><div id="connection-status" aria-live="polite"></div><button id="connect-digilocker" class="btn btn-primary block" type="button">Continue to DigiLocker <span aria-hidden="true">→</span></button><a class="text-action" href="#/verify/review">← Back to review</a></div>` }); }

function Consent() { return Page({ eyebrow: 'Step 3 of 4 • Consent', title: 'Review and give consent', description: 'Give permission only if the request matches what you intend to verify.', narrow: true, children: `${Stepper({ steps: ['Request', 'Consent', 'Verify', 'Result'], current: 1 })}<div class="form-card consent-card">${OrganisationCard()}<div class="consent-section"><span class="eyebrow">What will be shared</span>${RequestedDocuments()}</div><div class="consent-section"><span class="eyebrow">Why</span><h2>${currentRequest().purpose}</h2><p class="muted">The documents will be checked against their issuing sources to produce a verification result.</p></div>${Alert({ title: 'What will not happen', message: 'Other documents in your DigiLocker account will not be requested as part of this verification.', tone: 'success' })}<div class="consent-expiry"><strong>Consent validity</strong><span>This request expires in ${currentRequest().expiresInHours} hours.</span></div><label class="check-field consent-check"><input id="consent" type="checkbox"><span>I understand what is being requested and consent to this verification.</span></label><button id="give-consent" class="btn btn-primary block" type="button" disabled>Give consent and retrieve documents <span aria-hidden="true">→</span></button><a class="text-action" href="#/verify/digilocker">← Back</a></div>` }); }

function Retrieving() { return Page({ eyebrow: 'Step 3 of 4 • Retrieval', title: 'Retrieving your documents', description: 'We are retrieving only the documents you approved for this request.', narrow: true, children: `${Stepper({ steps: ['Request', 'Consent', 'Verify', 'Result'], current: 2 })}<div class="form-card retrieval-card"><div class="progress-ring" aria-hidden="true">●</div><div id="retrieval-status" aria-live="polite"><h2>Connecting securely…</h2><p class="muted">Please keep this page open.</p></div><ol class="process-list"><li class="active"><span>1</span><div><strong>Permission confirmed</strong><small>Your consent has been recorded.</small></div></li><li id="retrieve-step"><span>2</span><div><strong>Retrieve requested documents</strong><small>Getting the two documents in this request.</small></div></li><li id="prepare-step"><span>3</span><div><strong>Prepare verification</strong><small>Documents will be ready for the verification service.</small></div></li></ol></div>` }); }

function VerifyCheck() { return Page({ eyebrow: 'Step 4 • Verification', title: 'Ready to verify', description: 'Review the final verification scope before DigiIn checks the retrieved documents.', narrow: true, children: `${Stepper({ steps: ['Request', 'Consent', 'Verify', 'Result'], current: 2 })}<div class="form-card">${OrganisationCard()}<div class="review-block"><span class="eyebrow">Purpose</span><h2>${currentRequest().purpose}</h2><p class="muted">The retrieved documents will be checked against trusted verification data.</p></div><h2>Documents</h2>${state.retrieved.map((d) => `<div class="requested requested-rich"><div class="document-mini-icon" aria-hidden="true">▤</div><div><strong>${d.title}</strong><small>${d.issuer} • Ready</small></div>${Status({ status: 'retrieving' })}</div>`).join('')}<button id="begin-verification" class="btn btn-primary block" type="button">Start verification <span aria-hidden="true">→</span></button></div>` }); }

function VerifyProgress() { const p=state.verificationProgress; return Page({ eyebrow: 'Step 4 • Verification', title: 'Verification in progress', description: 'DigiIn is checking each requested document against trusted verification data.', narrow: true, children: `${Stepper({ steps: ['Request', 'Consent', 'Verify', 'Result'], current: 2 })}<div class="form-card retrieval-card"><div class="progress-ring" aria-hidden="true">●</div><div aria-live="polite"><h2>${p.label}</h2><p class="muted">Please keep this page open while verification is completed.</p></div><ol class="process-list verification-process"><li class="${['started','integrity','issuer','details'].includes(p.stage)?'active':''}"><span>1</span><div><strong>Documents received</strong><small>Retrieved with your consent.</small></div></li><li class="${['issuer','details','decision','completed'].includes(p.stage)?'active':''}"><span>2</span><div><strong>Integrity and issuer checks</strong><small>Checking document and issuing authority information.</small></div></li><li class="${['details','decision','completed'].includes(p.stage)?'active':''}"><span>3</span><div><strong>Match document details</strong><small>Comparing required details with trusted records.</small></div></li><li class="${['decision','completed'].includes(p.stage)?'active':''}"><span>4</span><div><strong>Prepare result</strong><small>Generating the verification reference.</small></div></li></ol></div>` }); }

function VerifyDocument({ id }) { const doc=(state.verificationResult?.documents||[]).find(d=>d.id===id); if(!doc) return Info('Document verification details', ['Document not found', 'Return to the verification result to view available documents.']); return Page({ eyebrow: 'Verification detail', title: doc.title, description: 'A transparent view of the checks used for this verification result.', narrow: true, children: `<div class="form-card"><div class="card-heading"><div><span class="eyebrow">${doc.issuer}</span><h2>${doc.title}</h2></div>${Status({ status: doc.status })}</div><div class="verification-checks">${doc.checks.map(c=>`<div class="verification-check"><span class="check-icon">✓</span><div><strong>${c.label}</strong><small>${c.message}</small></div></div>`).join('')}</div><a class="btn btn-primary block" href="#/verify/result">Back to result</a></div>` }); }

function VerificationResult() { const r=state.verificationResult; if(!r) return Page({ eyebrow:'Verification', title:'No result yet', description:'Complete verification first.', narrow:true, children:'<a class="btn btn-primary" href="#/verify/documents">Return to documents</a>' }); const tone=r.status==='verified'?'success':r.status==='partial'?'warning':'error'; const icon=r.status==='verified'?'✓':r.status==='partial'?'!':'×'; const label=r.status==='verified'?'Verified':r.status==='partial'?'Partially verified':'Verification failed'; return Page({ eyebrow:'Step 4 of 4 • Verification result', title:'Verification result', description:'Review the overall decision and the result for each requested document.', narrow:true, children:`<div class="result-card"><div class="result-icon result-${r.status}">${icon}</div>${Badge({label,tone,icon})}<div class="result-summary"><strong>${r.verified} of ${r.total}</strong><span>documents verified</span></div><div class="verification-list">${r.documents.map(d=>`<div><span>${Status({status:d.status})}</span><span><strong>${d.title}</strong><small>${d.issuer}</small></span><a class="link-button" href="#/verify/document/${d.id}">View details →</a></div>`).join('')}</div><div class="verification-id"><small>Verification ID</small><strong>${r.id}</strong><button id="copy-verification" class="btn btn-secondary btn-small" type="button">Copy ID</button><p id="verification-copy-msg" class="muted" aria-live="polite"></p></div><div class="verification-meta"><span>Purpose</span><strong>${currentRequest().purpose}</strong></div><div class="actions centered"><a class="btn btn-primary" href="#/dashboard">Go to dashboard</a><a class="btn btn-secondary" href="#/verify/request">Start another</a></div></div>` }); }

function DocumentsReady() { return Page({ eyebrow: 'Step 3 of 4 • Documents ready', title: 'Documents retrieved', description: `${state.retrieved.length} requested documents are ready for verification.`, narrow: true, children: `${Stepper({ steps: ['Request', 'Consent', 'Verify', 'Result'], current: 2 })}<div class="form-card"><div class="ready-summary"><span class="ready-icon">✓</span><div><h2>Ready for verification</h2><p class="muted">Only the documents approved in your consent are available to the verification step.</p></div></div><div class="document-grid single">${state.retrieved.map((d) => DocumentCard({ title: d.title, issuer: d.issuer, detail: 'Retrieved from DigiLocker • Ready for verification', status: 'retrieving' })).join('')}</div>${Alert({ title: 'Privacy note', message: 'DigiIn is using these documents only for the verification request you approved.', tone: 'info' })}<button id="start-verification" class="btn btn-primary block" type="button">Start verification <span aria-hidden="true">→</span></button></div>` }); }

function Result() { return Page({ eyebrow: 'Step 4 of 4 • Verification result', title: 'Verification complete', description: '2 of 2 requested documents were successfully verified.', narrow: true, children: `<div class="result-card"><div class="result-icon">✓</div>${Badge({ label: 'Verified', tone: 'success', icon: '✓' })}<div class="result-summary"><strong>2 of 2</strong><span>documents verified</span></div><div class="verification-list"><div>${Status({ status: 'verified' })}<span>Class 10 Certificate</span><small>CBSE</small></div><div>${Status({ status: 'verified' })}<span>Class 12 Certificate</span><small>CBSE</small></div></div><div class="verification-id"><small>Verification ID</small><strong>DIN-VRF-82A91</strong><button id="share" class="btn btn-secondary btn-small" type="button">Copy ID</button></div><p id="sharemsg" class="muted" aria-live="polite"></p><div class="actions centered"><a class="btn btn-primary" href="#/dashboard">Go to dashboard</a><a class="btn btn-secondary" href="#/verify/request">Start another</a></div></div>` }); }

const Info = (title, text, eyebrow = 'Information') => Page({ eyebrow, title, description: text[1], narrow: true, children: Card({ children: `<h2>${text[0]}</h2><p class="muted">${text[2] || 'This information is part of the DigiIn foundation build.'}</p>` }) });

function render() {
  const p = path();
  let c;
  if (p === '/') c = Home();
  else if (p === '/sign-in') c = SignIn();
  else if (p === '/dashboard') c = Dashboard();
  else if (p === '/verify' || p === '/verify/request') c = VerifyRequest();
  else if (p === '/verify/review') c = VerifyReview();
  else if (p === '/verify/digilocker') c = DigiLockerConnect();
  else if (p === '/verify/consent') c = Consent();
  else if (p === '/verify/retrieving') c = Retrieving();
  else if (p === '/verify/documents') c = DocumentsReady();
  else if (p === '/verify/check') c = VerifyCheck();
  else if (p === '/verify/progress') c = VerifyProgress();
  else if (p.startsWith('/verify/document/')) c = VerifyDocument({ id: p.split('/').pop() });
  else if (p === '/verify/result') c = VerificationResult();
  else if (p === '/result') c = Result();
  else if (p === '/how') c = Info('How DigiIn works', ['A consent-first verification journey', 'An organisation requests only the documents it needs. You review the purpose, connect your trusted source, and approve the request. DigiIn then produces a verification result.']);
  else if (p === '/security') c = Info('Security & privacy', ['Built around least-data sharing', 'The interface makes the requesting organisation, purpose, requested documents, consent state and verification result visible.']);
  else if (p === '/help') c = Info('Help', ['Need help?', 'This foundation uses simulated verification. Production integrations will provide real service status and recovery actions.']);
  else if (p === '/accessibility') c = Info('Accessibility', ['Accessible by default', 'Keyboard navigation, visible focus, semantic landmarks, live status regions, responsive layouts and reduced-motion support are built into the foundation.']);
  else if (p === '/privacy') c = Info('Privacy', ['Your data, your control', 'Production privacy notices and consent records will be connected during backend integration.']);
  else if (p === '/terms') c = Info('Terms of service', ['Hackathon foundation', 'This build contains demonstration content only. Production legal terms will be added before deployment.']);
  else c = Info('Page not found', ['The page does not exist', 'Return to the DigiIn home page.']);
  app.innerHTML = '<a class="skip" href="#main">Skip to main content</a>' + Header() + c + Footer();
  bind();
  if (p === '/verify/retrieving') setTimeout(startRetrieval, 0);
}

function bind() {
  document.querySelector('#menu')?.addEventListener('click', () => { state.menu = !state.menu; render(); });
  document.querySelector('#lang')?.addEventListener('click', () => { state.lang = state.lang === 'EN' ? 'HI' : 'EN'; render(); });
  document.querySelector('#signin')?.addEventListener('submit', (e) => { e.preventDefault(); state.user = { mobile: document.querySelector('#mobile').value }; go('/dashboard'); });
  document.querySelector('#copy-id')?.addEventListener('click', async (e) => { try { await navigator.clipboard.writeText('DIN-84K2-19Q7'); e.currentTarget.textContent = 'Copied ✓'; } catch { e.currentTarget.textContent = 'DIN-84K2-19Q7'; } });

  const connect = document.querySelector('#connect-digilocker');
  connect?.addEventListener('click', async () => {
    const status = document.querySelector('#connection-status');
    connect.disabled = true;
    connect.textContent = 'Connecting securely…';
    state.connection = 'connecting';
    status.innerHTML = Alert({ message: 'Opening DigiLocker authentication…', tone: 'info' });
    try {
      await digiLockerService.connect();
      state.connection = 'authenticating';
      status.innerHTML = Alert({ message: 'DigiLocker authentication complete in demo mode.', tone: 'success' });
      connect.textContent = 'Continue to consent →';
      connect.disabled = false;
      connect.onclick = () => go('/verify/consent');
    } catch {
      state.connection = 'failed';
      connect.disabled = false;
      connect.textContent = 'Try again';
      status.innerHTML = Alert({ title: 'We could not connect to DigiLocker', message: 'No documents were shared. Try again to continue.', tone: 'error' });
    }
  });

  const consent = document.querySelector('#consent');
  const giveConsent = document.querySelector('#give-consent');
  consent?.addEventListener('change', () => { state.consent = consent.checked; giveConsent.disabled = !consent.checked; });
  giveConsent?.addEventListener('click', async () => {
    if (!state.consent) return;
    giveConsent.disabled = true;
    giveConsent.textContent = 'Recording consent…';
    await digiLockerService.getConsentRequest(currentRequest().id);
    go('/verify/retrieving');
  });

  document.querySelector('#start-verification')?.addEventListener('click', () => go('/verify/check'));
  document.querySelector('#begin-verification')?.addEventListener('click', async () => { state.verificationProgress = { stage: 'started', label: 'Starting verification…' }; go('/verify/progress'); const result = await verificationService.verify(state.retrieved, (progress) => { state.verificationProgress = progress; }); state.verificationResult = result; go('/verify/result'); });
  document.querySelector('#copy-verification')?.addEventListener('click', async (e) => { const msg=document.querySelector('#verification-copy-msg'); try { await navigator.clipboard.writeText(state.verificationResult.id); e.currentTarget.textContent='Copied ✓'; msg.textContent='Verification ID copied. Share it only with the authorised organisation.'; } catch { msg.textContent=`Verification ID: ${state.verificationResult.id}`; } });
  document.querySelector('#share')?.addEventListener('click', async (e) => { const m = document.querySelector('#sharemsg'); try { await navigator.clipboard.writeText('DigiIn Verification ID: DIN-VRF-82A91'); e.currentTarget.textContent = 'Copied ✓'; m.textContent = 'Verification ID copied. Share it only with the authorised organisation.'; } catch { m.textContent = 'Verification ID: DIN-VRF-82A91'; } });
}

async function startRetrieval() {
  const status = document.querySelector('#retrieval-status');
  const retrieveStep = document.querySelector('#retrieve-step');
  const prepareStep = document.querySelector('#prepare-step');
  if (!status) return;
  await new Promise((r) => setTimeout(r, 700));
  status.innerHTML = '<h2>Retrieving requested documents…</h2><p class="muted">DigiLocker is returning only the documents in your consent.</p>';
  retrieveStep?.classList.add('active');
  state.retrieved = await digiLockerService.getDocuments();
  await new Promise((r) => setTimeout(r, 500));
  status.innerHTML = '<h2>Documents ready</h2><p class="muted">Your consented documents are ready for verification.</p>';
  prepareStep?.classList.add('active');
  setTimeout(() => go('/verify/documents'), 700);
}

window.addEventListener('hashchange', () => { state.menu = false; render(); });
render();
