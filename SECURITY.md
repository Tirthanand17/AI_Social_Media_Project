# Security Notes

This project is a prototype that can be deployed privately for demo or internship review. Before using it as a real live product, complete the checklist below.

## Required before production

- Set `DEMO_LOGIN_ENABLED=false`.
- Change `APP_SECRET` to a long random secret.
- Use environment variables for all passwords and API keys.
- Prefer `*_PASSWORD_HASH` and `*_PASSWORD_SALT` instead of plain role passwords.
- Restrict `ALLOWED_ORIGINS` to your real frontend domain.
- Keep `POSTING_MODE=dry_run` until each platform API is tested safely.
- Never commit `.env`, API keys, access tokens, model secrets, or personal data.

## Generate password hash

```bash
python -c "from api.auth import make_password_hash; print(make_password_hash('your_password'))"
```

Copy the generated `salt` and `hash` into `.env`:

```env
ADMIN_PASSWORD_HASH=generated_hash
ADMIN_PASSWORD_SALT=generated_salt
```

## Demo accounts

Demo passwords exist only for local testing. Do not keep them enabled in production.
