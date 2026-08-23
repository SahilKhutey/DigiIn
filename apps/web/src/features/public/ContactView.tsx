import React, { useState } from "react";
import { FormPage } from "../../patterns/FormPage";
import { FormField } from "../../components/ui/FormField";
import { Input } from "../../components/ui/Input";
import { Select } from "../../components/ui/Select";
import { Textarea } from "../../components/ui/Textarea";
import { Button } from "../../components/ui/Button";
import { Alert } from "../../components/ui/Alert";

export const ContactView: React.FC = () => {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [topic, setTopic] = useState("general");
  const [message, setMessage] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
  };

  return (
    <FormPage
      title="Contact the DigiIn Team"
      description="Submit a support request, report a verification discrepancy, or inquire about institutional API onboarding."
      backHref="#/help"
      backLabel="Back to Help & FAQ"
    >
      {submitted ? (
        <div className="space-y-4 text-center py-6">
          <div className="w-14 h-14 rounded-full bg-[#DFF6E8] text-[#14743F] text-2xl font-bold flex items-center justify-center mx-auto" aria-hidden="true">
            ✓
          </div>
          <h3 className="text-xl font-bold text-[#092F4F] m-0">Inquiry Received</h3>
          <p className="text-xs text-slate-600 max-w-sm mx-auto">
            Your inquiry reference <code>TKT-{Date.now().toString(36).toUpperCase()}</code> has been logged. Our engineering desk will respond within 24 hours.
          </p>
          <Button variant="secondary" size="sm" onClick={() => setSubmitted(false)}>
            Send Another Message
          </Button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <FormField label="Your Full Name" htmlFor="contact-name" required>
            <Input
              id="contact-name"
              placeholder="e.g. Rahul Sharma"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </FormField>

          <FormField label="Official Email Address" htmlFor="contact-email" required>
            <Input
              id="contact-email"
              type="email"
              placeholder="e.g. rahul@example.gov.in"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </FormField>

          <FormField label="Inquiry Category" htmlFor="contact-topic" required>
            <Select
              id="contact-topic"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              options={[
                { value: "general", label: "General Information & Questions" },
                { value: "citizen_support", label: "Citizen Verification Assistance" },
                { value: "institution_api", label: "University / Verifier API Onboarding" },
                { value: "accessibility", label: "Accessibility & Assistive Tech Feedback" },
              ]}
            />
          </FormField>

          <FormField label="Detailed Message" htmlFor="contact-message" required>
            <Textarea
              id="contact-message"
              rows={4}
              placeholder="Please describe your query or report a verification issue..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              required
            />
          </FormField>

          <div className="pt-2">
            <Button variant="primary" size="lg" type="submit" fullWidth>
              Submit Support Message →
            </Button>
          </div>
        </form>
      )}
    </FormPage>
  );
};
