# Copilot / AI Agent Instructions for `confsite` project

Summary
- This is a Django (5.2.6) monolith named `confsite` with multiple apps: `ConferenceApp`, `UserApp`, `SessionApp`, `SessionAppApi` and `securityConfigApp`.
- Main responsibilities: web UI for conferences/submissions (`ConferenceApp`), custom user model and auth (`UserApp`), session data (`SessionApp`) and a small DRF API (`SessionAppApi`) protected by JWT via `securityConfigApp`.

Quick start (Windows PowerShell)
- Activate the virtualenv: `.\.venv\Scripts\Activate.ps1` (or run `.\.venv\Scripts\activate.bat` in cmd).
- Run migrations: `py manage.py makemigrations; py manage.py migrate`.
- Run server: `py manage.py runserver`.
- Create superuser: `py manage.py createsuperuser`.

Key files & locations
- Project settings: `confsite/settings.py` (DB: sqlite3, `AUTH_USER_MODEL="UserApp.User"`, template dir `confsite/Templates`).
- Root URLs: `confsite/urls.py` — mounts app routes at `conferences/`, `user/`, `api/`, and `security/`.
- Templates: `confsite/Templates` and per-app templates under `confsite/Templates/conferences/` and submissions.
- Virtual env: `.venv/` (scripts present for Windows).

Important behaviors & conventions (codebase-specific)
- Custom primary keys: `User.user_id`, `Conference.conference_id`, and `Submission.submission_id` are generated in model `save()` methods (prefixed strings like `USER...`, `SUB...`). Preserve and follow these generators when creating fixtures or seeding data.
- Email domain restriction: `UserApp.verify_email` enforces specific domains (e.g. `esprit.tn`, `seasame.com`, `tek.tn`, `central.net`). Test accounts must use allowed domains or bypass validation explicitly in tests.
- Authentication: project uses Django auth for web views and DRF + `rest_framework_simplejwt` for API auth. `SIMPLE_JWT` is configured in `settings.py` (ACCESS_TOKEN_LIFETIME = 5 minutes, `SIGNING_KEY` set to `SECRET_KEY`).
- Login flows: `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL`, and `LOGIN_URL` are set in `settings.py` — many views use `LoginRequiredMixin`.
- Views: mix of function views and class-based generic views (`ListView`, `DetailView`, `CreateView`, etc.). Follow existing patterns (use `form_class`/`fields`, `success_url`, override `form_valid` to attach `request.user` when needed).

API notes
- DRF router in `SessionAppApi/urls.py` registers `sessions` (accessible at `/api/sessions/`).
- JWT endpoints live under `security/` (e.g. `/security/api/token/`). Use POST `{username, password}` to get tokens, then set header `Authorization: Bearer <access>`.

Cross-app interactions & pitfalls
- `ConferenceApp.Submission.user` references `UserApp.User` and `SessionAppApi` serializes `SessionApp.models.Session` — be careful with circular imports when editing imports across apps.
- Model validation exists (e.g., `Conference.clean` ensures `start_date <= end_date`) — creating objects programmatically should call `full_clean()` where appropriate.

Examples (concrete snippets to reference)
- Custom user model: `AUTH_USER_MODEL = "UserApp.User"` (settings.py).
- JWT routes: `/security/api/token/`, `/security/api/token/refresh/` (see `securityConfigApp/urls.py`).
- Router registration: `router.register('sessions', SessionViewSet)` (see `SessionAppApi/urls.py`).

Testing & debugging tips
- Use `py manage.py runserver` and watch stack traces in console (DEBUG=True in settings).
- Tests: `py manage.py test` (no custom test runner configured). If tests hit validation rules, use allowed email domains and ensure generated IDs don't conflict with manual fixtures.
- DB: sqlite file `db.sqlite3` at project root — quick to reset by deleting/migrating.

Language & messaging
- The codebase mixes French and English (error messages, template text). Preserve existing language when editing localized strings.

When making changes
- Follow existing view patterns (generic CBVs + `LoginRequiredMixin`).
- Avoid changing `SECRET_KEY` or `SIMPLE_JWT['SIGNING_KEY']` unless rotating secrets for production; note tests may rely on current settings.
- If adding APIs, register via `SessionAppApi` router pattern and protect with JWT when appropriate.

If anything is unclear or you want examples for a specific task (tests, new API, seed data), tell me which area to expand.
