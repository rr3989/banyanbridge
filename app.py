from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import secrets
import logging
import traceback
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config_from_properties():
    """Load configuration from application.properties file"""
    config = {}
    properties_file = 'application.properties'
    
    if os.path.exists(properties_file):
        with open(properties_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    
    return config

app = Flask(__name__)

# Configuration for serverless environment
instance_path = os.environ.get('INSTANCE_PATH', './instance')
app.instance_path = instance_path
app.instance_relative_config = False

# Load configuration from properties file first, then environment variables
properties_config = load_config_from_properties()

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', properties_config.get('SECRET_KEY', 'dev-secret-key-change-in-production'))

# Database configuration - Neon PostgreSQL only
database_url = os.environ.get('neon_banyanbridge_db_DATABASE_URL') or \
              os.environ.get('DATABASE_URL') or \
              properties_config.get('DATABASE_URL')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', properties_config.get('UPLOAD_FOLDER', '/tmp/uploads'))
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', properties_config.get('MAX_CONTENT_LENGTH', str(16 * 1024 * 1024))))
app.config['ALLOWED_EXTENSIONS'] = set(ext.strip() for ext in properties_config.get('ALLOWED_EXTENSIONS', 'pdf').split(','))
# app.config['SERVER_NAME'] = 'banyanbridge.org'  # Commented out for localhost development

# Email configuration
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', properties_config.get('MAIL_SERVER', 'smtp.gmail.com'))
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', properties_config.get('MAIL_PORT', '587')))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', properties_config.get('MAIL_USE_TLS', 'True')).lower() in ['true', 'on', '1']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', properties_config.get('MAIL_USERNAME', 'banyanbridgeteam@gmail.com'))
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', properties_config.get('MAIL_PASSWORD', ''))
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', properties_config.get('MAIL_DEFAULT_SENDER', 'banyanbridgeteam@gmail.com'))

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Ensure upload directory exists (only if not in read-only environment)
try:
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
except OSError:
    # Read-only filesystem, use /tmp
    app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # Increased from 120 to 255 for scrypt hashes
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'teacher', 'student'
    full_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    teaching_materials = db.relationship('TeachingMaterial', backref='teacher', lazy=True)
    assignments = db.relationship('Assignment', backref='student', lazy=True)
    exam_attempts = db.relationship('ExamAttempt', backref='student', lazy=True)

class TeachingMaterial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    filename = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    filename = db.Column(db.String(255), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    grade = db.Column(db.String(10))
    feedback = db.Column(db.Text)

class Exam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    duration_minutes = db.Column(db.Integer, default=30)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    questions = db.relationship('Question', backref='exam', lazy=True, cascade='all, delete-orphan')

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)  # 'A', 'B', 'C', or 'D'

class ExamAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=0)
    attempted_at = db.Column(db.DateTime, default=datetime.utcnow)
    answers = db.relationship('ExamAnswer', backref='attempt', lazy=True)

class ExamAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('exam_attempt.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    selected_answer = db.Column(db.String(1))
    is_correct = db.Column(db.Boolean, default=False)

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    subject = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def send_contact_email(name, email, phone, subject, message):
    """Send contact form submission email to admin"""
    try:
        logger.info(f"Attempting to send email for {name}")
        
        # Check if email configuration is available
        if not app.config['MAIL_PASSWORD']:
            logger.warning("Email password not configured - skipping email sending")
            return False
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"New Contact Form Submission: {subject}"
        msg['From'] = app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = 'banyanbridgeteam@gmail.com'
        
        # Create email body
        text_content = f"""
New Contact Form Submission

Name: {name}
Email: {email}
Phone: {phone if phone else 'Not provided'}
Subject: {subject}

Message:
{message}

Submitted at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
"""
        
        html_content = f"""
<html>
<body>
    <h2>New Contact Form Submission</h2>
    <p><strong>Name:</strong> {name}</p>
    <p><strong>Email:</strong> {email}</p>
    <p><strong>Phone:</strong> {phone if phone else 'Not provided'}</p>
    <p><strong>Subject:</strong> {subject}</p>
    <h3>Message:</h3>
    <p>{message}</p>
    <p><em>Submitted at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</em></p>
</body>
</html>
"""
        
        # Attach both plain text and HTML versions
        part1 = MIMEText(text_content, 'plain')
        part2 = MIMEText(html_content, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email
        with smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
            if app.config['MAIL_USE_TLS']:
                server.starttls()
            if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
                server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            server.send_message(msg)
            
        logger.info(f"Contact email sent successfully for {name}")
        return True
    except Exception as e:
        logger.error(f"Failed to send contact email: {e}")
        logger.error(traceback.format_exc())
        return False

# Favicon route to prevent 500 errors
@app.route('/favicon.ico')
def favicon():
    return '', 204  # Return 204 No Content

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    logger.error(f"404 error: {error}")
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {error}")
    logger.error(traceback.format_exc())
    return render_template('index.html'), 500

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {e}")
    logger.error(traceback.format_exc())
    return render_template('index.html'), 500

# Routes
@app.route('/health')
def health():
    return 'OK', 200

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index.html: {e}")
        logger.error(traceback.format_exc())
        return f"Error loading page: {str(e)}", 500

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        try:
            logger.info("Contact form submission received")
            logger.info(f"Form data: {dict(request.form)}")
            
            # Get form data
            name = request.form.get('name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            subject = request.form.get('subject')
            message = request.form.get('message')
            
            logger.info(f"Extracted data - Name: {name}, Email: {email}, Subject: {subject}")
            
            # Validate required fields
            if not name or not email or not subject or not message:
                logger.warning("Validation failed - missing required fields")
                return {'success': False, 'error': 'All required fields must be filled'}, 400
            
            # Create contact message record
            logger.info("Creating ContactMessage record")
            contact_message = ContactMessage(
                name=name,
                email=email,
                phone=phone,
                subject=subject,
                message=message
            )
            db.session.add(contact_message)
            logger.info("Added to session, committing...")
            db.session.commit()
            logger.info(f"Successfully saved contact message with ID: {contact_message.id}")
            
            # Send email notification
            email_sent = send_contact_email(name, email, phone, subject, message)
            
            if email_sent:
                return {'success': True, 'message': 'Thank you for your message! We will get back to you soon.'}
            else:
                # Email failed but message was saved
                return {'success': True, 'message': 'Thank you for your message! We will get back to you soon.'}
                
        except Exception as e:
            logger.error(f"Error processing contact form: {e}")
            logger.error(traceback.format_exc())
            return {'success': False, 'error': 'An error occurred while processing your message'}, 500
    
    return render_template('contact.html')

@app.route('/donate')
def donate():
    return render_template('donate.html')

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            
            # Redirect based on role
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            elif user.role == 'student':
                return redirect(url_for('student_dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        role = request.form.get('role')
        
        # Restrict registration to usernames containing 'banyanbridgeteam'
        if 'banyanbridgeteam' not in username.lower() and 'admin' in role.lower():
            flash('Restricted Only For Admin Users', 'error')
            return redirect(url_for('register'))

        # Restrict registration to Admin usernames containing 'banyanbridgeteam'
        if 'teacher' not in username.lower() and 'teacher' in role.lower():
            flash('Restricted Only For Teachers', 'error')
            return redirect(url_for('register'))


        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return redirect(url_for('register'))
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            full_name=full_name,
            role=role
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

# Admin Routes
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    exams = Exam.query.all()
    users = User.query.all()
    contact_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    return render_template('admin/dashboard.html', exams=exams, users=users, contact_messages=contact_messages)

@app.route('/admin/exam/create', methods=['GET', 'POST'])
@login_required
def create_exam():
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        exam = Exam(
            title=request.form.get('title'),
            subject=request.form.get('subject'),
            description=request.form.get('description'),
            duration_minutes=int(request.form.get('duration', 30))
        )
        db.session.add(exam)
        db.session.commit()
        
        # Add questions
        question_count = int(request.form.get('question_count', 5))
        for i in range(1, question_count + 1):
            question = Question(
                exam_id=exam.id,
                question_text=request.form.get(f'question_{i}'),
                option_a=request.form.get(f'option_{i}_a'),
                option_b=request.form.get(f'option_{i}_b'),
                option_c=request.form.get(f'option_{i}_c'),
                option_d=request.form.get(f'option_{i}_d'),
                correct_answer=request.form.get(f'correct_{i}').upper()
            )
            db.session.add(question)
        
        db.session.commit()
        flash('Exam created successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/create_exam.html')

@app.route('/admin/exam/<int:exam_id>/delete')
@login_required
def delete_exam(exam_id):
    if current_user.role != 'admin':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    exam = Exam.query.get_or_404(exam_id)
    db.session.delete(exam)
    db.session.commit()
    flash('Exam deleted successfully', 'success')
    return redirect(url_for('admin_dashboard'))

# Teacher Routes
@app.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    materials = TeachingMaterial.query.filter_by(teacher_id=current_user.id).all()
    return render_template('teacher/dashboard.html', materials=materials)

@app.route('/teacher/material/upload', methods=['GET', 'POST'])
@login_required
def upload_material():
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            material = TeachingMaterial(
                title=request.form.get('title'),
                subject=request.form.get('subject'),
                description=request.form.get('description'),
                filename=filename,
                teacher_id=current_user.id
            )
            
            db.session.add(material)
            db.session.commit()
            
            flash('Material uploaded successfully!', 'success')
            return redirect(url_for('teacher_dashboard'))
        else:
            flash('Only PDF files are allowed', 'error')
    
    return render_template('teacher/upload_material.html')

@app.route('/teacher/material/<int:material_id>/delete')
@login_required
def delete_material(material_id):
    if current_user.role != 'teacher':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    material = TeachingMaterial.query.get_or_404(material_id)
    if material.teacher_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('teacher_dashboard'))
    
    # Delete file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], material.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    db.session.delete(material)
    db.session.commit()
    flash('Material deleted successfully', 'success')
    return redirect(url_for('teacher_dashboard'))

# Student Routes
@app.route('/student/dashboard')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    materials = TeachingMaterial.query.all()
    my_assignments = Assignment.query.filter_by(student_id=current_user.id).all()
    available_exams = Exam.query.all()
    my_attempts = ExamAttempt.query.filter_by(student_id=current_user.id).all()
    
    return render_template('student/dashboard.html', 
                          materials=materials, 
                          assignments=my_assignments,
                          exams=available_exams,
                          attempts=my_attempts)

@app.route('/student/material/<int:material_id>/download')
@login_required
def download_material(material_id):
    if current_user.role != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    material = TeachingMaterial.query.get_or_404(material_id)
    return send_from_directory(app.config['UPLOAD_FOLDER'], material.filename, as_attachment=True)

@app.route('/student/assignment/upload', methods=['GET', 'POST'])
@login_required
def upload_assignment():
    if current_user.role != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            assignment = Assignment(
                title=request.form.get('title'),
                subject=request.form.get('subject'),
                description=request.form.get('description'),
                filename=filename,
                student_id=current_user.id
            )
            
            db.session.add(assignment)
            db.session.commit()
            
            flash('Assignment uploaded successfully!', 'success')
            return redirect(url_for('student_dashboard'))
        else:
            flash('Only PDF files are allowed', 'error')
    
    return render_template('student/upload_assignment.html')

@app.route('/student/exam/<int:exam_id>/take', methods=['GET', 'POST'])
@login_required
def take_exam(exam_id):
    if current_user.role != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    exam = Exam.query.get_or_404(exam_id)
    
    # Check if already attempted
    existing_attempt = ExamAttempt.query.filter_by(
        exam_id=exam_id, 
        student_id=current_user.id
    ).first()
    
    if existing_attempt:
        flash('You have already taken this exam', 'info')
        return redirect(url_for('student_dashboard'))
    
    if request.method == 'POST':
        # Create exam attempt
        attempt = ExamAttempt(
            exam_id=exam_id,
            student_id=current_user.id,
            total_questions=len(exam.questions)
        )
        db.session.add(attempt)
        db.session.commit()
        
        # Process answers
        correct_count = 0
        for question in exam.questions:
            selected = request.form.get(f'question_{question.id}')
            answer = ExamAnswer(
                attempt_id=attempt.id,
                question_id=question.id,
                selected_answer=selected.upper() if selected else None,
                is_correct=(selected.upper() == question.correct_answer) if selected else False
            )
            
            if answer.is_correct:
                correct_count += 1
            
            db.session.add(answer)
        
        attempt.score = correct_count
        db.session.commit()
        
        flash(f'Exam submitted! Your score: {correct_count}/{len(exam.questions)}', 'success')
        return redirect(url_for('student_dashboard'))
    
    return render_template('student/take_exam.html', exam=exam)

@app.route('/student/attempt/<int:attempt_id>/view')
@login_required
def view_attempt(attempt_id):
    if current_user.role != 'student':
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    attempt = ExamAttempt.query.get_or_404(attempt_id)
    if attempt.student_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('student_dashboard'))
    
    return render_template('student/view_attempt.html', attempt=attempt)

# Initialize database (only in development or when explicitly called)
def init_db():
    with app.app_context():
        try:
            db.create_all()
            
            # Create default admin user if not exists
            if not User.query.filter_by(username='admin').first():
                admin = User(
                    username='admin',
                    email='admin@banyanbridge.org',
                    password_hash=generate_password_hash('admin123'),
                    full_name='Administrator',
                    role='admin'
                )
                db.session.add(admin)
                db.session.commit()
                print("Default admin user created: username=admin, password=admin123")
        except Exception as e:
            print(f"Database initialization error: {e}")

# Initialize database for production if needed
if os.environ.get('INIT_DB') == 'true':
    init_db()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
else:
    # For production/deployment environments
    init_db()