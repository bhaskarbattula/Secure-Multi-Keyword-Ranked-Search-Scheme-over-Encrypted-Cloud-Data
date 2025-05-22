from flask import Blueprint, render_template, request, session, redirect, flash
from datetime import datetime
import os
import json
import pickle
from werkzeug.utils import secure_filename
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from app.utils.encryption import encrypt_text_file, decrypt_text_file
from app.utils.encryption import TreeNode, generate_secret_key, encrypt_tree, generate_key
from app.utils.encryption import encrypt_key
import base64


admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect("/")
    return render_template("dashboard_admin.html")


@admin_bp.route("/admin/upload", methods=["GET", "POST"])
def upload_file():
    if session.get("role") != "admin":
        return redirect("/")

    if request.method == "POST":
        file = request.files["document"]
        if file:
            filename = secure_filename(file.filename)
            path = os.path.join("data/raw_docs", filename)
            os.makedirs("data/raw_docs", exist_ok=True)
            file.save(path)

            # Log upload
            log_path = "data/logs.json"
            with open(log_path, "r") as f:
                logs = json.load(f)

            logs["files"].append({
                "filename": filename,
                "uploaded_by": session.get("username")
            })

            with open(log_path, "w") as f:
                json.dump(logs, f, indent=4)

            return "✅ File uploaded successfully!"

    return render_template("admin_upload.html")


def ensure_data_dir():
    """Ensure all required directories exist"""
    os.makedirs('data/raw_docs', exist_ok=True)
    os.makedirs('data/encrypted_docs', exist_ok=True)
    if not os.path.exists('data/logs.json'):
        with open('data/logs.json', 'w') as f:
            json.dump({'files': [], 'requests': [], 'batch_keys': {}}, f)

@admin_bp.route('/admin/encrypt')
def encrypt_files():
    if session.get('role') != 'admin':
        return redirect('/')

    ensure_data_dir()
    raw_dir = 'data/raw_docs'
    enc_dir = 'data/encrypted_docs'

    try:
        # Generate new encryption key for this batch
        enc_key = generate_key()
        
        # Process documents
        docs, file_ids = [], []
        encrypted_files = []  # Track encrypted files
        
        # First collect all files to encrypt
        files_to_encrypt = [
            fname for fname in os.listdir(raw_dir) 
            if fname.endswith('.txt')
        ]
        
        if not files_to_encrypt:
            flash('No text files found to encrypt', 'warning')
            return redirect('/admin')

        # TF-IDF Vectorization
        for fname in files_to_encrypt:
            with open(os.path.join(raw_dir, fname), 'r', encoding='utf-8') as f:
                docs.append(f.read())
                file_ids.append(fname)

        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(docs).toarray()

        # Save vectorizer
        with open('data/vectorizer.pkl', 'wb') as f:
            pickle.dump(vectorizer, f)

        # Build and encrypt tree
        nodes = [TreeNode(vec, fid) for vec, fid in zip(tfidf_matrix, file_ids)]
        while len(nodes) > 1:
            new_nodes = []
            for i in range(0, len(nodes) - 1, 2):
                merged = np.maximum(nodes[i].vector, nodes[i + 1].vector)
                parent = TreeNode(merged)
                parent.left, parent.right = nodes[i], nodes[i + 1]
                new_nodes.append(parent)
            nodes = new_nodes if len(new_nodes) > 0 else nodes
        root = nodes[0]

        # Generate and save secret key
        S, M1, M2 = generate_secret_key(tfidf_matrix.shape[1])
        encrypted_tree = encrypt_tree(root, S, M1, M2)

        with open('data/index_tree.pkl', 'wb') as f:
            pickle.dump(encrypted_tree, f)
        with open('data/secret_key.pkl', 'wb') as f:
            pickle.dump((S, M1, M2), f)

        # Encrypt files
        for fname in files_to_encrypt:
            raw_path = os.path.join(raw_dir, fname)
            enc_path = os.path.join(enc_dir, fname + '.enc')
            encrypt_text_file(raw_path, enc_path, enc_key)
            encrypted_files.append(fname + '.enc')

        # Update logs
        with open('data/logs.json', 'r+') as f:
            logs = json.load(f)
            logs['batch_keys'][datetime.now().isoformat()] = enc_key.decode()
            f.seek(0)
            json.dump(logs, f, indent=4)
            f.truncate()

        flash(f'Successfully encrypted {len(encrypted_files)} files', 'success')
        return render_template('admin_encrypt_result.html', files=encrypted_files)

    except Exception as e:
        flash(f'Encryption failed: {str(e)}', 'error')
        return redirect('/admin')



@admin_bp.route('/admin/decrypt', methods=['GET', 'POST'])
def decrypt_file():
    if session.get('role') != 'admin':
        return redirect('/')

    files = os.listdir("data/encrypted_docs")
    content = None
    filename = None

    if request.method == 'POST':
        filename = request.form.get('filename')
        if filename:
            path = os.path.join("data/encrypted_docs", filename)
            
            # Get the encryption key from batch_keys
            with open('data/logs.json', 'r') as f:
                logs = json.load(f)
                
            # Find the most recent batch key
            if not logs.get('batch_keys'):
                flash('No encryption keys found', 'error')
                return redirect('/admin/decrypt')
                
            latest_key = list(logs['batch_keys'].values())[-1]
            key = latest_key.encode()  # Convert to bytes
            
            content = decrypt_text_file(path, key)

    return render_template('admin_decrypt.html', files=files, content=content, file=filename)



@admin_bp.route("/admin/encrypted-view", methods=["GET", "POST"])
def view_encrypted_file():
    if session.get("role") != "admin":
        return redirect("/")

    files = os.listdir("data/encrypted_docs")
    encrypted_content = None
    filename = None

    if request.method == "POST":
        filename = request.form.get("filename")
        if filename:
            filepath = os.path.join("data/encrypted_docs", filename)
            with open(filepath, "rb") as f:
                encrypted_content = f.read().hex()

    return render_template("admin_encrypted_view.html", files=files, content=encrypted_content, file=filename)


@admin_bp.route('/admin/requests', methods=['GET', 'POST'])
def handle_requests():
    if session.get('role') != 'admin':
        return redirect('/admin')

    # Load requests data
    with open('data/logs.json', 'r') as f:
        logs = json.load(f)

    # Handle POST request (approval/rejection)
    if request.method == 'POST':
        try:
            filename = request.form['filename']
            username = request.form['username']
            action = request.form['action']

            # Find and update the request
            for req in logs['requests']:
                if req['filename'] == filename and req['username'] == username:
                    if action == 'approve':
                        req['status'] = 'approved'
                        req['approved_by'] = session.get('username')
                        req['approval_time'] = datetime.now().isoformat()
                    elif action == 'reject':
                        req['status'] = 'rejected'
                    
                    break

            # Save updated logs
            with open('data/logs.json', 'w') as f:
                json.dump(logs, f, indent=4)

            flash('Request processed successfully', 'success')
            return redirect('/admin/requests')

        except Exception as e:
            flash(f'Error processing request: {str(e)}', 'error')
            return redirect('/admin/requests')

    # Handle GET request (show requests page)
    uploaded_by_admin = {f['filename'] for f in logs['files'] if f['uploaded_by'] == session['username']}
    relevant_requests = [
        req for req in logs.get('requests', [])
        if req['filename'] in uploaded_by_admin and req.get('status') == 'pending'
    ]

    return render_template('admin_approve_requests.html', requests=relevant_requests)


@admin_bp.route("/admin/files")
def view_encrypted_files():
    if session.get("role") != "admin":
        return redirect("/")

    username = session.get("username")

    with open("data/logs.json", "r") as f:
        logs = json.load(f)

    # Get uploaded files by the admin
    uploaded_files = [
        f["filename"] for f in logs["files"] if f["uploaded_by"] == username
    ]

    encrypted_path = "data/encrypted_docs"
    encrypted_files = os.listdir(encrypted_path) if os.path.exists(encrypted_path) else []

    # Filter files to show only those encrypted files that the admin uploaded
    user_encrypted_files = [f for f in encrypted_files if f in uploaded_files]

    return render_template("admin_encrypted_files.html", files=user_encrypted_files)
