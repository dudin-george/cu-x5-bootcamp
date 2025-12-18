.PHONY: help build push deploy-dev deploy-prod lint clean

# Config
REGISTRY := ghcr.io/dudin-george/cu-x5-bootcamp
TAG ?= $(shell git rev-parse --short HEAD 2>/dev/null || echo "latest")

help:
	@echo "Usage:"
	@echo "  make build        - Build all Docker images"
	@echo "  make push         - Push images to GHCR"
	@echo "  make deploy-dev   - Deploy to dev namespace"
	@echo "  make deploy-prod  - Deploy to prod namespace"
	@echo "  make lint         - Lint code"
	@echo "  make clean        - Clean artifacts"
	@echo ""
	@echo "Variables:"
	@echo "  TAG=$(TAG)"

# ============ Docker ============

build:
	docker build -t $(REGISTRY)/core-api:$(TAG) services/core_api
	docker build -t $(REGISTRY)/candidate-bot:$(TAG) services/candidate_bot
	docker build -t $(REGISTRY)/hm-bot:$(TAG) services/hm_bot
	docker build -t $(REGISTRY)/worker:$(TAG) services/worker
	docker build -t $(REGISTRY)/recruiter-web:$(TAG) services/recruiter_web

push: build
	docker push $(REGISTRY)/core-api:$(TAG)
	docker push $(REGISTRY)/candidate-bot:$(TAG)
	docker push $(REGISTRY)/hm-bot:$(TAG)
	docker push $(REGISTRY)/worker:$(TAG)
	docker push $(REGISTRY)/recruiter-web:$(TAG)

# ============ Helm ============

helm-deps:
	helm dependency update infra/helm/charts/app

deploy-dev: helm-deps
	helm upgrade --install x5-app infra/helm/charts/app \
		--namespace dev --create-namespace \
		-f infra/helm/charts/app/values-dev.yaml \
		--set global.image.tag=$(TAG)

deploy-prod: helm-deps
	helm upgrade --install x5-app infra/helm/charts/app \
		--namespace prod --create-namespace \
		-f infra/helm/charts/app/values-prod.yaml \
		--set global.image.tag=$(TAG)

# ============ Lint ============

lint:
	@echo "Linting Python..."
	cd services/core_api && ruff check src/ || true
	cd services/candidate_bot && ruff check src/ || true
	cd services/hm_bot && ruff check src/ || true
	cd services/worker && ruff check src/ || true
	@echo "Linting Helm..."
	helm lint infra/helm/charts/app || true

# ============ Local Dev ============

run-core-api:
	cd services/core_api && uvicorn src.main:app --reload --port 8001

run-candidate-bot:
	cd services/candidate_bot && uvicorn src.main:app --reload --port 8002

run-hm-bot:
	cd services/hm_bot && uvicorn src.main:app --reload --port 8003

run-worker:
	cd services/worker && python -m src.main

run-frontend:
	cd services/recruiter_web && npm run dev

# ============ Clean ============

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
