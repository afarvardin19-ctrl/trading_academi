from flask import Flask, request, render_template, redirect, session
import psycopg2
import os
import random
import string
from datetime import datetime
import pytz

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

DATABASE_URL = os.environ.get('DATABASE_URL')
TEHRAN_TZ = pytz.timezone('Asia/Tehran')

# ===== صفحه اصلی با دوره‌ها و گرافیک =====
@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>آکادمی ترید | ۲۶ جلسه</title>
        <style>
            body { font-family: Arial, sans-serif; direction: rtl; background: #f0f2f5; margin: 0; padding: 20px; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
            h1 { text-align: center; color: #2c3e50; }
            .subtitle { text-align: center; color: #7f8c8d; font-size: 18px; }
            .jalsat { list-style: none; padding: 0; }
            .jalsat li { padding: 10px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; }
            .free { color: #27ae60; font-weight: bold; }
            .lock { color: #e74c3c; font-weight: bold; }
            .btn { display: inline-block; padding: 10px 20px; background: #3498db; color: white; text-decoration: none; border-radius: 8px; margin: 5px; }
            .btn:hover { background: #2980b9; }
            .center { text-align: center; margin: 20px 0; }
            .teachers { display: flex; justify-content: space-around; flex-wrap: wrap; margin-top: 20px; }
            .teacher { background: #f8f9fa; padding: 15px; border-radius: 10px; width: 45%; margin: 10px 0; }
            .teacher h3 { margin: 0; color: #2c3e50; }
            .teacher p { margin: 5px 0; color: #7f8c8d; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📈 آکادمی ترید | ۲۶ جلسه</h1>
            <p class="subtitle">۲۶ جلسه تخصصی</p>
            <p class="subtitle">برای دسترسی به جلسات ثبت‌نام کنید</p>
            
            <ul class="jalsat">
                <li>جلسه 1 کندلشناسی <span class="free">رایگان</span></li>
                <li>جلسه 2 حمایت و مقاومت <span class="free">رایگان</span></li>
                <li>جلسه 3 پرایس اکشن مقدماتی <span class="free">رایگان</span></li>
                <li>جلسه 4 الگوهای کلاسیک <span class="free">رایگان</span></li>
                <li>جلسه 5 ترند و خط روند <span class="free">رایگان</span></li>
                <li>جلسه 6 RSI <span class="lock">قفل 3 دعوت</span></li>
                <li>جلسه 7 MACD <span class="lock">قفل 3 دعوت</span></li>
                <li>جلسه 8 میانگین متحرک (MA) <span class="lock">قفل 3 دعوت</span></li>
                <li>جلسه 9 باند بولینگر <span class="lock">قفل 3 دعوت</span></li>
                <li>جلسه 10 استوکستیک <span class="lock">قفل 3 دعوت</span></li>
                <li>جلسه 11 فیبوناچی اصلاحی <span class="lock">قفل 3 دعوت</span></li>
                <li>جلسه 12 فیبوناچی گسترده <span class="lock">قفل 3 دعوت</span></li>
                <li>جلسه 13 چنگال اندروز <span class="lock">قفل 3 دعوت</span></li>
                <li>جلسه 14 امواج الیوت <span class="lock">قفل 3 دعوت</span></li>
                <li>جلسه 15 الگوهای هارمونیک <span class="lock">قفل 3 دعوت</span></li>
                <li>جلسه 16 وایکوف <span class="lock">قفل 3 دعوت</span></li>
                <li>جلسه 17 اسمارت مانی <span class="lock">قفل 3 دعوت</span></li>
                <li>جلسه 18 ICT <span class="lock">قفل 3 دعوت</span></li>
                <li>جلسه 19 پرایس اکشن پیشرفته <span class="lock">قفل 4 دعوت</span></li>
                <li>جلسه 20 مدیریت سرمایه <span class="lock">قفل 4 دعوت</span></li>
                <li>جلسه 21 مدیریت ریسک <span class="lock">قفل 4 دعوت</span></li>
                <li>جلسه 22 روانشناسی بازار <span class="lock">قفل 4 دعوت</span></li>
                <li>جلسه 23 استراتژی معاملاتی <span class="lock">قفل 4 دعوت</span></li>
                <li>جلسه 24 بک تست <span class="lock">قفل 4 دعوت</span></li>
                <li>جلسه 25 سشنهای معاملاتی <span class="lock">قفل 4 دعوت</span></li>
                <li>جلسه 26 🎯 سیگنالگیری حرفهای <span class="lock">قفل 10 دعوت</span></li>
            </ul>
            
            <div class="center">
                <a href="/register" class="btn">📝 ثبت نام</a>
                <a href="/users" class="btn">👥 کاربران</a>
            </div>

            <h2 style="text-align:center;">اساتید برتر</h2>
            <div class="teachers">
                <div class="teacher">
                    <h3>محمد کریمی</h3>
                    <p>تحلیلگر بازار سرمایه</p>
                </div>
                <div class="teacher">
                    <h3>سارا محمدی</h3>
                    <p>متخصص پرایس اکشن</p>
                </div>
                <div class="teacher">
                    <h3>رضا احمدی</h3>
                    <p>مدرس ارشد فارکس</p>
                </div>
                <div class="teacher">
                    <h3>نازنین حسینی</h3>
                    <p>روانشناس بازار</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

# ===== ثبت نام =====
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return '''
        <h2>📝 فرم ثبت نام</h2>
        <form method="POST">
            <input type="text" name="name" placeholder="نام کامل" required><br>
            <input type="text" name="mobile" placeholder="شماره موبایل" required><br>
            <input type="email" name="email" placeholder="ایمیل" required><br>
            <input type="text" name="national_code" placeholder="کد ملی"><br>
            <input type="text" name="address" placeholder="آدرس"><br>
            <input type="text" name="postal_code" placeholder="کد پستی"><br>
            <input type="text" name="code" placeholder="کد معرف"><br>
            <button type="submit">ثبت نام</button>
        </form>
        <a href="/">بازگشت</a>
        '''
    
    name = request.form.get('name', '').strip()
    mobile = request.form.get('mobile', '').strip()
    email = request.form.get('email', '').strip()
    national_code = request.form.get('national_code', '').strip()
    address = request.form.get('address', '').strip()
    postal_code = request.form.get('postal_code', '').strip()
    user_code = request.form.get('code', '').strip()
    now_tehran = datetime.now(TEHRAN_TZ)

    if not name or not mobile or not email:
        return "❌ نام، موبایل و ایمیل اجباری است", 400

    try:
        conn = psycopg2.connect(DATABASE_URL)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                mobile TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                national_code TEXT,
                address TEXT,
                postal_code TEXT,
                code TEXT,
                points INTEGER DEFAULT 0,
                unlocked INTEGER DEFAULT 0,
                invites INTEGER DEFAULT 0,
                invited_by TEXT,
                invited_by_name TEXT,
                created_at TIMESTAMP
            )
        ''')
        c.execute('''
            INSERT INTO users (name, mobile, email, national_code, address, postal_code, code, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (name, mobile, email, national_code, address, postal_code, user_code, now_tehran))
        conn.commit()
        conn.close()
        return f'✅ ثبت نام موفق! <a href="/users">مشاهده کاربران</a> | <a href="/">خانه</a>'
    except Exception as e:
        return f'❌ خطا: {str(e)}', 500

# ===== لیست کاربران =====
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

# ===== ورود و خروج =====
@app.route('/login')
def login():
    return '<h2>🔐 صفحه ورود</h2><a href="/">خانه</a>'

@app.route('/logout')
def logout():
    return '<h2>🚪 خارج شدید</h2><a href="/">خانه</a>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
