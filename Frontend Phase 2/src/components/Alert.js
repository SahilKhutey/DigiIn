/**
 * Accessible Alert Component (Phase 2)
 */
export function Alert({
  type = 'info',
  title = '',
  message = '',
  actionLabel = '',
  actionId = '',
}) {
  const icons = {
    info: 'ℹ️',
    success: '✓',
    warning: '⚠️',
    danger: '✕',
  };

  const icon = icons[type] || 'ℹ️';

  return `
    <div class="alert ${type}" role="${type === 'danger' ? 'alert' : 'status'}" aria-live="polite">
      <div style="display: flex; gap: 0.75rem; align-items: flex-start;">
        <span style="font-size: 1.2rem; flex-shrink: 0;" aria-hidden="true">${icon}</span>
        <div style="flex: 1;">
          ${title ? `<strong style="display: block; font-size: 0.95rem; margin-bottom: 0.25rem;">${title}</strong>` : ''}
          <div style="line-height: 1.5;">${message}</div>
          ${actionLabel ? `<button id="${actionId}" class="btn secondary" style="min-height: 32px; padding: 0.25rem 0.65rem; font-size: 0.8rem; margin-top: 0.5rem;">${actionLabel}</button>` : ''}
        </div>
      </div>
    </div>
  `;
}
