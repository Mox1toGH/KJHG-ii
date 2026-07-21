# MDVL Setup Guide

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Django](https://img.shields.io/badge/Django-5.2-green.svg)
![Vue.js](https://img.shields.io/badge/Vue.js-3.5-42b883.svg)
![Docker](https://img.shields.io/badge/Docker-Supported-2496ED.svg)

This guide provides comprehensive instructions for setting up the MDVL development environment. MDVL supports two development modes:

- **Local Development** - SQLite database, no Docker
- **Docker Development** - PostgreSQL database, Docker Compose

> **Tip**: For quick testing, you can contact [@ihmaiw2d_kc] on Telegram to get a pre-configured `.env` file for testing purposes.
>
> **Підказка**: Для швидкого тестування ви можете зв'язатися з [@ihmaiw2d_kc] в Telegram, щоб отримати готовий файл `.env` для тестування.

---

## Table of Contents

- [Requirements](#requirements)
- [Project Cloning](#project-cloning)
- [Environment Configuration](#environment-configuration)
- [Local Development (SQLite)](#local-development-sqlite)
- [Docker Development (PostgreSQL)](#docker-development-postgresql)
- [Database Migrations](#database-migrations)
- [Superuser Creation](#superuser-creation)
- [Static Files](#static-files)
- [Running Development Servers](#running-development-servers)
- [Running Tests](#running-tests)
- [Coverage Reports](#coverage-reports)
- [Google OAuth Configuration](#google-oauth-configuration)
- [Maps Configuration](#maps-configuration)
- [Common Issues](#common-issues)
- [Troubleshooting](#troubleshooting)
- [Useful Development Commands](#useful-development-commands)
- [Production Notes](#production-notes)

---

## Requirements

### For Local Development (SQLite)

- **Python**: 3.12 or higher
- **Node.js**: 22.18.0 or 24.12.0 or higher
- **npm**: (comes with Node.js)
- **Git**: for cloning the repository

### For Docker Development (PostgreSQL)

- **Docker Desktop** or **Docker Engine**: Latest stable version
- **Docker Compose**: v2 or higher
- **Git**: for cloning the repository

> **Tip**: Docker Desktop is recommended for macOS and Windows users. Linux users can install Docker Engine directly.

### Optional (for production deployment)

- **Redis**: For WebSocket channel layer in production
- **PostgreSQL**: 16 (if not using Docker)
- **Nginx**: For reverse proxy (production)

---

## Project Cloning

Clone the repository from your Git hosting service:

```bash
git clone <repository-url>
cd MDVL
```

Verify the project structure:

```bash
ls -la
```

You should see:
- `backend/` - Django backend
- `frontend/` - Vue.js frontend
- `docker-compose.yml` - Docker Compose configuration
- `.env.example` - Local development environment template
- `.env.docker` - Docker environment template
- `Dockerfile.backend` - Backend container definition
- `Dockerfile.frontend` - Frontend container definition

---

## Environment Configuration

MDVL uses environment variables for configuration. The project provides two template files:

- `.env.example` - For local development with SQLite
- `.env.docker` - For Docker development with PostgreSQL

### Step 1: Choose Your Development Mode

**For Local Development (SQLite)**:
```bash
cp .env.example .env
```

**For Docker Development (PostgreSQL)**:
```bash
cp .env.docker .env
```

### Step 2: Review and Update Environment Variables

Open `.env` in your editor and review the following key variables:

#### Django Settings

```env
SECRET_KEY=change-me-to-a-random-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

**Important**:
- `SECRET_KEY`: Generate a secure random key (see below)
- `DEBUG`: Set to `False` in production
- `ALLOWED_HOSTS`: Add your domain in production
- `CSRF_TRUSTED_ORIGINS` and `CORS_ALLOWED_ORIGINS`: Must include your frontend URL

#### Database Settings

**Local Development (SQLite)**:
```env
DB_ENGINE=sqlite
DB_NAME=db.sqlite3
```

**Docker Development (PostgreSQL)**:
```env
DB_ENGINE=postgres
DB_NAME=mdvl
DB_USER=mdvl
DB_PASSWORD=change-me-postgres-password
DB_HOST=db
DB_PORT=5432
```

#### JWT Settings

```env
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=15
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
```

#### Email Settings

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=no-reply@example.com
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
```

**Note**: For local development, the console backend prints emails to the terminal. For real email delivery, configure SMTP settings.

#### Notification Defaults

```env
DEFAULT_EMAIL_NOTIFICATIONS_ENABLED=False
DEFAULT_IN_APP_NOTIFICATIONS_ENABLED=True
```

#### Google OAuth (Optional)

```env
GOOGLE_OAUTH_CLIENT_ID=your-google-web-client-id.apps.googleusercontent.com
VITE_GOOGLE_CLIENT_ID=your-google-web-client-id.apps.googleusercontent.com
```

#### Frontend Settings

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_BASE_URL=ws://localhost:8000
VITE_GOOGLE_CLIENT_ID=your-google-web-client-id.apps.googleusercontent.com
```

### Step 3: Generate a Secure SECRET_KEY

Run this command to generate a secure random key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and use it as the `SECRET_KEY` value in your `.env` file.

> **Tip**: For quick testing, you can contact [@USERNAME] on Telegram to get a pre-configured `.env` file for testing purposes.
>
> **Підказка**: Для швидкого тестування ви можете зв'язатися з [@USERNAME] в Telegram, щоб отримати готовий файл `.env` для тестування.

> **Warning**: Never commit the `.env` file to version control. It contains sensitive information including your SECRET_KEY and database credentials. The `.env` file is already included in `.gitignore`.

---

## Local Development (SQLite)

This mode uses SQLite for the database and runs services directly on your machine.

### Backend Setup

- [ ] Create Python virtual environment
- [ ] Activate virtual environment
- [ ] Install Python dependencies
- [ ] Run database migrations
- [ ] Create superuser (optional)
- [ ] Start Django development server

#### 1. Create Python Virtual Environment

```bash
python3 -m venv .venv
```

#### 2. Activate Virtual Environment

**On Linux/macOS**:
```bash
source .venv/bin/activate
```

**On Windows**:
```bash
.venv\Scripts\activate
```

> **Tip**: Your terminal prompt should change to indicate the virtual environment is active (e.g., `(.venv) user@host:~/MDVL$`).

#### 3. Install Python Dependencies

```bash
pip install -r backend/requirements.txt
```

#### 4. Run Database Migrations

```bash
cd backend
python manage.py migrate
```

#### 5. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

#### 6. Start Django Development Server

```bash
python manage.py runserver
```

The backend will be available at http://localhost:8000

> **Note**: For WebSocket support in local development, you can use Daphne instead:
> ```bash
> daphne -b 0.0.0.0 -p 8000 backend.asgi:application
> ```

### Frontend Setup

- [ ] Install Node dependencies
- [ ] Start Vite development server

#### 1. Install Node Dependencies

Open a new terminal and navigate to the frontend directory:

```bash
cd frontend
npm ci
```

> **Note**: `npm ci` is preferred over `npm install` for clean installs as it installs exact versions from `package-lock.json`.

#### 2. Start Vite Development Server

```bash
npm run dev
```

The frontend will be available at http://localhost:5173

### Verification

- [ ] Open http://localhost:5173 in your browser
- [ ] Verify the MDVL application loads
- [ ] Try registering a new account or logging in
- [ ] Check the browser console for any errors

1. Open http://localhost:5173 in your browser
2. You should see the MDVL application
3. Try registering a new account or logging in
4. Check the browser console for any errors

---

## Docker Development (PostgreSQL)

This mode uses Docker Compose to run all services in containers with PostgreSQL.

### Backend Setup

- [ ] Build Docker images
- [ ] Start Docker Compose services
- [ ] Verify services are running
- [ ] Create superuser (optional)

#### 1. Build Docker Images

```bash
docker compose build
```

This builds images for:
- `backend` - Django with runserver (development)
- `frontend` - Vite dev server
- `db` - PostgreSQL 16

> **Note**: The first build may take several minutes as it downloads base images and installs dependencies.

#### 2. Start All Services

```bash
docker compose up
```

This will:
- Start PostgreSQL database
- Wait for database to be healthy
- Run database migrations
- Start Django backend with runserver
- Start Vite frontend server

The services will be available at:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000

#### 3. Start in Background (Optional)

To run services in the background:

```bash
docker compose up -d
```

View logs with:

```bash
docker compose logs -f
```

### Frontend Setup

The frontend is automatically started by Docker Compose. No additional setup is required.

### Verification

- [ ] Open http://localhost:5173 in your browser
- [ ] Verify the MDVL application loads
- [ ] Try registering a new account or logging in
- [ ] Check the browser console for any errors

1. Open http://localhost:5173 in your browser
2. You should see the MDVL application
3. Try registering a new account or logging in
4. Check the browser console for any errors

### Docker-Specific Operations

#### Create Superuser

While containers are running:

```bash
docker compose exec backend python manage.py createsuperuser
```

#### Run Management Commands

```bash
docker compose exec backend python manage.py <command>
```

Examples:

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py shell
```

#### Access PostgreSQL Shell

```bash
docker compose exec db psql -U mdvl -d mdvl
```

> **Tip**: Use `\q` to exit the PostgreSQL shell.

#### Stop Services

```bash
docker compose down
```

#### Stop Services and Remove Volumes

This deletes all PostgreSQL data:

```bash
docker compose down -v
```

> **Warning**: Using `-v` will permanently delete all database data. Use with caution.

#### Rebuild Images

```bash
docker compose build --no-cache
docker compose up
```

<details>
<summary><strong>Advanced: Docker Compose Service Health Checks</strong></summary>

The `docker-compose.yml` includes health checks for the PostgreSQL service:

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U mdvl -d mdvl"]
  interval: 5s
  timeout: 5s
  retries: 5
```

This ensures the backend service waits for PostgreSQL to be fully ready before starting. The backend service depends on the database being healthy:

```yaml
depends_on):
  db:
    condition: service_healthy
```

</details>

---

## Database Migrations

### Local Development

```bash
cd backend
python manage.py migrate
```

### Docker Development

Migrations run automatically on backend startup. To run manually:

```bash
docker compose exec backend python manage.py migrate
```

> **Note**: Migrations are idempotent - running them multiple times is safe and will only apply pending migrations.

### Create New Migration

After making model changes:

```bash
# Local
cd backend
python manage.py makemigrations

# Docker
docker compose exec backend python manage.py makemigrations
```

### View Migration Status

```bash
# Local
cd backend
python manage.py showmigrations

# Docker
docker compose exec backend python manage.py showmigrations
```

### Rollback Migration

```bash
# Local
cd backend
python manage.py migrate <app_name> <migration_name>

# Docker
docker compose exec backend python manage.py migrate <app_name> <migration_name>
```

<details>
<summary><strong>Advanced: Migration Conflict Resolution</strong></summary>

When merging branches with conflicting migrations, you may encounter migration conflicts. To resolve:

```bash
# Identify the conflict
python manage.py showmigrations

# Create a merge migration
python manage.py makemigrations --merge

# Review the generated migration
# Apply it
python manage.py migrate
```

The `--merge` flag creates a new migration that reconciles the conflicting branches.

</details>

---

## Superuser Creation

### Local Development

```bash
cd backend
python manage.py createsuperuser
```

### Docker Development

```bash
docker compose exec backend python manage.py createsuperuser
```

Follow the prompts to create an admin account with:
- Username
- Email address
- Password

---

## Static Files

### Local Development

Static files are served automatically by Django in development mode. No collection is required.

### Docker Development

Static files are collected automatically on backend startup. To collect manually:

```bash
docker compose exec backend python manage.py collectstatic --noinput
```

### Production

In production, static files should be served by a web server like Nginx. Collect static files:

```bash
python manage.py collectstatic --noinput
```

Then configure your web server to serve files from `STATIC_ROOT`.

---

## Running Development Servers

### Local Development

#### Backend Only

```bash
cd backend
python manage.py runserver
```

#### Frontend Only

```bash
cd frontend
npm run dev
```

#### Both (Recommended)

Run backend in one terminal and frontend in another terminal:

**Terminal 1**:
```bash
cd backend
python manage.py runserver
```

**Terminal 2**:
```bash
cd frontend
npm run dev
```

### Docker Development

#### Start All Services

```bash
docker compose up
```

#### Start in Background

```bash
docker compose up -d
```

#### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db
```

#### Restart Services

```bash
docker compose restart
```

#### Restart Specific Service

```bash
docker compose restart backend
```

---

## Running Tests

### Backend Tests (pytest)

#### Local Development

```bash
cd backend
pytest
```

#### With Coverage

```bash
cd backend
pytest --cov
```

#### Coverage HTML Report

```bash
cd backend
pytest --cov --cov-report=html
```

Open `htmlcov/index.html` in your browser to view the report.

#### Run Specific Test File

```bash
cd backend
pytest accounts/tests/test_api.py
```

#### Run Specific Test

```bash
cd backend
pytest accounts/tests/test_api.py::TestLoginView::test_login_success
```

#### Docker Development

```bash
docker compose exec backend pytest
```

#### With Coverage in Docker

```bash
docker compose exec backend pytest --cov
```

> **Tip**: Use the `-v` flag for verbose output to see individual test names and their pass/fail status.

### Frontend Tests (vitest)

#### Local Development

```bash
cd frontend
npm run test:unit
```

#### Watch Mode

```bash
cd frontend
npm run test:unit -- --watch
```

#### Docker Development

```bash
docker compose exec frontend npm run test:unit
```

### Test Configuration

#### Backend (pytest.ini)

The backend uses `pytest.ini` for configuration:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = backend.settings
python_files = tests.py test_*.py *_tests.py
addopts = --strict-markers
testpaths = accounts activities chat checkpoints locations notifications points scratch_map tracking tests
markers =
    integration: tests that exercise several application boundaries
```

#### Frontend (vitest.config.ts)

The frontend uses `vitest.config.ts` for configuration with Vue Test Utils.

---

## Coverage Reports

### Backend Coverage

#### Generate Coverage Report

```bash
# Local
cd backend
pytest --cov --cov-report=html --cov-report=xml

# Docker
docker compose exec backend pytest --cov --cov-report=html --cov-report=xml
```

#### View Coverage

- HTML report: Open `backend/htmlcov/index.html`
- XML report: `backend/coverage.xml` (for CI/CD)

#### Coverage Thresholds

The project aims for 80%+ coverage. To enforce coverage:

```bash
pytest --cov --cov-fail-under=80
```

### Frontend Coverage

#### Generate Coverage Report

```bash
cd frontend
npm run test:unit -- --coverage
```

Coverage reports are generated in the `coverage/` directory.

---

## Google OAuth Configuration

Google OAuth is optional but recommended for production use. MDVL currently supports Google OAuth only.

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable Google+ API or Google Identity Services

### Step 2: Create OAuth 2.0 Credentials

1. Navigate to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Select **Web application**
4. Configure authorized redirect URIs:
   - Local: `http://localhost:5173`
   - Production: `https://your-domain.com`
5. Copy the **Client ID**

> **Note**: For local development, you may need to add `http://localhost:5173` to both "Authorized JavaScript origins" and "Authorized redirect URIs".

### Step 3: Configure Environment Variables

Add to your `.env` file:

```env
GOOGLE_OAUTH_CLIENT_ID=your-google-web-client-id.apps.googleusercontent.com
VITE_GOOGLE_CLIENT_ID=your-google-web-client-id.apps.googleusercontent.com
```

### Step 4: Test OAuth Integration

- [ ] Restart the development servers
- [ ] Navigate to the login page
- [ ] Click "Sign in with Google"
- [ ] Complete the Google authentication flow
- [ ] Verify you are logged in

1. Restart the development servers
2. Navigate to the login page
3. Click "Sign in with Google"
4. Complete the Google authentication flow
5. Verify you are logged in

### Troubleshooting OAuth

| Issue | Solution |
|-------|----------|
| **Redirect URI mismatch** | Ensure the redirect URI in Google Console matches your frontend URL exactly |
| **Client ID mismatch** | Ensure `GOOGLE_OAUTH_CLIENT_ID` and `VITE_GOOGLE_CLIENT_ID` match |
| **CORS errors** | Add your frontend URL to Google Console authorized JavaScript origins |
| **OAuth consent screen** | Configure the OAuth consent screen with required scopes |

---

## Maps Configuration

MDVL uses MapLibre GL for interactive maps. The default configuration uses OpenStreetMap tiles.

### Default Configuration

No additional configuration is required for development. The application uses OpenStreetMap tiles by default.

### Custom Map Tiles (Optional)

To use custom map tiles (e.g., Mapbox, Google Maps):

1. Obtain map tile URL from your provider
2. Add tile URL to frontend map configuration
3. Update map style in the frontend components

### MapLibre GL Configuration

The map configuration is in the frontend map components. Key settings:

- **Tile URL**: OpenStreetMap by default
- **Center**: Initial map center coordinates
- **Zoom**: Initial zoom level
- **Max Zoom**: Maximum zoom level
- **Min Zoom**: Minimum zoom level

---

## Common Issues

### Port Already in Use

**Problem**: Port 8000 or 5173 is already in use.

**Solution**:

**Local Development**:
```bash
# Change backend port
python manage.py runserver 8001

# Change frontend port (edit vite.config.ts)
# Or use:
npm run dev -- --port 5174
```

**Docker Development**:
```bash
# Edit .env file
BACKEND_PORT=8001
FRONTEND_PORT=5174

# Restart services
docker compose up
```

### Database Lock Errors (SQLite)

**Problem**: SQLite database is locked.

**Solution**:
```bash
# Stop the backend server
# Delete the lock files
cd backend
rm -f db.sqlite3-shm db.sqlite3-wal
# Restart the server
python manage.py runserver
```

> **Note**: SQLite lock files (`-shm` and `-wal`) are created for write-ahead logging. Deleting them is safe when the server is stopped.

### PostgreSQL Connection Errors (Docker)

**Problem**: Backend cannot connect to PostgreSQL.

**Solution**:
```bash
# Check database logs
docker compose logs db

# Restart services
docker compose down
docker compose up

# If credentials changed, reset database
docker compose down -v
docker compose up
```

### CORS Errors

**Problem**: Browser CORS errors when accessing the API.

**Solution**:
Ensure your `.env` file has the correct CORS configuration:

```env
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
CSRF_TRUSTED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Restart the backend after changing these values.

### CSRF Errors

**Problem**: CSRF token validation errors.

**Solution**:
The frontend should automatically handle CSRF tokens. If you see errors:

1. Ensure the frontend calls `/api/accounts/csrf/` before unsafe requests
2. Check that cookies are being sent with requests
3. Verify `CSRF_TRUSTED_ORIGINS` includes your frontend URL

### Module Import Errors

**Problem**: Python module import errors.

**Solution**:
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r backend/requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

### Node Module Errors

**Problem**: Frontend build or dependency errors.

**Solution**:
```bash
cd frontend

# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm ci

# Clear cache
npm cache clean --force
```

### WebSocket Connection Errors

**Problem**: WebSocket connections fail.

**Solution**:
1. Ensure the backend is running with Daphne for WebSocket support (or use `runserver` for basic testing)
2. Check that `VITE_WS_BASE_URL` is correct in `.env`
3. Verify the WebSocket endpoint URL in the frontend
4. Check browser console for specific error messages

> **Note**: For local development, `runserver` supports basic WebSocket functionality. For full WebSocket testing, use Daphne.

### Docker Hot Reload Not Working

**Problem**: Code changes not reflected in Docker containers.

**Solution**:
```bash
# Verify bind mounts are active
docker compose ps

# Restart services
docker compose down
docker compose up

# Rebuild if necessary
docker compose up --build
```

---

## Troubleshooting

### Backend Issues

#### Django Admin Not Loading

**Problem**: Django admin panel not loading or styles missing.

**Solution**:
```bash
# Collect static files
python manage.py collectstatic

# Or in Docker
docker compose exec backend python manage.py collectstatic --noinput
```

#### Migration Conflicts

**Problem**: Migration conflicts after merging branches.

**Solution**:
```bash
# Show migration conflicts
python manage.py showmigrations

# Resolve conflicts
python manage.py migrate --merge

# Or create new migration
python manage.py makemigrations --merge
```

#### Permission Denied Errors

**Problem**: Permission denied errors when accessing files.

**Solution**:
```bash
# Fix file permissions
chmod -R 755 backend/media
chmod -R 755 backend/staticfiles
```

### Frontend Issues

#### Vite Build Errors

**Problem**: Vite build fails with TypeScript errors.

**Solution**:
```bash
# Type check
npm run type-check

# Fix TypeScript errors
# Then rebuild
npm run build
```

#### Vue Component Errors

**Problem**: Vue component runtime errors.

**Solution**:
1. Check browser console for specific error messages
2. Verify component props and data types
3. Check for missing imports
4. Review Vue DevTools for component state

#### Map Not Rendering

**Problem**: MapLibre GL map not rendering.

**Solution**:
1. Check browser console for WebGL errors
2. Verify map container has height
3. Check tile URL is accessible
4. Ensure MapLibre GL is properly initialized

### Docker Issues

#### Container Won't Start

**Problem**: Docker container fails to start.

**Solution**:
```bash
# Check logs
docker compose logs <service-name>

# Rebuild image
docker compose build --no-cache <service-name>

# Check disk space
df -h
```

#### Volume Mount Issues

**Problem**: Volume mounts not working correctly.

**Solution**:
```bash
# Check volume mounts
docker compose config

# Remove volumes and restart
docker compose down -v
docker compose up
```

#### Network Issues

**Problem**: Services cannot communicate.

**Solution**:
```bash
# Check network
docker network ls
docker network inspect mdvl_default

# Recreate network
docker compose down
docker compose up
```

---

## Useful Development Commands

### Backend Commands

```bash
# Run development server
python manage.py runserver

# Run with ASGI (Daphne) for WebSockets
daphne -b 0.0.0.0 -p 8000 backend.asgi:application

> **Note**: The default development server (`runserver`) is sufficient for most local development. Use Daphne only when testing WebSocket functionality.

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Open Django shell
python manage.py shell

# Collect static files
python manage.py collectstatic

# Run tests
pytest

# Run tests with coverage
pytest --cov

# Check for code issues
flake8
black --check .
```

### Frontend Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run type-check

# Lint code
npm run lint

# Format code
npm run format

# Run unit tests
npm run test:unit
```

### Docker Commands

```bash
# Build images
docker compose build

# Start services
docker compose up

# Start in background
docker compose up -d

# Stop services
docker compose down

# Stop and remove volumes
docker compose down -v

# View logs
docker compose logs -f

# View logs for specific service
docker compose logs -f backend

# Execute command in container
docker compose exec backend <command>

# Rebuild images
docker compose build --no-cache

# Restart services
docker compose restart

# View running containers
docker compose ps

# View resource usage
docker stats
```

### Git Commands

```bash
# Check status
git status

# Stage changes
git add .

# Commit changes
git commit -m "message"

# Push changes
git push

# Pull changes
git pull

# Create branch
git checkout -b feature-name

# Switch branch
git checkout branch-name

# Merge branch
git merge branch-name

# View log
git log
```

---

## Production Notes

### Security Considerations

> **Warning**: Production deployments require careful security configuration. Never deploy with `DEBUG=True` in production.

- [ ] Set DEBUG to False
- [ ] Use secure SECRET_KEY
- [ ] Configure ALLOWED_HOSTS
- [ ] Enable HTTPS
- [ ] Secure database access
- [ ] Configure email backend
- [ ] Enable secure cookie flags

1. **Set DEBUG to False**:
   ```env
   DEBUG=False
   ```

2. **Use secure SECRET_KEY**:
   - Generate a strong random key
   - Never commit `.env` file
   - Use environment variables in production

3. **Configure ALLOWED_HOSTS**:
   ```env
   ALLOWED_HOSTS=your-domain.com,www.your-domain.com
   ```

4. **Use HTTPS**:
   - Configure SSL/TLS certificate
   - Redirect HTTP to HTTPS
   - Use secure cookie flags

5. **Database Security**:
   - Use strong database password
   - Restrict database access
   - Use PostgreSQL in production

6. **Configure Email Backend**:
   ```env
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.your-provider.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@example.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

### Performance Considerations

1. **Use PostgreSQL** instead of SQLite
2. **Configure Redis** for WebSocket channel layer:
   ```env
   REDIS_URL=redis://redis:6379/0
   ```
3. **Use production ASGI server** (Daphne or Gunicorn+Uvicorn)
4. **Serve static files with Nginx**:
   ```nginx
   location /static/ {
       alias /path/to/staticfiles/;
   }
   location /media/ {
       alias /path/to/media/;
   }
   ```
5. **Enable caching**:
   - Redis for caching
   - Browser caching for static assets
   - CDN for static assets

### Deployment Options

#### Traditional VPS

1. Set up server (Ubuntu/Debian recommended)
2. Install Python, Node.js, PostgreSQL, Redis
3. Configure Nginx as reverse proxy
4. Set up systemd services for backend and frontend
5. Configure SSL with Let's Encrypt

#### Docker Deployment

1. Use Docker Compose in production
2. Configure production `.env` file
3. Use external volumes for persistence
4. Configure health checks
5. Set up log rotation

#### Cloud Services

| Service | Providers |
|---------|-----------|
| **Backend** | Heroku, Railway, Render, AWS ECS |
| **Frontend** | Vercel, Netlify, AWS S3 + CloudFront |
| **Database** | AWS RDS, Google Cloud SQL, Railway |
| **Redis** | AWS ElastiCache, Redis Labs |

### Monitoring

1. **Application Monitoring**:
   - Sentry for error tracking
   - New Relic or Datadog for APM

2. **Log Management**:
   - Papertrail, Loggly, or AWS CloudWatch

3. **Uptime Monitoring**:
   - UptimeRobot, Pingdom

4. **Performance Monitoring**:
   - Google Lighthouse
   - WebPageTest

### Backup Strategy

1. **Database Backups**:
   - Regular PostgreSQL dumps
   - Automated backup scripts
   - Off-site storage

2. **Media Backups**:
   - Backup user-uploaded files
   - Use object storage (S3) for media

3. **Configuration Backups**:
   - Version control for configuration
   - Secure storage for secrets

---

## Additional Resources

### Documentation

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Vue.js Documentation](https://vuejs.org/)
- [MapLibre GL](https://maplibre.org/)
- [Docker Documentation](https://docs.docker.com/)

### Community

- [Django Forum](https://forum.djangoproject.com/)
- [Vue.js Forum](https://forum.vuejs.org/)
- [Stack Overflow](https://stackoverflow.com/)

### Tools

- [Django Extensions](https://django-extensions.readthedocs.io/)
- [Vue DevTools](https://devtools.vuejs.org/)
- [Postman](https://www.postman.com/) for API testing

---

## Support

If you encounter issues not covered in this guide:

1. Check the [README.md](./README.md) for project overview
2. Review the troubleshooting section above
3. Check the project's issue tracker (if available)
4. Search for similar issues in the community forums

---

## Summary

This guide covers the complete setup process for MDVL in both local and Docker development modes. Key points:

- **Local Development**: Use SQLite for quick setup without Docker
- **Docker Development**: Use PostgreSQL for production-like environment
- **Environment Variables**: Configure `.env` file for your setup
- **Database**: Run migrations after setup and after model changes
- **Testing**: Use pytest for backend, vitest for frontend
- **Troubleshooting**: Check logs and verify configuration first

For production deployment, ensure proper security measures, monitoring, and backup strategies are in place.
