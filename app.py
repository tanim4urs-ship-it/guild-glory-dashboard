import os
import sqlite3
from functools import wraps
from flask import Flask, request, redirect, url_for, session, render_template_string, flash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-before-deploying")
DB_PATH = os.environ.get("DB_PATH", "guild_glory.db")
DASHBOARD_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "change-me")

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT NOT NULL,
                player_uid TEXT DEFAULT '',
                glory INTEGER NOT NULL DEFAULT 0,
                daily_target INTEGER NOT NULL DEFAULT 100,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

init_db()

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

LOGIN_PAGE = """
<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Guild Glory • Login</title>
<style>
*{box-sizing:border-box}body{margin:0;min-height:100vh;display:grid;place-items:center;background:#0b1020;color:#f5f7ff;font-family:system-ui,Arial;padding:20px}
.card{width:min(420px,100%);background:#151d33;border:1px solid #2b3858;border-radius:20px;padding:28px}
h1{margin:0 0 8px;font-size:26px}p{color:#aebbd5}input,button{width:100%;padding:13px;border-radius:10px;margin-top:12px;font-size:16px}
input{background:#0b1020;color:white;border:1px solid #364565}button{background:#72e0b5;border:0;font-weight:700;cursor:pointer}
.error{color:#ff9b9b}
</style></head><body><div class="card"><h1>Guild Glory</h1><p>Sign in to your private tracking dashboard.</p>
{% for msg in get_flashed_messages() %}<p class="error">{{msg}}</p>{% endfor %}
<form method="post"><input name="password" type="password" placeholder="Dashboard password" required autofocus>
<button type="submit">Sign in</button></form></div></body></html>
"""

DASHBOARD = """
<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Guild Glory Dashboard</title>
<style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#0b1020;color:#f5f7ff;font-family:system-ui,Arial}
header{padding:22px clamp(16px,4vw,44px);border-bottom:1px solid #24314f;display:flex;gap:16px;align-items:center;justify-content:space-between;flex-wrap:wrap}
h1{margin:0;font-size:clamp(22px,4vw,32px)}.muted{color:#aebbd5}.wrap{max-width:1100px;margin:auto;padding:24px clamp(14px,4vw,40px)}
.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-bottom:22px}
.card{background:#151d33;border:1px solid #2b3858;border-radius:16px;padding:18px;min-width:0}
.metric{font-size:28px;font-weight:800;margin-top:8px}.formgrid{display:grid;grid-template-columns:2fr 1.4fr 1fr 1fr auto;gap:10px}
input{min-width:0;width:100%;padding:11px;border-radius:9px;border:1px solid #364565;background:#0b1020;color:#fff}
button,.btn{padding:11px 14px;border-radius:9px;border:0;background:#72e0b5;color:#08131a;font-weight:750;cursor:pointer;text-decoration:none;display:inline-block}
.btn.secondary{background:#263553;color:#fff}.danger{background:#61303b;color:#fff}
table{width:100%;border-collapse:collapse;margin-top:12px}th,td{text-align:left;padding:12px 8px;border-bottom:1px solid #2b3858}th{color:#aebbd5;font-size:13px}
.progress{height:7px;background:#263553;border-radius:99px;overflow:hidden;margin-top:7px}.bar{height:100%;background:#72e0b5}
.flash{padding:12px;border-radius:10px;background:#203d3a;margin-bottom:12px}
.small{font-size:13px}.top-actions{display:flex;gap:10px;align-items:center}
@media(max-width:760px){.grid{grid-template-columns:1fr}.formgrid{grid-template-columns:1fr 1fr}.formgrid button{grid-column:1/-1}table,tbody,tr,td{display:block}thead{display:none}tr{padding:12px 0;border-bottom:1px solid #2b3858}td{border:0;padding:5px 0}td:before{content:attr(data-label) ": ";color:#aebbd5;font-weight:600}.top-actions{width:100%;justify-content:space-between}}
</style></head><body>
<header><div><h1>🔥 Guild Glory</h1><div class="muted">Guild progress tracker</div></div>
<div class="top-actions"><span class="muted small">Manual tracking mode</span><a class="btn secondary" href="{{url_for('logout')}}">Log out</a></div></header>
<main class="wrap">
{% for msg in get_flashed_messages() %}<div class="flash">{{msg}}</div>{% endfor %}
<section class="grid">
<div class="card"><div class="muted">Tracked members</div><div class="metric">{{members|length}}</div></div>
<div class="card"><div class="muted">Total recorded Glory</div><div class="metric">{{total_glory}}</div></div>
<div class="card"><div class="muted">Members at daily target</div><div class="metric">{{on_target}}</div></div>
</section>
<section class="card"><h2>Add guild member</h2><p class="muted small">Enter values you have verified in-game. This dashboard does not connect to Free Fire or farm Glory automatically.</p>
<form class="formgrid" method="post" action="{{url_for('add_member')}}">
<input name="player_name" placeholder="Player name" required maxlength="60">
<input name="player_uid" placeholder="Player UID (optional)" maxlength="40">
<input name="glory" type="number" min="0" placeholder="Glory" value="0" required>
<input name="daily_target" type="number" min="0" placeholder="Daily target" value="100" required>
<button type="submit">Add member</button></form></section>
<section class="card" style="margin-top:18px"><h2>Guild members</h2>
{% if members %}
<table><thead><tr><th>Player</th><th>UID</th><th>Glory</th><th>Daily target progress</th><th>Update Glory</th><th></th></tr></thead><tbody>
{% for m in members %}
<tr><td data-label="Player"><strong>{{m.player_name}}</strong><div class="muted small">Updated {{m.updated_at}}</div></td>
<td data-label="UID">{{m.player_uid or '—'}}</td><td data-label="Glory">{{m.glory}}</td>
<td data-label="Progress"><div>{{m.glory}} / {{m.daily_target}}</div><div class="progress"><div class="bar" style="width:{{[100, (m.glory * 100 / (m.daily_target if m.daily_target > 0 else 1))]|min}}%"></div></div></td>
<td data-label="Update Glory"><form method="post" action="{{url_for('update_member', member_id=m.id)}}" style="display:flex;gap:6px"><input name="glory" type="number" min="0" value="{{m.glory}}" required aria-label="New Glory"><button type="submit">Save</button></form></td>
<td data-label="Delete"><form method="post" action="{{url_for('delete_member', member_id=m.id)}}" onsubmit="return confirm('Delete this member?')"><button class="danger" type="submit">Delete</button></form></td></tr>
{% endfor %}</tbody></table>
{% else %}<p class="muted">No members yet. Add your first guild member above.</p>{% endif %}
</section>
<p class="muted small" style="margin-top:18px">Tip: set a strong dashboard password in your hosting environment. For durable cloud storage, attach a persistent disk or connect a managed database before relying on this for long-term records.</p>
</main></body></html>
"""

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password", "") == DASHBOARD_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("index"))
        flash("Incorrect password.")
    return render_template_string(LOGIN_PAGE)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
@login_required
def index():
    with db() as conn:
        members = conn.execute("SELECT * FROM members ORDER BY glory DESC, player_name COLLATE NOCASE").fetchall()
    total_glory = sum(m["glory"] for m in members)
    on_target = sum(1 for m in members if m["glory"] >= m["daily_target"])
    return render_template_string(DASHBOARD, members=members, total_glory=total_glory, on_target=on_target)

@app.route("/add", methods=["POST"])
@login_required
def add_member():
    name = request.form.get("player_name", "").strip()
    uid = request.form.get("player_uid", "").strip()
    try:
        glory = max(0, int(request.form.get("glory", "0")))
        target = max(0, int(request.form.get("daily_target", "100")))
    except ValueError:
        flash("Glory and target must be whole numbers.")
        return redirect(url_for("index"))
    if not name:
        flash("Player name is required.")
        return redirect(url_for("index"))
    with db() as conn:
        conn.execute("INSERT INTO members (player_name, player_uid, glory, daily_target, updated_at) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)", (name, uid, glory, target))
    flash(f"Added {name}.")
    return redirect(url_for("index"))

@app.route("/update/<int:member_id>", methods=["POST"])
@login_required
def update_member(member_id):
    try:
        glory = max(0, int(request.form.get("glory", "0")))
    except ValueError:
        flash("Glory must be a whole number.")
        return redirect(url_for("index"))
    with db() as conn:
        conn.execute("UPDATE members SET glory=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (glory, member_id))
    flash("Glory updated.")
    return redirect(url_for("index"))

@app.route("/delete/<int:member_id>", methods=["POST"])
@login_required
def delete_member(member_id):
    with db() as conn:
        conn.execute("DELETE FROM members WHERE id=?", (member_id,))
    flash("Member deleted.")
    return redirect(url_for("index"))

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))
