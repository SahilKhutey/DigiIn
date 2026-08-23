/**
 * UX4G Card Component (Phase 2)
 */
export function Card({
  title = '',
  description = '',
  badge = '',
  content = '',
  footer = '',
  variant = 'default',
  className = '',
  id = '',
}) {
  const headerMarkup = (title || badge)
    ? `<div class="card-header">
        <div>
          ${title ? `<h3 class="card-title">${title}</h3>` : ''}
          ${description ? `<p class="card-desc">${description}</p>` : ''}
        </div>
        ${badge ? `<div>${badge}</div>` : ''}
      </div>`
    : '';

  const footerMarkup = footer ? `<div class="card-footer" style="margin-top: 1rem; padding-top: 0.75rem; border-top: 1px solid var(--slate-200);">${footer}</div>` : '';

  return `
    <div id="${id}" class="card ${variant} ${className}">
      ${headerMarkup}
      <div class="card-body">
        ${content}
      </div>
      ${footerMarkup}
    </div>
  `;
}
