# Vidyavana Computer Educational Institute — Backend API

Production-ready Django REST Framework backend for the Vidyavana website:
courses, reviews, testimonials, contact, enquiry, FAQ, dashboard statistics,
chatbot, and language support.

## Stack

* Python 3.11+, Django 4.2, Django REST Framework
* PostgreSQL
* JWT authentication (djangorestframework-simplejwt) — architecture ready for
staff/admin-authenticated clients
* django-cors-headers, django-filter, drf-spectacular (OpenAPI docs)
* Structured logging (console + rotating file handlers)

## Project layout

```
config/            Django project (settings, urls, wsgi/asgi)
core/               Shared abstract models, pagination, exception handler,
                    permissions, request-logging middleware
apps/
  languages/        Supported languages (EN, KN, TE, ...)
  courses/          Course categories + courses
  reviews/          Star-rated student reviews (moderation queue)
  testimonials/      Curated homepage testimonial cards
  contact/          "Contact Us" form submissions
  enquiry/          Admission / course-interest leads
  faq/              FAQ categories + entries
  dashboard/        Homepage statistics (live counts + manual overrides)
  chatbot/          Chat sessions/messages + rule-based reply service
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt

cp .env.example .env               # then edit .env with real values
# For local development without PostgreSQL, you can instead set in .env:
#   DB\_ENGINE=django.db.backends.sqlite3
#   DB\_NAME=db.sqlite3

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

API is served at `http://localhost:8000/api/v1/`.

## API documentation

* Swagger UI: `/api/v1/docs/`
* Redoc: `/api/v1/redoc/`
* Raw OpenAPI schema: `/api/v1/schema/`

## Authentication

Public endpoints (GET on courses, reviews, testimonials, FAQ, languages,
dashboard stats; POST on contact, enquiry, chatbot) require no auth.

Admin/write endpoints require a JWT access token:

```bash
POST /api/v1/auth/token/          {"username": "...", "password": "..."}
POST /api/v1/auth/token/refresh/  {"refresh": "..."}
POST /api/v1/auth/token/verify/   {"token": "..."}
```

Send `Authorization: Bearer <access\_token>` on subsequent requests. Only
`is\_staff` users can write to admin-managed resources (courses, FAQ, site
statistics) or read internal ones (enquiry pipeline, contact inbox, chatbot
transcripts, admin dashboard stats).

## Response conventions

**Success (list):**

```json
{
  "success": true,
  "count": 42,
  "total\_pages": 4,
  "current\_page": 1,
  "page\_size": 12,
  "next": "http://.../?page=2",
  "previous": null,
  "results": \[ ... ]
}
```

**Error:**

```json
{
  "success": false,
  "error": {
    "code": "invalid",
    "status\_code": 400,
    "message": "Validation failed",
    "errors": \[ { "field": "email", "message": "Enter a valid email address." } ]
  }
}
```

## Filtering \& search

Every list endpoint supports `?search=`, `?ordering=`, and resource-specific
filters (e.g. `/courses/?category=web-development\&level=beginner\&min\_fee=0\&max\_fee=5000`,
`/enquiry/?status=new\&source=chatbot`). See `/api/v1/docs/` for the full set
per endpoint.

## Logging

Logs write to `logs/vidyavana.log` (all levels) and `logs/errors.log`
(errors only), plus console output. Every `/api/` request is logged with
method, path, status code, and duration via `core.middleware.RequestLoggingMiddleware`.

## Chatbot architecture

`apps/chatbot/services.py` contains a rule-based `generate\_reply()` used as a
placeholder. The endpoint contract (session tracking, intent field, message
history) is already production-shaped — swap that function's internals for a
call to an LLM or external NLU service without touching models, serializers,
or views.

## Production checklist

* Set `DEBUG=False` and a strong, unique `SECRET\_KEY`
* Set real `ALLOWED\_HOSTS` and `CORS\_ALLOWED\_ORIGINS`
* Point `DB\_\*` at your managed PostgreSQL instance
* Run `python manage.py collectstatic`
* Serve with `gunicorn config.wsgi:application`
* Put a reverse proxy (nginx) in front for TLS and static/media serving

