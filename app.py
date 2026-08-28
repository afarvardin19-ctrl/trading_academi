import os
import psycopg2
from flask import Flask, request
from datetime import datetime
import pytz

app = Flask(__name__)
DATABASE_URL = os.environ.get('DATABASE_URL')
TEHRAN_TZ = pytz.timezone('Asia/Tehran')

@app.route('/')
def home():
    now = datetime.now(TEHRAN_TZ)
    return f'''
    <h2>📈 آکادمی ترید</h2>
    <p>⏰ {now.strftime("%Y-%m-%d %H:%M:%S")} (تهران)</p>
    <form action="/register" method="POST">
        <input type="text" name="name" placeholder="نام" required><br>
        <input type="text" name="mobile" placeholder="موبایل" required><br>
        <input type="email" name="email" placeholder="ایمیل" required><br>
        <button type="submit">ثبت نام</button>
    </form>
    <a href="/users">👥 کاربران</a> |
    <a href="/db">🗄️ دیتابیس</a>
    '''

@app.route('/register', methods=['POST'])
def register():
    try:
        name = request.form.get('name', '').strip()
        mobile = request.form.get('mobile', '').strip()
        email = request.form.get('email', '').strip()
        now_tehran = datetime.now(TEHRAN_TZ)

        if not name or not mobile or not email:
            return '❌ Name, Mobile and Email are required', 400

        conn = psycopg2.connect(DATABASE_URL)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                mobile TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP
            )
        ''')
        c.execute('''
            INSERT INTO users (name, mobile, email, created_at)
            VALUES (%s, %s, %s, %s)
        ''', (name, mobile, email, now_tehran))
        conn.commit()
        conn.close()
        return f'''✅ ثبت نام موفق!
🕐 {now_tehran.strftime("%Y-%m-%d %H:%M:%S")}
<a href="/users">مشاهده کاربران</a> | <a href="/">خانه</a>'''
    except Exception as e:
        return f'❌ خطا: {str(e)}', 500

@app.route('/users')
def show_users():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        c = conn.cursor()
        c.execute('SELECT id, name, mobile, email, created_at FROM users ORDER BY id DESC')
        rows = c.fetchall()
        conn.close()

        if not rows:
            return '<h2>📭 هیچ کاربری ثبت نشده است</h2><a href="/">خانه</a>'

        html = '<h2>📋 لیست کاربران</h2><table border="1"><tr><th>ID</th><th>Name</th><th>Mobile</th><th>Email</th><th>زمان ثبت</th></tr>'
        for row in rows:
            html += f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td></tr>'
        html += f'</table><p>🔢 تعداد: {len(rows)}</p><a href="/">خانه</a>'
        return html
    except Exception as e:
        return f'❌ خطا: {str(e)}', 500

# ================== صفحه دیتابیس (DB) ==================
@app.route('/db')
def show_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        c = conn.cursor()
        c.execute('SELECT * FROM users ORDER BY id DESC')
        rows = c.fetchall()
        conn.close()

        if not rows:
            return '<h2>📭 دیتابیس خالی است</h2><a href="/">خانه</a>'

        html = '<h2>🗄️ محتوای دیتابیس (users)</h2>'
        html += '<table border="1" cellpadding="5"><tr>'
        # ستون‌ها
        html += '<th>id</th><th>name</th><th>mobile</th><th>email</th><th>created_at</th></tr>'
        for row in rows:
            html += f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td></tr>'
        html += f'</table><p>🔢 تعداد کل: {len(rows)}</p><a href="/">خانه</a>'
        return html
    except Exception as e:
        return f'❌ خطا: {str(e)}', 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
