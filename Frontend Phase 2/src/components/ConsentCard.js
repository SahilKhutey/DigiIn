import { Badge } from './Badge.js';
import { Button } from './Button.js';
import { Alert } from './Alert.js';

/**
 * Informed Purpose-Bound Consent Card (Phase 2)
 */
export function ConsentCard({
  requesterName = 'ABC University',
  purpose = 'Undergraduate Admissions 2026',
  documents = [],
}) {
  const docRows = documents.map(doc => `
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem; background: var(--white); border: 1px solid var(--slate-200); border-radius: var(--radius-sm); margin-bottom: 0.5rem;">
      <div>
        <strong style="color: var(--blue-900); font-size: 0.92rem; display: block;">${doc.name}</strong>
        <span style="font-size: 0.78rem; color: var(--slate-600);">${doc.purpose}</span>
      </div>
      <div>
        ${Badge({ text: doc.authority, variant: 'info' })}
      </div>
    </div>
  `).join('');

  return `
    <div class="card elevated">
      <div class="card-header">
        <div>
          <span class="badge warning">Informed Consent</span>
          <h2 class="card-title" style="margin-top: 0.4rem;">Authorize Document Sharing</h2>
          <p class="card-desc">Review what <strong>${requesterName}</strong> is requesting before granting permission.</p>
        </div>
      </div>

      <div style="margin: 1rem 0;">
        <h4 style="font-size: 0.82rem; text-transform: uppercase; color: var(--slate-500); margin: 0 0 0.5rem;">Requested Documents (${documents.length})</h4>
        ${docRows}
      </div>

      ${Alert({
        type: 'info',
        title: 'Zero-Knowledge Minimum Disclosure',
        message: 'Only cryptographically signed assertions will be exchanged. Unrelated personal data is never shared.',
      })}

      <div style="margin-top: 1.25rem; padding: 1rem; background: var(--blue-100); border-radius: var(--radius-sm); border: 1px solid #BAE6FD;">
        <label style="display: flex; gap: 0.75rem; align-items: flex-start; cursor: pointer;">
          <input type="checkbox" id="consent-check" style="margin-top: 0.2rem; width: 18px; height: 18px; accent-color: var(--blue-700);">
          <span style="font-size: 0.85rem; color: var(--blue-900); line-height: 1.45;">
            <strong>I give explicit consent</strong> for DigiIn to verify the documents above with official government issuers and share proof assertions with ${requesterName}.
          </span>
        </label>
      </div>

      <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1.5rem; pt-3; border-top: 1px solid var(--slate-200);">
        ${Button({ text: '← Back', variant: 'secondary', href: '#/verify' })}
        ${Button({ text: 'Continue & Authorize →', variant: 'primary', id: 'btn-consent-proceed', disabled: true })}
      </div>
    </div>
  `;
}
