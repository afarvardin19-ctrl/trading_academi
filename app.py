from flask import Flask, render_template_string, request, session, redirect, url_for, jsonify
import random
import string
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret_key_12345'

# ============ دیتابیس ============
def get_db():
    conn = sqlite3.connect('users_new.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            family TEXT,
            mobile TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            national_code TEXT,
            address TEXT,
            postal_code TEXT,
            code TEXT UNIQUE NOT NULL,
            points INTEGER DEFAULT 0,
            unlocked INTEGER DEFAULT 5,
            invites INTEGER DEFAULT 0,
            invited_by TEXT,
            invited_by_name TEXT,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ دیتابیس راه‌اندازی شد!")

init_db()

# ============ مسیر JSON برای بکاپ ============
@app.route('/api/users')
def api_users():
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT * FROM users ORDER BY id DESC")
        users = c.fetchall()
        conn.close()
        
        data = []
        for u in users:
            data.append({
                'id': u['id'],
                'name': u['name'],
                'family': u['family'],
                'mobile': u['mobile'],
                'email': u['email'],
                'password': u['password'],
                'national_code': u['national_code'],
                'address': u['address'],
                'postal_code': u['postal_code'],
                'code': u['code'],
                'points': u['points'],
                'unlocked': u['unlocked'],
                'invites': u['invites'],
                'registered_at': u['registered_at']
            })
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ صفحه اصلی ============
@app.route('/')
def home():
    return '''
    <h1>📈 آکادمی ترید</h1>
    <p>۲۶ جلسه تخصصی</p>
    <a href="/register">ثبت نام</a> |
    <a href="/api/users">JSON</a>
    '''

# ============ ثبت نام ============
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return '''
        <h2>📝 فرم ثبت نام</h2>
        <form method="POST">
            <input type="text" name="name" placeholder="نام" required><br>
            <input type="text" name="family" placeholder="نام خانوادگی"><br>
            <input type="text" name="mobile" placeholder="موبایل" required><br>
            <input type="email" name="email" placeholder="ایمیل" required><br>
            <input type="password" name="password" placeholder="رمز عبور" required><br>
            <button type="submit">ثبت نام</button>
        </form>
        <a href="/">بازگشت</a>
        '''
    
    name = request.form.get('name')
    family = request.form.get('family')
    mobile = request.form.get('mobile')
    email = request.form.get('email')
    password = request.form.get('password')
    
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO users (name, family, mobile, email, password, code) VALUES (?, ?, ?, ?, ?, ?)",
              (name, family, mobile, email, password, 'VIP-123456'))
    conn.commit()
    conn.close()
    
    return "✅ ثبت نام موفق! <a href='/'>خانه</a>"

# ============ اجرا ============
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
