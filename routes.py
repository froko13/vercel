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
import time
import math
import random

# ─── Кэш данных (живёт пока сервер запущен) ───────────────────────
_stock_cache = {}
CACHE_TTL = 3600  # 1 час

# ─── Генератор демо-данных если yfinance недоступен ───────────────
def generate_demo_data(ticker, days=320):
    """Генерирует реалистичные цены через геометрическое броуновское движение"""
    seed_prices = {
        'AAPL': 185.0, 'MSFT': 375.0, 'GOOGL': 140.0, 'AMZN': 178.0,
        'TSLA': 220.0, 'NFLX': 480.0, 'NVDA': 495.0, 'JPM': 195.0,
    }
    start_price = seed_prices.get(ticker, 100.0)
    random.seed(hash(ticker) % 9999)

    prices = [start_price]
    for _ in range(days - 1):
        drift = 0.0003
        vol   = 0.018
        ret   = drift + vol * random.gauss(0, 1)
        prices.append(round(prices[-1] * math.exp(ret), 4))

    # даты с 2024-01-01
    start = datetime(2024, 1, 1)
    dates = []
    d = start
    count = 0
    while count < days:
        if d.weekday() < 5:  # только рабочие дни
            dates.append(d.strftime('%Y-%m-%d'))
            count += 1
        d += timedelta(days=1)

    return {'dates': dates, 'prices': prices}


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
        username = request.form['username']
        password = request.form['password']
        email    = request.form['email']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password, email=email, user_id=0)
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('main.home'), 301)
        except exc.IntegrityError:
            db.session.rollback()
            labelLogin = 'Этот Email уже зарегистрирован. Войдите в аккаунт'
    return render_template('register.html', labelLogin=labelLogin)

@bp.route('/login', methods=["GET", "POST"])
def login():
    statusLogin = ''
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        new_user = User.query.filter_by(username=username).first()
        if new_user and check_password_hash(new_user.password, password):
            login_user(new_user, remember=True)
            return redirect(url_for('main.home'))
        else:
            statusLogin = 'Вы ввели неправильные данные'
    return render_template('login.html', statusLogin=statusLogin)

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
    ticker = ticker.upper()
    now = time.time()

    # 1. Есть свежий кэш — отдаём сразу
    if ticker in _stock_cache and now - _stock_cache[ticker]['ts'] < CACHE_TTL:
        data = _stock_cache[ticker]['data']
        data['source'] = 'cache'
        return jsonify(data)

    # 2. Пробуем yfinance
    try:
        stock = yf.Ticker(ticker)
        hist  = stock.history(start='2024-01-01', end='2025-04-09')

        if hist.empty:
            raise ValueError('Пустой ответ от yfinance')

        response_data = {
            'dates':  hist.index.strftime('%Y-%m-%d').tolist(),
            'prices': [round(float(p), 4) for p in hist['Close'].tolist()],
            'source': 'yfinance'
        }

        # Кэшируем успешный ответ
        _stock_cache[ticker] = {'data': response_data, 'ts': now}
        return jsonify(response_data)

    except Exception as e:
        # 3. yfinance недоступен — смотрим устаревший кэш
        if ticker in _stock_cache:
            data = _stock_cache[ticker]['data'].copy()
            data['source'] = 'stale_cache'
            return jsonify(data)

        # 4. Совсем нет данных — отдаём демо
        demo = generate_demo_data(ticker)
        demo['source'] = 'demo'
        # Кэшируем демо на 10 минут — попробуем обновить позже
        _stock_cache[ticker] = {'data': demo, 'ts': now - CACHE_TTL + 600}
        return jsonify(demo)


@bp.route('/api/current_point', methods=['POST'])
def current_point():
    data = request.json
    current_index = data.get('index')
    current_price = data.get('price')
    current_date  = data.get('date')
    if None in [current_index, current_price, current_date]:
        return jsonify({'error': 'Missing data'}), 400
    return jsonify({'status': 'success', 'received': {
        'index': current_index, 'price': current_price, 'date': current_date
    }})

@bp.route('/api/profile', methods=['GET'])
@login_required
def get_profile():
    return jsonify({
        "status":  "success",
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

        if 'balance' in update_data:
            current_user.balance = float(update_data['balance'])

        if 'profile' in update_data:
            if isinstance(update_data['profile'], str):
                current_user.profile = json.loads(update_data['profile'])
            else:
                current_user.profile = update_data['profile']

        db.session.commit()

        return jsonify({
            "status":  "success",
            "balance": current_user.balance,
            "profile": current_user.profile
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@bp.route('/advanced')
def news1():
    return render_template('news_podrobniy.html')

@bp.route('/portfile', methods=['GET'])
@login_required
def portfile():
    return render_template('portfile.html')
