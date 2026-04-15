## Unreleased

- feat: Dynamic template generation for Pro/Admin users
  - Added `backend/template_generator.py` to generate DOCX/PDF templates on demand.
  - `GET /api/templates/<id>/download` now requires JWT and only allows `subscription_tier: pro` or `is_admin: true` to generate/download templates.
  - Templates are saved to `backend/static/templates/` on first generation.
  - Added `reportlab` to backend requirements for PDF generation.
