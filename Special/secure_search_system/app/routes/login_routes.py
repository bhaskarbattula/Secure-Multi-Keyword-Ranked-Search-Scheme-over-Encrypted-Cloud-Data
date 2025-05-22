from flask import Blueprint, render_template, request, redirect, session
import json
import os

login_bp = Blueprint("login", __name__)

USER_DB = "data/users.json"

if not os.path.exists(USER_DB):
    with open(USER_DB, "w") as f:
        json.dump({
            "admins": [{"username": "admin1", "password": "adminpass"}],
            "users": [{"username": "user1", "password": "userpass"}],
            "auths": [{"username": "auth1", "password": "authpass"}]
        }, f, indent=4)


# Data Owner Login
@login_bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
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
        return render_template("admin_login.html", error="❌ Invalid credentials")
    return render_template("admin_login.html")


# Data User Login
@login_bp.route("/user/login", methods=["GET", "POST"])
def user_login():
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
        return render_template("user_login.html", error="❌ Invalid credentials")
    return render_template("user_login.html")


# Server Admin Login
@login_bp.route("/auth/login", methods=["GET", "POST"])
def auth_login():
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
        return render_template("auth_login.html", error="❌ Invalid credentials")
    return render_template("auth_login.html")


# Logout
@login_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")
