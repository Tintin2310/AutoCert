from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ------------------ DATABASE MODELS ------------------

class User(db.Model):
    """User model for storing student user details."""
    roll_number = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Admin(db.Model):
    """Admin model for storing admin details."""
    username = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(100), nullable=False)

class Certificate(db.Model):
    """Certificate model for storing extracted certificate details."""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_name = db.Column(db.String(100), nullable=False)
    event = db.Column(db.String(200), nullable=False)
    rank_position = db.Column(db.String(100), nullable=False)
    certificate_type = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(300), nullable=False)

# ------------------ DATABASE OPERATIONS ------------------

def init_db(app):
    """Initialize the database with Flask app."""
    db.init_app(app)
    with app.app_context():
        db.create_all()

def register_user(roll_number, name, email, password):
    """Register a new user in the database."""
    user = User(roll_number=roll_number, name=name, email=email, password=password)
    db.session.add(user)
    try:
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False  # User already exists

def authenticate_user(roll_number, password):
    """Authenticate user login."""
    user = User.query.filter_by(roll_number=roll_number, password=password).first()
    return {"name": user.name, "email": user.email} if user else None

def register_admin(username, password):
    """Register a new admin."""
    admin = Admin(username=username, password=password)
    db.session.add(admin)
    try:
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False  # Admin already exists

def authenticate_admin(username, password):
    """Authenticate admin login."""
    return Admin.query.filter_by(username=username, password=password).first() is not None

def store_certificate(student_name, event, rank_position, certificate_type, image_url):
    """Store extracted certificate details in the database."""
    certificate = Certificate(student_name=student_name, event=event, rank_position=rank_position, certificate_type=certificate_type, image_url=image_url)
    db.session.add(certificate)
    db.session.commit()

def get_all_certificates():
    """Retrieve all stored certificates."""
    certificates = Certificate.query.all()
    return [{"Name": c.student_name, "Event": c.event, "Rank/Position": c.rank_position, "Type": c.certificate_type, "Image_URL": c.image_url} for c in certificates]
