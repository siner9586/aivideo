.PHONY: setup dev api web test demo models-list models-wan models-ltx models-cogvideox models-hunyuan
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
	PYTHONPATH=services/api pytest tests -q
demo:
	PYTHONPATH=services/api python -m app.demo
models-list:
	python scripts/download_model_weights.py --list
models-wan:
	python scripts/download_model_weights.py --model wan_t2v_1_3b
models-ltx:
	python scripts/download_model_weights.py --model ltx_video
models-cogvideox:
	python scripts/download_model_weights.py --model cogvideox_5b
models-hunyuan:
	python scripts/download_model_weights.py --model hunyuan_video
