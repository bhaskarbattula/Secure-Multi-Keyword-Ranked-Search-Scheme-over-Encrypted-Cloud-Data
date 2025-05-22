# ✅ signup_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
import os
import json

signup_bp = Blueprint('signup', __name__)

DATA_FILE = 'data/users.json'

def load_users():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_users(users):
    with open(DATA_FILE, 'w') as f:
        json.dump(users, f, indent=4)

@signup_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        users = load_users()
        for user in users:
            if user['username'] == username:
                flash('Username already exists')
                return redirect(url_for('signup.signup'))

        users.append({
            'username': username,
            'password': password,
            'role': role
        })
        save_users(users)
        flash('Signup successful. Please log in.')
        return redirect(url_for('main.login'))

    return render_template('signup.html')
