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
├── app.py                        # Flask application (API + Home UI)
├── requirements.txt              # Python dependencies
├── test_app.py                   # Pytest test suite (25 tests)
├── Dockerfile                    # Production Docker image (multi-stage, non-root)
├── Dockerfile.test               # Test Docker image (includes test files)
├── .flake8                       # Flake8 linting configuration
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
git clone https://github.com/rrprabhakar2003/fitness-gym.git
cd fitness-gym

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the Flask development server
python app.py
```

The app will be available at `http://localhost:5000`.
Open your browser to see the **Home UI dashboard**.

### Run with Docker (recommended)

```bash
docker build -t acefitness:latest .
docker run -p 5000:5000 acefitness:latest
```

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

The app will be available at `http://localhost:5000`.

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

1. **Install Jenkins** via Docker:
   ```bash
   docker run -d -p 8080:8080 -p 50000:50000 \
     -v jenkins_home:/var/jenkins_home \
     -v /var/run/docker.sock:/var/run/docker.sock \
     jenkins/jenkins:lts
   ```

2. **Install Docker CLI inside Jenkins container** (required for Docker builds):
   ```bash
   docker exec -u root jenkins bash -c "
     apt-get update -qq &&
     apt-get install -y ca-certificates curl gnupg &&
     curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg &&
     echo 'deb [arch=arm64 signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian bookworm stable' > /etc/apt/sources.list.d/docker.list &&
     apt-get update -qq && apt-get install -y docker-ce-cli
   "
   docker exec -u root jenkins chmod 666 /var/run/docker.sock
   ```

3. **Create a new Pipeline job**:
   - Dashboard → New Item → Pipeline
   - Under *Pipeline*, select **Pipeline script from SCM**
   - SCM: Git → `https://github.com/rrprabhakar2003/fitness-gym.git`
   - Branch: `*/main`
   - Script Path: `Jenkinsfile`

4. **Trigger a build**:
   - Click **Build Now**

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

### Home UI

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Web dashboard (members, classes, programs) |

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

### Programs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/programs` | List all fitness programs (FL, MG, BG) |
| GET | `/programs/<code>` | Get a specific program by code |

**Program codes:** `FL` (Fat Loss), `MG` (Muscle Gain), `BG` (Beginner)

---

## Evaluation Checklist

- [x] Flask application with modular endpoints
- [x] Home UI dashboard for gym management
- [x] Programs API based on ACEest baseline scripts (FL/MG/BG)
- [x] Meaningful Git commits and branch management
- [x] Pytest suite — 25 tests covering all core functionalities
- [x] Multi-stage Dockerfile (optimized, non-root user)
- [x] GitHub Actions workflow (Build → Docker → Test)
- [x] Jenkins declarative pipeline (Checkout → Build → Lint → Test → Quality Gate)
- [x] Professional README documentation
