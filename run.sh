#!/usr/bin/env bash
# run.sh — sets up and starts the Stock Management System

set -e  # exit immediately on any error

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/venv"

echo ""
echo "=== Stock Management System Setup ==="
echo ""

# ── 1. Check Python ────────────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(sys.version_info.minor)")
if [ "$PYTHON_VERSION" -lt 10 ]; then
    echo "ERROR: Python 3.10+ is required. Found: $(python3 --version)"
    exit 1
fi

echo "✓ Python $(python3 --version) found"

# ── 2. Create virtual environment if it doesn't exist ─────────────────────────
if [ ! -d "$VENV_DIR" ]; then
    echo "→ Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

PYTHON="$VENV_DIR/bin/python"
PIP="$VENV_DIR/bin/pip"

# ── 3. Install dependencies ────────────────────────────────────────────────────
echo "→ Installing dependencies..."
"$PIP" install --upgrade pip --quiet
"$PIP" install -r "$PROJECT_DIR/requirements.txt" --quiet
echo "✓ Dependencies installed"

# ── 4. Set up .env file ────────────────────────────────────────────────────────
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "→ Creating .env from .env.example..."
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"

    # Generate a random secret key
    SECRET=$(python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$%^&*(-_=+)') for _ in range(50)))")
    # Replace the placeholder in .env
    sed -i "s|your-secret-key-here|$SECRET|g" "$PROJECT_DIR/.env"
    echo "✓ .env created with a generated secret key"
else
    echo "✓ .env already exists"
fi

# ── 5. Run migrations ──────────────────────────────────────────────────────────
echo "→ Applying database migrations..."
"$PYTHON" "$PROJECT_DIR/manage.py" migrate --run-syncdb
echo "✓ Database ready"

# ── 6. Create superuser (only if DB is fresh) ──────────────────────────────────
USER_COUNT=$("$PYTHON" "$PROJECT_DIR/manage.py" shell -c "from django.contrib.auth import get_user_model; print(get_user_model().objects.count())" 2>/dev/null || echo "0")

if [ "$USER_COUNT" -eq 0 ]; then
    echo ""
    echo "=== Create Admin Account ==="
    "$PYTHON" "$PROJECT_DIR/manage.py" createsuperuser
fi

# ── 7. Start the development server ───────────────────────────────────────────
echo ""
echo "✓ Everything is ready."
echo ""
echo "  App:        http://127.0.0.1:8000/"
echo "  Admin:      http://127.0.0.1:8000/admin/"
echo "  REST API:   http://127.0.0.1:8000/api/v1/"
echo ""
echo "  Press Ctrl+C to stop the server."
echo ""

"$PYTHON" "$PROJECT_DIR/manage.py" runserver
