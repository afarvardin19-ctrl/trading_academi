# ===== کل محتوای فایل app.py اینجا =====
from flask import Flask, request, render_template, redirect, session
import psycopg2
import os
import random
import string

app = Flask(__name__)
DATABASE_URL = os.environ.get("DATABASE_URL")
app.secret_key = 'your-secret-key-here'

# ===== تابع ثبت‌نام جدید =====
@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        # دریافت داده‌ها
        name = request.form.get('name', '').strip()
        mobile = request.form.get('mobile', '').strip()
        email = request.form.get('email', '').strip()
        national_code = request.form.get('national_code', '').strip()
        address = request.form.get('address', '').strip()
        postal_code = request.form.get('postal_code', '').strip()
        user_code = request.form.get('code', '').strip()
        
        try:
            points = int(request.form.get('points', 0))
        except:
            points = 0
        try:
            unlocked = int(request.form.get('unlocked', 0))
        except:
            unlocked = 0
        try:
            invites = int(request.form.get('invites', 0))
        except:
            invites = 0
            
        invited_by = request.form.get('invited_by', '').strip()
        invited_by_name = request.form.get('invited_by_name', '').strip()
        
        # اعتبارسنجی
        if not name:
            return "❌ نام اجباری است", 400
        if not mobile:
            return "❌ موبایل اجباری است", 400
        if not email:
            return "❌ ایمیل اجباری است", 400
        
        conn = None
        try:
            conn = psycopg2.connect('database.db', timeout=30)
            c = conn.cursor()
            
            c.execute('''
                INSERT INTO users 
                (name, mobile, email, national_code, address, postal_code, 
                 code, points, unlocked, invites, invited_by, invited_by_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (name, mobile, email, national_code, address, postal_code, 
                  user_code, points, unlocked, invites, invited_by, invited_by_name))
            
            conn.commit()
            return "✅ ثبت‌نام موفق!", 200
            
        except psycopg2.IntegrityError as e:
            if 'UNIQUE' in str(e):
                return "❌ ایمیل یا موبایل تکراری است", 400
            return f"❌ خطا: {str(e)}", 400
            
        except Exception as e:
            if 'locked' in str(e):
                return "❌ دیتابیس مشغول است، لحظاتی دیگر تلاش کن", 503
            return f"❌ خطا: {str(e)}", 500
            
        except Exception as e:
            return f"❌ خطا: {str(e)}", 500
            
        finally:
            if conn:
                conn.close()

# بقیه کدهای قبلی (خانه، لاگین، logout و ...)
@app.route('/')
def home():
    return "Welcome to Trading Academy!"

@app.route('/login', methods=['GET', 'POST'])
def login():
    return "Login page"

@app.route('/logout')
def logout():
    return "Logout"

if __name__ == '__main__':
    app.run(debug=True)
