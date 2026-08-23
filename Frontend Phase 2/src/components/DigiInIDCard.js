import { Button } from './Button.js';

/**
 * Sovereign DigiIn ID Card Component (Phase 2)
 */
export function DigiInIDCard({
  idNumber = 'DIN-84K2-19Q7',
  holderName = 'Citizen Account',
  status = 'Active & Sovereign',
}) {
  return `
    <div class="digiin-id-card">
      <div class="digiin-id-header">
        <div>
          <span style="font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; opacity: 0.85;">Digital Public Infrastructure</span>
          <strong style="display: block; font-size: 1.1rem;">DigiIn Sovereign ID</strong>
        </div>
        <div style="font-size: 1.5rem;" aria-hidden="true">🇮🇳</div>
      </div>

      <div style="margin: 1.25rem 0;">
        <span style="font-size: 0.75rem; opacity: 0.8;">Universal Verification Identifier</span>
        <span class="digiin-id-number">${idNumber}</span>
      </div>

      <div style="display: flex; justify-content: space-between; align-items: flex-end; border-top: 1px solid rgba(255, 255, 255, 0.2); padding-top: 0.75rem;">
        <div>
          <span style="font-size: 0.7rem; opacity: 0.8; display: block;">Status</span>
          <span style="font-size: 0.82rem; font-weight: 700; color: #86EFAC;">✓ ${status}</span>
        </div>
        <div>
          <button id="btn-copy-id" class="btn secondary" style="min-height: 32px; padding: 0.3rem 0.75rem; font-size: 0.78rem;">
            Copy ID
          </button>
        </div>
      </div>
    </div>
  `;
}
