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
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>آکادمی ترید</title>
        <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet" />
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Vazirmatn', Tahoma, sans-serif; background: #f0f2f5; color: #1a1a2e; min-height: 100vh; padding: 20px; display: flex; justify-content: center; align-items: center; }
            .card { background: #fff; max-width: 500px; width: 100%; padding: 40px; border-radius: 24px; box-shadow: 0 10px 40px rgba(0,0,0,0.06); text-align: center; }
            .logo { font-size: 48px; margin-bottom: 16px; }
            h1 { font-size: 24px; font-weight: 800; margin-bottom: 8px; }
            .sub { color: #5f6368; font-size: 14px; margin-bottom: 24px; }
            .btn { display: inline-block; background: #1a73e8; color: #fff; padding: 14px 40px; border-radius: 60px; text-decoration: none; font-weight: 700; transition: 0.3s; }
            .btn:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(26,115,232,0.2); }
        </style>
    </head>
    <body>
        <div class="card">
            <div class="logo">📊</div>
            <h1>آکادمی ترید</h1>
            <p class="sub">دوره جامع آموزش کریپتو از صفر تا حرفه‌ای</p>
            <a href="/register" class="btn">ثبت‌نام رایگان</a>
        </div>
    </body>
    </html>
    '''

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return '''
        <!DOCTYPE html>
        <html lang="fa" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ثبت‌نام</title>
            <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet" />
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { font-family: 'Vazirmatn', Tahoma, sans-serif; background: #f0f2f5; color: #1a1a2e; min-height: 100vh; padding: 20px; display: flex; justify-content: center; align-items: center; }
                .card { background: #fff; max-width: 450px; width: 100%; padding: 40px; border-radius: 24px; box-shadow: 0 10px 40px rgba(0,0,0,0.06); }
                h2 { text-align: center; margin-bottom: 20px; }
                input { width: 100%; padding: 14px 16px; border: 1px solid #dadce0; border-radius: 12px; font-size: 14px; font-family: inherit; margin-bottom: 12px; outline: none; }
                input:focus { border-color: #1a73e8; }
                .btn { width: 100%; padding: 14px; background: #1a73e8; color: #fff; border: none; border-radius: 12px; font-size: 16px; font-weight: 700; cursor: pointer; transition: 0.3s; }
                .btn:hover { background: #1557b0; }
                .back { text-align: center; margin-top: 16px; }
                .back a { color: #1a73e8; text-decoration: none; }
            </style>
        </head>
        <body>
            <div class="card">
                <h2>📝 ثبت‌نام</h2>
                <form method="post">
                    <input type="text" name="name" placeholder="نام و نام خانوادگی" required>
                    <input type="text" name="mobile" placeholder="شماره موبایل" required>
                    <input type="text" name="national_code" placeholder="کد ملی" required>
                    <input type="email" name="email" placeholder="ایمیل" required>
                    <input type="text" name="address" placeholder="آدرس منزل">
                    <input type="text" name="postal_code" placeholder="کد پستی">
                    <input type="text" name="ref_code" placeholder="کد معرف (اختیاری)">
                    <button type="submit" class="btn">ثبت‌نام</button>
                </form>
                <div class="back"><a href="/">↩ بازگشت</a></div>
            </div>
        </body>
        </html>
        '''
    
    # POST: ذخیره کاربر
    name = request.form.get('name')
    mobile = request.form.get('mobile')
    national_code = request.form.get('national_code')
    email = request.form.get('email')
    address = request.form.get('address', '')
    postal_code = request.form.get('postal_code', '')
    ref_code = request.form.get('ref_code', '').strip()
    
    conn = get_db()
    c = conn.cursor()
    
    # چک کن قبلاً ثبت‌نام کرده
    c.execute("SELECT * FROM users WHERE mobile = ?", (mobile,))
    if c.fetchone():
        conn.close()
        return '<h2 style="color:#ea4335;">❌ این شماره قبلاً ثبت‌نام کرده!</h2><a href="/">بازگشت</a>'
    
    if not ref_code:
        ref_code = generate_code()
    
    c.execute('''
        INSERT INTO users (name, mobile, email, national_code, address, postal_code, ref_code)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, mobile, email, national_code, address, postal_code, ref_code))
    conn.commit()
    conn.close()
    
    return f'''
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ثبت‌نام موفق</title>
        <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet" />
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
        <style>
            * {{ margin:0; padding:0; box-sizing:border-box; }}
            body {{ font-family:'Vazirmatn',Tahoma,sans-serif; background:linear-gradient(135deg,#f0f2f5,#e8ecf1); min-height:100vh; display:flex; justify-content:center; align-items:center; padding:20px; }}
            .box {{ background:#fff; max-width:500px; width:100%; padding:40px; border-radius:24px; text-align:center; box-shadow:0 10px 40px rgba(0,0,0,0.06); border-top:5px solid #1a73e8; }}
            .icon {{ font-size:64px; margin-bottom:12px; }}
            h2 {{ color:#1a73e8; font-size:24px; margin-bottom:6px; }}
            .sub {{ color:#5f6368; font-size:14px; margin-bottom:16px; }}
            .ref {{ background:#fef7e0; border:1px solid #ffd700; border-radius:12px; padding:12px; margin:12px 0 16px; font-size:18px; font-weight:700; color:#e37400; font-family:monospace; }}
            .btn {{ display:inline-block; background:#1a73e8; color:#fff; padding:12px 40px; border-radius:60px; text-decoration:none; font-weight:700; transition:0.3s; }}
            .btn:hover {{ transform:translateY(-2px); box-shadow:0 8px 30px rgba(26,115,232,0.2); }}
        </style>
    </head>
    <body>
        <div class="box">
            <div class="icon">🎉</div>
            <h2>ثبت‌نام موفق!</h2>
            <p class="sub">به آکادمی ترید خوش آمدید</p>
            <div class="ref">🔑 کد معرف: {ref_code}</div>
            <a href="/" class="btn">🚀 شروع یادگیری</a>
        </div>
    </body>
    </html>
    '''

# ============ دیتابیس ============
@app.route('/db')
def db():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    conn.close()
    
    html = '<html dir="rtl"><head><title>دیتابیس</title></head><body style="font-family:Vazirmatn;padding:20px;background:#f0f2f5;">'
    html += '<h1 style="color:#1a73e8;">📊 دیتابیس کاربران</h1>'
    html += f'<p>تعداد: {len(users)}</p><table border="1" style="border-collapse:collapse;width:100%;background:#fff;">'
    html += '<tr><th>#</th><th>نام</th><th>موبایل</th><th>ایمیل</th><th>کد معرف</th></tr>'
    for u in users:
        html += f'<tr><td>{u[0]}</td><td>{u[1]}</td><td>{u[2]}</td><td>{u[3]}</td><td>{u[7]}</td></tr>'
    html += '</table><br><a href="/">↩ بازگشت</a></body></html>'
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
