from flask import Flask, redirect, url_for, session, request, render_template, jsonify
from authlib.integrations.flask_client import OAuth
from flask_login import LoginManager, login_user, logout_user, UserMixin, login_required, current_user
import os, requests
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
DEVICE_SECRET = os.environ.get("DEVICE_SECRET")
DB_FILE = "/data/database.db"
# Configure OAuth
oauth = OAuth(app)
github = oauth.register(
    name='github',
    client_id=os.environ.get("GITHUB_CLIENT_ID"),
    client_secret=os.environ.get("GITHUB_CLIENT_SECRET"),
    authorize_url='https://github.com/login/oauth/authorize',
    access_token_url='https://github.com/login/oauth/access_token',
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'read:org'}
)

# Login manager
login_manager = LoginManager(app)
# Initialize DB
def init_db():
    if not os.path.exists(DB_FILE):
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("""
                CREATE TABLE reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    serial TEXT,
                    customer TEXT,
                    sw_version TEXT,
                    hw_version TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

init_db()

# Delete old entries
@app.before_request
def delete_old():
    with sqlite3.connect(DB_FILE) as conn:
        cutoff = datetime.now() - timedelta(days=5)
        conn.execute("DELETE FROM reports WHERE timestamp < ?", (cutoff.isoformat(),))

#  user class
class User(UserMixin):
    def __init__(self, id, login):
        self.id = id
        self.name = login

@login_manager.user_loader
def load_user(user_id):
    return session.get('user')

@app.route('/login')
def login():
    return github.authorize_redirect(redirect_uri=url_for('callback', _external=True))

@app.route('/callback')
def callback():
    token = github.authorize_access_token()
    user_info = github.get('user').json()
    username = user_info['login']

    # ✅ Check if user is in your org
    orgs = github.get('user/orgs').json()
    allowed_orgs = ['your-org-name']  # Replace with your GitHub org

    if any(org['login'] in allowed_orgs for org in orgs):
        session['user'] = User(user_info['id'], username).__dict__
        login_user(User(user_info['id'], username))
        return redirect('/')
    return "Access denied – not a member of required org", 403

@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect('/')

@app.route('/')
@login_required
def dashboard():
    # Your current dashboard code goes here (render devices etc.)
    return render_template('index.html')  # Example only

@app.route('/data', methods=['POST'])
def receive_data():
    data = request.get_json()
    required = ['serial', 'customer', 'sw_version', 'hw_version']
    if not all(k in data for k in required):
        return jsonify({"error": "Missing fields"}), 400

    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            INSERT INTO reports (serial, customer, sw_version, hw_version)
            VALUES (?, ?, ?, ?)
        """, (data['serial'], data['customer'], data['sw_version'], data['hw_version']))

    return jsonify({"status": "stored"}), 200

@app.route('/')
@login_required
def dashboard():
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        data = conn.execute("SELECT * FROM reports ORDER BY timestamp DESC").fetchall()
    return render_template("index.html", devices=data)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

