# Django Celery Ad Agency Assignment

## Overview
This project is a backend system for an Ad Agency to manage advertising campaigns, budgets, and dayparting using Django and Celery. It tracks daily and monthly ad spend, automatically turns campaigns on/off based on budgets, resets spends at the start of each day/month, and enforces dayparting schedules.

## Tech Stack
- Django (ORM, admin, management commands)
- Celery (background/periodic tasks)
- SQlite3 (database)
- Redis (Celery broker)
- Python type hints (PEP 484, mypy, django-stubs)

## Prerequisites
- Python 3.9+
- SQlite3
- Redis

## Setup Instructions

### 1. Clone the repository
```sh
git clone <repository-url>
cd django_celery_assignment
```

### 2. Create and activate virtual environment
```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```sh
pip install -r requirements.txt
```

### 4. Set up PostgreSQL database
```sh
# Create database
createdb ad_agency_db

# Or using psql
psql -U postgres
CREATE DATABASE ad_agency_db;
\q
```

### 5. Configure environment variables
Copy `env.example` to `.env` and update the values:
```sh
cp env.example .env
```

Edit `.env` with your database credentials:
```env
DB_NAME=ad_agency_db
DB_USER=your_postgres_user
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432
CELERY_BROKER_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### 6. Run migrations
```sh
python manage.py migrate
```

### 7. Create a superuser
```sh
python manage.py createsuperuser
```

### 8. Seed the database with test data (optional)
```sh
python manage.py seed_data --brands 5 --campaigns-per-brand 3
```

### 9. Start Redis (if not already running)
```sh
redis-server
```

### 10. Run the development server
```sh
python manage.py runserver
```

### 11. Start Celery worker and beat (in separate terminals)
```sh
# Terminal 1: Celery worker
celery -A ad_agency worker -l info

# Terminal 2: Celery beat (scheduler)
celery -A ad_agency beat -l info
```

## Data Models

### Brand
- Represents a client/brand
- Has many campaigns
- Fields: name, description, is_active, timestamps

### Campaign
- Belongs to a brand
- Tracks daily/monthly budgets and spend
- Status: DRAFT, ACTIVE, PAUSED, COMPLETED
- Fields: name, brand, status, budgets, spend, date range

### DaypartingSchedule
- Defines allowed hours for a campaign per day of week
- Fields: campaign, day_of_week, start_time, end_time, is_active

### SpendLog
- Logs spend transactions for campaigns
- Fields: campaign, amount, timestamp, description

## System Workflow

### Daily Operations
1. **Budget Monitoring**: Every 5 minutes, Celery checks all active campaigns
2. **Spend Tracking**: Campaigns automatically pause when budgets are exceeded
3. **Dayparting Enforcement**: Every 5 minutes, campaigns are enabled/disabled based on schedules
4. **Campaign Activation**: Every 10 minutes, eligible draft campaigns are activated

### Reset Operations
1. **Daily Reset**: At midnight, all daily spends are reset to $0.00
2. **Monthly Reset**: Monthly spends are reset and campaigns are reactivated if eligible
3. **Campaign Reactivation**: Paused campaigns are reactivated if budgets allow

### Management Commands
```sh
# Check campaign budgets
python manage.py check_budgets

# Reset daily spends
python manage.py reset_daily_spends

# Reset monthly spends
python manage.py reset_monthly_spends

# Enforce dayparting
python manage.py enforce_dayparting

# Seed test data
python manage.py seed_data --brands 5 --campaigns-per-brand 3
```

## Celery Tasks

### Periodic Tasks (configured in settings.py)
- `check_campaign_budgets`: Every 5 minutes
- `enforce_dayparting`: Every 5 minutes
- `reset_daily_spends`: Daily at midnight
- `reset_monthly_spends`: Monthly
- `activate_eligible_campaigns`: Every 10 minutes

### Manual Tasks
- `add_campaign_spend`: Add spend to a campaign
- `generate_spend_report`: Generate spending reports

## Static Typing
- All code uses Python type hints (PEP 484)
- `mypy.ini` is configured for strict type checking
- Run type checks with:
  ```sh
  mypy .
  ```
- Zero mypy errors expected

## Testing
```sh
# Run tests
pytest

# Run with coverage
pytest --cov=campaigns
```

## Admin Panel
Access the Django admin at `http://localhost:8000/admin/` to manage:
- Brands and campaigns
- Dayparting schedules
- Spend logs
- Celery task results

## Assumptions & Simplifications
- Campaigns are paused immediately when budgets are exceeded
- Campaigns are reactivated at the start of a new day/month if within budget and date range
- Dayparting schedules are enforced per campaign, per day of week
- No external queueing libraries are used except Celery
- Timezone is UTC by default (configurable in settings)
- PostgreSQL is used for production-ready database operations

## Production Deployment
For production deployment:
1. Set `DEBUG=False`
2. Use environment variables for sensitive settings
3. Configure proper PostgreSQL connection pooling
4. Set up Redis clustering if needed
5. Use proper logging configuration
6. Configure Celery with multiple workers

## Extending the System
- Add more granular spend logging or reporting
- Integrate with ad delivery systems for real spend updates
- Add campaign performance metrics
- Implement budget forecasting
- Add user roles and permissions

---

**Author:** Ad Agency Backend Team 