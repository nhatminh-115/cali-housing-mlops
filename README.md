[![MLOps CI Pipeline](https://github.com/nhatminh-115/cali-housing-mlops/actions/workflows/mlops-ci.yml/badge.svg)](https://github.com/nhatminh-115/cali-housing-mlops/actions/workflows/mlops-ci.yml)

# Cali Housing MLOps: Evolution of a Production-Grade Architecture

This repository demonstrates the architectural evolution of an end-to-end Machine Learning Operations (MLOps) pipeline. The project transitions from a monolithic, manual execution script to a standardized, containerized CI/CD/CT architecture deployed on AWS EC2.

The primary objective is to engineer a highly reproducible, automated, and fault-tolerant ML system capable of handling continuous integration, continuous training, and seamless deployment.

---



## Phase 1.0 — Native & Manual Execution (Ad-hoc Deployment)

Initially, the model deployment relied on local development and manual server configuration.
- Model trained locally and artifacts serialized via `joblib`.
- Direct SSH access to the AWS EC2 instance.
- Manual execution of `git pull`, virtual environment activation, and application runtime management.

**Architectural Bottlenecks:**
- **Configuration Drift:** Discrepancies between local and production environments.
- **Lack of Reproducibility:** No version control over the runtime environment.
- **High Operational Friction:** Manual intervention required for every iteration.

---

## Phase 2.0 — Automated CI/CD Integration

To eliminate manual bottlenecks, GitHub Actions was introduced as the orchestration engine.

- **Continuous Integration (CI):** Automated execution of unit tests using `pytest`.
- **Continuous Deployment (CD):** Automated SSH tunneling to pull source code and restart the `systemd` background service.

**Engineering Challenges & Resolutions:**
- **I/O Latency & Missing Artifacts in CI:** The testing environment lacked the serialized parameter matrix $\theta$.
- **Resolution (Hermetic Testing):** Implemented **Dependency Injection** and **Mocking Objects**. Instead of loading the actual model, a inference function was mocked to return a deterministic constant, ensuring the REST API and exception handling could be validated independently of disk I/O.

---

## Phase 3.0 — Containerized MLOps (CI/CD/CT)

The architecture was entirely refactored using **Docker** to encapsulate the application layer, ensuring mathematical and structural immutability.

Instead of transmitting raw source code, the pipeline now executes the following Directed Acyclic Graph (DAG):
1. **Build-time Continuous Training (CT):** The `Dockerfile` enforces the execution of `train.py` within the isolated container. The system autonomously optimizes the loss function $\mathcal{L}(\theta)$ and serializes the optimal weights $\theta^*$ natively.
2. **Serialization Mismatch Resolution:** Eliminated the `STACK_GLOBAL` deserialization error by ensuring the model is both trained and served within the exact same Python interpreter environment (Python 3.9).
3. **Registry Push:** The immutable image is pushed to Docker Hub.
4. **Automated Deployment:** EC2 pulls the latest image and executes the container natively, decoupling the host OS from the application dependencies.

This implementation guarantees absolute environment consistency and zero-downtime deployment.

---

## Infrastructure & System Evolution

### 1. AWS CloudShell Initialization
<img width="2529" height="592" alt="AWS Infrastructure" src="https://github.com/user-attachments/assets/e8387ad5-3a2b-4b4b-acab-1f0161994820" />

### 2. API Inference Validation
<img width="1698" height="215" alt="Feature Input Validation" src="https://github.com/user-attachments/assets/f88dc1ca-0d3a-4fc6-838b-1e92ae3527a8" />

### 3. Pipeline Metrics
**Initial State**                                             
<img width="712" height="87" alt="Initial Manual State" src="https://github.com/user-attachments/assets/08106c52-d8e2-449b-8d2b-2f7635ac0dbc" />

**Intermediate CI/CD Stage**                                         
<img width="712" height="87" alt="CI/CD Integration" src="https://github.com/user-attachments/assets/846bd1ae-7033-4d72-9169-5ab5cbf28ca2" />

**Final Containerized Architecture**                      
<img width="1343" height="964" alt="Dockerized Pipeline" src="https://github.com/user-attachments/assets/26016316-c988-4989-91d8-8c346d297b5b" />

---

## Future Scope (Upcoming Enhancements)

- **Infrastructure as Code (IaC):** Provisioning AWS resources systematically using Terraform.
- **Model Observability:** Integrating Prometheus and Grafana to track computational metrics and mathematically monitor Data Drift (Covariate Shift) using statistical distance metrics such as Kullback-Leibler Divergence: 
  $$D_{KL}(P \parallel Q) = \int p(x) \log \left( \frac{p(x)}{q(x)} \right) dx$$
