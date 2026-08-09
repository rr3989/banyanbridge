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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///banyanbridge.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
# app.config['SERVER_NAME'] = 'banyanbridge.org'  # Commented out for localhost development

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

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

@app.route('/contact')
def contact():
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
    return render_template('admin/dashboard.html', exams=exams, users=users)

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