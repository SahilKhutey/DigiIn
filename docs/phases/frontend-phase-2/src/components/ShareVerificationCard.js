import { Badge } from './Badge.js';
import { Button } from './Button.js';

/**
 * Shareable Verification Proof Receipt Component (Phase 2)
 */
export function ShareVerificationCard({
  verificationId = 'DIN-VRF-82A91',
  verifierName = 'ABC University',
  verifiedDate = '23 Aug 2026, 10:30 IST',
  documentsCount = '2 of 2',
}) {
  return `
    <div class="card elevated" style="text-align: center;">
      <div style="width: 64px; height: 64px; border-radius: 50%; background: var(--green-100); color: var(--green-700); display: grid; place-items: center; font-size: 2rem; font-weight: 900; margin: 0 auto 1rem;">
        ✓
      </div>

      <span class="badge success" style="margin-bottom: 0.5rem;">Level 4 • Source Verified</span>
      <h2 class="card-title" style="font-size: 1.5rem; margin-bottom: 0.25rem;">Verification Complete</h2>
      <p class="card-desc">${documentsCount} requested documents were successfully matched with official registries.</p>

      <div style="background: var(--blue-50); border: 1px solid var(--slate-200); border-radius: var(--radius-sm); padding: 1rem; margin: 1.25rem 0; text-align: left;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; font-size: 0.85rem;">
          <span style="color: var(--slate-600);">Verification Reference:</span>
          <strong style="font-family: var(--font-mono); color: var(--blue-900); font-size: 0.95rem;">${verificationId}</strong>
        </div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; font-size: 0.85rem;">
          <span style="color: var(--slate-600);">Verified For:</span>
          <strong style="color: var(--blue-900);">${verifierName}</strong>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.85rem;">
          <span style="color: var(--slate-600);">Timestamp:</span>
          <strong style="color: var(--blue-900);">${verifiedDate}</strong>
        </div>
      </div>

      <div style="display: flex; gap: 0.75rem; justify-content: center; flex-wrap: wrap;">
        ${Button({ text: 'Go to Citizen Dashboard', variant: 'primary', href: '#/dashboard' })}
        ${Button({ text: 'Share Proof Reference', variant: 'secondary', id: 'btn-share-proof' })}
      </div>
      <p id="share-toast" style="font-size: 0.8rem; color: var(--green-700); margin-top: 0.75rem; min-height: 1.2rem;" aria-live="polite"></p>
    </div>
  `;
}
