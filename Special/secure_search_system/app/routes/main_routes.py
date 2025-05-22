# Updated: main_routes.py
from flask import Blueprint, render_template, request, redirect, session
import json
import os

main_bp = Blueprint("main", __name__)

USER_DB = "data/users.json"

if not os.path.exists(USER_DB):
    with open(USER_DB, "w") as f:
        json.dump({
            "admins": [{"username": "admin1", "password": "adminpass"}],
            "users": [{"username": "user1", "password": "userpass"}],
            "auths": [{"username": "auth1", "password": "authpass"}]
        }, f, indent=4)

# Home page (NO login)
@main_bp.route("/")
def home():
    return render_template("home.html")

# Data Owner login
@main_bp.route("/data_owner_login", methods=["GET", "POST"])
def data_owner_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        with open(USER_DB) as f:
            data = json.load(f)
        for admin in data["admins"]:
            if admin["username"] == username and admin["password"] == password:
                session["username"] = username
                session["role"] = "admin"
                return redirect("/admin")
        return render_template("data_owner_login.html", error="❌ Invalid credentials")
    return render_template("data_owner_login.html")

# Data User login
@main_bp.route("/data_user_login", methods=["GET", "POST"])
def data_user_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        with open(USER_DB) as f:
            data = json.load(f)
        for user in data["users"]:
            if user["username"] == username and user["password"] == password:
                session["username"] = username
                session["role"] = "user"
                return redirect("/user")
        return render_template("data_user_login.html", error="❌ Invalid credentials")
    return render_template("data_user_login.html")

# Server Admin login
@main_bp.route("/server_admin_login", methods=["GET", "POST"])
def server_admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        with open(USER_DB) as f:
            data = json.load(f)
        for auth in data["auths"]:
            if auth["username"] == username and auth["password"] == password:
                session["username"] = username
                session["role"] = "auth"
                return redirect("/auth")
        return render_template("server_admin_login.html", error="❌ Invalid credentials")
    return render_template("server_admin_login.html")

@main_bp.route("/register", methods=["GET"])
def new_registration():
    return render_template("new_registration.html")



@main_bp.route("/user/register", methods=["GET", "POST"])
def user_register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        with open(USER_DB, "r") as f:
            data = json.load(f)

        for user in data["users"]:
            if user["username"] == username:
                return render_template("user_register.html", error="Username already exists")

        data["users"].append({"username": username, "password": password})

        with open(USER_DB, "w") as f:
            json.dump(data, f, indent=4)

        return redirect("/")

    return render_template("user_register.html")

@main_bp.route("/admin/register", methods=["GET", "POST"])
def admin_register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        with open(USER_DB, "r") as f:
            data = json.load(f)

        for admin in data["admins"]:
            if admin["username"] == username:
                return render_template("admin_register.html", error="Username already exists")

        data["admins"].append({"username": username, "password": password})

        with open(USER_DB, "w") as f:
            json.dump(data, f, indent=4)

        return redirect("/")

    return render_template("admin_register.html")



# Logout
@main_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")
