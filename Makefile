.PHONY: help api candidate-bot hm-bot worker web install

help:
	@echo "Локальный запуск сервисов:"
	@echo "  make api           - Core API (port 8001)"
	@echo "  make candidate-bot - Telegram бот кандидатов (port 8002)"
	@echo "  make hm-bot        - Telegram бот HR (port 8003)"
	@echo "  make worker        - Background worker"
	@echo "  make web           - Frontend (port 5173)"
	@echo ""
	@echo "  make install       - Установить зависимости всех сервисов"

# ============ Сервисы ============

api:
	cd services/core_api && uvicorn src.main:app --reload --port 8001

candidate-bot:
	cd services/candidate_bot && uvicorn src.main:app --reload --port 8002

hm-bot:
	cd services/hm_bot && uvicorn src.main:app --reload --port 8003

worker:
	cd services/worker && python -m src.main

web:
	cd services/recruiter_web && npm run dev

# ============ Setup ============

install:
	cd services/core_api && pip install -r requirements.txt
	cd services/candidate_bot && pip install -r requirements.txt
	cd services/hm_bot && pip install -r requirements.txt
	cd services/worker && pip install -r requirements.txt
	cd services/recruiter_web && npm install
