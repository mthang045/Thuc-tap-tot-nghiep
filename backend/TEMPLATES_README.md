Dynamic Template Generation
===========================

Overview
--------
The backend dynamically generates contract template files (DOCX/PDF) on demand when a Pro or Admin user requests a download. Files are created under `backend/static/templates/` and served as attachments.

Behavior
--------
- Endpoint: `GET /api/templates/<template_id>/download`
- Authorization: Requires a valid JWT in the `Authorization: Bearer <token>` header.
- Permissions: Only users with `subscription_tier` == `pro` or users with `is_admin: true` can trigger generation/download.
- Generation: If the requested file does not exist, the server will generate a mock DOCX or PDF using `python-docx` and `reportlab` and save it to `backend/static/templates/` for future requests.

Extensibility
-------------
The generator logic lives in `backend/template_generator.py` with functions:

- `generate_template_file(template_id, output_path, context=None)` — creates a DOCX or PDF using mock content.
- `build_mock_content(template_id, context=None)` — returns the textual mock content (useful to replace with real AI output later).

Next steps
----------
- Replace mock content generation with AI analysis results when generating final reports.
- Add logging and usage metrics for template generation events.

Requirements
------------
Ensure the backend virtualenv has the following packages installed (already added to `backend/requirements-flask.txt`):

- `python-docx`
- `reportlab`
