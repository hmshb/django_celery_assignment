# Django + Celery Budget Management System

## 🎯 Overview
A robust backend system for managing advertising campaigns with automated budget control, dayparting schedules, and real-time campaign optimization. Built with Django and Celery, this system provides comprehensive campaign management capabilities for ad agencies.

### ✨ Key Features
- **Automated Budget Management**: Real-time tracking of daily and monthly ad spend
- **Smart Campaign Control**: Automatic activation/deactivation based on budget limits
- **Dayparting Support**: Schedule-based campaign execution with time restrictions
- **Periodic Resets**: Automated daily and monthly budget resets with campaign reactivation
- **Comprehensive Logging**: Detailed spend tracking and audit trails
- **Type-Safe Code**: Full Python type hints with mypy integration

## 🛠 Tech Stack
- **Django 4.2.7** - Web framework with ORM and admin interface
- **Celery 5.3.4** - Distributed task queue for background processing
- **Redis 5.0.1** - Message broker and caching layer
- **SQLite** - Lightweight database (included with Python)
- **Python 3.9+** - Modern Python with type hints

## 📋 Prerequisites
- Python 3.9 or higher
- Redis server
- Git

##  Quick Start

### 1. Clone and Setup
```bash
git clone [<repository-url>](https://github.com/hmshb/django_celery_assignment)
cd django_celery_assignment

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
# Create .env file with your settings
cat > .env << EOF
CELERY_BROKER_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
DEBUG=True
EOF
```

### 3. Database Setup
```bash
# Run migrations (SQLite database will be created automatically)
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 4. Start Services
```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start Django development server
python manage.py runserver

# Terminal 3: Start Celery worker
celery -A ad_agency worker -l info

# Terminal 4: Start Celery beat scheduler
celery -A ad_agency beat -l info
```

### 5. Seed Test Data (Optional)
```bash
python manage.py seed_data
```

### Manual Operations
```bash
# Budget management
python manage.py check_budgets [--async]

# Spend resets
python manage.py reset_daily_spends [--async]
python manage.py reset_monthly_spends [--async]

# Dayparting enforcement
python manage.py enforce_dayparting [--async]

# Data seeding
python manage.py seed_data --brands 5 --campaigns-per-brand 3
```
## 🌐 Admin Interface

Access the Django admin at `http://localhost:8000/admin/` to manage:
- **Brands**: Create and manage client brands
- **Campaigns**: Monitor campaign status and budgets
- **Dayparting Schedules**: Configure time-based restrictions
- **Spend Logs**: View transaction history
- **Celery Results**: Monitor task execution
- **Periodic Tasks**: Manage scheduled tasks

## 🔍 Troubleshooting

### Common Issues
1. **Redis Connection Error**
   ```bash
   redis-cli ping  # Should return PONG
   ```

2. **Celery Worker Not Starting**
   ```bash
   celery -A ad_agency worker -l debug
   ```

3. **Tasks Not Executing**
   ```bash
   celery -A ad_agency inspect active
   celery -A ad_agency inspect scheduled
   ```

4. **Database Issues**
   ```bash
   python manage.py check --database default
   ```

### Logs
```bash
# Celery worker logs
tail -f /var/log/celery/worker.log

# Django logs
tail -f /var/log/django/app.log

# Redis logs
tail -f /var/log/redis/redis-server.log
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors
- **Maintainer**: Hassan Mehmood

##  Acknowledgments

- Django community for the excellent framework
- Celery team for the robust task queue system
- Redis team for the fast message broker
