/**
 * Verification Timeline / Progress Pipeline Component (Phase 2)
 */
export function VerificationTimeline({ steps = [], currentStepIndex = 0 }) {
  const stepsMarkup = steps.map((step, idx) => {
    const isCompleted = idx < currentStepIndex;
    const isActive = idx === currentStepIndex;
    const stateClass = isCompleted ? 'completed' : (isActive ? 'active' : 'pending');
    const icon = isCompleted ? '✓' : (idx + 1);

    return `
      <div class="timeline-step ${stateClass}">
        <div class="timeline-icon" aria-hidden="true">${icon}</div>
        <div>
          <strong style="color: var(--blue-900); font-size: 0.92rem; display: block;">${step.title}</strong>
          <span style="font-size: 0.78rem; color: var(--slate-600);">${step.desc}</span>
        </div>
      </div>
    `;
  }).join('');

  return `
    <div class="timeline" aria-label="Verification Progress" aria-live="polite">
      ${stepsMarkup}
    </div>
  `;
}
