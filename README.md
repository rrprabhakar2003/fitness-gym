# ACEest Fitness & Gym — DevOps CI/CD Assignment

A Flask-based gym management REST API with a fully automated CI/CD pipeline using **GitHub Actions** and **Jenkins**, containerized with **Docker**.

---

## Table of Contents
1. [Project Structure](#project-structure)
2. [Local Setup & Execution](#local-setup--execution)
3. [Running Tests Manually](#running-tests-manually)
4. [Docker Usage](#docker-usage)
5. [GitHub Actions Pipeline](#github-actions-pipeline)
6. [Jenkins Integration](#jenkins-integration)
7. [API Reference](#api-reference)

---

## Project Structure

```
acefitness/
├── app.py                        # Flask application
├── requirements.txt              # Python dependencies
├── test_app.py                   # Pytest test suite
├── Dockerfile                    # Production Docker image (multi-stage, non-root)
├── Dockerfile.test               # Test Docker image (includes test files)
├── .dockerignore                 # Files excluded from Docker build context
├── Jenkinsfile                   # Jenkins declarative pipeline
├── .github/
│   └── workflows/
│       └── main.yml              # GitHub Actions CI/CD workflow
└── README.md
```

---

## Local Setup & Execution

### Prerequisites
- Python 3.11+
- pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/acefitness-devops.git
cd acefitness-devops

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the Flask development server
python app.py
```

The API will be available at `http://localhost:5000`.

---

## Running Tests Manually

### Without Docker (local Python environment)

```bash
# Run all tests
pytest test_app.py -v

# Run with coverage report
pytest test_app.py -v --cov=app --cov-report=term-missing
```

### Inside Docker

```bash
# Build the test image
docker build -t acefitness-test -f Dockerfile.test .

# Run Pytest inside the container
docker run --rm acefitness-test pytest test_app.py -v
```

---

## Docker Usage

### Build the production image

```bash
docker build -t acefitness:latest .
```

### Run the container

```bash
docker run -p 5000:5000 acefitness:latest
```

The API will be available at `http://localhost:5000`.

---

## GitHub Actions Pipeline

The workflow is defined in [.github/workflows/main.yml](.github/workflows/main.yml) and triggers on every **push** and **pull request**.

### Stages

| Job | Description |
|-----|-------------|
| **Build & Lint** | Installs dependencies and runs `flake8` to catch syntax errors and style issues |
| **Docker Image Assembly** | Builds the production Docker image and verifies it was created successfully |
| **Automated Testing** | Builds the test Docker image and runs the full Pytest suite inside the container |

Each job depends on the previous one — a failure at any stage blocks progression downstream, acting as a quality gate.

```
push / pull_request
        │
        ▼
┌──────────────────┐
│  Build & Lint    │  (flake8 syntax + style check)
└────────┬─────────┘
         │ pass
         ▼
┌──────────────────┐
│  Docker Build    │  (docker build production image)
└────────┬─────────┘
         │ pass
         ▼
┌──────────────────┐
│ Automated Tests  │  (pytest inside container)
└──────────────────┘
```

---

## Jenkins Integration

Jenkins handles the **BUILD** phase as a secondary quality gate, pulling the latest code from GitHub and performing a clean build in a controlled environment.

### Setup Instructions

1. **Install Jenkins** (local or Docker):
   ```bash
   docker run -p 8080:8080 -p 50000:50000 \
     -v jenkins_home:/var/jenkins_home \
     jenkins/jenkins:lts
   ```

2. **Install required plugins** in Jenkins:
   - Git Plugin
   - Pipeline Plugin
   - Docker Pipeline Plugin

3. **Create a new Pipeline job**:
   - Dashboard → New Item → Pipeline
   - Under *Pipeline*, select **Pipeline script from SCM**
   - SCM: Git → enter your GitHub repository URL
   - Script Path: `Jenkinsfile`

4. **Trigger a build**:
   - Click **Build Now**, or configure a GitHub webhook to trigger on push.

### Jenkins Pipeline Stages

| Stage | Description |
|-------|-------------|
| **Checkout** | Pulls latest code from GitHub via SCM |
| **Build Environment** | Runs `docker build` to create the production image |
| **Lint** | Runs `flake8` inside the container |
| **Unit Tests** | Builds test image and runs `pytest` inside the container |
| **Quality Gate** | Reports final pass/fail status |

Post-build, temporary Docker images are automatically cleaned up to conserve disk space.

---

## API Reference

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Service health check |

### Members

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/members` | List all members |
| GET | `/members/<id>` | Get a specific member |
| POST | `/members` | Register a new member |
| DELETE | `/members/<id>` | Remove a member |

**POST /members — Request body:**
```json
{
  "name": "Alice",
  "email": "alice@gym.com",
  "membership_type": "premium"
}
```

### Classes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/classes` | List all gym classes |
| GET | `/classes/<id>` | Get a specific class |
| POST | `/classes` | Add a new class |

**POST /classes — Request body:**
```json
{
  "name": "Yoga",
  "instructor": "Jane Doe",
  "schedule": "Mon/Wed 9am",
  "capacity": 15
}
```

---

## Evaluation Checklist

- [x] Flask application with modular endpoints
- [x] Meaningful Git commits and branch management
- [x] Pytest suite covering all core functionalities
- [x] Multi-stage Dockerfile (optimized, non-root user)
- [x] GitHub Actions workflow (Build → Docker → Test)
- [x] Jenkins declarative pipeline (Checkout → Build → Lint → Test)
- [x] Professional README documentation
