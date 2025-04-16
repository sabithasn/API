from flask import Flask, redirect, url_for, session
from routes import routes  # Import the Blueprint from routes.py
from flask_session import Session

app = Flask(__name__)

from flask_session import Session

app = Flask(__name__)
# Configure session
app.secret_key = "your_secret_key"  # Add a secret key for encryption
app.config["SESSION_TYPE"] = "filesystem"  # Store session data in a local file system

Session(app)  # Initialize Flask-Session

app.register_blueprint(routes)

@app.route("/")
def home():
    print("inside home, before session printing")
    print("Session Data:", session)  # Check if session variables exist
    # Check if the user is already logged in and their role
    if "role" in session and session["role"] == "Faculty":
        return redirect(url_for("routes.faculty_dashboard"))  # Redirect Faculty directly

    return redirect(url_for("routes.login"))  # Default to login page for new users

if __name__ == "__main__":
    app.run(debug=True)