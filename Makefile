.PHONY: sync migrate run stop

HOST=0.0.0.0
PORT=8000

sync:
	@echo "📦 Syncing dependencies..."
	@uv sync

migrate: sync
	@echo "🗄️ Running database migrations..."
	@uv run alembic upgrade head

run: migrate
	@echo "🚀 Starting FastAPI..."
	@uv run uvicorn app.app:app --host $(HOST) --port $(PORT) --reload

stop:
	@pkill -f "uvicorn" || true
	@echo "🛑 FastAPI stopped."