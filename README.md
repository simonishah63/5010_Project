# 🌐 Cloud-Native MOGA Optimizer on GKE

This project simulates and optimizes microservice-based authentication using a Multi-Objective Genetic Algorithm (MOGA). It is deployed on **Google Kubernetes Engine (GKE)**, load-tested with **Apache JMeter**, and monitored via **Prometheus** and **Grafana**.

---

## 📋 Prerequisites

Before running the project, ensure you have:

### ✅ Google Cloud Setup

- A GCP project: `${PROJECT_ID}`
- A GKE cluster created in `us-central1` region
- Billing and Container Registry APIs enabled:

```bash
gcloud services enable container.googleapis.com containerregistry.googleapis.com
```

- Docker authenticated to GCR:

```bash
gcloud auth configure-docker
```

### ✅ Tools Installed Locally

| Tool             | Purpose                     |
|------------------|-----------------------------|
| [Docker](https://www.docker.com/)     | Build & push images          |
| [gcloud CLI](https://cloud.google.com/sdk) | Deploy and connect to GKE     |
| kubectl          | Manage Kubernetes resources |
| Apache JMeter    | Load testing                |
| Make             | Automation (via Makefile)   |

---

## 🛠️ Setup & Deployment

### Configure GKE and Connect

```bash
export PROJECT_ID=your-gcp-project-id && gcloud config set project ${PROJECT_ID}
gcloud config set compute/region us-central1
gcloud container clusters get-credentials <your-cluster-name> --zone us-central1-a
```

---

## 🚀 Usage via Makefile

All project operations can be done using this Makefile.

### 🔨 Build Docker Images

```bash
make build-all
```

Or individually:

```bash
make build-auth     # Auth microservice
make build-moga     # MOGA optimizer
```

### 📤 Push Docker Images to Google Container Registry (GCR)

```bash
make push-all
```

Or separately:

```bash
make push-auth
make push-moga
```

### ☸️ Deploy to GKE

Deploy individual services:

```bash
make deploy-auth
make deploy-moga
```

Or deploy all services:

```bash
make deploy-services
```

---

### 📈 Deploy Monitoring Stack

Prometheus + Grafana:

```bash
make deploy-monitoring
```

Or deploy everything (services + monitoring):

```bash
make deploy-all
```

---

### 🧪 Run Apache JMeter Load Test

Make sure your `.jmx` file is in `load-testing/`.

```bash
make load-test
```

---

### 🌐 Get External IPs of Services

```bash
make get-ips
```

Use the returned IPs to access:
- Grafana UI
- Prometheus UI
- Auth and MOGA Optimizer APIs

---

### 🧹 Cleanup All Resources from GKE

```bash
make cleanup
```

This deletes:
- Auth & MOGA deployments
- Prometheus & Grafana
- All services and configmaps

---

## 📊 Monitoring Setup

1. **Grafana Login**  
   Visit Grafana's external IP from `make get-ips`.  
   Default login: `admin / admin`.

2. **Add Prometheus as a Data Source**  
   Use:
   ```
   http://<prometheus-external-ip>:9090
   ```

3. **Import Dashboard**  
   Use dashboard ID `11074` to import a FastAPI monitoring dashboard.

---

## 📁 Project Structure

```
5010_Project/
├── auth-service/           # FastAPI-based Auth microservice
├── moga-optimizer/         # Python-based MOGA optimizer
├── monitoring/             # Prometheus & Grafana configs
├── load-testing/           # JMeter load scripts
└── Makefile                # Automation commands
```