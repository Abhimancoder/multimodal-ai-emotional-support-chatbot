# Security & Privacy Policy

## 1. Secrets Management
- All API keys and database credentials reside exclusively in server-side environment variables loaded via `.env`.
- No credentials are ever passed to the frontend (Streamlit) or committed to git.
- `.env.example` provides the template with empty values.

## 2. File Upload Security
- Inspect actual binary magic bytes (not just extensions) to prevent disguised executable execution.
- File size restrictions: max 5MB for images, max 10MB for audio.
- Files stored with random UUID filenames outside web-accessible roots (`storage/uploads/`).
- Prevent path traversal attacks via strict filename sanitization (`os.path.basename`).

## 3. Database Security
- Parameterized queries via SQLAlchemy ORM (zero string concatenation in SQL).
- Least-privilege database user.

## 4. Privacy & Data Retention
- Audio files and temporary uploads are scheduled for cleanup after processing.
- Logs redact sensitive user inputs and tokens.
