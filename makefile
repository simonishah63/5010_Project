# ---- Makefile for cloud-native-moga-optimizer ----

PROJECT_ID ?= finalproject-5010-467518
REGION ?= us-central1

TAG ?= $(shell date +%Y%m%d%H%M%S)
AUTH_IMAGE = gcr.io/$(PROJECT_ID)/auth-service
MOGA_IMAGE = gcr.io/$(PROJECT_ID)/moga-optimizer

# ---- Build & Push Docker Images ----

build-auth:
	cd auth-service && docker buildx build --no-cache --platform linux/amd64 -t $(AUTH_IMAGE) .

push-auth:
	docker push $(AUTH_IMAGE)

build-moga:
	cd moga-optimizer && docker buildx build --no-cache --platform linux/amd64 -t $(MOGA_IMAGE) .

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

deploy-jmeter: 
	kubectl apply -f load-testing/deployment.yaml
	kubectl apply -f load-testing/service.yaml

deploy-monitoring:
	kubectl apply -f monitoring/prometheus-deployment.yaml
	kubectl apply -f monitoring/prometheus-service.yaml
	kubectl apply -f monitoring/grafana-deployment.yaml
	kubectl apply -f monitoring/grafana-service.yaml

deploy-all: deploy-services deploy-monitoring deploy-jmeter

# ---- Kubernetes ReDeployment ----

redeploy-auth: build-auth push-auth deploy-auth
redeploy-moga: build-moga push-moga deploy-moga
redeploy-all: redeploy-auth redeploy-moga

# ---- Load Test ----

# load-test:
# 	cd load-testing && jmeter -n -t moga-load-script.jmx -l results.csv -j jmeter.log

# ---- Load Test (Run JMeter in Cluster) ----

load-test:
	@JMETER_POD=$$(kubectl get pod -l app=jmeter -o jsonpath="{.items[0].metadata.name}") && \
	echo "Copying JMX script into pod: $$JMETER_POD" && \
	kubectl cp load-testing/moga-load-script.jmx default/$$JMETER_POD:/moga-load-script.jmx && \
	kubectl exec -it $$JMETER_POD -- mkdir -p /jmeter-results && \
	kubectl exec -it $$JMETER_POD -- jmeter -n -t /moga-load-script.jmx -l /jmeter-results/results.csv -j /jmeter-results/jmeter.log && \
	echo "Copying JMeter results from pod to local machine..." && \
	kubectl cp default/$$JMETER_POD:/jmeter-results/results.csv ./load-testing/results.csv && \
	kubectl cp default/$$JMETER_POD:/jmeter-results/jmeter.log ./load-testing/jmeter.log

# ---- Generate PDF Plot Report ----

POD_NAME := $(shell kubectl get pods -l app=moga-optimizer -o jsonpath="{.items[0].metadata.name}")
POD_NAME_JMETER := $(shell kubectl get pod -l app=jmeter -o jsonpath="{.items[0].metadata.name}")
copy-csv:
	kubectl cp $(POD_NAME):/app/plot_data/convergence_all.csv ./moga-optimizer/plot_data/convergence_all.csv
	kubectl cp $(POD_NAME):/app/plot_data/final_generation_all.csv ./moga-optimizer/plot_data/final_generation_all.csv
	kubectl cp ${POD_NAME_JMETER}:/jmeter-results/results.csv ./moga-optimizer/plot_data/results.csv

generate-plot: copy-csv
	docker run --rm \
		-v $(shell pwd)/moga-optimizer:/app/ \
		python:3.10-slim bash -c "pip install matplotlib pandas && python /app/app/generate_plots.py"

# ---- Cleanup ----

cleanup:
	kubectl delete deployment auth-service moga-optimizer prometheus grafana jmeter || true
	kubectl delete svc auth-service moga-optimizer prometheus grafana jmeter || true
	kubectl delete configmap prometheus-config || true

# ---- Info ----

get-ips:
	kubectl get svc grafana prometheus auth-service moga-optimizer jmeter

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
	@echo "  deploy-jmeter      Deploy JMeter pod for in-cluster testing"
	@echo "  deploy-monitoring  Deploy Prometheus + Grafana"
	@echo "  deploy-all         Deploy everything (services + monitoring)"
	@echo "  load-test          Run Apache JMeter load test inside cluster"
	@echo "  generate-plot      Generate performance plot as PDF"
	@echo "  cleanup            Remove all K8s deployments/services/configmaps"
	@echo "  get-ips            Show external IPs of all services"