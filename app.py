from flask import Flask, redirect, url_for, session
from flask_dance.contrib.google import make_google_blueprint, google
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Configure Google OAuth
google_bp = make_google_blueprint(
    client_id="",
    client_secret="",
    offline=True,
    scope=["profile", "email"]
)
app.register_blueprint(google_bp, url_prefix="/login")

# Flask-Login Setup
login_manager = LoginManager(app)

# Simulated User Database
users = {}

class User(UserMixin):
    def __init__(self, user_id, email, name):
        self.id = user_id
        self.email = email
        self.name = name

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

# Google OAuth Callback
@app.route("/login/callback")
def google_callback():
    if not google.authorized:
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    user_info = resp.json()
    
    user_id = user_info["id"]
    email = user_info["email"]
    name = user_info["name"]

    # Store user in session
    if user_id not in users:
        users[user_id] = User(user_id, email, name)

    login_user(users[user_id])
    return redirect(url_for("profile"))

@app.route("/profile")
def profile():
    if not current_user.is_authenticated:
        return redirect(url_for("google.login"))
    return f"Welcome {current_user.name}! Your email is {current_user.email}."

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("google.login"))

if __name__ == "__main__":
    app.run(debug=True)
