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
    ACTIVE: { label: 'Active', tone: 'success', icon: '✓' },
    VALID: { label: 'Valid', tone: 'success', icon: '✓' },
    EXPIRED: { label: 'Expired', tone: 'warning', icon: '!' },
    REVOKED: { label: 'Revoked', tone: 'danger', icon: '✕' },
    INVALID: { label: 'Invalid', tone: 'danger', icon: '✕' }
  };
  const s = map[status] || { label: status, tone: 'neutral', icon: '•' };
  return `<span class="status-pill status-${s.tone}"><span class="status-icon" aria-hidden="true">${s.icon}</span> ${s.label}</span>`;
};

export const OrganisationIdentity = ({ name, category = 'Verified Organisation', requestId = 'VR-82A91' }) => {
  return `<div class="requester"><div class="org-mark">${name.split(' ').map(w => w[0]).slice(0,2).join('')}</div><div class="org-info"><strong>${name}</strong><span>${category}</span><small class="request-id-badge">Request ID: ${requestId}</small></div><span class="verified-org">✓ Verified</span></div>`;
};

export const Stepper = ({ steps, current }) => {
  return `<ol class="stepper" aria-label="Progress">${steps.map((s, i) => `<li class="${i === current ? 'current' : i < current ? 'complete' : ''}" aria-current="${i === current ? 'step' : 'false'}"><span class="step-num">${i < current ? '✓' : i + 1}</span><span>${s}</span></li>`).join('')}</ol>`;
};

export const VerificationProofCard = ({ proofId, verificationId, organisation, purpose, expiresAt }) => {
  return `
    <div class="form-card text-center">
      <div class="result-icon">✓</div>
      ${Badge({ label: 'Verification Complete', tone: 'success', icon: '✓' })}
      <h2 style="margin: 0.75rem 0 0.25rem;">Verification proof ready</h2>
      <p class="muted" style="margin-bottom: 1.5rem;">Your proof has been created and can now be shared with relying organisations.</p>

      <div class="request-summary" style="text-align: left;">
        <div><small>Proof ID</small><strong style="font-family: var(--font-mono); color: var(--color-primary-900);">${proofId}</strong></div>
        <div><small>Verification ID</small><strong style="font-family: var(--font-mono);">${verificationId}</strong></div>
        <div><small>Verified for</small><strong>${organisation}</strong></div>
        <div><small>Purpose</small><strong>${purpose}</strong></div>
        <div><small>Valid until</small><strong>${expiresAt}</strong></div>
      </div>

      <div class="actions" style="margin-top: 1.5rem;">
        <a class="btn btn-primary" href="#/proof/${proofId}">View proof →</a>
        <a class="btn btn-secondary" href="#/proof/${proofId}/share">Share</a>
        <a class="btn btn-secondary" href="#/proof/${proofId}/qr">Show QR</a>
      </div>
    </div>
  `;
};

export const ProofDetails = ({ proof }) => {
  return `
    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--color-border-subtle); padding-bottom: 1rem;">
        <div>
          <span class="eyebrow">Verification Proof</span>
          <h2 style="margin: 0.35rem 0 0;">${proof.organisation}</h2>
        </div>
        ${Status({ status: proof.status })}
      </div>

      <div class="request-summary" style="margin: 1.5rem 0;">
        <div><small>Purpose</small><strong>${proof.purpose}</strong></div>
        <div><small>Proof ID</small><strong style="font-family: var(--font-mono);">${proof.proofId}</strong></div>
        <div><small>Verification ID</small><strong style="font-family: var(--font-mono);">${proof.verificationId}</strong></div>
        <div><small>Issued on</small><strong>${proof.issuedAt}</strong></div>
        <div><small>Expires on</small><strong>${proof.expiresAt}</strong></div>
      </div>

      <h3>Documents verified</h3>
      <div class="verification-list">
        ${proof.verifiedDocuments.map(d => `
          <div>
            <span class="status-pill status-success"><span class="status-icon">✓</span> Verified</span>
            <span>${d}</span>
            <small>Central Board of Secondary Education</small>
          </div>
        `).join('')}
      </div>

      <div class="actions" style="margin-top: 2rem;">
        <a class="btn btn-primary" href="#/proof/${proof.proofId}/share">Share proof</a>
        <a class="btn btn-secondary" href="#/proof/${proof.proofId}/qr">Show QR</a>
        ${proof.status === 'ACTIVE' ? `
          <a class="btn btn-secondary text-danger" href="#/proof/${proof.proofId}/revoke" style="color: var(--color-error-700);">Revoke proof</a>
        ` : ''}
      </div>
    </div>
  `;
};

export const ShareProof = ({ proofId, shareUrl, expiresAt }) => {
  return `
    <div class="share-card">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
          <span class="eyebrow">Secure Share Link</span>
          <h2 style="margin: 0.4rem 0 0;">Share this verification</h2>
        </div>
        ${Badge({ label: 'Active Proof', tone: 'success', icon: '✓' })}
      </div>

      <p class="muted" style="margin-top: 0.5rem; font-size: 0.9rem;">
        Anyone with this link can check whether the verification proof is currently valid.
      </p>

      <div class="share-id-box">
        <small class="muted" style="display: block; font-size: 0.75rem; text-transform: uppercase;">Proof ID</small>
        <strong>${proofId}</strong>
      </div>

      <label style="font-size: 0.82rem; font-weight: 700; color: var(--color-text-secondary); display: block; margin-top: 1rem;">
        Secure verification link
      </label>
      <div class="share-link-box">
        <input type="text" value="${shareUrl}" readonly id="share-link-input" />
        <button id="copy-share-link" class="btn btn-primary btn-small" type="button">Copy link</button>
      </div>
      <p id="share-toast" class="muted" style="font-size: 0.8rem; text-align: center; margin: 0.25rem 0 0;" aria-live="polite"></p>

      <div class="actions" style="margin-top: 1.5rem;">
        <button id="native-share-btn" class="btn btn-secondary" type="button">Share</button>
        <a class="btn btn-secondary" href="#/proof/${proofId}/qr">Show QR</a>
      </div>
    </div>
  `;
};

export const QRCodePanel = ({ proofId, qrSvg }) => {
  return `
    <div class="form-card text-center">
      <h2 style="margin: 0 0 0.5rem;">Scan to verify this DigiIn proof</h2>
      <p class="muted" style="font-size: 0.88rem;">Encodes the verification endpoint rather than raw documents or credentials.</p>

      <div class="qr-svg-container">
        ${qrSvg}
      </div>

      <div style="font-family: var(--font-mono); font-size: 1.1rem; font-weight: 800; color: var(--color-primary-900); margin-bottom: 1.5rem;">
        ${proofId}
      </div>

      <div class="actions centered">
        <a class="btn btn-primary" href="#/proof/${proofId}/share">Share link</a>
        <a class="btn btn-secondary" href="#/proof/${proofId}">Back to proof</a>
      </div>
    </div>
  `;
};

export const ProofValidationResult = ({ result }) => {
  if (result.status === 'VALID') {
    return `
      <div class="result-card">
        <div class="result-icon">✓</div>
        ${Badge({ label: 'Verification Confirmed', tone: 'success', icon: '✓' })}
        <h2 style="margin: 0.75rem 0 0.25rem;">Verification confirmed</h2>
        <p class="muted">${result.proof.organisation}</p>

        <div class="request-summary" style="text-align: left; margin: 1.5rem 0;">
          <div><small>Purpose</small><strong>${result.proof.purpose}</strong></div>
          <div><small>Documents verified</small><strong>${result.proof.verifiedDocuments.length} documents verified</strong></div>
          <div><small>Issued</small><strong>${result.proof.issuedAt}</strong></div>
          <div><small>Valid until</small><strong>${result.proof.expiresAt}</strong></div>
          <div><small>Proof ID</small><strong style="font-family: var(--font-mono);">${result.proof.proofId}</strong></div>
          <div><small>Verification ID</small><strong style="font-family: var(--font-mono);">${result.proof.verificationId}</strong></div>
        </div>

        <div class="verification-list">
          ${result.proof.verifiedDocuments.map(d => `
            <div>
              <span class="status-pill status-success"><span class="status-icon">✓</span> Verified</span>
              <span>${d}</span>
              <small>Central Board of Secondary Education</small>
            </div>
          `).join('')}
        </div>

        ${Alert({
          title: 'Privacy Guarantee',
          message: 'The organisation receives the verification result, not unrestricted document access.',
          tone: 'info'
        })}

        <div class="actions centered" style="margin-top: 20px;">
          <a class="btn btn-primary" href="#/verify-proof">Verify another proof</a>
        </div>
      </div>
    `;
  }

  if (result.status === 'EXPIRED') {
    return `
      <div class="result-card">
        <div class="result-icon" style="background: #FFF0CC; color: #744B00;">!</div>
        ${Badge({ label: 'Proof Expired', tone: 'warning', icon: '!' })}
        <h2 style="margin: 0.75rem 0 0.25rem;">Verification proof expired</h2>
        <p class="muted">This proof was valid until ${result.proof.expiresAt}.</p>

        <div class="alert alert-warning" style="text-align: left; margin: 1.5rem 0;">
          <strong>Notice:</strong>
          <p>A new verification may be required. The organisation should request a new verification from the citizen.</p>
        </div>

        <div class="actions centered">
          <a class="btn btn-primary" href="#/verify-proof">Verify another proof</a>
        </div>
      </div>
    `;
  }

  if (result.status === 'REVOKED') {
    return `
      <div class="result-card">
        <div class="result-icon" style="background: #FDE8E8; color: #9B1C1C;">✕</div>
        ${Badge({ label: 'Proof Revoked', tone: 'danger', icon: '✕' })}
        <h2 style="margin: 0.75rem 0 0.25rem;">Verification proof revoked</h2>
        <p class="muted">This proof was previously valid but is no longer active.</p>

        <div class="alert alert-error" style="text-align: left; margin: 1.5rem 0;">
          <strong>Status Details:</strong>
          <p>The citizen has revoked this verification proof. It can no longer be validated.</p>
        </div>

        <div class="actions centered">
          <a class="btn btn-primary" href="#/verify-proof">Verify another proof</a>
        </div>
      </div>
    `;
  }

  if (result.status === 'SERVICE_UNAVAILABLE') {
    return `
      <div class="result-card">
        <div class="result-icon" style="background: #FFF0CC; color: #744B00;">⚡</div>
        ${Badge({ label: 'Service Unavailable', tone: 'warning', icon: '!' })}
        <h2 style="margin: 0.75rem 0 0.25rem;">We couldn't reach DigiIn</h2>
        <p class="muted">No conclusion can be made about the verification at this time.</p>

        <div class="actions centered" style="margin-top: 1.5rem;">
          <a class="btn btn-primary" href="#/verify-proof">Try again</a>
        </div>
      </div>
    `;
  }

  // INVALID
  return `
    <div class="result-card">
      <div class="result-icon" style="background: #FDE8E8; color: #9B1C1C;">✕</div>
      ${Badge({ label: 'Invalid Proof', tone: 'danger', icon: '✕' })}
      <h2 style="margin: 0.75rem 0 0.25rem;">Verification could not be confirmed</h2>
      <p class="muted">This proof is not recognised by DigiIn.</p>

      <div class="alert alert-error" style="text-align: left; margin: 1.5rem 0;">
        <strong>Possible reasons:</strong>
        <ul style="margin: 0.5rem 0 0; padding-left: 1.25rem; font-size: 0.85rem;">
          <li>The proof ID is incorrect</li>
          <li>The proof no longer exists</li>
          <li>The proof was altered</li>
        </ul>
      </div>

      <div class="actions centered">
        <a class="btn btn-primary" href="#/verify-proof">Try again</a>
      </div>
    </div>
  `;
};

export const VerificationHistory = ({ proofs = [] }) => {
  return `
    <div class="verification-list" style="margin-top: 1rem;">
      ${proofs.map(p => `
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 1rem; border-bottom: 1px solid var(--color-border-subtle);">
          <div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
              <strong>${p.organisation}</strong>
              ${Status({ status: p.status })}
            </div>
            <p class="muted" style="margin: 0.2rem 0; font-size: 0.82rem;">${p.purpose} • ID: <code style="font-family: var(--font-mono); font-weight: 700;">${p.proofId}</code></p>
            <small class="muted">Issued: ${p.issuedAt} • Expires: ${p.expiresAt}</small>
          </div>
          <div style="display: flex; gap: 0.5rem;">
            <a class="btn btn-secondary btn-small" href="#/proof/${p.proofId}">View</a>
            ${p.status === 'ACTIVE' ? `
              <a class="btn btn-secondary btn-small" href="#/proof/${p.proofId}/share">Share</a>
              <a class="btn btn-secondary btn-small text-danger" href="#/proof/${p.proofId}/revoke" style="color: var(--color-error-700);">Revoke</a>
            ` : ''}
          </div>
        </div>
      `).join('')}
    </div>
  `;
};
