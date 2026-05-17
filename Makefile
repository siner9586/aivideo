.PHONY: setup dev api web test demo
setup:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
	cd apps/web && npm install || true
api:
	PYTHONPATH=services/api uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
web:
	cd apps/web && npm run dev
# Run API and web in two terminals for development.
dev:
	@echo "Run 'make api' and 'make web' in two terminals."
test:
	PYTHONPATH=services/api pytest services/api/tests -q
demo:
	PYTHONPATH=services/api python -m app.demo
