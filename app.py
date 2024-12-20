from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_login import LoginManager

# Initialize the db, bcrypt, login_manager, and migrate globally
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Import and register the routes
    import routes
    routes.register_routes(app, db)

    return app

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    from models import Seeker, Provider
    user = Seeker.query.get(user_id) or Provider.query.get(user_id)
    return user
