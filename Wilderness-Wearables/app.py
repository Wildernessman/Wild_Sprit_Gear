import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__, static_folder='static', static_url_path='/static')

# Production Configuration
app.config.update(
    # Security settings
    SECRET_KEY=os.environ.get("FLASK_SECRET_KEY", os.urandom(24)),
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=1800,  # 30 minutes
    
    # Database settings
    SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SQLALCHEMY_ENGINE_OPTIONS={
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_timeout": 900,
        "pool_size": 10,
        "max_overflow": 5,
    },
    
    # File upload settings
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # 16MB max file size
    UPLOAD_FOLDER=os.path.join('static', 'uploads'),
    
    # Production settings
    DEBUG=False,
    TESTING=False,
    PROPAGATE_EXCEPTIONS=True,
)

# Ensure upload directory exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return 'Page not found', 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return 'Internal server error', 500

@app.errorhandler(413)
def request_entity_too_large(error):
    return 'File too large (max 16MB)', 413

@login_manager.user_loader
def load_user(user_id):
    from models import Admin
    return Admin.query.get(int(user_id))

# Initialize database and create admin user
with app.app_context():
    try:
        import models
        db.create_all()
        
        # Create initial admin user if not exists
        from models import Admin
        if not Admin.query.first():
            admin = Admin(username='admin')
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()

        # Create initial sections if not exists
        from models import Section
        if not Section.query.first():
            sections = [
                Section(content='<h1>Welcome to ThreadCraft</h1><p class="featured-text">Where Style Meets Comfort</p>', position=1),
                Section(content='<h2>Crafting Premium T-Shirts Since 2020</h2>', position=2),
                Section(content='<h2>Our Collection</h2>', position=3),
                Section(content='<h2>Sustainable Fashion</h2>', position=4),
                Section(content='<h2>Design Your Perfect Tee</h2>', position=5),
                Section(content='<h2>Join Our Fashion Community</h2>', position=6)
            ]
            db.session.add_all(sections)
            db.session.commit()
    except Exception as e:
        app.logger.error(f"Error during initialization: {str(e)}")
