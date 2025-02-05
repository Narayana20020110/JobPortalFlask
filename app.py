from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
# Initialize the db, bcrypt, login_manager, and migrate globally
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__,template_folder='templates',static_folder='static')
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
     # Configure app (email settings)
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'nreddy1102002@gmail.com'  # Your email
    app.config['MAIL_PASSWORD'] = 'xhpy hump ggsb ibvg'        # Your email password

    # Initialize Flask-Mail with the app
    mail = Mail(app)
    # Initialize the extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Import and register the routes
    import routes
    routes.register_routes(app, db, mail)

    return app

# User loader for Flask-Login
@login_manager.user_loader
def load_user(email):

    from models import Seeker, Provider
    user = Seeker.query.get(email) or Provider.query.get(email)
    return user
