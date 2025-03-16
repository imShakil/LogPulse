import os
import requests
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from services.logger import setup_logger
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()
logger = setup_logger('flask_app')

auth_bp = Blueprint('auth', __name__)
db = SQLAlchemy()
login_manager = LoginManager()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def __init__(self, username):
        self.username = username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, salt_length=8)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class ExternalUser(UserMixin):
    def __init__(self, user_data, access_token):
        self.id = user_data['employeeId']
        self.username = user_data['email']
        self.first_name = user_data['firstName']
        self.last_name = user_data['lastName']
        self.role = user_data['roleName']
        self.access_token = access_token

    def get_id(self):
        return f"ext_{self.id}"

@login_manager.user_loader
def load_user(user_id):
    if user_id.startswith('ext_'):
        if 'user_data' in session and 'access_token' in session:
            return ExternalUser(session['user_data'], session['access_token'])
        return None
    return User.query.get(int(user_id))

def authenticate_with_api(email, password):
    api_url = os.getenv('API_URL')
    if not api_url:
        return None

    try:
        response = requests.post(api_url, json={
            'email': email,
            'password': password
        })
        if response.status_code == 201:
            return response.json()
        else:
            logger.error(f"API returned status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"API call failed: {e}")
        return None

def local_authenticate(email, password):
    user = User.query.filter_by(username=email).first()
    logger.info(f"Attempting local authentication for user: {email}")
    if user and user.check_password(password):
        return user
    else:
        logger.warning(f"Invalid credentials for local user: {email}")
    return None

@auth_bp.route('/logs/auth/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('username')
        password = request.form.get('password')
        auth_mode = int(os.getenv('AUTH_MODE', '0'))
        # API Authentication (Mode 1 or 2)
        if auth_mode in [1, 2] and os.getenv('API_URL'):
            logger.info("Attempting API authentication")
            auth_result = authenticate_with_api(email, password)
            if auth_result:
                user_data = auth_result['data']
                access_token = auth_result['token']['access_token']
                
                external_user = ExternalUser(user_data, access_token)
                login_user(external_user)
                session['user_data'] = user_data
                session['access_token'] = access_token
                return redirect(url_for('index'))
            elif auth_mode == 2:
                logger.info("API authentication failed, falling back to local authentication")
                user = local_authenticate(email, password)
                if user:
                    login_user(user)
                    return redirect(url_for('index'))
            else:
                # API-only mode
                flash('Invalid email or password')
                return render_template('login.html')
            

        # Local Authentication (Mode 0 or 2)
        if auth_mode == 0:
            logger.info("Attempting local authentication for user: {email}")
            user = local_authenticate(email, password)
            if user:
                login_user(user)
                return redirect(url_for('index'))
        
        flash('Invalid email or password')
    return render_template('login.html')

@auth_bp.route('/logs/auth/logout')
@login_required
def logout():
    session.pop('user_data', None)
    session.pop('access_token', None)
    logout_user()
    return redirect(url_for('auth.login'))

def init_auth(app):
    # PostgreSQL connection configuration
    auth_mode = int(os.getenv('AUTH_MODE', '1'))
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')

    if auth_mode in [0, 2]:
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        db_host = os.getenv('DB_HOST')
        db_port = os.getenv('DB_PORT')
        db_name = os.getenv('DB_NAME')
        
        # URL encode the password and create connection string
        encoded_password = quote_plus(db_password) if db_password else ''
     
        app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(app)
        with app.app_context():
            db.create_all()
    
    login_manager.init_app(app)
    setattr(login_manager, 'login_view', 'auth.login')
