from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, login_required, logout_user, current_user, login_manager
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import func, desc
from sqlalchemy import exc
from datetime import datetime, timedelta
from app.models import User
from runner import bp, db
import yfinance as yf
import json



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

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

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
@login_required
def courses():
    return render_template('index_courses.html')

@bp.route('/stocks')
@login_required
def stocks():
    return render_template('index_stock.html')

@bp.route('/plot')
@login_required
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

@bp.route('/api/current_point', methods=['POST'])
def current_point():
    data = request.json
    current_index = data.get('index')
    current_price = data.get('price')
    current_date = data.get('date')
    
    # Проверяем, что все данные получены
    if None in [current_index, current_price, current_date]:
        return jsonify({'error': 'Missing data'}), 400
    
    print(f"Received: index={current_index}, price={current_price}, date={current_date}")
    
    # Возвращаем полученные данные для проверки
    return jsonify({
        'status': 'success',
        'received': {
            'index': current_index,
            'price': current_price,
            'date': current_date
        }
    })

@bp.route('/api/profile', methods=['GET'])
@login_required
def get_profile():
    """Получить профиль текущего пользователя"""
    return jsonify({
        "status": "success",
        "profile": current_user.profile,
        "balance": current_user.balance
    })

@bp.route('/api/profile', methods=['PUT'])
@login_required
def update_profile():
    try:
        update_data = request.get_json()
        
        if not update_data:
            return jsonify({"status": "error", "message": "Нет данных"}), 400
        
        # Обновляем баланс
        if 'balance' in update_data:
            current_user.balance = float(update_data['balance'])
        
        # Обновляем профиль (2 варианта на случай разных форматов)
        if 'profile' in update_data:
            if isinstance(update_data['profile'], str):
                current_user.profile = json.loads(update_data['profile'])
            else:
                current_user.profile = update_data['profile']
        elif 'AAPL' in update_data:
            if not isinstance(current_user.profile, dict):
                current_user.profile = {}
            current_user.profile['AAPL'] = int(update_data['AAPL'])
        
        db.session.commit()
        
        return jsonify({
            "status": "success",
            "balance": current_user.balance,
            "profile": current_user.profile,
            "AAPL": current_user.profile.get('AAPL', 0)
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500