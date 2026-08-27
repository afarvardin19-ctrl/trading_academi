from flask import Flask, render_template_string, request, session, redirect, url_for
import random
import string
import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret_key_12345'

# ============ Supabase (PostgreSQL) ============
DATABASE_URL = "postgresql://postgres:trading_academi@db.beizodqbxsqydjsenjpo.supabase.co:5432/postgres"

def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            mobile TEXT UNIQUE NOT NULL,
            email TEXT,
            national_code TEXT,
            address TEXT,
            postal_code TEXT,
            ref_code TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.close()
    print("✅ دیتابیس Supabase راه‌اندازی شد!")

init_db()

lessons = [
    {"id": 1, "name": "کندل‌شناسی", "free": True},
    {"id": 2, "name": "حمایت و مقاومت", "free": True},
    {"id": 3, "name": "پرایس اکشن مقدماتی", "free": True},
    {"id": 4, "name": "الگوهای کلاسیک", "free": True},
    {"id": 5, "name": "ترند و خط روند", "free": True},
    {"id": 6, "name": "RSI", "free": False},
    {"id": 7, "name": "MACD", "free": False},
    {"id": 8, "name": "میانگین متحرک (MA)", "free": False},
    {"id": 9, "name": "باند بولینگر", "free": False},
    {"id": 10, "name": "استوکستیک", "free": False},
    {"id": 11, "name": "فیبوناچی اصلاحی", "free": False},
    {"id": 12, "name": "فیبوناچی گسترده", "free": False},
    {"id": 13, "name": "چنگال اندروز", "free": False},
    {"id": 14, "name": "امواج الیوت", "free": False},
    {"id": 15, "name": "الگوهای هارمونیک", "free": False},
    {"id": 16, "name": "وایکوف", "free": False},
    {"id": 17, "name": "اسمارت مانی", "free": False},
    {"id": 18, "name": "ICT", "free": False},
    {"id": 19, "name": "پرایس اکشن پیشرفته", "free": False},
    {"id": 20, "name": "مدیریت سرمایه", "free": False},
    {"id": 21, "name": "مدیریت ریسک", "free": False},
    {"id": 22, "name": "روانشناسی بازار", "free": False},
    {"id": 23, "name": "استراتژی معاملاتی", "free": False},
    {"id": 24, "name": "بک تست", "free": False},
    {"id": 25, "name": "سشن‌های معاملاتی", "free": False},
    {"id": 26, "name": "🎯 سیگنال‌گیری حرفه‌ای", "free": False, "special": True},
]

def get_invites_needed(lesson_id):
    if lesson_id <= 5:
        return 0
    elif 6 <= lesson_id <= 18:
        return 3
    elif 19 <= lesson_id <= 25:
        return 4
    elif lesson_id == 26:
        return 10
    return 0

# ============ HTML ============
HTML = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>آکادمی ترید | ۲۶ جلسه تخصصی</title>
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Vazirmatn', Tahoma, sans-serif;
            background: #f0f2f5;
            color: #1a1a2e;
            min-height: 100vh;
            padding: 20px;
        }
        .header {
            max-width: 1200px;
            margin: 0 auto 35px;
            background: #ffffff;
            border-radius: 24px;
            padding: 20px 30px;
            border: 1px solid rgba(0,0,0,0.06);
            box-shadow: 0 4px 20px rgba(0,0,0,0.04);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }
        .logo {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .logo i {
            font-size: 32px;
            color: #1a73e8;
        }
        .logo h1 {
            font-size: 22px;
            font-weight: 800;
            color: #1a1a2e;
        }
        .logo h1 span {
            font-size: 12px;
            color: #5f6368;
            font-weight: 400;
        }
        .header-badge {
            background: #e8f0fe;
            border: 1px solid #d2e3fc;
            padding: 8px 18px;
            border-radius: 40px;
            font-size: 13px;
            color: #1a73e8;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .header-badge a {
            color: #1a73e8;
            text-decoration: none;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        
        .hero-banner {
            background: linear-gradient(135deg, #ffffff, #f8f9fa);
            border: 1px solid rgba(0,0,0,0.06);
            border-radius: 28px;
            padding: 40px 45px;
            margin-bottom: 35px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 25px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        }
        .hero-text h2 {
            font-size: 28px;
            font-weight: 800;
            margin-bottom: 8px;
            color: #1a1a2e;
        }
        .hero-text h2 i { color: #1a73e8; margin-left: 10px; }
        .hero-text p {
            color: #5f6368;
            font-size: 14px;
            max-width: 450px;
            line-height: 1.8;
        }
        .hero-btn {
            background: linear-gradient(135deg, #1a73e8, #1557b0);
            color: #fff;
            padding: 14px 35px;
            border: none;
            border-radius: 60px;
            font-size: 16px;
            font-weight: 700;
            font-family: inherit;
            cursor: pointer;
            transition: all 0.4s;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .hero-btn:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 12px 40px rgba(26,115,232,0.25);
        }
        .section-title {
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 22px;
            display: flex;
            align-items: center;
            gap: 10px;
            color: #1a1a2e;
        }
        .section-title i { color: #1a73e8; }
        .section-title .line {
            flex: 1;
            height: 1px;
            background: linear-gradient(to left, rgba(0,0,0,0.08), transparent);
        }
        .section-title .count {
            font-size: 12px;
            color: #5f6368;
            font-weight: 400;
        }
        .lessons-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
            margin-bottom: 40px;
        }
        .lesson-card {
            background: #ffffff;
            border: 1px solid rgba(0,0,0,0.06);
            border-radius: 14px;
            padding: 16px 20px;
            transition: all 0.3s;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.02);
            cursor: pointer;
        }
        .lesson-card:hover {
            transform: translateY(-3px);
            border-color: rgba(26,115,232,0.15);
            box-shadow: 0 8px 25px rgba(0,0,0,0.06);
        }
        .lesson-card.special {
            border-color: #e37400;
            background: #fef7e0;
        }
        .lesson-card .info {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .lesson-card .num {
            font-size: 12px;
            font-weight: 700;
            color: #9aa0a6;
            min-width: 30px;
        }
        .lesson-card .name {
            font-size: 14px;
            font-weight: 500;
            color: #1a1a2e;
        }
        .lesson-card .badge {
            font-size: 10px;
            padding: 3px 12px;
            border-radius: 30px;
            font-weight: 700;
        }
        .lesson-card .badge.free {
            background: #e6f4ea;
            color: #0f9d58;
        }
        .lesson-card .badge.locked {
            background: #fce8e6;
            color: #ea4335;
        }
        .lesson-card .badge .invite-info {
            font-size: 9px;
            display: block;
            color: #5f6368;
            font-weight: 400;
        }

        .teachers-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .teacher-card {
            background: #ffffff;
            border: 1px solid rgba(0,0,0,0.06);
            border-radius: 18px;
            padding: 20px;
            text-align: center;
            transition: 0.3s;
            box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        }
        .teacher-card:hover {
            box-shadow: 0 8px 30px rgba(0,0,0,0.06);
            border-color: rgba(26,115,232,0.15);
        }
        .teacher-avatar {
            width: 70px;
            height: 70px;
            border-radius: 50%;
            background: #e8f0fe;
            margin: 0 auto 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            color: #1a73e8;
            border: 2px solid #d2e3fc;
        }
        .teacher-card h4 {
            font-size: 14px;
            font-weight: 600;
            color: #1a1a2e;
        }
        .teacher-card p {
            font-size: 11px;
            color: #5f6368;
        }
        .form-section {
            background: #ffffff;
            border: 1px solid rgba(0,0,0,0.06);
            border-radius: 24px;
            padding: 35px 40px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            align-items: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        }
        .form-text h3 {
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 6px;
            color: #1a1a2e;
        }
        .form-text h3 i { color: #1a73e8; }
        .form-text p {
            color: #5f6368;
            font-size: 13px;
            line-height: 1.8;
        }
        .form-text .points {
            margin-top: 12px;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        .form-text .points span {
            font-size: 13px;
            color: #1a1a2e;
        }
        .form-text .points i {
            color: #0f9d58;
            margin-left: 8px;
        }
        .form-box input {
            width: 100%;
            padding: 14px 18px;
            background: #f8f9fa;
            border: 1px solid #dadce0;
            border-radius: 14px;
            color: #1a1a2e;
            font-size: 14px;
            font-family: inherit;
            margin-bottom: 12px;
            outline: none;
            transition: 0.3s;
        }
        .form-box input:focus {
            border-color: #1a73e8;
            box-shadow: 0 0 0 3px rgba(26,115,232,0.1);
        }
        .form-box input::placeholder { color: #9aa0a6; }
        .form-box .btn-gold {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #1a73e8, #1557b0);
            border: none;
            border-radius: 14px;
            color: #fff;
            font-size: 15px;
            font-weight: 700;
            font-family: inherit;
            cursor: pointer;
            transition: 0.3s;
        }
        .form-box .btn-gold:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(26,115,232,0.2);
        }

        .footer {
            margin-top: 40px;
            text-align: center;
            color: #5f6368;
            font-size: 12px;
            border-top: 1px solid rgba(0,0,0,0.04);
            padding-top: 25px;
        }
        .footer i { color: #1a73e8; margin: 0 4px; }
        .progress-bar {
            background: #e8f0fe;
            border-radius: 30px;
            height: 6px;
            margin: 12px 0 20px;
            overflow: hidden;
        }
        .progress-bar .fill {
            height: 100%;
            background: linear-gradient(135deg, #1a73e8, #1557b0);
            border-radius: 30px;
            transition: width 0.5s;
        }
        .modal {
            display: none;
            position: fixed;
            z-index: 999;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.6);
            backdrop-filter: blur(8px);
            justify-content: center;
            align-items: center;
        }
        .modal.show {
            display: flex;
        }
        .modal-content {
            background: #ffffff;
            border-radius: 24px;
            padding: 40px 45px;
            max-width: 450px;
            width: 90%;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            animation: modalIn 0.4s ease;
        }
        @keyframes modalIn {
            from { transform: scale(0.8); opacity: 0; }
            to { transform: scale(1); opacity: 1; }
        }
        .modal-content .icon {
            font-size: 56px;
            margin-bottom: 16px;
        }
        .modal-content h3 {
            font-size: 20px;
            font-weight: 700;
            color: #1a1a2e;
            margin-bottom: 8px;
        }
        .modal-content p {
            color: #5f6368;
            font-size: 14px;
            line-height: 1.8;
            margin-bottom: 20px;
        }
        .modal-content .btn-modal {
            background: linear-gradient(135deg, #1a73e8, #1557b0);
            color: #fff;
            border: none;
            padding: 12px 35px;
            border-radius: 60px;
            font-size: 15px;
            font-weight: 700;
            font-family: inherit;
            cursor: pointer;
            transition: 0.3s;
        }
        .modal-content .btn-modal:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 30px rgba(26,115,232,0.3);
        }
        .modal-content .btn-modal.secondary {
            background: #e8f0fe;
            color: #1a73e8;
            margin-right: 10px;
        }
        .modal-content .btn-modal.secondary:hover {
            background: #d2e3fc;
        }

        .toast {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            background: #323232;
            color: #fff;
            padding: 12px 28px;
            border-radius: 12px;
            font-size: 14px;
            font-family: 'Vazirmatn', Tahoma;
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.4s;
            pointer-events: none;
            box-shadow: 0 8px 30px rgba(0,0,0,0.3);
        }
        .toast.show {
            opacity: 1;
            pointer-events: auto;
        }

        .register-message {
            text-align: center;
            background: linear-gradient(135deg, #e8f0fe, #d2e3fc);
            padding: 14px 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            color: #1a73e8;
            font-weight: 700;
            font-size: 16px;
            border: 1px solid #b7d1f5;
        }
        .register-message i {
            margin-left: 10px;
            font-size: 18px;
        }

        @media (max-width: 768px) {
            .hero-banner { padding: 25px; flex-direction: column; text-align: center; }
            .hero-text h2 { font-size: 22px; }
            .form-section { grid-template-columns: 1fr; padding: 25px; }
            .header { flex-direction: column; text-align: center; }
            .lessons-grid { grid-template-columns: 1fr; }
            .modal-content { padding: 30px 25px; }
        }
    </style>
</head>
<body>

    <div class="toast" id="toast"></div>

    <div class="modal" id="registerModal">
        <div class="modal-content">
            <div class="icon">🔒</div>
            <h3>برای دسترسی ثبت‌نام کنید</h3>
            <p>برای مشاهده این جلسه و تمام جلسات آموزشی، ابتدا باید ثبت‌نام کنید.<br>
            <span style="color:#0f9d58;font-weight:600;">با ثبت‌نام، ۵ جلسه اول برات باز میشه!</span></p>
            <div>
                <button class="btn-modal" onclick="document.getElementById('registerModal').classList.remove('show'); document.getElementById('register').scrollIntoView();">
                    <i class="fas fa-user-plus"></i> ثبت‌نام
                </button>
                <button class="btn-modal secondary" onclick="document.getElementById('registerModal').classList.remove('show');">
                    <i class="fas fa-times"></i> بستن
                </button>
            </div>
        </div>
    </div>

    <div class="header">
        <div class="logo">
            <i class="fas fa-chart-line"></i>
            <div>
                <h1>آکادمی ترید <span>| ۲۶ جلسه</span></h1>
            </div>
        </div>
        <div class="header-badge">
            <i class="fas fa-graduation-cap"></i> ۲۶ جلسه تخصصی
        </div>
    </div>

    <div class="container">

        <div class="hero-banner">
            <div class="hero-text">
                <h2><i class="fas fa-crown"></i> ۲۶ جلسه تخصصی بازار مالی</h2>
                <p>از کندل‌شناسی تا سیگنال‌گیری حرفه‌ای، با اساتید برتر ایران.</p>
            </div>
            <button class="hero-btn" onclick="document.getElementById('register').scrollIntoView()">
                <i class="fas fa-play-circle"></i> شروع رایگان
            </button>
        </div>

        <div class="section-title">
            <i class="fas fa-graduation-cap"></i> دوره‌های آموزشی
            <span class="line"></span>
            <span class="count">{{ lessons|length }} جلسه</span>
        </div>

        <div class="register-message">
            <i class="fas fa-info-circle"></i> ثبت‌نام کنید و به ۵ جلسه رایگان دسترسی پیدا کنید
        </div>

        <div style="font-size:13px;color:#5f6368;margin-bottom:8px;">
            <i class="fas fa-unlock" style="color:#0f9d58;"></i> 
            ۰ از {{ lessons|length }} جلسه باز شده
        </div>
        <div class="progress-bar">
            <div class="fill" style="width: 0%;"></div>
        </div>

        <div class="lessons-grid">
            {% for lesson in lessons %}
                <div class="lesson-card {% if lesson.special %}special{% endif %}">
                    <div class="info">
                        <span class="num">جلسه {{ lesson.id }}</span>
                        <span class="name">{{ lesson.name }}</span>
                    </div>
                    {% if lesson.free %}
                        <span class="badge free"><i class="fas fa-unlock"></i> رایگان</span>
                    {% else %}
                        {% set needed = get_invites_needed(lesson.id) %}
                        <span class="badge locked"><i class="fas fa-lock"></i> قفل <span class="invite-info">{{ needed }} دعوت</span></span>
                    {% endif %}
                </div>
            {% endfor %}
        </div>

        <div class="section-title">
            <i class="fas fa-user-tie"></i> اساتید برتر
            <span class="line"></span>
        </div>

        <div class="teachers-grid">
            <div class="teacher-card">
                <div class="teacher-avatar"><i class="fas fa-user-circle"></i></div>
                <h4>محمد کریمی</h4>
                <p>تحلیلگر بازار سرمایه</p>
            </div>
            <div class="teacher-card">
                <div class="teacher-avatar"><i class="fas fa-user-circle"></i></div>
                <h4>سارا محمدی</h4>
                <p>متخصص پرایس اکشن</p>
            </div>
            <div class="teacher-card">
                <div class="teacher-avatar"><i class="fas fa-user-circle"></i></div>
                <h4>رضا احمدی</h4>
                <p>مدرس ارشد فارکس</p>
            </div>
            <div class="teacher-card">
                <div class="teacher-avatar"><i class="fas fa-user-circle"></i></div>
                <h4>نازنین حسینی</h4>
                <p>روانشناس بازار</p>
            </div>
        </div>

        <div class="form-section" id="register">
            <div class="form-text">
                <h3><i class="fas fa-gift"></i> ثبت‌نام کنید و ۵ جلسه هدیه بگیرید!</h3>
                <p>همین الان ثبت‌نام کنید و به ۵ جلسه اول دوره دسترسی پیدا کنید.</p>
                <div class="points">
                    <span><i class="fas fa-check-circle"></i> ۵ جلسه آموزشی با ثبت‌نام</span>
                    <span><i class="fas fa-check-circle"></i> دریافت مدرک معتبر</span>
                    <span><i class="fas fa-check-circle"></i> بدون نیاز به پرداخت</span>
                </div>
            </div>
            <div class="form-box">
                <form action="/register" method="post" id="registerForm">
                    <input type="text" name="name" placeholder="👤 نام و نام خانوادگی" required>
                    <input type="text" name="mobile" placeholder="📞 شماره موبایل" required>
                    <input type="text" name="national_code" placeholder="🪪 کد ملی" required>
                    <input type="email" name="email" placeholder="📧 ایمیل" required>
                    <input type="text" name="address" placeholder="🏠 آدرس منزل">
                    <input type="text" name="postal_code" placeholder="📮 کد پستی">
                    <input type="text" name="ref_code" placeholder="🔑 کد معرف (اگر دارید)">
                    <button type="submit" class="btn-gold">ثبت‌نام و مشاهده دوره</button>
                </form>
            </div>
        </div>

        <div class="footer">
            <i class="fas fa-crown"></i> آکادمی ترید حرفه‌ای ایران · ۱۴۰۴ <br>
            ۲۶ جلسه تخصصی از مبتدی تا سیگنال‌گیری حرفه‌ای
        </div>

    </div>

    <script>
    function showToast(msg) {
        const t = document.getElementById('toast');
        t.textContent = msg;
        t.classList.add('show');
        setTimeout(() => t.classList.remove('show'), 2500);
    }

    document.getElementById('registerModal').addEventListener('click', function(e) {
        if (e.target === this) {
            this.classList.remove('show');
        }
    });
    </script>

</body>
</html>
"""

# ============ روت‌های اصلی ============
@app.route('/')
def index():
    return render_template_string(HTML, lessons=lessons, get_invites_needed=get_invites_needed)

@app.route('/register', methods=['POST'])
def register():
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
    c.execute("SELECT * FROM users WHERE mobile = %s", (mobile,))
    existing = c.fetchone()
    if existing:
        conn.close()
        return """
        <div style="text-align:center;padding:60px 20px;font-family:'Vazirmatn',Tahoma;background:#f0f2f5;color:#1a1a2e;min-height:100vh;display:flex;flex-direction:column;justify-content:center;align-items:center;">
            <div style="font-size:64px;margin-bottom:20px;">⚠️</div>
            <h2 style="color:#ea4335;font-size:26px;">این شماره قبلاً ثبت‌نام کرده!</h2>
            <a href="/" style="color:#1a73e8;text-decoration:none;margin-top:20px;border:1px solid #1a73e8;padding:10px 30px;border-radius:40px;transition:0.3s;">↩ بازگشت به سایت</a>
        </div>
        """
    
    # تولید کد معرف
    if not ref_code:
        ref_code = generate_code()
    
    # ذخیره کاربر
    c.execute('''
        INSERT INTO users (name, mobile, email, national_code, address, postal_code, ref_code)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', (name, mobile, email, national_code, address, postal_code, ref_code))
    conn.commit()
    conn.close()
    
    return f"""
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ثبت‌نام موفق</title>
        <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet" />
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
        <style>
            *{{ margin:0; padding:0; box-sizing:border-box; }}
            body{{
                font-family:'Vazirmatn',Tahoma,sans-serif;
                background:linear-gradient(135deg, #f0f2f5 0%, #e8ecf1 100%);
                color:#1a1a2e;
                min-height:100vh;
                display:flex;
                justify-content:center;
                align-items:center;
                padding:20px;
            }}
            .success-box{{
                background:#ffffff;
                border-radius:32px;
                padding:50px 60px;
                max-width:520px;
                width:100%;
                text-align:center;
                box-shadow:0 20px 60px rgba(0,0,0,0.08);
                border-top:5px solid #1a73e8;
            }}
            .icon{{ font-size:72px; margin-bottom:16px; }}
            h2{{ color:#1a73e8; font-size:26px; font-weight:800; margin-bottom:8px; }}
            .sub{{ color:#5f6368; font-size:14px; line-height:2; margin-bottom:20px; }}
            .box{{
                background:#e8f0fe;
                border-radius:16px;
                padding:16px 20px;
                margin:16px 0 24px;
                border-right:4px solid #1a73e8;
                text-align:right;
            }}
            .box p{{ font-size:13px; color:#1a1a2e; line-height:2; }}
            .box i{{ color:#0f9d58; margin-left:8px; }}
            .btn{{
                background:linear-gradient(135deg, #1a73e8, #1557b0);
                color:#fff;
                border:none;
                padding:14px 40px;
                border-radius:60px;
                font-size:16px;
                font-weight:700;
                font-family:inherit;
                cursor:pointer;
                transition:all 0.3s;
                text-decoration:none;
                display:inline-block;
            }}
            .btn:hover{{
                transform:translateY(-3px);
                box-shadow:0 10px 35px rgba(26,115,232,0.3);
            }}
            .ref-box{{
                background:#fef7e0;
                border-radius:12px;
                padding:12px 16px;
                margin:10px 0 16px;
                border:1px solid #ffd700;
                text-align:center;
            }}
            .ref-box span{{
                font-size:18px;
                font-weight:700;
                color:#e37400;
                letter-spacing:2px;
                font-family:monospace;
            }}
        </style>
    </head>
    <body>
        <div class="success-box">
            <div class="icon">🎓</div>
            <h2>ثبت‌نام شما با موفقیت انجام شد</h2>
            <p class="sub">به خانواده بزرگ آکادمی ترید خوش آمدید.<br>هم‌اکنون می‌توانید ویدیوهای آموزشی را مشاهده کنید.</p>
            <div class="ref-box">
                🔑 کد معرف شما: <span>{ref_code}</span>
            </div>
            <div class="box">
                <p><i class="fas fa-unlock"></i> <b>۵ جلسه آموزشی</b> برای شما باز شده است</p>
                <p><i class="fas fa-certificate"></i> پس از تکمیل دوره، <b>مدرک معتبر</b> دریافت می‌کنید</p>
                <p><i class="fas fa-user-plus"></i> با دعوت دوستان، جلسات بیشتر را باز کنید</p>
            </div>
            <a href="/" class="btn"><i class="fas fa-play-circle"></i> شروع یادگیری</a>
        </div>
    </body>
    </html>
    """

def generate_code():
    return 'VIP-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# ============ صفحات دیتابیس و ادمین ============
@app.route('/db')
def db_viewer():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users ORDER BY id DESC")
    users = c.fetchall()
    conn.close()
    return render_template_string("""
    <html dir='rtl'>
    <head>
        <title>دیتابیس کاربران</title>
        <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
        <style>
            body{font-family:'Vazirmatn',Tahoma;background:#f0f2f5;padding:20px;}
            .container{max-width:1200px;margin:0 auto;background:#fff;border-radius:16px;padding:20px;box-shadow:0 4px 20px rgba(0,0,0,0.05);}
            h1{color:#1a73e8;font-size:24px;margin-bottom:20px;}
            table{width:100%;border-collapse:collapse;font-size:14px;}
            th{background:#e8f0fe;padding:12px;text-align:right;border-bottom:2px solid #d2e3fc;}
            td{padding:10px 12px;border-bottom:1px solid #eef2f7;}
            tr:hover{background:#f8faff;}
            .badge{background:#e8f0fe;color:#1a73e8;padding:2px 10px;border-radius:30px;font-size:12px;}
            .back{color:#1a73e8;text-decoration:none;font-weight:600;}
            .back:hover{text-decoration:underline;}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 دیتابیس کاربران</h1>
            <p style="color:#5f6368;margin-bottom:16px;">تعداد کاربران: <span class="badge">{{ users|length }}</span></p>
            <table>
                <tr><th>#</th><th>نام</th><th>موبایل</th><th>ایمیل</th><th>کد ملی</th><th>آدرس</th><th>کد پستی</th><th>کد معرف</th></tr>
                {% for user in users %}
                <tr>
                    <td>{{ user[0] }}</td>
                    <td><strong>{{ user[1] }}</strong></td>
                    <td dir="ltr">{{ user[2] }}</td>
                    <td>{{ user[3] or '-' }}</td>
                    <td>{{ user[4] or '-' }}</td>
                    <td style="max-width:200px;word-wrap:break-word;">{{ user[5] or '-' }}</td>
                    <td dir="ltr">{{ user[6] or '-' }}</td>
                    <td><code>{{ user[7] or '-' }}</code></td>
                </tr>
                {% else %}
                <tr><td colspan="8" style="text-align:center;padding:40px;color:#9aa0a6;">❌ هیچ کاربری ثبت‌نام نکرده است</td></tr>
                {% endfor %}
            </table>
            <p style="margin-top:20px;"><a href="/" class="back">↩ بازگشت به سایت</a></p>
        </div>
    </body>
    </html>
    """, users=users)

@app.route('/admin')
def admin():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users ORDER BY id DESC")
    users = c.fetchall()
    conn.close()
    return render_template_string("""
    <html dir='rtl'>
    <head>
        <title>پنل مدیریت</title>
        <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
        <style>
            body{font-family:'Vazirmatn',Tahoma;background:#f0f2f5;padding:20px;}
            .container{max-width:1200px;margin:0 auto;background:#fff;border-radius:16px;padding:20px;box-shadow:0 4px 20px rgba(0,0,0,0.05);}
            h1{color:#1a73e8;font-size:24px;margin-bottom:20px;}
            table{width:100%;border-collapse:collapse;font-size:14px;}
            th{background:#e8f0fe;padding:12px;text-align:right;border-bottom:2px solid #d2e3fc;}
            td{padding:10px 12px;border-bottom:1px solid #eef2f7;}
            tr:hover{background:#f8faff;}
            .badge{background:#e8f0fe;color:#1a73e8;padding:2px 10px;border-radius:30px;font-size:12px;}
            .back{color:#1a73e8;text-decoration:none;font-weight:600;}
            .back:hover{text-decoration:underline;}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔐 پنل مدیریت</h1>
            <p style="color:#5f6368;margin-bottom:16px;">تعداد کاربران: <span class="badge">{{ users|length }}</span></p>
            <table>
                <tr><th>#</th><th>نام</th><th>موبایل</th><th>ایمیل</th><th>کد ملی</th><th>آدرس</th><th>کد پستی</th><th>کد معرف</th></tr>
                {% for user in users %}
                <tr>
                    <td>{{ user[0] }}</td>
                    <td><strong>{{ user[1] }}</strong></td>
                    <td dir="ltr">{{ user[2] }}</td>
                    <td>{{ user[3] or '-' }}</td>
                    <td>{{ user[4] or '-' }}</td>
                    <td style="max-width:200px;word-wrap:break-word;">{{ user[5] or '-' }}</td>
                    <td dir="ltr">{{ user[6] or '-' }}</td>
                    <td><code>{{ user[7] or '-' }}</code></td>
                </tr>
                {% else %}
                <tr><td colspan="8" style="text-align:center;padding:40px;color:#9aa0a6;">❌ هیچ کاربری ثبت‌نام نکرده است</td></tr>
                {% endfor %}
            </table>
            <p style="margin-top:20px;"><a href="/" class="back">↩ بازگشت به سایت</a></p>
        </div>
    </body>
    </html>
    """, users=users)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
