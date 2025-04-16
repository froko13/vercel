from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, login_required, logout_user, current_user, login_manager
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import func, desc
from sqlalchemy import exc
from datetime import datetime, timedelta
from app.models import User
from runner import bp, db
import yfinance as yf




# Ваши маршруты

ticker = 'AAPL'  # Например, Apple
start_date = '2023-01-01'
end_date = '2023-10-01'

# Загружаем данные о ценах акций
data = yf.download(ticker, start=start_date, end=end_date)
dates = data.index
close_prices = data['Close']

@bp.route('/')
def home():
    return render_template('index_home.html')

@bp.route("/register", methods=["GET", "POST"])
def register():

    labelLogin = ''

    if request.method == 'POST':
        username = request.form['username'] #получает логин
        password = request.form['password'] #получает пароль
        email = request.form['email']

        #хэшируем пароль
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        #создаем нового пользователя с username и хэшированным паролем
        new_user = User(username=username, password=hashed_password, email = email, user_id = 0)

        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('main.home'), 301)  

        except exc.IntegrityError:
            db.session.rollback()
            labelLogin = 'Этот Email уже зарегистрирован. Войдите в аккаунт'

    
    return render_template('register.html', labelLogin = labelLogin)

@bp.route('/login', methods=["GET", "POST"])
def login():
    statusLogin = ''

    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        new_user = User.query.filter_by(username = username).first()
        if new_user and check_password_hash(new_user.password, password):
            login_user(new_user, remember=True)
            return redirect(url_for('main.home'))
        else:
            statusLogin = 'Вы ввели неправильные данные'
    return render_template('login.html', statusLogin = statusLogin)

@bp.route('/news')
def news():
    return render_template('index_new.html')

@bp.route('/courses')
def courses():
    return render_template('index_courses.html')

@bp.route('/stocks')
def stocks():
    return render_template('index_stock.html')

@bp.route('/plot')
def plot():
    return render_template('plot.html')

@bp.route('/api/stock/<ticker>')
def stock_data(ticker):
    # Получаем данные о ценах акций с 1 января 2024 по 9 апреля 2025
    stock = yf.Ticker(ticker)
    data = stock.history(start='2024-01-01', end='2025-04-09')
    
    # Форматируем данные для отправки на фронтенд
    response_data = {
        'dates': data.index.strftime('%Y-%m-%d').tolist(),
        'prices': data['Close'].tolist()
    }
    
    return jsonify(response_data)

@bp.route('/get_post_json', methods=["GET", "POST"])
def get_post_json():    
    data = request.get_json()

    return jsonify(status="success", data=data)