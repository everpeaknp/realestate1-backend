# Realtor Pal Backend

Django REST API backend for the Realtor Pal real estate platform with Jazzmin admin theme.

## Features

- **Properties Management**: Full CRUD for property listings with search and filters
- **Lead Management**: Contact forms, property inquiries, newsletter subscriptions
- **Blog System**: Blog posts with comments and approval workflow
- **Testimonials**: Client reviews with approval system
- **Projects**: Showcase completed projects
- **FAQs**: Frequently asked questions management
- **Agents**: Real estate agent profiles
- **Jazzmin Admin**: Beautiful, modern admin interface
- **API Documentation**: Auto-generated Swagger/OpenAPI docs

## Tech Stack

- **Framework**: Django 5.1.5
- **API**: Django REST Framework 3.15.2
- **Admin Theme**: Django Jazzmin 3.0.1
- **Database**: SQLite (default) / PostgreSQL (production)
- **API Docs**: drf-spectacular 0.28.0

## Installation

### Prerequisites

- Python 3.10+
- pip
- virtualenv (recommended)

### Setup Steps

1. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment variables**
   
   Copy `.env.example` to `.env` and configure:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your settings:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   
   # Database (optional - defaults to SQLite)
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=realtor_pal
   DB_USER=postgres
   DB_PASSWORD=your-password
   DB_HOST=localhost
   DB_PORT=5432
   
   # CORS
   CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   
   # Email (optional)
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver 5001
   ```

The API will be available at `http://localhost:5001`

## API Endpoints

### Properties
- `GET /api/properties/` - List all properties
- `GET /api/properties/{slug}/` - Get property by slug
- `GET /api/properties/featured/` - Get featured properties
- `GET /api/properties/search/` - Search properties

### Leads
- `POST /api/leads/contact/` - Submit contact form
- `POST /api/leads/property-inquiry/` - Property inquiry
- `POST /api/leads/newsletter/` - Newsletter subscription

### Blog
- `GET /api/blog/posts/` - List all blog posts
- `GET /api/blog/posts/{slug}/` - Get single post
- `POST /api/blog/comments/` - Submit comment
- `GET /api/blog/comments/?post_id={id}` - Get comments for post

### Testimonials
- `GET /api/testimonials/` - List all testimonials
- `POST /api/testimonials/` - Submit testimonial
- `GET /api/testimonials/featured/` - Get featured testimonials
- `GET /api/testimonials/video/` - Get video testimonials

### Projects
- `GET /api/projects/` - List all projects
- `GET /api/projects/{id}/` - Get single project
- `GET /api/projects/featured/` - Get featured projects

### FAQs
- `GET /api/faqs/` - List all FAQs
- `GET /api/faqs/categories/` - Get all categories
- `GET /api/faqs/by_category/?category={name}` - Get FAQs by category

### Agents
- `GET /api/agents/` - List all agents
- `GET /api/agents/{id}/` - Get single agent

## Admin Interface

Access the Jazzmin admin at: `http://localhost:5001/admin/`

Features:
- Modern, responsive design
- Dark mode support
- Advanced search and filters
- Bulk actions
- Custom dashboard
- API documentation link

## API Documentation

Interactive API documentation available at:
- Swagger UI: `http://localhost:5001/api/schema/swagger-ui/`
- OpenAPI Schema: `http://localhost:5001/api/schema/`

## Project Structure

```
backend/
├── realtor_pal/          # Project settings
│   ├── settings.py       # Django settings
│   ├── urls.py           # Main URL configuration
│   └── wsgi.py           # WSGI configuration
├── properties/           # Properties app
├── leads/                # Leads management app
├── blog/                 # Blog system app
├── testimonials/         # Testimonials app
├── projects/             # Projects showcase app
├── faqs/                 # FAQs app
├── agents/               # Agents app
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
└── .env.example          # Environment variables template
```

## Development

### Running Tests
```bash
python manage.py test
```

### Create Migrations
```bash
python manage.py makemigrations
```

### Apply Migrations
```bash
python manage.py migrate
```

### Collect Static Files
```bash
python manage.py collectstatic
```

### Create Sample Data
```bash
python manage.py shell
# Then run your data creation scripts
```

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Configure production database (PostgreSQL recommended)
3. Set up proper `SECRET_KEY`
4. Configure `ALLOWED_HOSTS`
5. Set up static file serving (WhiteNoise or CDN)
6. Configure email backend
7. Set up HTTPS
8. Use gunicorn or uWSGI as WSGI server

Example with gunicorn:
```bash
pip install gunicorn
gunicorn realtor_pal.wsgi:application --bind 0.0.0.0:5001
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | (required) |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1` |
| `DB_ENGINE` | Database engine | `django.db.backends.sqlite3` |
| `DB_NAME` | Database name | `db.sqlite3` |
| `CORS_ALLOWED_ORIGINS` | CORS origins | `http://localhost:3000` |
| `EMAIL_BACKEND` | Email backend | `console` |

## Support

For issues and questions, please contact the development team.

## License

Proprietary - All rights reserved
