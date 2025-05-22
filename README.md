# 🔐 Secure Multi-Keyword Ranked Search Scheme over Encrypted Cloud Data

This project implements a **Secure and Dynamic Multi-Keyword Ranked Search Scheme** for encrypted documents stored on a cloud platform. It enables secure data storage, encrypted keyword-based search, and privacy-preserving access control, inspired by research from IEEE TPDS.

## 📁 Project Structure

secure_search_system/
│
├── app/
│ ├── routes/ # Flask route handlers
│ ├── templates/ # HTML Templates
│ ├── utils/ # Encryption, search, and key handling utilities
│ └── init.py # Flask app factory
│
├── data/
│ ├── raw_docs/ # Plain text files uploaded by admin
│ ├── encrypted_docs/ # Encrypted documents
│ ├── logs.json # Logs for uploaded files and user access
│ ├── secret_key.pkl # Secret matrix keys used for search
│ ├── index_tree.pkl # Encrypted search tree
│ └── vectorizer.pkl # TF-IDF vectorizer object
│
├── static/ # Optional CSS, JS, etc.
├── run.py # Entry point to launch Flask app
├── requirements.txt # Dependencies
└── README.md # This file


---

## ✨ Features

- 🔒 **Encrypted File Upload**: Admins can upload and encrypt text files.
- 🔍 **Search Over Encrypted Data**: Users can perform ranked keyword-based searches using trapdoor generation.
- 📜 **Access Requests**: Users can request access to encrypted documents.
- ✅ **Admin Approval System**: Admins approve/reject access requests securely.
- 📥 **Decryption & Download**: Only approved users can decrypt and download requested files.
- 🔄 **Dynamic Indexing**: Uses a tree-based structure over TF-IDF vectors for ranked retrieval.

---

## 🔧 How to Run

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/secure_search_system.git
cd secure_search_system

2. Install Dependencies

pip install -r requirements.txt

3. Start the Flask Server

python run.py

4. Open in Browser
Visit: http://127.0.0.1:5000


## 👥 User Roles
Admin: Uploads, encrypts, and manages files. Approves user requests.

User: Searches encrypted files and requests access.

Authenticator: Views logs, file uploads, and registered users (monitor-only).

## 🛠 Tech Stack
Backend: Python, Flask

Frontend: HTML, CSS (with inline styling for simplicity)

Encryption: Python Cryptography (Fernet), TF-IDF, Secure kNN (trapdoor & tree)

Storage: Local JSON files & Pickle for demo; can be upgraded to a DB

## 🧪 Testing Credentials

| Role          | Username | Password  |
| ------------- | -------- | --------- |
| Admin         | admin1   | adminpass |
| User          | user1    | userpass  |
| Authenticator | auth1    | authpass  |


## 📚 References
IEEE TPDS Paper: "Secure and Dynamic Multi-keyword Ranked Search Scheme over Encrypted Cloud Data"

TF-IDF & Vector Space Model for keyword ranking

Secure trapdoor generation & encrypted tree indexing

## 📬 License
This project is for academic and learning purposes only.

