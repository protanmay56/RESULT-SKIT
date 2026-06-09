from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'skit-exam-portal-secret-2024')

# ── Database ──────────────────────────────────────────────────────────────────
DB_USER = os.environ.get('MYSQLUSER')
DB_PASS = os.environ.get('MYSQLPASSWORD')
DB_HOST = os.environ.get('MYSQLHOST')
DB_PORT = os.environ.get('MYSQLPORT')
DB_NAME = os.environ.get('MYSQL_DATABASE')

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# ── Models ────────────────────────────────────────────────────────────────────

class Admin(db.Model):
    __tablename__ = 'admins'
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name     = db.Column(db.String(120), default='Examination Controller')
    created  = db.Column(db.DateTime, default=datetime.utcnow)


class Student(db.Model):
    __tablename__ = 'students'
    id                = db.Column(db.Integer, primary_key=True)
    # identity fields
    college_id        = db.Column(db.String(30), unique=True, nullable=False)  # login key 1
    dob               = db.Column(db.String(20), nullable=False)                # login key 2
    roll              = db.Column(db.String(30), nullable=False)
    registration_no   = db.Column(db.String(40), default='')
    enrollment_no     = db.Column(db.String(40), default='')
    abc_id            = db.Column(db.String(40), default='')
    # personal
    name              = db.Column(db.String(120), nullable=False)
    mother_name       = db.Column(db.String(120), default='')
    # academic
    branch            = db.Column(db.String(30), nullable=False)
    program           = db.Column(db.String(60), default='')   # e.g. B.Tech, M.Tech, MCA
    email             = db.Column(db.String(120), default='')
    created           = db.Column(db.DateTime, default=datetime.utcnow)
    results           = db.relationship('Result', backref='student', lazy=True, cascade='all,delete')


class Result(db.Model):
    __tablename__ = 'results'
    id         = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    semester   = db.Column(db.Integer, nullable=False)
    year       = db.Column(db.String(20), nullable=False)
    published  = db.Column(db.Boolean, default=True)
    uploaded   = db.Column(db.DateTime, default=datetime.utcnow)
    subjects   = db.relationship('Subject', backref='result', lazy=True, cascade='all,delete')

    @property
    def total_marks(self):
        return sum((s.internal or 0) + (s.external or 0) for s in self.subjects)

    @property
    def max_marks(self):
        return sum((s.int_max or 30) + (s.ext_max or 70) for s in self.subjects)

    @property
    def percentage(self):
        return round(self.total_marks / self.max_marks * 100, 2) if self.max_marks else 0

    @property
    def sgpa(self):
        return round(self.percentage / 10, 2)

    @property
    def overall_status(self):
        statuses = [s.status for s in self.subjects]
        if 'Fail' in statuses:
            return 'Fail'
        if 'Back' in statuses:
            return 'Back'
        return 'Pass'


class Subject(db.Model):
    __tablename__ = 'subjects'
    id        = db.Column(db.Integer, primary_key=True)
    result_id = db.Column(db.Integer, db.ForeignKey('results.id'), nullable=False)
    name      = db.Column(db.String(120), nullable=False)
    code      = db.Column(db.String(30), default='')
    internal  = db.Column(db.Integer, default=0)
    external  = db.Column(db.Integer, default=0)
    int_max   = db.Column(db.Integer, default=30)
    ext_max   = db.Column(db.Integer, default=70)

    @property
    def total(self):
        return (self.internal or 0) + (self.external or 0)

    @property
    def max_total(self):
        return (self.int_max or 30) + (self.ext_max or 70)

    @property
    def status(self):
        pass_ext = (self.external or 0) >= round((self.ext_max or 70) * 0.35)
        pass_int = (self.internal or 0) >= round((self.int_max or 30) * 0.40)
        pass_tot = self.max_total > 0 and self.total / self.max_total >= 0.33
        if pass_ext and pass_int and pass_tot:
            return 'Pass'
        if pass_tot:
            return 'Back'
        return 'Fail'


# ── Decorators ────────────────────────────────────────────────────────────────

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_id'):
            flash('Please login as admin first.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated


def student_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('student_id'):
            flash('Please login first.', 'error')
            return redirect(url_for('student_login'))
        return f(*args, **kwargs)
    return decorated


# ── Public ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


# ── Student Auth ──────────────────────────────────────────────────────────────

@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if session.get('student_id'):
        return redirect(url_for('student_dashboard'))
    if request.method == 'POST':
        college_id = request.form.get('college_id', '').strip().upper()
        dob        = request.form.get('dob', '').strip()
        sem        = request.form.get('semester', '1')
        student = Student.query.filter_by(college_id=college_id, dob=dob).first()
        if student:
            session['student_id']  = student.id
            session['student_sem'] = sem
            return redirect(url_for('student_dashboard'))
        flash('Invalid College ID or Date of Birth. Please try again.', 'error')
    return render_template('student_login.html')


@app.route('/student/logout')
def student_logout():
    session.pop('student_id',  None)
    session.pop('student_sem', None)
    return redirect(url_for('index'))


@app.route('/student/dashboard')
@student_required
def student_dashboard():
    student  = Student.query.get(session['student_id'])
    sem      = int(session.get('student_sem', 1))
    result   = Result.query.filter_by(
        student_id=student.id, semester=sem, published=True
    ).first()
    all_sems = db.session.query(Result.semester).filter_by(
        student_id=student.id, published=True
    ).order_by(Result.semester).all()
    all_sems = [r[0] for r in all_sems]
    return render_template('student_dashboard.html',
        student=student, result=result, sem=sem, all_sems=all_sems)


@app.route('/student/switch-sem/<int:sem>')
@student_required
def switch_sem(sem):
    session['student_sem'] = sem
    return redirect(url_for('student_dashboard'))


# ── Admin Auth ────────────────────────────────────────────────────────────────

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_id'):
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password, password):
            session['admin_id']   = admin.id
            session['admin_name'] = admin.name
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials.', 'error')
    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id',   None)
    session.pop('admin_name', None)
    return redirect(url_for('index'))


# ── Admin Dashboard ───────────────────────────────────────────────────────────

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    students_count = Student.query.count()
    results_count  = Result.query.count()
    recent         = Result.query.order_by(Result.uploaded.desc()).limit(10).all()
    return render_template('admin_dashboard.html',
        students_count=students_count,
        results_count=results_count,
        recent=recent)


# ── Admin Results List ────────────────────────────────────────────────────────

@app.route('/admin/results')
@admin_required
def admin_results():
    q      = request.args.get('q', '')
    sem    = request.args.get('sem', '')
    query  = Result.query.join(Student)
    if q:
        query = query.filter(
            db.or_(
                Student.college_id.ilike(f'%{q}%'),
                Student.roll.ilike(f'%{q}%'),
                Student.name.ilike(f'%{q}%')
            )
        )
    if sem:
        query = query.filter(Result.semester == int(sem))
    results = query.order_by(Result.uploaded.desc()).all()
    return render_template('admin_results.html', results=results, q=q, sem=sem)


@app.route('/admin/results/delete/<int:rid>', methods=['POST'])
@admin_required
def admin_delete_result(rid):
    r = Result.query.get_or_404(rid)
    db.session.delete(r)
    db.session.commit()
    flash('Result deleted.', 'success')
    return redirect(url_for('admin_results'))


@app.route('/admin/results/toggle/<int:rid>', methods=['POST'])
@admin_required
def admin_toggle_result(rid):
    r = Result.query.get_or_404(rid)
    r.published = not r.published
    db.session.commit()
    return jsonify({'published': r.published})


# ── Admin Upload Result ───────────────────────────────────────────────────────

@app.route('/admin/results/upload', methods=['GET', 'POST'])
@admin_required
def admin_upload_result():
    if request.method == 'POST':
        # Student fields
        college_id      = request.form.get('college_id', '').strip().upper()
        roll            = request.form.get('roll', '').strip().upper()
        registration_no = request.form.get('registration_no', '').strip()
        enrollment_no   = request.form.get('enrollment_no', '').strip()
        abc_id          = request.form.get('abc_id', '').strip()
        name            = request.form.get('name', '').strip()
        mother_name     = request.form.get('mother_name', '').strip()
        dob             = request.form.get('dob', '').strip()
        branch          = request.form.get('branch', '').strip()
        program         = request.form.get('program', '').strip()
        email           = request.form.get('email', '').strip()
        # Result fields
        semester        = int(request.form.get('semester', 1))
        year            = request.form.get('year', '').strip()
        published       = request.form.get('published') == 'on'

        if not college_id or not name or not dob:
            flash('College ID, Name and DOB are required.', 'error')
            return redirect(url_for('admin_upload_result'))

        # Upsert student
        student = Student.query.filter_by(college_id=college_id).first()
        if not student:
            student = Student(college_id=college_id)
            db.session.add(student)
        student.roll            = roll
        student.registration_no = registration_no
        student.enrollment_no   = enrollment_no
        student.abc_id          = abc_id
        student.name            = name
        student.mother_name     = mother_name
        student.dob             = dob
        student.branch          = branch
        student.program         = program
        student.email           = email
        db.session.flush()

        # Upsert result
        result = Result.query.filter_by(student_id=student.id, semester=semester).first()
        if result:
            for s in result.subjects:
                db.session.delete(s)
            db.session.flush()
        else:
            result = Result(student_id=student.id, semester=semester, year=year)
            db.session.add(result)
        result.year      = year
        result.published = published
        db.session.flush()

        # Subjects
        names     = request.form.getlist('subj_name[]')
        codes     = request.form.getlist('subj_code[]')
        internals = request.form.getlist('subj_internal[]')
        externals = request.form.getlist('subj_external[]')
        int_maxes = request.form.getlist('subj_int_max[]')
        ext_maxes = request.form.getlist('subj_ext_max[]')

        for i, n in enumerate(names):
            if not n.strip():
                continue
            db.session.add(Subject(
                result_id = result.id,
                name      = n.strip(),
                code      = codes[i]     if i < len(codes)     else '',
                internal  = int(internals[i]) if i < len(internals) and internals[i] else 0,
                external  = int(externals[i]) if i < len(externals) and externals[i] else 0,
                int_max   = int(int_maxes[i]) if i < len(int_maxes) and int_maxes[i] else 30,
                ext_max   = int(ext_maxes[i]) if i < len(ext_maxes) and ext_maxes[i] else 70,
            ))

        db.session.commit()
        flash(f'Result for {student.name} (Sem {semester}) uploaded successfully!', 'success')
        return redirect(url_for('admin_results'))

    return render_template('admin_upload_result.html')


# ── API: autofill by college_id ───────────────────────────────────────────────

@app.route('/api/student/<college_id>')
@admin_required
def api_student(college_id):
    s = Student.query.filter_by(college_id=college_id.upper()).first()
    if s:
        return jsonify({
            'roll': s.roll, 'registration_no': s.registration_no,
            'enrollment_no': s.enrollment_no, 'abc_id': s.abc_id,
            'name': s.name, 'mother_name': s.mother_name,
            'dob': s.dob, 'branch': s.branch,
            'program': s.program, 'email': s.email
        })
    return jsonify({})


# ── Init DB ───────────────────────────────────────────────────────────────────

def init_db():
    with app.app_context():
        db.create_all()
        if not Admin.query.filter_by(username='admin').first():
            db.session.add(Admin(
                username='admin',
                password=generate_password_hash('admin123'),
                name='Examination Controller'
            ))
            db.session.commit()
            print('✅  Admin created — login: admin / admin123')


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
