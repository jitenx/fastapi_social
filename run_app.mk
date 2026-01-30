.PHONY: run fastapi streamlit stop

FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
STREAMLIT_PORT=8501

run:
	@echo "Starting FastAPI..."
	@uv run uvicorn app.app:app --host $(FASTAPI_HOST) --port $(FASTAPI_PORT) --reload & \
	echo $$! > .fastapi.pid
	@echo "Starting Streamlit..."
	@uv run streamlit run streamlit_app/app.py --server.port $(STREAMLIT_PORT) & \
	echo $$! > .streamlit.pid
	@wait


stop:
	@echo "Stopping FastAPI..."
	@kill $$(cat .fastapi.pid) 2>/dev/null || true
	@echo "Stopping Streamlit..."
	@kill $$(cat .streamlit.pid) 2>/dev/null || true
	@pkill -f "streamlit.web.cli" || true
	@rm -f .fastapi.pid .streamlit.pid

