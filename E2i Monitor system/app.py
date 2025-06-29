from flask import Flask, redirect, url_for, session, request, render_template, jsonify
from authlib.integrations.flask_client import OAuth
from flask_login import LoginManager, login_user, logout_user, UserMixin, login_required, current_user
import os, requests

app = Flask(__name__)
app.secret_key = 'your-super-secret-key'

# Configure OAuth
oauth = OAuth(app)
github = oauth.register(
    name='github',
    client_id='YOUR_CLIENT_ID',
    client_secret='YOUR_CLIENT_SECRET',
    authorize_url='https://github.com/login/oauth/authorize',
    access_token_url='https://github.com/login/oauth/access_token',
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'read:org'}
)

# Login manager
login_manager = LoginManager(app)

# Fake user class
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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
