from flask import Flask, request, render_template, redirect, session
import json, uuid
from functools import wraps

app = Flask(__name__)
app.secret_key = "secret123"

DATA_FILE = "data.json"
CONFIG_FILE = "config.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin"):
            return redirect("/admin/login")
        return f(*args, **kwargs)
    return decorated

@app.route("/", methods=["GET", "POST"])
def form_page():
    submitted = False
    if request.method == "POST":
        form = request.form
        entry = {
            "id": str(uuid.uuid4())[:8],
            "recruiter": form.get("recruiter"),
            "referral": {
                "name": form.get("name") or "-",
                "phone": form.get("phone") or "-",
                "citizenship": form.get("citizenship") or "-",
                "city": form.get("city") or "-",
                "dob": form.get("dob") or "-"
            },
            "status": "new",
            "chat": [],
            "deleted": False
        }
        db = load_data()
        db.append(entry)
        save_data(db)
        submitted = True
    return render_template("form.html", submitted=submitted)

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/recruiter_lookup")
def recruiter_lookup():
    return render_template("recruiter_lookup.html")

@app.route("/submit", methods=["POST"])
def submit():
    return redirect("/")

@app.route("/recruiter")
def recruiter_panel():
    name = request.args.get("name", "").strip()
    db = load_data()
    my = [e for e in db if e["recruiter"].lower() == name.lower() and not e["deleted"]]
    return render_template("recruiter.html", name=name, entries=my)

@app.route("/edit/<id>", methods=["POST"])
def edit_entry(id):
    db = load_data()
    for e in db:
        if e["id"] == id and e["status"] == "new":
            e["referral"]["name"] = request.form.get("name")
            e["referral"]["phone"] = request.form.get("phone")
            e["referral"]["citizenship"] = request.form.get("citizenship")
            e["referral"]["city"] = request.form.get("city")
            e["referral"]["dob"] = request.form.get("dob")
    save_data(db)
    return redirect(f"/recruiter?name={e['recruiter']}")

@app.route("/delete/<id>")
def delete_entry(id):
    db = load_data()
    for e in db:
        if e["id"] == id:
            e["deleted"] = True
    save_data(db)
    return redirect("/admin")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        pwd = request.form.get("password")
        cfg = load_config()
        if pwd == cfg.get("admin_password"):
            session["admin"] = True
            return redirect("/admin")
        else:
            return "❌ Неверный пароль"
    return '''
    <h2>🔐 Вход для администратора</h2>
    <form method="POST">
        Пароль: <input name="password" type="password">
        <button>Войти</button>
    </form>
    '''

@app.route("/admin")
@admin_required
def admin():
    db = load_data()
    tab = request.args.get("tab", "new")
    if tab == "new":
        entries = [e for e in db if e["status"] == "new" and not e["deleted"]]
    elif tab == "checking":
        entries = [e for e in db if e["status"] == "checking" and not e["deleted"]]
    elif tab == "accepted":
        entries = [e for e in db if e["status"] == "accepted" and not e["deleted"]]
    elif tab == "rejected":
        entries = [e for e in db if e["status"] == "rejected" and not e["deleted"]]
    elif tab == "trash":
        entries = [e for e in db if e["deleted"]]
    else:
        entries = db
    return render_template("admin.html", entries=entries, tab=tab)

@app.route("/status/<id>/<action>")
@admin_required
def update_status(id, action):
    db = load_data()
    for e in db:
        if e["id"] == id:
            if action in ["checking", "accepted", "rejected"]:
                e["status"] = action
    save_data(db)
    return redirect("/admin")

@app.route("/comment/<id>", methods=["POST"])
@admin_required
def comment(id):
    msg = request.form.get("msg")
    db = load_data()
    for e in db:
        if e["id"] == id:
            e["chat"].append({"from": "admin", "text": msg})
    save_data(db)
    return redirect("/admin")

@app.route("/recruiter_comment/<id>", methods=["POST"])
def recruiter_comment(id):
    msg = request.form.get("msg")
    db = load_data()
    for e in db:
        if e["id"] == id:
            e["chat"].append({"from": "recruiter", "text": msg})
            return redirect(f"/recruiter?name={e['recruiter']}")
    save_data(db)
    return "❌ Не найдено"

@app.route("/clear_trash")
@admin_required
def clear_trash():
    db = load_data()
    db = [e for e in db if not e["deleted"]]
    save_data(db)
    return redirect("/admin?tab=trash")

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
