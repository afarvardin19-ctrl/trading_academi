from flask import Flask, render_template_string, request, redirect, url_for
import sqlite3
import random
import string
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret_key_12345'

# ============ دیتابیس ============
def get_db():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT UNIQUE NOT NULL,
            email TEXT,
            national_code TEXT,
            address TEXT,
            postal_code TEXT,
            ref_code TEXT,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ دیتابیس راه‌اندازی شد!")

init_db()

def generate_code():
    return 'VIP-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# ============ صفحات ============
@app.route('/')
def index():
    return '''
    <h1>📊 آکادمی ترید</h1>
    <a href="/register">ثبت‌نام</a> | <a href="/db">دیتابیس</a>
    '''

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return '''
        <h2>📝 ثبت‌نام</h2>
        <form method="post">
            <input type="text" name="name" placeholder="نام" required><br>
            <input type="text" name="mobile" placeholder="موبایل" required><br>
            <input type="email" name="email" placeholder="ایمیل"><br>
            <input type="text" name="national_code" placeholder="کد ملی"><br>
            <input type="text" name="address" placeholder="آدرس"><br>
            <input type="text" name="postal_code" placeholder="کد پستی"><br>
            <input type="text" name="ref_code" placeholder="کد معرف"><br>
            <button type="submit">ثبت‌نام</button>
        </form>
        <a href="/">بازگشت</a>
        '''
    
    name = request.form.get('name')
    mobile = request.form.get('mobile')
    email = request.form.get('email')
    national_code = request.form.get('national_code')
    address = request.form.get('address', '')
    postal_code = request.form.get('postal_code', '')
    ref_code = request.form.get('ref_code', '').strip()
    
    conn = get_db()
    c = conn.cursor()
    
    c.execute("SELECT * FROM users WHERE mobile = ?", (mobile,))
    if c.fetchone():
        conn.close()
        return '❌ این شماره قبلاً ثبت‌نام کرده! <a href="/">بازگشت</a>'
    
    if not ref_code:
        ref_code = generate_code()
    
    c.execute('''
        INSERT INTO users (name, mobile, email, national_code, address, postal_code, ref_code)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, mobile, email, national_code, address, postal_code, ref_code))
    conn.commit()
    conn.close()
    
    return f'''
    <h2>✅ ثبت‌نام موفق!</h2>
    <p>کد معرف شما: <b>{ref_code}</b></p>
    <a href="/">بازگشت</a>
    '''

@app.route('/db')
def db():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    conn.close()
    
    html = '<h1>📊 کاربران</h1>'
    html += f'<p>تعداد: {len(users)}</p>'
    html += '<table border="1"><tr><th>#</th><th>نام</th><th>موبایل</th><th>ایمیل</th><th>کد معرف</th></tr>'
    for u in users:
        html += f'<tr><td>{u[0]}</td><td>{u[1]}</td><td>{u[2]}</td><td>{u[3]}</td><td>{u[7]}</td></tr>'
    html += '</table><br><a href="/">بازگشت</a>'
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
