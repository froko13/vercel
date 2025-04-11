import os
import sys
from flask import Flask
from flask_sqlalchemy import  SQLAlchemy
from runner import bp, db
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import app.models
import app.routes
from app.models import User

app = Flask(__name__)

app.secret_key = b'42_ZV/[qq/roman]'

app.register_blueprint(bp)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view='main.login'
login_manager.login_message = 'Войдите в аккаунт, чтобы получить доступ.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
