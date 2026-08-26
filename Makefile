.PHONY: help dev test lint build openapi docker-up docker-down demo-reset hackathon-gate

help:
	@echo "DigiLocker X (DigiIn) Monorepo Developer Commands:"
	@echo "  make test            - Run all 7 lint, unit, worker, cryptographic, and E2E test suites"
	@echo "  make lint            - Run Ruff format and linter check"
	@echo "  make openapi         - Generate OpenAPI 3.1 schema specs"
	@echo "  make build           - Build frontend production bundles"
	@echo "  make docker-up       - Start PostgreSQL, Redis, API, Worker, and Web in Docker"
	@echo "  make docker-down     - Stop all Docker containers"
	@echo "  make demo-reset      - Reset DB and seed deterministic demo data (DIN-DEMO-001)"
	@echo "  make hackathon-gate  - Run the 12-criteria Builder Brief automated release gate"

test:
	python tests/run_all_tests.py

lint:
	cd services/api && python -m ruff check app/ tests/

openapi:
	python scripts/generate_openapi.py

build:
	cd apps/web && npm run build

docker-up:
	cd infrastructure && docker compose up -d

docker-down:
	cd infrastructure && docker compose down

demo-reset:
	python scripts/reset_db.py
	python scripts/seed_demo_data.py
	@echo ""
	@echo "✓ Demo reset complete"
	@echo "  Citizen:          DIN-DEMO-001"
	@echo "  Scholarship:      Ready"
	@echo "  Credentials:      4"
	@echo "  Institution:      Ready"
	@echo "  Verification Lab: Ready"

hackathon-gate:
	PYTHONPATH=services/api:. python scripts/hackathon_check.py
