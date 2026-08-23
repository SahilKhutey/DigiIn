import React from "react";
import { ServicePage } from "../../patterns/ServicePage";
import { Card } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { Alert } from "../../components/ui/Alert";

export const AccessibilityView: React.FC = () => {
  return (
    <ServicePage
      title="Accessibility Statement (WCAG 2.1 Level AA)"
      description="DigiIn is engineered so that every citizen, regardless of device, physical ability, or assistive technology, can complete document verifications without barrier."
      breadcrumbs={[
        { label: "Home", href: "#/" },
        { label: "Accessibility" },
      ]}
    >
      <div className="space-y-6">
        <div className="flex items-center gap-2">
          <Badge variant="success" size="lg">✓ WCAG 2.1 Level AA Baseline</Badge>
          <Badge variant="info" size="lg">UX4G 3.0 Standard</Badge>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card variant="elevated" className="space-y-2">
            <h3 className="text-base font-bold text-[#092F4F] m-0">Full Keyboard Navigation</h3>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              Every action, button, form field, and modal can be navigated using only <code>Tab</code>, <code>Shift+Tab</code>, and <code>Enter</code> without mouse reliance.
            </p>
          </Card>

          <Card variant="elevated" className="space-y-2">
            <h3 className="text-base font-bold text-[#092F4F] m-0">High-Contrast Tokens</h3>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              Color contrast strictly exceeds 4.5:1 for normal body text and 3:1 for large typography and interactive borders.
            </p>
          </Card>

          <Card variant="elevated" className="space-y-2">
            <h3 className="text-base font-bold text-[#092F4F] m-0">Screen Reader Live Regions</h3>
            <p className="text-xs text-slate-600 leading-relaxed m-0">
              Asynchronous verification progress and toast alerts use <code>aria-live="polite"</code> for seamless screen reader announcements.
            </p>
          </Card>
        </div>

        <Alert type="info" title="Skip Navigation Link">
          A dedicated <em>Skip to main content</em> anchor is provided on every page for immediate keyboard access to primary content.
        </Alert>
      </div>
    </ServicePage>
  );
};
