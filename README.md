[![MLOps CI Pipeline](https://github.com/nhatminh-115/cali-housing-mlops/actions/workflows/mlops-ci.yml/badge.svg)](https://github.com/nhatminh-115/cali-housing-mlops/actions/workflows/mlops-ci.yml)

# Cali Housing MLOps: From Manual to GitOps Architecture

This repository tracks the step-by-step evolution of an MLOps pipeline. The goal is to transform a locally run machine learning model into a fully automated, containerized, and self-provisioning system on AWS.



---

## Phase 1.0 — Manual Execution (The Baseline)
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

## Phase 2.0 — Automated CI/CD
What I did:
* Introduced GitHub Actions to automate workflows.
* **Continuous Integration (CI):** Wrote a YAML workflow to automatically run `pytest` every time code is pushed. Used Mocking object to bypass missing model artifacts during testing.
* **Continuous Deployment (CD):** Added an SSH action so GitHub automatically logs into the EC2 instance, pulls the latest code, and restarts the app.

*Problem:* The environment on the EC2 server was still not strictly version-controlled.

---

## Phase 3.0 — Containerized MLOps (CI/CD/CT)
What I did:
* Wrapped the entire application and its dependencies inside **Docker**.
* **Continuous Training (CT):** Configured the `Dockerfile` to automatically execute `train.py` during the build phase. The model trains and saves its weights natively inside the container.
* Pushed the finished, immutable Docker Image to Docker Hub.
* **CD Upgrade:** The deployment step now just pulls the latest Docker image and runs the container. Zero dependency conflicts.

---

## Phase 4.0 — Infrastructure as Code (GitOps)
What I did:
* Replaced manual AWS Console clicking with **Terraform**.
* Bootstrapped an S3 Bucket and DynamoDB table locally to act as a Remote State Backend.
* Integrated Terraform directly into the GitHub Actions pipeline.
* **Full Automation:** GitHub Actions now automatically checks the infrastructure state, provisions or updates the EC2 instance, extracts the dynamic IP, and passes it to the Docker deployment job. 

*Result:* If the server dies, the pipeline automatically builds a new one. 100% automated lifecycle.

---

## Images

**Initial State**                                             

<img width="712" height="87" alt="Initial Manual State" src="https://github.com/user-attachments/assets/08106c52-d8e2-449b-8d2b-2f7635ac0dbc" />



**Intermediate CI/CD Stage**                                         

<img width="712" height="87" alt="CI/CD Integration" src="https://github.com/user-attachments/assets/846bd1ae-7033-4d72-9169-5ab5cbf28ca2" />



**Final Containerized Architecture**                      

<img width="1343" height="964" alt="Dockerized Pipeline" src="https://github.com/user-attachments/assets/26016316-c988-4989-91d8-8c346d297b5b" />
