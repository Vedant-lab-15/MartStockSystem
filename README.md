# Stock Management System

This is a Django-based stock management system project.

## Setup Instructions

1. Create and activate a Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Apply database migrations:

```bash
python manage.py migrate
```

4. Create a superuser to access the admin panel:

```bash
python manage.py createsuperuser
```

5. Run the development server:

```bash
python manage.py runserver
```

6. Access the application in your browser at:

```
http://127.0.0.1:8000/
```

## Features

- Product and category management
- Transaction tracking
- Dashboard with reports and alerts
- User authentication and permissions

## Troubleshooting

- If you encounter template loading errors, ensure the `templates` directory is present in the project root and contains all required templates.
- Restart the development server after making changes to templates or settings.
- Check file permissions to ensure the Django process can read template files.

## Contact

For further assistance, please contact the project maintainer.
