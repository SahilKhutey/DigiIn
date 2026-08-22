import type { Scenario } from "../../types";

type ScenarioPickerProps = {
  scenarios: Scenario[];
  selectedScenarioId: string;
  onSelectScenario: (id: string) => void;
};

export function ScenarioPicker({
  scenarios,
  selectedScenarioId,
  onSelectScenario,
}: ScenarioPickerProps) {
  const currentScenario = scenarios.find((s) => s.id === selectedScenarioId);

  return (
    <section className="scenario-picker" aria-labelledby="scenario-title">
      <div>
        <p className="eyebrow">2. DIAGNOSE THE JOURNEY</p>
        <h2 id="scenario-title">What happened?</h2>
      </div>
      <label>
        Fictional diagnostic case
        <select
          value={selectedScenarioId}
          onChange={(e) => onSelectScenario(e.target.value)}
          aria-label="Diagnostic scenario selection"
        >
          {scenarios.map((scenario) => (
            <option key={scenario.id} value={scenario.id}>
              {scenario.title}
            </option>
          ))}
        </select>
      </label>
      <p>{currentScenario?.description}</p>
    </section>
  );
}
