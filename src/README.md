# COGRABIG INSTITUTE OF ARTS - Student Management Portal

## Quick Start

### Prerequisites
- Python 3.10+
- MySQL 8.0
- Node.js (for Tailwind CSS)

### Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. Create database:
   ```sql
   CREATE DATABASE cioa_portal CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

5. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Run development server:
   ```bash
   python manage.py runserver
   ```

### Docker Deployment

```bash
docker-compose up -d --build
```

### Excel Import

```bash
python manage.py import_continuous data/import.xlsx --import-name "Batch 2024-01" --dry-run
python manage.py import_continuous data/import.xlsx --import-name "Batch 2024-01"
```

## Project Structure

- `src/core/` - Core Django configuration
- `src/students/` - Student management app
- `src/faculty/` - Faculty management app
- `src/portal/` - Portal views and templates

## Features

- Role-based dashboards (Student, Faculty, Admin)
- Excel batch import with dry-run support
- Cash payment recording with auto-receipt numbers
- Progress tracking and balance calculation
- Course enrollment management
- Payment verification workflow

## Technology Stack

- Django 4.2+
- MySQL 8.0
- Tailwind CSS 3
- Alpine.js 3
- Gunicorn + Nginx (production)
- Docker Compose

## Currency

All amounts are displayed in Maloti (M).

## Security

- HTTPS enforced in production
- Secure cookies
- CSRF protection
- Role-based access control
- Password hashing (PBKDF2)

## Support

Contact: admin@cioa.edu.ls
