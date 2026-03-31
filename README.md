# Stock Management System

A Django-based inventory management system with product tracking, transaction history, stock alerts, a reporting dashboard, and a REST API.

---

## Quick Start

The fastest way to get running — one command does everything:

```bash
bash run.sh
```

It will:
- create a Python virtual environment
- install all dependencies
- generate a `.env` file with a random secret key
- apply database migrations
- prompt you to create an admin account (first run only)
- start the development server

Once running, open your browser:

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000/ | Main application |
| http://127.0.0.1:8000/admin/ | Django admin panel |
| http://127.0.0.1:8000/api/v1/ | REST API (browsable) |

---

## Requirements

- Python 3.10 or higher
- No other system dependencies needed

---

## Manual Setup

If you prefer to set things up yourself:

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create your .env file
cp .env.example .env
# Edit .env and set a strong SECRET_KEY

# 4. Apply migrations
python manage.py migrate

# 5. Create an admin user
python manage.py createsuperuser

# 6. Start the server
python manage.py runserver
```

---

## Features

- **Products & Categories** — create, update, and delete products with SKU, pricing, and stock thresholds
- **Transactions** — stock in, stock out, and stock adjustments with full audit trail
- **Stock Alerts** — automatic alerts when stock falls below threshold, with resolve workflow
- **Dashboard** — live summary of stock value, today's activity, and low-stock items
- **Reports** — stock levels, sales, and profit reports with configurable date ranges
- **REST API** — full CRUD API at `/api/v1/` for products, categories, transactions, and alerts
- **User Auth** — login-required throughout, permission-based write access, brute-force protection

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key — change this in production | required |
| `DEBUG` | Enable debug mode | `True` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hostnames | `127.0.0.1,localhost` |

---

## REST API

The API uses session authentication (same login as the web app). All endpoints require authentication.

| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/api/v1/products/` | GET, POST | List and create products |
| `/api/v1/products/{slug}/` | GET, PUT, PATCH, DELETE | Product detail |
| `/api/v1/categories/` | GET, POST | List and create categories |
| `/api/v1/transactions/` | GET, POST | List and create transactions |
| `/api/v1/alerts/` | GET | List stock alerts |
| `/api/v1/alerts/{id}/resolve/` | POST | Mark alert as resolved |

Query parameters for products: `?search=`, `?low_stock=1`, `?category={slug}`  
Query parameters for transactions: `?product={id}`, `?type=IN|OUT|ADJ+|ADJ-`

---

## Running Tests

```bash
source venv/bin/activate
python manage.py test products transactions dashboard
```

---

## Project Structure

```
stock_management_system/
├── dashboard/          # Dashboard views, reports, user preferences
├── products/           # Product and category models, views, API
├── transactions/       # Stock transactions, alerts, API
├── stock_mart/         # Django project settings and URLs
├── templates/          # HTML templates
├── static/             # Static files (CSS, JS)
├── media/              # Uploaded product images
├── requirements.txt
├── run.sh              # One-command setup and start
└── .env.example        # Environment variable template
```
