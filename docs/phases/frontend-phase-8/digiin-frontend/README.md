# DigiIn Frontend — Phase 8: Organisation Portal & Request Management

UX4G-aligned frontend foundation for DigiIn's **Organisation Portal & Verification Request Management System**.

## Phase 8 Overview

Phase 8 builds the complete institutional side of the DigiIn two-sided ecosystem:
1. **Organisation Authentication & Session**: Dedicated access for verified relying parties (`ORG-84K2-19Q7`).
2. **Organisation Dashboard**: KPI metrics (`18 Requests`, `11 Verified`, `4 Pending`, `3 Expired`) and quick actions.
3. **5-Step Request Wizard (`/organisation/requests/new`)**:
   - Step 1: Citizen Identification (`DIN-7K4P-92M8`).
   - Step 2: Verification Purpose selection.
   - Step 3: Document selection with justification.
   - Step 4: Validity duration selection.
   - Step 5: Review & Creation $\rightarrow$ Mints `VR-82A91`.
4. **Request Management (`/organisation/requests`)**: Filterable table by `All`, `Pending`, `Verified`, `Expired`, `Cancelled`.
5. **Integrated Proof Verifier (`/organisation/verify-proof`)**: Inspect and validate proof tokens directly within the workspace.
6. **Audit History & Profile**: Institutional transaction logs and public key registry info.

## Run Locally

```bash
python -m http.server 4180
```

Open `http://localhost:4180`.
