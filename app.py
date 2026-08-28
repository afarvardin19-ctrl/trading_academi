from flask import Flask, request, session, redirect, url_for, render_template
import psycopg2
import os
import random
import string
from datetime import datetime
import pytz

app = Flask(__name__)
app.secret_key = 'secret_key_12345'

DATABASE_URL = os.environ.get('DATABASE_URL')
TEHRAN_TZ = pytz.timezone('Asia/Tehran')

# ============ دیتابیس ============
def get_db():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            mobile TEXT UNIQUE NOT NULL,
            email TEXT,
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

init_db()

# ============ کد معرف ============
def generate_code():
    chars = string.ascii_uppercase + string.digits
    chars = ''.join(c for c in chars if c not in 'O0I1')
    return 'TR-' + ''.join(random.choices(chars, k=10))

def generate_unique_code():
    conn = get_db()
    c = conn.cursor()
    while True:
        code = generate_code()
        c.execute('SELECT id FROM users WHERE code = %s', (code,))
        if not c.fetchone():
            conn.close()
            return code
        conn.close()

# ============ صفحه اصلی ============
@app.route('/')
def home():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    user_count = c.fetchone()[0]
    conn.close()
    
    return f'''
    <h1 style="text-align:center; color:#2c3e50;">📈 آکادمی ترید</h1>
    <p style="text-align:center;">۲۶ جلسه تخصصی</p>
    <p style="text-align:center;">تعداد کاربران: {user_count}</p>
    <ul>
        <li>جلسه 1 کندلشناسی - رایگان</li>
        <li>جلسه 2 حمایت و مقاومت - رایگان</li>
        <li>جلسه 3 پرایس اکشن مقدماتی - رایگان</li>
        <li>جلسه 4 الگوهای کلاسیک - رایگان</li>
        <li>جلسه 5 ترند و خط روند - رایگان</li>
        <li>جلسه 6 RSI - قفل 3 دعوت</li>
        <li>جلسه 7 MACD - قفل 3 دعوت</li>
        <li>جلسه 26 🎯 سیگنالگیری حرفهای - قفل 10 دعوت</li>
    </ul>
    <div style="text-align:center;">
        <a href="/register">ثبت نام</a> |
        <a href="/users">کاربران</a>
    </div>
    '''

# ============ ثبت نام ============
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return '''
        <h2>📝 فرم ثبت نام</h2>
        <form method="POST">
            <input type="text" name="name" placeholder="نام کامل" required><br>
            <input type="text" name="mobile" placeholder="شماره موبایل" required><br>
            <input type="email" name="email" placeholder="ایمیل"><br>
            <input type="text" name="address" placeholder="آدرس"><br>
            <input type="text" name="postal_code" placeholder="کد پستی"><br>
            <input type="text" name="code" placeholder="کد معرف (اختیاری)"><br>
            <button type="submit">ثبت نام</button>
        </form>
        <a href="/">بازگشت</a>
        '''
    
    name = request.form.get('name', '').strip()
    mobile = request.form.get('mobile', '').strip()
    email = request.form.get('email', '').strip()
    address = request.form.get('address', '').strip()
    postal_code = request.form.get('postal_code', '').strip()
    invited_code = request.form.get('code', '').strip()
    
    if not name or not mobile:
        return "❌ نام و موبایل اجباری است", 400
    
    user_code = generate_unique_code()
    now_tehran = datetime.now(TEHRAN_TZ)
    
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('''
            INSERT INTO users (name, mobile, email, address, postal_code, code, registered_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (name, mobile, email, address, postal_code, user_code, now_tehran))
        conn.commit()
        conn.close()
        return f'✅ ثبت نام موفق! کد شما: {user_code} <a href="/users">مشاهده کاربران</a> | <a href="/">خانه</a>'
    except Exception as e:
        return f'❌ خطا: {str(e)}', 500

# ============ لیست کاربران ============
@app.route('/users')
def show_users():
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT id, name, mobile, email, code, registered_at FROM users ORDER BY id DESC')
        rows = c.fetchall()
        conn.close()

        if not rows:
            return '<h2>📭 هیچ کاربری ثبت نشده است</h2><a href="/">خانه</a>'

        html = '<h2>📋 لیست کاربران</h2><table border="1"><tr><th>ID</th><th>Name</th><th>Mobile</th><th>Email</th><th>Code</th><th>زمان ثبت</th></tr>'
        for row in rows:
            html += f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td></tr>'
        html += f'</table><p>🔢 تعداد: {len(rows)}</p><a href="/">خانه</a>'
        return html
    except Exception as e:
        return f'❌ خطا: {str(e)}', 500

# ============ ورود و خروج ============
@app.route('/login')
def login():
    return '<h2>🔐 صفحه ورود</h2><a href="/">خانه</a>'

@app.route('/logout')
def logout():
    return '<h2>🚪 خارج شدید</h2><a href="/">خانه</a>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
