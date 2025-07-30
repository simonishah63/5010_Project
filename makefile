# ---- Makefile for cloud-native-moga-optimizer ----

PROJECT_ID ?= finalproject-5010-467518
REGION ?= us-central1

AUTH_IMAGE = gcr.io/$(PROJECT_ID)/auth-service:latest
MOGA_IMAGE = gcr.io/$(PROJECT_ID)/moga-optimizer:latest

# ---- Build & Push Docker Images ----

build-auth:
	cd auth-service && docker buildx build --platform linux/amd64 -t $(AUTH_IMAGE) .

push-auth:
	docker push $(AUTH_IMAGE)

build-moga:
	cd moga-optimizer && docker buildx build --platform linux/amd64 -t $(MOGA_IMAGE) .

push-moga:
	docker push $(MOGA_IMAGE)

build-all: build-auth build-moga
push-all: push-auth push-moga

# ---- Kubernetes Deployment ----

deploy-auth:
	kubectl apply -f auth-service/k8s/deployment.yaml
	kubectl apply -f auth-service/k8s/service.yaml

deploy-moga:
	kubectl apply -f moga-optimizer/k8s/deployment.yaml
	kubectl apply -f moga-optimizer/k8s/service.yaml

deploy-services: deploy-auth deploy-moga

deploy-monitoring:
	kubectl apply -f monitoring/prometheus-deployment.yaml
	kubectl apply -f monitoring/prometheus-service.yaml
	kubectl apply -f monitoring/grafana-deployment.yaml
	kubectl apply -f monitoring/grafana-service.yaml

deploy-all: deploy-services deploy-monitoring

# ---- Load Test ----

load-test:
	cd load-testing && jmeter -n -t moga-load-script.jmx -l results.csv -j jmeter.log

# ---- Cleanup ----

cleanup:
	kubectl delete deployment auth-service moga-optimizer prometheus grafana || true
	kubectl delete svc auth-service moga-optimizer prometheus grafana || true
	kubectl delete configmap prometheus-config || true

# ---- Info ----

get-ips:
	kubectl get svc grafana prometheus auth-service moga-optimizer

# ---- Help ----

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  build-auth         Build Docker image for auth-service"
	@echo "  build-moga         Build Docker image for moga-optimizer"
	@echo "  push-auth          Push auth-service image to GCR"
	@echo "  push-moga          Push moga-optimizer image to GCR"
	@echo "  build-all          Build both images"
	@echo "  push-all           Push both images"
	@echo "  deploy-auth        Deploy auth
	@echo "  deploy-moga        Deploy moga-optimizer to GKE"
	@echo "  deploy-services    Deploy all services"
	@echo "  deploy-monitoring  Deploy Prometheus + Grafana"
	@echo "  deploy-all         Deploy everything (services + monitoring)"
	@echo "  load-test          Run Apache JMeter test"
	@echo "  cleanup            Remove all K8s deployments/services/configmaps"
	@echo "  get-ips            Show external IPs of all services"