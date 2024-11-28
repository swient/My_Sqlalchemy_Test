import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from models import db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # 設置文件上傳的目錄
app.config['DEFAULT_PROFILE_IMAGE'] = 'default.png'  # 預設頭像圖片
db.init_app(app)
migrate = Migrate(app, db)

# 檢查並創建 uploads 目錄
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html', page_title='首頁')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('用戶不存在', 'error')
        elif not user.check_password(password):
            flash('密碼錯誤', 'error')
        else:
            session['username'] = username
            return redirect(url_for('success'))
    return render_template('login.html', page_title='登入')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        profile_image = request.files.get('profile_image')
        if User.query.filter_by(username=username).first():
            flash('用戶名已存在', 'error')
        else:
            new_user = User(username=username)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            user_id = new_user.id  # 獲取用戶的 ID
            if profile_image:
                filename = f"{user_id}.png"
                profile_image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                profile_image.save(profile_image_path)
            else:
                filename = app.config['DEFAULT_PROFILE_IMAGE']
            new_user.profile_image = filename
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html', page_title='註冊')

@app.route('/success')
def success():
    username = session.get('username')
    user = User.query.filter_by(username=username).first()
    return render_template('success.html', username=username, profile_image=user.profile_image, user_id=user.id, page_title='登入成功')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run(debug=True)