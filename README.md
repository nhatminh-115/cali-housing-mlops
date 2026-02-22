[![MLOps CI Pipeline](https://github.com/nhatminh-115/cali-housing-mlops/actions/workflows/mlops-ci.yml/badge.svg)](https://github.com/nhatminh-115/cali-housing-mlops/actions/workflows/mlops-ci.yml)
[![Continuous Training (CT) Pipeline](https://github.com/nhatminh-115/cali-housing-mlops/actions/workflows/mlops-ct.yml/badge.svg)](https://github.com/nhatminh-115/cali-housing-mlops/actions/workflows/mlops-ct.yml)

# Cali Housing MLOps: From Manual to GitOps Architecture

This repository tracks the step-by-step evolution of an MLOps pipeline. The goal is to transform a locally run machine learning model into a fully automated, containerized, and self-provisioning system on AWS.

<img width="4407" height="3109" alt="MLOps Pipeline" src="https://github.com/user-attachments/assets/1561f69e-d3b7-4835-82b2-d106804170be" />


---

## Phase 1.0 - Manual Execution (The Baseline)
What I did:
* Coded the ML model and Flask API on my local machine.
* Pushed the source code to GitHub.
* Logged into the AWS Console and manually clicked through to create an EC2 instance.
* SSH'd into the EC2 instance.
* Manually installed Python, pip, and all required dependencies.
* Ran `git clone` to pull the code.
* Executed the app manually in the background.

*Problem:* Slow, repetitive, and prone to "it works on my machine" errors.

---

## Phase 2.0 - Automated CI/CD
What I did:
* Introduced GitHub Actions to automate workflows.
* **Continuous Integration (CI):** Wrote a YAML workflow to automatically run `pytest` every time code is pushed. Used Mocking object to bypass missing model artifacts during testing.
* **Continuous Deployment (CD):** Added an SSH action so GitHub automatically logs into the EC2 instance, pulls the latest code, and restarts the app.

*Problem:* The environment on the EC2 server was still not strictly version-controlled.

---

## Phase 3.0 - Containerized MLOps (CI/CD/Model Packaging)
What I did:
* Wrapped the entire application and its dependencies inside **Docker**.
* **Continuous Training (CT):** Configured the `Dockerfile` to automatically execute `train.py` during the build phase. The model trains and saves its weights natively inside the container.
* Pushed the finished, immutable Docker Image to Docker Hub.
* **CD Upgrade:** The deployment step now just pulls the latest Docker image and runs the container. Zero dependency conflicts.

---

## Phase 4.0 - Infrastructure as Code (GitOps)
What I did:
* Replaced manual AWS Console clicking with **Terraform**.
* Bootstrapped an S3 Bucket and DynamoDB table locally to act as a Remote State Backend.
* Integrated Terraform directly into the GitHub Actions pipeline.
* **Full Automation:** GitHub Actions now automatically checks the infrastructure state, provisions or updates the EC2 instance, extracts the dynamic IP, and passes it to the Docker deployment job. 

*Result:* If the server dies, the pipeline automatically builds a new one. 100% automated lifecycle.

---

## Phase 5.0 - Data Drift Observability (Event-Driven Monitoring)
What I did:
* Engineered a mathematical monitoring script using `numpy` and `pandas` to calculate the **Population Stability Index (PSI)**.
* Simulated **Covariate Shift** by perturbing the inference data to test system resilience.
* Configured a Time-based Job Scheduler (CRON) via GitHub Actions to execute drift analysis autonomously.
* Integrated a **Telegram REST API Webhook** for real-time alerting whenever the PSI score breaches the critical threshold ($PSI \ge 0.2$), signaling the need for model retraining.

---

## Phase 6.0 - Closed-Loop MLOps Level 1 (Dynamic Decoupling & Automated CT)
What I did:
* Migrated local file-based logging to a Serverless database (Supabase).
* Replaced manual mathematical scripts with **Evidently AI** for multivariate statistical hypothesis testing. Implemented a Sliding Window extraction mechanism (24h) to process only recent inference data and prevent redundant alerting.
* Separated the machine learning model lifecycle from the Docker image lifecycle. Integrated **MLflow Model Registry** (via DagsHub) as the Single Source of Truth for model artifacts.
* Split the monolithic CI/CD pipeline. Created a dedicated `mlops-ct.yml` workflow. Upon detecting Data Drift, the monitoring service autonomously triggers the CT pipeline via **GitHub REST API Webhooks**.
* The Flask application now leverages dynamic model loading. It queries the MLflow Registry at runtime to fetch the latest production-ready model without requiring container rebuilds or EC2 redeployments.

*Result:* The architecture is now a fully autonomous, closed-loop system. When covariate shift occurs, the system detects it, alerts the on-call engineer via Telegram, retrains the model, registers the new artifact, and serves it seamlessly with zero human intervention.

However, the current system still lacks of validation gate before promoting models, performance monitoring after serving, rollback logic, multiple instances, etc.

---

## Results and Images
 
 
**Database on Supabase (after Injection)**

<img width="2559" height="1470" alt="image" src="https://github.com/user-attachments/assets/39d1895f-bebf-4476-8588-e014ad69ea96" />
 
 
 
**MLFlow Runs**

<img width="2559" height="1470" alt="image" src="https://github.com/user-attachments/assets/6cbe8a77-502b-4a0b-abc7-847f320855e0" />
 
 
 
**MLFlow Artifacts**

<img width="2559" height="1472" alt="image" src="https://github.com/user-attachments/assets/8eadefe4-2b53-47cf-b9f2-f975bd26911e" />
 
 
 
**Alerting via Telegram API**

<img width="975" height="265" alt="image" src="https://github.com/user-attachments/assets/2d44e892-008d-4017-b179-03999d1f2cbc" />


