---

# FPLMate Backend

FPLMate Backend is a Django REST Framework service that powers the FPLMate application. It handles data ingestion, storage, machine learning inference, and authentication. The backend exposes RESTful endpoints for player data, team management, and ML-driven recommendations.

---

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Tech Stack](#tech-stack)
4. [Getting Started](#getting-started)

   * [Prerequisites](#prerequisites)
   * [Installation](#installation)
   * [Configuration](#configuration)
   * [Running Locally](#running-locally)
5. [Project Structure](#project-structure)
6. [Data Management](#data-management)
7. [Machine Learning Integration](#machine-learning-integration)
8. [API Endpoints](#api-endpoints)
9. [Testing](#testing)
10. [Deployment](#deployment)
11. [Contributing](#contributing)
12. [License](#license)

---

## Features

* Player CRUD: Create, retrieve, update, and delete player records.
* Team Management: Manage user-specific FPL teams.
* Recommendations: ML-powered transfer suggestions and performance forecasts.
* Bulk Data Import: Load historical seasons via CSV ingestion scripts.
* Real-Time Data Sync: Fetch latest FPL API data with scheduled commands.
* Authentication: Secure user login via Firebase token validation.
* Health Check: Simple endpoint to verify service status.

---

## Architecture

* **Django REST Framework** serves all API endpoints.
* **Celery** (optional) enables asynchronous tasks such as data ingestion and model retraining.
* **PostgreSQL** is recommended for production; **SQLite** is used for development.
* **Firebase Admin SDK** verifies JWTs issued by the frontend.
* **Pickle-serialized ML models** are loaded at startup for fast inference.

---

## Tech Stack

| Component         | Technology                                    |
| ----------------- | --------------------------------------------- |
| Web Framework     | Django, Django REST Framework                 |
| Language          | Python 3.8+                                   |
| Database          | SQLite (development), PostgreSQL (production) |
| ML & Data Science | scikit-learn, pandas, numpy                   |
| Authentication    | Firebase Admin SDK                            |
| Background Tasks  | Celery + Redis (optional)                     |
| API Documentation | DRF Browsable API, Swagger UI                 |

---

## Getting Started

### Prerequisites

* Python 3.8 or higher
* pip
* Git
* Firebase service account JSON

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Ron111104/fplmate_backend.git
   cd fplmate_backend
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv env
   source env/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Configuration

Create a `.env` file in the project root:

```env
# Django Settings
DJANGO_SECRET_KEY=<your_django_secret_key>
DEBUG=True
ALLOWED_HOSTS=*

# Database (override DATABASE_URL for production)
DATABASE_URL=sqlite:///db.sqlite3

# Firebase Admin
FIREBASE_CREDENTIALS=/path/to/serviceAccountKey.json

# ML Model Paths
RECOMMENDATION_MODEL=trained_models/recommendation_model.pkl
PREDICTOR_MODEL=trained_models/performance_predictor.pkl
SCALER=trained_models/feature_scaler.pkl
```

> Note: Install `python-dotenv` if you want `.env` values to be automatically loaded.

### Running Locally

1. Apply migrations:

   ```bash
   python manage.py migrate
   ```

2. (Optional) Import initial data:

   ```bash
   python manage.py import_data --path data/players_2020-21.csv
   ```

3. Start the development server:

   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

4. Access API documentation:

   * DRF Interface: `http://localhost:8000/api/`
   * Swagger UI: `http://localhost:8000/swagger/`

---

## Project Structure

```
fplmate_backend/
├── data/                     # CSV datasets and ingestion scripts
├── trained_models/           # Serialized ML models and scalers
├── fplmate_backend/          # Django project configuration
│   ├── settings.py           # Settings and REST framework config
│   ├── urls.py               # URL routing
│   └── wsgi.py               # WSGI entrypoint
├── models/                   # Django app with models, views, serializers
│   ├── player.py             # Player model and serializer
│   ├── team.py               # Team model and serializer
│   ├── recommendation.py     # Recommendation logic and API views
│   └── serializers.py        # DRF serializers
├── requirements.txt          # Python dependencies
└── manage.py                 # Django management script
```

---

## Data Management

* **CSV Import**: Use `python manage.py import_data` to ingest historical season data.
* **Real-Time Sync**: Schedule a cron job or Celery Beat task to invoke `sync_fpl_data`.
* **Validation**: Scripts include schema validation and duplicate filtering.

---

## Machine Learning Integration

* **Model Storage**: Place trained `.pkl` models under `trained_models/`.
* **Inference**: Models are loaded into memory at application startup.
* **Retraining**: Use `python manage.py train_models` to update models with fresh data.

---

## API Endpoints

| Method | Endpoint                | Description                            |
| ------ | ----------------------- | -------------------------------------- |
| POST   | `/api/auth/login/`      | Validate Firebase token and return JWT |
| GET    | `/api/players/`         | List or create player entries          |
| GET    | `/api/players/{id}/`    | Retrieve, update, or delete a player   |
| GET    | `/api/recommendations/` | Get ML-based transfer suggestions      |
| POST   | `/api/teams/`           | Create or update a user's team         |
| GET    | `/api/teams/{id}/`      | Get details of a user's team           |
| GET    | `/api/health/`          | Health check to verify server status   |

---

## Testing

Run the test suite using:

```bash
python manage.py test
```

You can also use tools like `pytest` or `coverage` for extended test reporting.

---

## Deployment

For production deployment:

* Use **Gunicorn** or **uWSGI** with **Nginx**.
* Configure a **PostgreSQL** database.
* Set `DEBUG=False` and define production-ready `ALLOWED_HOSTS`.
* Load Firebase credentials securely via environment variables.
* Use **supervisor**, **systemd**, or **Docker** to manage services.
* (Optional) Set up **Celery** and **Redis** for background jobs.

---

## Contributing

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Install dependencies and ensure all tests pass.
4. Submit a pull request with a clear explanation of changes.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---
