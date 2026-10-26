# Free Fire Guild Glory Tracker (starter)

A responsive, password-protected manual Glory tracking dashboard built with Flask and SQLite.

## Run locally (Windows)
1. Install Python 3.11+ and Git (optional).
2. Extract this folder and open it in VS Code.
3. In the VS Code terminal:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   $env:SECRET_KEY = "replace-with-a-long-random-secret"
   $env:DASHBOARD_PASSWORD = "choose-a-strong-password"
   py app.py
   ```
4. Visit http://127.0.0.1:10000

If PowerShell blocks activation, use `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` and then `.\.venv\Scripts\python.exe app.py`.

## Deploy to Render
1. Create a GitHub account and a new repository.
2. Upload `app.py`, `requirements.txt`, and `render.yaml` to the repository.
3. In Render, choose **New + > Blueprint**, connect the repository, and deploy.
4. Render will ask for `DASHBOARD_PASSWORD`; enter a strong, unique password.
5. The included `render.yaml` requests a persistent disk at `/var/data`. Persistent disks generally require a paid Render service, so check current pricing before deploying. If you choose a free instance without a persistent disk, local SQLite data may be lost when the service restarts or redeploys.
6. After deployment, open the Render URL and sign in with your dashboard password.

## Important
- This is a tracking dashboard, not a Free Fire client, gameplay bot, or official API integration.
- Add/update Glory manually using verified in-game values.
- Never put game passwords, session tokens, or private account credentials in this project.
- Keep `SECRET_KEY` and `DASHBOARD_PASSWORD` private.
- For a more robust production setup, use a managed database and consider adding CSRF protection and rate limiting before sharing it publicly.
