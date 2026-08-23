import { Badge } from './Badge.js';
import { Button } from './Button.js';

/**
 * UX4G Document Card Component (Phase 2)
 */
export function DocumentCard({
  title,
  issuer,
  issueDate,
  status = 'VERIFIED',
  trustLevel = 4,
  onView = null,
}) {
  const statusBadge = status === 'VERIFIED'
    ? Badge({ text: 'Verified', variant: 'success' })
    : status === 'PENDING'
    ? Badge({ text: 'Pending', variant: 'warning' })
    : Badge({ text: 'Not Found', variant: 'danger' });

  const trustTierBadge = Badge({
    text: `Level ${trustLevel} • Gov Verified`,
    variant: 'info',
  });

  return `
    <div class="document-item">
      <div style="flex: 1;">
        <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
          <strong style="color: var(--blue-900); font-size: 1rem;">${title}</strong>
          ${trustTierBadge}
        </div>
        <div class="doc-meta">
          <span>Issued by: <strong>${issuer}</strong></span> • 
          <span>Date: <strong>${issueDate}</strong></span>
        </div>
      </div>
      <div style="display: flex; align-items: center; gap: 0.75rem;">
        ${statusBadge}
        ${Button({ text: 'View Details', variant: 'outline', className: 'btn-sm', href: '#/dashboard' })}
      </div>
    </div>
  `;
}
