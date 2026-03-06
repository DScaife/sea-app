# Asset Manager

## Overview

Asset Manager is a simple web-based asset management system built with Flask.
- User Functions: Register, log in, and submit asset requests.
- Admin Functions: Review, approve, or reject asset submissions.

## Features

- User Authentication: Secure registration and login using Flask-Login.
- Asset Management: Submit asset details and track their status.
- Role-Based Access: Separate interfaces for regular users and administrators.

## Getting Started

### Prerequisites

- Python 3.x
- pip

### Installation

1. Clone the Repository:

   git clone (REPO LINK)
   cd asset_manager

2. Set Up a Virtual Environment:

   python -m venv venv
   # Activate the virtual environment:
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate

3. Install Dependencies:

   pip install -r requirements.txt

4. Configure Environment Variables:

   Copy the example file and set values:

   copy .env.example .env

   Required keys include:
   - SECRET_KEY
   - DATABASE_URL
   - BOOTSTRAP_ADMIN_USERNAME
   - BOOTSTRAP_ADMIN_PASSWORD

## Running the Application

1. Start the Application:

   python run.py

2. Login with bootstrap admin credentials from your `.env`:

   - Username: value of `BOOTSTRAP_ADMIN_USERNAME`
   - Password: value of `BOOTSTRAP_ADMIN_PASSWORD`

3. Access the Application:

   Open your browser and navigate to http://127.0.0.1:5000

## Security Controls (OWASP-aligned)

The application includes protections aligned to OWASP Top 10 areas:

- **A01: Broken Access Control**
  - Role checks restrict approve/reject operations to admins only.
  - Regular users cannot manage other users’ assets.

- **A07: Identification and Authentication Failures**
  - Passwords are hashed with Werkzeug PBKDF2.
  - Registration enforces password strength rules.
  - Login lockout is applied after repeated failed attempts.

- **A03: Injection**
  - SQLAlchemy ORM is used for parameterized query handling.
  - Tests include SQL injection-like payload login attempts.

## Running the Tests

1. Ensure Your Virtual Environment is Active.

2. Run Pytest:

   pytest

   This will execute all the tests in the tests/ folder.

### Test Categories (for assignment evidence)

Tests are grouped by marker so you can report outcomes by type:

- **Unit tests**
  ```
  pytest asset_manager/tests -m unit -v -ra
  ```
- **Integration tests**
  ```
  pytest asset_manager/tests -m integration -v -ra
  ```
- **Security tests**
  ```
  pytest asset_manager/tests -m security -v -ra
  ```

### Coverage + JUnit reports

To generate richer artefacts for your report:

```
pytest asset_manager/tests -v --cov=asset_manager/app --cov-report=term-missing --cov-report=xml:reports/coverage.xml --junitxml=reports/all-tests.xml
```

This supports evidence such as test counts/status by category and exported XML report files.

## DevOps Pipeline Artefacts (Task 3)

This repository includes a minimal CI pipeline and container artefacts suitable for assessment evidence.

- **SCM:** GitHub repository with commits/branches/PRs
- **CI Workflow:** `.github/workflows/ci.yml`
  - Installs dependencies
  - Runs `pytest`
  - Runs `ruff` lint checks
  - Runs `bandit` static security scan
  - Runs `pip-audit` dependency vulnerability scan
- **Containerisation:** `asset_manager/Dockerfile` and `asset_manager/.dockerignore`

### Local DevOps Tooling

Install development tools:

```
pip install -r requirements-dev.txt
```

Run checks locally:

```
pytest tests -q
pytest tests -m unit -v -ra
pytest tests -m integration -v -ra
pytest tests -m security -v -ra
ruff check app tests --select E9,F63,F7,F82
bandit -r app -q
pip-audit -r requirements.txt
```

### Docker Build/Run

From inside `asset_manager/`:

```
docker build -t asset-manager .
docker run --env-file .env -p 5000:5000 asset-manager
```

### Suggested Evidence Screenshots

- GitHub Actions workflow run (tests/lint/security all green)
- Bandit output in CI logs
- Ruff output in CI logs
- Docker build and running container output

## Usage

- User Registration:
  Click "Register" on the login page, fill in your username and password, and submit the form.

- User Login:
  Enter your credentials on the login page to access your dashboard.

- Asset Submission (Regular Users):
  After logging in, navigate to the asset submission page, enter asset details (e.g., asset name, category, purchase date), and submit the form.

- Asset Approval (Admins):
  Log in with admin credentials, navigate to the admin dashboard, and use the provided controls to approve or reject asset submissions.

## Additional Information

- Source Code:
  The complete source code is available on GitHub at: (REPO LINK)

- Deployment:
  This app can be deployed on free public cloud platforms (e.g., Heroku, AWS, or Azure).
