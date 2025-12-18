# X5 Hiring Bootcamp

Kubernetes-ready монорепа для хакатона.

## Архитектура

```
┌─────────────────────────────────────────────────────────┐
│                       CLUSTER                           │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  namespace: infra                                │   │
│  │  • ingress-nginx (LoadBalancer)                 │   │
│  │  • cert-manager (Let's Encrypt)                 │   │
│  └─────────────────────────────────────────────────┘   │
│                          │                              │
│         ┌────────────────┴────────────────┐            │
│         ▼                                 ▼            │
│  ┌─────────────────┐           ┌─────────────────┐    │
│  │ namespace: dev  │           │ namespace: prod │    │
│  │ dev.x5teamintern│           │ x5teamintern.ru │    │
│  └─────────────────┘           └─────────────────┘    │
└─────────────────────────────────────────────────────────┘

Auth: Ory Network (SaaS) → auth.x5teamintern.ru (CNAME)
```

## Сервисы

| Сервис | Описание | Endpoint |
|--------|----------|----------|
| **core-api** | Основной API | `/api/*` |
| **candidate-bot** | Telegram бот кандидатов | `/tg/candidate/{secret}` |
| **hm-bot** | Telegram бот HR | `/tg/hm/{secret}` |
| **worker** | Фоновый воркер | — |
| **recruiter-web** | Веб-интерфейс | `/` |

## DNS записи

| Запись | Тип | Значение |
|--------|-----|----------|
| `x5teamintern.ru` | A | `<LB_IP>` |
| `dev.x5teamintern.ru` | A | `<LB_IP>` |
| `auth.x5teamintern.ru` | CNAME | `<project>.projects.oryapis.com` |

## Quick Start

### 1. Настройка кластера (infra namespace)

```bash
# Создать namespace
kubectl create namespace infra

# Установить ingress-nginx
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace infra \
  --set controller.service.type=LoadBalancer

# Установить cert-manager
helm repo add jetstack https://charts.jetstack.io
helm install cert-manager jetstack/cert-manager \
  --namespace infra \
  --set crds.enabled=true

# Создать ClusterIssuer для Let's Encrypt
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
      - http01:
          ingress:
            class: nginx
EOF

# Получить External IP
kubectl get svc -n infra ingress-nginx-controller
```

### 2. Сборка и деплой

```bash
# Собрать образы
make build TAG=v1.0.0

# Залогиниться в GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Запушить
make push TAG=v1.0.0

# Задеплоить в dev
make deploy-dev TAG=v1.0.0

# Задеплоить в prod
make deploy-prod TAG=v1.0.0
```

### 3. Проверка

```bash
kubectl get pods -n dev
kubectl get pods -n prod
kubectl get ingress -n dev
kubectl get ingress -n prod
```

## GitHub Secrets

| Secret | Описание |
|--------|----------|
| `KUBE_CONFIG` | `base64 -w0 ~/.kube/config` |
| `TELEGRAM_BOT_TOKEN_CANDIDATE` | Токен бота кандидатов |
| `TELEGRAM_BOT_TOKEN_HM` | Токен бота HR |
| `WEBHOOK_SECRET_CANDIDATE` | Секрет webhook кандидатов |
| `WEBHOOK_SECRET_HM` | Секрет webhook HR |

## Структура

```
.
├── .github/workflows/      # CI/CD
│   ├── ci.yml             # Lint + build check
│   ├── build-images.yml   # Build & push to GHCR
│   ├── deploy-dev.yml     # Deploy to dev
│   └── deploy-prod.yml    # Deploy to prod
├── infra/helm/charts/
│   ├── app/               # Umbrella chart
│   ├── core-api/
│   ├── candidate-bot/
│   ├── hm-bot/
│   ├── worker/
│   └── recruiter-web/
├── services/
│   ├── core_api/
│   ├── candidate_bot/
│   ├── hm_bot/
│   ├── worker/
│   └── recruiter_web/
├── Makefile
└── README.md
```

## Локальная разработка

```bash
# Python сервисы
cd services/core_api
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
make run-core-api

# Frontend
cd services/recruiter_web
npm install
npm run dev
```
