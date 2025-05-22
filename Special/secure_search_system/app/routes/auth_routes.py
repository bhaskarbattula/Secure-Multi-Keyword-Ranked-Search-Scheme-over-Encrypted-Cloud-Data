from flask import Blueprint, render_template, redirect, session, json
import os

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

USER_FILE = "data/users.json"
LOG_FILE = "data/logs.json"
ENCRYPTED_DIR = "data/encrypted_docs"

# 🔐 Auth Dashboard
@auth_bp.route("/", methods=["GET"])
def show_auth_dashboard():
    if session.get("role") != "auth":
        return redirect("/")
    return render_template("dashboard_auth.html")


# 📩 View Access Requests
@auth_bp.route("/requests", methods=["GET"])
def view_all_requests():
    if session.get("role") != "auth":
        return redirect("/")

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            json.dump({"files": [], "requests": []}, f)

    with open(LOG_FILE, "r") as f:
        logs = json.load(f)

    requests = logs.get("requests", [])
    return render_template("auth_requests.html", requests=requests)


# 👥 View All Registered Users and Admins
@auth_bp.route("/users")
def view_all_users():
    with open("data/users.json", "r") as f:
        data = json.load(f)

    users = data.get("users", [])

    return render_template("auth_users.html", users=users)

@auth_bp.route("/admins")
def view_all_admins():
    with open("data/users.json", "r") as f:
        data = json.load(f)

    admins = data.get("admins", [])


    return render_template("auth_admins.html", admins=admins)

# 📂 View All Encrypted Files
@auth_bp.route("/files", methods=["GET"])
def view_all_encrypted_files():
    if session.get("role") != "auth":
        return redirect("/")

    if not os.path.exists(ENCRYPTED_DIR):
        os.makedirs(ENCRYPTED_DIR)

    files = os.listdir(ENCRYPTED_DIR)
    return render_template("auth_files.html", files=files)
