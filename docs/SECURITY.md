# Security / Seguridad

## Secrets live outside the app

```
%USERPROFILE%\.gmailbot\.env
```

Never put real App Passwords or API keys in the project folder, especially if that folder syncs with OneDrive or Dropbox.

## Never commit

- `.env` (only `.env.example` with placeholders)
- `data/`, `ghosttown/`, `attachments/`
- Real email files or attachments
- `credentials*.json`, `token*.json`, `*.key`, `*.pem`

This repo ships a `.gitignore` and a pre-commit hook that blocks those paths.

## Setup tip

1. Copy `.env.example` → `%USERPROFILE%\.gmailbot\.env`
2. Fill in your Gmail + App Password there
3. Run `GhostTown.bat`

If an App Password ever lived inside OneDrive, revoke it and create a new one.
