# DigiIn Documentation

This folder records the current product, architecture, security and delivery decisions for the DigiIn prototype.

## Reading order

| Document | Purpose |
| --- | --- |
| [Product scope](product-scope.md) | Defines what DigiIn is, what it is not, and the first citizen problem being solved. |
| [Foundation architecture](foundation-architecture.md) | Describes the implemented modular monolith, modules, APIs and integration boundaries. |
| [Architecture](architecture.md) | Summarises system structure, data flow and workspace layout. |
| [Website workflow](website-workflow.md) | Maps the citizen-facing web journey, states, recovery actions and trust labels. |
| [Implementation plan](implementation-plan.md) | Tracks milestones, backlog and acceptance criteria. |
| [Security baseline](security.md) | Captures privacy, data minimisation and future production controls. |

## Current implementation status

DigiIn currently ships as a synthetic, local-first prototype:

- React/Vite citizen web app under `apps/web`.
- FastAPI modular service under `services/api`.
- Versioned diagnostic contract under `packages/contracts`.
- Fictional example data under `data/examples`.

No live government system, identity credential, Aadhaar number, OTP, password, or official document file is processed by this prototype.
