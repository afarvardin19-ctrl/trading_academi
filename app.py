from flask import Flask, render_template_string, request, session, redirect, url_for
import random
import string
import sqlite3
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
        c.execute("SELECT id FROM users WHERE code = ?", (code,))
        if not c.fetchone():
            conn.close()
            return code
        conn.close()

def get_user_by_code(code):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE code = ?", (code,))
    user = c.fetchone()
    conn.close()
    return user

def get_user_by_mobile(mobile):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE mobile = ?", (mobile,))
    user = c.fetchone()
    conn.close()
    return user

def update_user_points(mobile, points, unlocked, invites):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE users SET points = ?, unlocked = ?, invites = ? WHERE mobile = ?", 
              (points, unlocked, invites, mobile))
    conn.commit()
    conn.close()

# ============ جلسات ============
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

# ============ HTML کامل (همان قبلی با تغییرات) ============
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
        .logo { display: flex; align-items: center; gap: 12px; }
        .logo i { font-size: 32px; color: #1a73e8; }
        .logo h1 { font-size: 22px; font-weight: 800; color: #1a1a2e; }
        .logo h1 span { font-size: 12px; color: #5f6368; font-weight: 400; }
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
        .header-badge a { color: #1a73e8; text-decoration: none; }
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
        .hero-text h2 { font-size: 28px; font-weight: 800; margin-bottom: 8px; color: #1a1a2e; }
        .hero-text h2 i { color: #1a73e8; margin-left: 10px; }
        .hero-text p { color: #5f6368; font-size: 14px; max-width: 450px; line-height: 1.8; }
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
        .hero-btn:hover { transform: translateY(-3px) scale(1.02); box-shadow: 0 12px 40px rgba(26,115,232,0.25); }
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
        .section-title .line { flex: 1; height: 1px; background: linear-gradient(to left, rgba(0,0,0,0.08), transparent); }
        .section-title .count { font-size: 12px; color: #5f6368; font-weight: 400; }
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
        .lesson-card:hover { transform: translateY(-3px); border-color: rgba(26,115,232,0.15); box-shadow: 0 8px 25px rgba(0,0,0,0.06); }
        .lesson-card.special { border-color: #e37400; background: #fef7e0; }
        .lesson-card .info { display: flex; align-items: center; gap: 12px; }
        .lesson-card .num { font-size: 12px; font-weight: 700; color: #9aa0a6; min-width: 30px; }
        .lesson-card .name { font-size: 14px; font-weight: 500; color: #1a1a2e; }
        .lesson-card .badge {
            font-size: 10px;
            padding: 3px 12px;
            border-radius: 30px;
            font-weight: 700;
        }
        .lesson-card .badge.free { background: #e6f4ea; color: #0f9d58; }
        .lesson-card .badge.locked { background: #fce8e6; color: #ea4335; }
        .lesson-card .badge.register { background: #e8f0fe; color: #1a73e8; }
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
        .teacher-card:hover { box-shadow: 0 8px 30px rgba(0,0,0,0.06); border-color: rgba(26,115,232,0.15); }
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
        .teacher-card h4 { font-size: 14px; font-weight: 600; color: #1a1a2e; }
        .teacher-card p { font-size: 11px; color: #5f6368; }
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
        .form-text h3 { font-size: 20px; font-weight: 700; margin-bottom: 6px; color: #1a1a2e; }
        .form-text h3 i { color: #1a73e8; }
        .form-text p { color: #5f6368; font-size: 13px; line-height: 1.8; }
        .form-text .points { margin-top: 12px; display: flex; flex-direction: column; gap: 6px; }
        .form-text .points span { font-size: 13px; color: #1a1a2e; }
        .form-text .points i { color: #0f9d58; margin-left: 8px; }
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
        .form-box input:focus { border-color: #1a73e8; box-shadow: 0 0 0 3px rgba(26,115,232,0.1); }
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
        .form-box .btn-gold:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(26,115,232,0.2); }
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
        .logout-btn {
            background: none;
            border: none;
            color: #ea4335;
            font-family: inherit;
            font-size: 13px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .logout-btn:hover { text-decoration: underline; }
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
        .modal.show { display: flex; }
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
        .modal-content .icon { font-size: 56px; margin-bottom: 16px; }
        .modal-content h3 { font-size: 20px; font-weight: 700; color: #1a1a2e; margin-bottom: 8px; }
        .modal-content p { color: #5f6368; font-size: 14px; line-height: 1.8; margin-bottom: 20px; }
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
        .modal-content .btn-modal:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(26,115,232,0.3); }
        .modal-content .btn-modal.secondary { background: #e8f0fe; color: #1a73e8; margin-right: 10px; }
        .modal-content .btn-modal.secondary:hover { background: #d2e3fc; }
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
        .toast.show { opacity: 1; pointer-events: auto; }

        /* پنل ادمین */
        .admin-link {
            background: #fef7e0;
            border: 1px solid #ffd700;
            padding: 6px 14px;
            border-radius: 30px;
            font-size: 12px;
            color: #e37400;
            text-decoration: none;
            transition: 0.3s;
        }
        .admin-link:hover { background: #ffd700; color: #1a1a2e; }

        @media (max-width: 768px) {
            .hero-banner { padding: 25px; flex-direction: column; text-align: center; }
            .hero-text h2 { font-size: 22px; }
            .form-section { grid-template-columns: 1fr; padding: 25px; }
            .header { flex-direction: column; text-align: center; }
            .lessons-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>

    <div class="toast" id="toast"></div>

    <div class="modal" id="registerModal">
        <div class="modal-content">
            <div class="icon">🔒</div>
            <h3>برای دسترسی ثبت‌نام کنید</h3>
            <p>برای مشاهده ویدیوهای آموزشی و استفاده از تمام امکانات، ابتدا ثبت‌نام خود را تکمیل کنید.<br>
            <span style="color:#0f9d58;font-weight:600;">پس از ثبت‌نام، ۵ جلسه اول برای شما باز خواهد شد.</span></p>
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
            {% if session.get('user_code') %}
                <i class="fas fa-user-circle"></i>
                <a href="#panel">{{ session.get('name', 'کاربر') }}</a>
                <form action="/logout" method="post" style="display:inline;">
                    <button type="submit" class="logout-btn"><i class="fas fa-sign-out-alt"></i> خروج</button>
                </form>
            {% else %}
                <i class="fas fa-graduation-cap"></i> ۲۶ جلسه تخصصی
            {% endif %}
            <a href="/admin" class="admin-link"><i class="fas fa-user-shield"></i> مدیریت</a>
        </div>
    </div>

    <div class="container">

        <div class="hero-banner">
            <div class="hero-text">
                <h2><i class="fas fa-crown"></i> ۲۶ جلسه تخصصی بازار مالی</h2>
                <p>از کندل‌شناسی تا سیگنال‌گیری حرفه‌ای، با اساتید برتر ایران.</p>
            </div>
            {% if not session.get('user_code') %}
            <button class="hero-btn" onclick="document.getElementById('register').scrollIntoView()">
                <i class="fas fa-play-circle"></i> شروع رایگان
            </button>
            {% else %}
            <button class="hero-btn" onclick="document.getElementById('register').scrollIntoView()">
                <i class="fas fa-user-plus"></i> دعوت دوستان
            </button>
            {% endif %}
        </div>

        <div class="section-title">
            <i class="fas fa-graduation-cap"></i> دوره‌های آموزشی
            <span class="line"></span>
            <span class="count">{{ lessons|length }} جلسه</span>
        </div>

        {% set unlocked = session.get('unlocked', 5) if session.get('user_code') else 0 %}
        <div style="font-size:13px;color:#5f6368;margin-bottom:8px;">
            <i class="fas fa-unlock" style="color:#0f9d58;"></i> 
            {% if session.get('user_code') %}
                {{ unlocked }} از {{ lessons|length }} جلسه باز شده
            {% else %}
                برای مشاهده ویدیوهای آموزشی، <a href="#register" style="color:#1a73e8;font-weight:600;">ثبت‌نام</a> کنید
            {% endif %}
        </div>
        <div class="progress-bar">
            <div class="fill" style="width: {{ (unlocked / lessons|length * 100)|round if session.get('user_code') else 0 }}%;"></div>
        </div>

        <div class="lessons-grid">
            {% for lesson in lessons %}
                <div class="lesson-card {% if lesson.special %}special{% endif %}" 
                     onclick="{% if not session.get('user_code') %}document.getElementById('registerModal').classList.add('show');{% endif %}">
                    <div class="info">
                        <span class="num">جلسه {{ lesson.id }}</span>
                        <span class="name">{{ lesson.name }}</span>
                    </div>
                    {% if session.get('user_code') %}
                        {% if lesson.free or lesson.id <= unlocked %}
                            <span class="badge free"><i class="fas fa-unlock"></i> باز</span>
                        {% elif lesson.special and unlocked >= 26 %}
                            <span class="badge free"><i class="fas fa-unlock"></i> باز</span>
                        {% else %}
                            <span class="badge locked"><i class="fas fa-lock"></i> قفل</span>
                        {% endif %}
                    {% else %}
                        {% if lesson.free %}
                            <span class="badge register"><i class="fas fa-user-plus"></i> ثبت‌نام</span>
                        {% else %}
                            <span class="badge locked"><i class="fas fa-lock"></i> قفل</span>
                        {% endif %}
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
                <h3><i class="fas fa-gift"></i> {% if session.get('user_code') %}دوستان خود را دعوت کنید!{% else %}ثبت‌نام کنید و ۵ جلسه آموزشی را ببینید!{% endif %}</h3>
                <p>{% if session.get('user_code') %}هر دعوت = ۱ امتیاز | هر قفل = ۷ امتیاز | جلسه آخر = ۱۲ امتیاز{% else %}همین الان ثبت‌نام کنید و به ۵ جلسه اول دوره دسترسی پیدا کنید.{% endif %}</p>
                <div class="points">
                    {% if session.get('user_code') %}
                        <span><i class="fas fa-check-circle"></i> هر دعوت = ۱ امتیاز</span>
                        <span><i class="fas fa-check-circle"></i> هر قفل = ۷ امتیاز</span>
                        <span><i class="fas fa-check-circle"></i> جلسه آخر = ۱۲ امتیاز</span>
                    {% else %}
                        <span><i class="fas fa-check-circle"></i> ۵ جلسه آموزشی با ثبت‌نام</span>
                        <span><i class="fas fa-check-circle"></i> دریافت مدرک معتبر</span>
                        <span><i class="fas fa-check-circle"></i> بدون نیاز به پرداخت</span>
                    {% endif %}
                </div>
                {% if session.get('user_code') %}
                <div style="margin-top:12px;background:#e6f4ea;border-radius:10px;padding:12px 16px;border:1px solid #b7e1cd;">
                    <span style="color:#0f9d58;font-size:13px;">
                        <i class="fas fa-check-circle"></i> امتیاز شما: {{ session.get('points', 0) }}
                        &nbsp;|&nbsp; <i class="fas fa-user-plus"></i> {{ session.get('invites', 0) }} دعوت
                        &nbsp;|&nbsp; <i class="fas fa-unlock"></i> {{ session.get('unlocked', 5) }} جلسه باز
                    </span>
                </div>
                {% endif %}
            </div>
            <div class="form-box">
                <form action="/register" method="post" id="registerForm">
                    <input type="text" name="name" placeholder="👤 نام و نام خانوادگی" required>
                    <input type="text" name="mobile" placeholder="📞 شماره موبایل" required>
                    <input type="email" name="email" placeholder="📧 ایمیل" required>
                    <input type="text" name="address" placeholder="🏠 آدرس منزل">
                    <input type="text" name="postal_code" placeholder="📮 کد پستی">
                    <input type="text" name="ref_code" placeholder="🔑 کد معرف (اگر دارید)">
                    <button type="submit" class="btn-gold">
                        <i class="fas fa-rocket"></i> {% if session.get('user_code') %}ثبت‌نام مجدد{% else %}ثبت‌نام و مشاهده دوره{% endif %}
                    </button>
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

# ============ ADMIN HTML ============
ADMIN_HTML = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>پنل مدیریت | آکادمی ترید</title>
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Vazirmatn', Tahoma, sans-serif;
            background: #f0f2f5;
            color: #1a1a2e;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            background: #ffffff;
            border-radius: 24px;
            padding: 20px 30px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.04);
        }
        .header h1 { font-size: 24px; font-weight: 800; }
        .header h1 i { color: #1a73e8; }
        .header .stats { display: flex; gap: 20px; font-size: 14px; flex-wrap: wrap; }
        .header .stats span { background: #e8f0fe; padding: 6px 16px; border-radius: 30px; }
        .card {
            background: #ffffff;
            border-radius: 24px;
            padding: 25px 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.03);
            overflow-x: auto;
        }
        .card h2 { font-size: 18px; margin-bottom: 16px; }
        .card h2 i { color: #1a73e8; }
        table { width: 100%; border-collapse: collapse; font-size: 13px; }
        th {
            background: #f8f9fa;
            padding: 12px 14px;
            text-align: right;
            font-weight: 700;
            border-bottom: 2px solid #e8edf2;
            white-space: nowrap;
        }
        td { padding: 10px 14px; border-bottom: 1px solid #eef2f7; vertical-align: middle; }
        tr:hover { background: #f8faff; }
        .badge {
            font-size: 11px;
            padding: 3px 10px;
            border-radius: 30px;
            font-weight: 600;
        }
        .badge.green { background: #e6f4ea; color: #0f9d58; }
        .badge.blue { background: #e8f0fe; color: #1a73e8; }
        .badge.gold { background: #fef7e0; color: #e37400; }
        .badge.red { background: #fce8e6; color: #ea4335; }
        .code-mono {
            font-family: monospace;
            background: #f1f3f4;
            padding: 2px 8px;
            border-radius: 6px;
            font-size: 12px;
        }
        .empty { text-align: center; color: #9aa0a6; padding: 40px; }
        .btn {
            background: #1a73e8;
            color: #fff;
            border: none;
            padding: 6px 14px;
            border-radius: 30px;
            font-size: 12px;
            cursor: pointer;
            transition: 0.3s;
        }
        .btn:hover { background: #1557b0; }
        .btn.danger { background: #ea4335; }
        .btn.danger:hover { background: #c62828; }
        .search-box {
            display: flex;
            gap: 10px;
            margin-bottom: 16px;
            flex-wrap: wrap;
        }
        .search-box input {
            padding: 10px 16px;
            border: 1px solid #dadce0;
            border-radius: 14px;
            font-size: 14px;
            font-family: inherit;
            flex: 1;
            min-width: 200px;
            outline: none;
        }
        .search-box input:focus { border-color: #1a73e8; }
        .back-link {
            color: #1a73e8;
            text-decoration: none;
        }
        .back-link:hover { text-decoration: underline; }
        @media (max-width: 768px) {
            .header { flex-direction: column; text-align: center; }
            table { font-size: 11px; }
            th, td { padding: 6px 8px; }
        }
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <h1><i class="fas fa-user-shield"></i> پنل مدیریت</h1>
        <div class="stats">
            <span><i class="fas fa-users"></i> {{ users|length }} کاربر</span>
            <span><i class="fas fa-star"></i> کل امتیازات: {{ total_points }}</span>
            <span><a href="/" class="back-link"><i class="fas fa-arrow-left"></i> بازگشت به سایت</a></span>
        </div>
    </div>

    <div class="card">
        <h2><i class="fas fa-list"></i> لیست کاربران</h2>
        <div class="search-box">
            <input type="text" id="searchInput" placeholder="🔍 جستجو در نام، موبایل، ایمیل..." onkeyup="searchTable()">
        </div>
        <div style="overflow-x:auto;">
            <table id="userTable">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>نام</th>
                        <th>موبایل</th>
                        <th>ایمیل</th>
                        <th>کد معرف</th>
                        <th>امتیاز</th>
                        <th>جلسات باز</th>
                        <th>دعوت‌ها</th>
                        <th>تاریخ ثبت</th>
                        <th>عملیات</th>
                    </tr>
                </thead>
                <tbody>
                    {% for user in users %}
                    <tr>
                        <td>{{ user.id }}</td>
                        <td><strong>{{ user.name }}</strong></td>
                        <td dir="ltr">{{ user.mobile }}</td>
                        <td>{{ user.email or '-' }}</td>
                        <td><span class="code-mono">{{ user.code }}</span></td>
                        <td><span class="badge gold">{{ user.points }}</span></td>
                        <td><span class="badge green">{{ user.unlocked }}</span></td>
                        <td>{{ user.invites }}</td>
                        <td dir="ltr" style="font-size:11px;color:#5f6368;">{{ user.registered_at[:16] }}</td>
                        <td>
                            <form action="/admin/delete/{{ user.id }}" method="post" style="display:inline;" onsubmit="return confirm('حذف این کاربر؟')">
                                <button class="btn danger" style="padding:4px 10px;font-size:11px;"><i class="fas fa-trash"></i></button>
                            </form>
                        </td>
                    </tr>
                    {% else %}
                    <tr><td colspan="10" class="empty">❌ هیچ کاربری یافت نشد</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<script>
function searchTable() {
    const input = document.getElementById('searchInput');
    const filter = input.value.toLowerCase();
    const table = document.getElementById('userTable');
    const rows = table.getElementsByTagName('tr');
    for (let i = 1; i < rows.length; i++) {
        const cells = rows[i].getElementsByTagName('td');
        let found = false;
        for (let j = 0; j < cells.length - 1; j++) {
            if (cells[j]) {
                const text = cells[j].textContent.toLowerCase();
                if (text.includes(filter)) { found = true; break; }
            }
        }
        rows[i].style.display = found ? '' : 'none';
    }
}
</script>

</body>
</html>
"""

# ============ روت‌های اصلی ============
@app.route('/')
def index():
    return render_template_string(HTML, lessons=lessons)

@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    mobile = request.form.get('mobile')
    email = request.form.get('email')
    address = request.form.get('address', '')
    postal_code = request.form.get('postal_code', '')
    ref_code = request.form.get('ref_code', '').strip()
    
    existing = get_user_by_mobile(mobile)
    if existing:
        session['user_code'] = existing['code']
        session['name'] = existing['name']
        session['mobile'] = existing['mobile']
        session['points'] = existing['points']
        session['unlocked'] = existing['unlocked']
        session['invites'] = existing['invites']
        return redirect(url_for('index'))
    
    user_code = generate_unique_code()
    points = 0
    unlocked = 5
    invites = 0
    invited_by = None
    invited_by_name = None
    
    if ref_code:
        referrer = get_user_by_code(ref_code)
        if referrer:
            invited_by = referrer['mobile']
            invited_by_name = referrer['name']
            new_points = referrer['points'] + 1
            new_invites = referrer['invites'] + 1
            new_unlocked = 5 + (new_points // 7)
            if new_points >= 12:
                new_unlocked = max(new_unlocked, 26)
            update_user_points(referrer['mobile'], new_points, new_unlocked, new_invites)
    
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO users (name, mobile, email, address, postal_code, code, points, unlocked, invites, invited_by, invited_by_name)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, mobile, email, address, postal_code, user_code, points, unlocked, invites, invited_by, invited_by_name))
    conn.commit()
    conn.close()
    
    session['user_code'] = user_code
    session['name'] = name
    session['mobile'] = mobile
    session['points'] = points
    session['unlocked'] = unlocked
    session['invites'] = invites
    
    return redirect(url_for('index'))

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))

# ============ روت‌های ادمین ============
@app.route('/admin')
def admin():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users ORDER BY id DESC")
    users = c.fetchall()
    conn.close()
    total_points = sum(u['points'] for u in users)
    return render_template_string(ADMIN_HTML, users=users, total_points=total_points)

@app.route('/admin/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

@app.route('/db')
def db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    conn.close()
    
    html = '<h1>📊 دیتابیس کاربران</h1>'
    html += f'<p>تعداد: {len(users)}</p>'
    html += '<table border="1"><tr><th>#</th><th>نام</th><th>موبایل</th><th>ایمیل</th><th>کد معرف</th></tr>'
    for u in users:
        html += f'<tr><td>{u[0]}</td><td>{u[1]}</td><td>{u[2]}</td><td>{u[3]}</td><td>{u[7]}</td></tr>'
    html += '</table><br><a href="/">↩ بازگشت</a>'
    return html
