from flask import Blueprint, render_template, request, session, redirect, flash, make_response
import os
import json
import pickle
import base64
from datetime import datetime, timedelta
from cryptography.fernet import Fernet, InvalidToken
import numpy as np
from app.utils.trapdoor import build_trapdoor, match_node
from app.utils.encryption import decrypt_text_file

user_bp = Blueprint('user', __name__, template_folder='templates')

def validate_fernet_key(key_str):
    """Validate and prepare Fernet key"""
    try:
        # Ensure proper length (44 chars)
        if len(key_str) < 44:
            key_str = key_str.ljust(44, '=')
        elif len(key_str) > 44:
            key_str = key_str[:44]
        
        # Ensure URL-safe base64
        key_str = key_str.replace(' ', '+')
        key_bytes = base64.urlsafe_b64decode(key_str)
        return base64.urlsafe_b64encode(key_bytes)  # Re-encode to ensure validity
    except Exception as e:
        raise ValueError(f"Invalid key: {str(e)}")

@user_bp.route('/user')
def user_dashboard():
    if not session.get('role') == 'user':
        return redirect('/login')
    return render_template('dashboard_user.html')

@user_bp.route('/user/search', methods=['GET', 'POST'])
def user_search():
    if not session.get('role') == 'user':
        return redirect('/login')

    results = []
    if request.method == 'POST':
        keywords = request.form.get('keywords', '').strip()
        if not keywords:
            flash('Please enter search keywords', 'warning')
            return redirect('/user/search')

        try:
            # Load search index
            with open('data/index_tree.pkl', 'rb') as f:
                root = pickle.load(f)
            with open('data/secret_key.pkl', 'rb') as f:
                S, M1, M2 = pickle.load(f)
            with open('data/vectorizer.pkl', 'rb') as f:
                vectorizer = pickle.load(f)

            # Build trapdoor and search
            vec = vectorizer.transform([keywords]).toarray()[0]
            trapdoor = build_trapdoor(vec, S, M1, M2)
            
            results = []
            def traverse(node):
                if not node:
                    return
                if hasattr(node, 'fid'):
                    score = match_node(trapdoor, node.vector)
                    results.append((node.fid, float(score)))
                traverse(node.left)
                traverse(node.right)
            
            traverse(root)
            results = sorted(results, key=lambda x: x[1], reverse=True)[:5]

        except Exception as e:
            flash(f'Search error: {str(e)}', 'error')

    return render_template('user_search.html', results=results)

@user_bp.route('/user/request', methods=['POST'])
def user_request_access():
    if not session.get('role') == 'user':
        return redirect('/login')

    filename = request.form.get('filename')
    if not filename:
        flash('No file specified', 'error')
        return redirect('/user/search')

    try:
        with open('data/logs.json', 'r+') as f:
            logs = json.load(f)
            
            # Check for existing request
            if any(req['filename'] == filename and req['username'] == session['username']
                   for req in logs.get('requests', [])):
                flash('You already requested this file', 'info')
                return redirect('/user/search')

            # Add new request
            logs.setdefault('requests', []).append({
                'username': session['username'],
                'filename': filename,
                'status': 'pending',
                'request_time': datetime.now().isoformat()
            })
            
            f.seek(0)
            json.dump(logs, f, indent=4)

        flash('File access requested successfully', 'success')
        return redirect('/user/search')

    except Exception as e:
        flash(f'Request failed: {str(e)}', 'error')
        return redirect('/user/search')

@user_bp.route('/user/approved')
def view_approved_files():
    if not session.get('role') == 'user':
        return redirect('/login')

    try:
        with open('data/logs.json', 'r') as f:
            logs = json.load(f)

        approved_files = []
        current_user = session.get('username')
        
        for req in logs.get('requests', []):
            # Check if request is approved for current user
            if (req.get('username') == current_user and 
                req.get('status') == 'approved' and
                'approval_time' in req):
                
                # Verify the file exists
                enc_filename = f"{req['filename']}.enc"
                filepath = os.path.join('data', 'encrypted_docs', enc_filename)
                
                if os.path.exists(filepath):
                    approved_files.append({
                        'filename': req['filename'],
                        'approved_by': req.get('approved_by', 'Admin'),
                        'approval_time': req['approval_time'],
                        'size': f"{os.path.getsize(filepath) / 1024:.2f} KB"
                    })
                else:
                    # File doesn't exist, skip this entry
                    continue

        return render_template('user_granted_files.html', 
                            approved_files=approved_files,
                            username=current_user)

    except Exception as e:
        flash(f'Error loading approved files: {str(e)}', 'error')
        return render_template('user_granted_files.html', approved_files=[],username=session.get('username'))
    


@user_bp.route('/user/download/<filename>')
def download_file(filename):
    if not session.get('role') == 'user':
        return redirect('/login')

    try:
        # 1. Verify approval status
        with open('data/logs.json', 'r') as f:
            logs = json.load(f)

        approved_request = next(
            (req for req in logs.get('requests', [])
            if req['filename'] == filename
            and req['username'] == session['username']
            and req.get('status') == 'approved'),
            None
        )

        if not approved_request:
            flash('File not approved for download', 'error')
            return redirect('/user/approved')

        # 2. Get the encryption key
        if 'encryption_key' not in approved_request:
            flash('Decryption key missing', 'error')
            return redirect('/user/approved')

        key = approved_request['encryption_key'].encode()

        # 3. Handle file path (with or without .enc extension)
        enc_filename = f"{filename}.enc" 
        filepath = os.path.join('data', 'encrypted_docs', enc_filename)

        if not os.path.exists(filepath):
            flash('Encrypted file not found', 'error')
            return redirect('/user/approved')

        # 4. Decrypt and return file
        decrypted_content = decrypt_text_file(filepath, key)
        if decrypted_content is None:
            flash('Decryption failed - invalid key or corrupted file', 'error')
            return redirect('/user/approved')

        response = make_response(decrypted_content)
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        flash(f'Download error: {str(e)}', 'error')
        return redirect('/user/approved')