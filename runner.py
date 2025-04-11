from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask import Flask
from flask_sqlalchemy import  SQLAlchemy
from flask_login import login_user, login_required, logout_user, current_user, LoginManager


bp = Blueprint('main', __name__)

db = SQLAlchemy()
