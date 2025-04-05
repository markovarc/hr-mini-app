from flask import Flask, render_template, request, redirect, url_for
import json, os
from datetime import datetime
from google_sheets import add_to_all, add_to_approved

app = Flask(__name__)
DATA_FILE = "data.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route("/")
def recruiter_view():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    data = load_data()
    entry = {
        "id": len(data) + 1,
        "recruiter": request.form.get("recruiter", "Неизвестный"),
        "referral": {
            "name": request.form.get("name", "-"),
            "phone": request.form.get("phone", "-"),
            "citizenship": request.form.get("citizenship", "-"),
            "city": request.form.get("city", "-"),
            "dob": request.form.get("dob", "-")
        },
        "status": "Новая",
        "created_at": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "chat": [],
        "comments": []
    }
    data.append(entry)
    save_data(data)

    # Добавим в Google Таблицу (все заявки)
    add_to_all([
        entry["recruiter"],
        entry["referral"]["name"],
        entry["referral"]["phone"],
        entry["referral"]["city"],
        entry["referral"]["dob"],
        entry["referral"]["citizenship"],
        entry["status"],
        entry["created_at"]
    ])
    return redirect("/thanks")

@app.route("/thanks")
def thanks():
    return "✅ Заявка отправлена! Ожидайте модератора."

@app.route("/admin", methods=["GET", "POST"])
def admin():
    data = load_data()

    if request.method == "POST":
        id = int(request.form.get("id"))
        action = request.form.get("action")
        comment = request.form.get("comment", "").strip()

        for item in data:
            if item["id"] == id:
                if action == "accept":
                    item["status"] = "Принята"
                    add_to_approved([
                        item["recruiter"],
                        item["referral"]["name"],
                        item["referral"]["phone"],
                        item["referral"]["city"],
                        item["referral"]["dob"],
                        item["referral"]["citizenship"],
                        "Принята",
                        item["created_at"]
                    ])
                elif action == "reject":
                    item["status"] = "Отклонена"
                elif action == "checking":
                    item["status"] = "На проверке"

                if comment:
                    item["comments"].append({"role": "admin", "text": comment})

        save_data(data)
        return redirect("/admin")

    return render_template("admin.html", entries=data)

@app.route("/recruiter", methods=["GET", "POST"])
def recruiter_panel():
    data = load_data()
    recruiter_name = request.args.get("name")

    if request.method == "POST":
        id = int(request.form.get("id"))
        message = request.form.get("message")
        for item in data:
            if item["id"] == id:
                item["comments"].append({"role": "recruiter", "text": message})
                break
        save_data(data)
        return redirect(url_for("recruiter_panel", name=recruiter_name))

    filtered = [x for x in data if x["recruiter"].lower() == recruiter_name.lower()]
    return render_template("recruiter.html", entries=filtered, name=recruiter_name)

@app.route("/delete", methods=["POST"])
def delete():
    id = int(request.form.get("id"))
    name = request.form.get("name")
    data = load_data()
    data = [d for d in data if d["id"] != id]
    save_data(data)
    return redirect(url_for("recruiter_panel", name=name))
