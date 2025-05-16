from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, ForeignKey, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'wowixczzzzz'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fernandez_clinic.db'
db = SQLAlchemy(app)


class Base(DeclarativeBase):
    pass


class Patient(db.Model):
    __tablename__ = "patient"

    patient_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    birthdate: Mapped[str] = mapped_column(String(10))
    gender: Mapped[str] = mapped_column(String(10))
    contact_number: Mapped[str] = mapped_column(String(20))
    account_id: Mapped[int] = mapped_column(ForeignKey("account.account_id"), unique=True)

    account: Mapped["Account"] = relationship(back_populates="patient")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="patient")
    records: Mapped[list["MedicalRecord"]] = relationship(back_populates="patient")


class Doctor(db.Model):
    __tablename__ = "doctor"

    doctor_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firstname: Mapped[str] = mapped_column(String(50))
    middlename: Mapped[str] = mapped_column(String(50), nullable=True)
    lastname: Mapped[str] = mapped_column(String(50))
    age: Mapped[int] = mapped_column(Integer)
    bloodtype: Mapped[str] = mapped_column(String(5), nullable=True)
    height: Mapped[str] = mapped_column(String, nullable=True)
    weight: Mapped[str] = mapped_column(String, nullable=True)
    specialization: Mapped[str] = mapped_column(String(100))
    gender: Mapped[str] = mapped_column(String(20))
    dob: Mapped[str] = mapped_column(String(10))
    pob: Mapped[str] = mapped_column(String(100), nullable=True)
    civilstatus: Mapped[str] = mapped_column(String(20), nullable=True)
    degree: Mapped[str] = mapped_column(String(100), nullable=True)
    nationality: Mapped[str] = mapped_column(String(50), nullable=True)
    religion: Mapped[str] = mapped_column(String(50), nullable=True)
    phone: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String(100))
    account_id: Mapped[int] = mapped_column(ForeignKey("account.account_id"), unique=True)

    account: Mapped["Account"] = relationship(back_populates="doctor")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="doctor")
    records: Mapped[list["MedicalRecord"]] = relationship(back_populates="doctor")


class Appointment(db.Model):
    __tablename__ = "appointment"

    appointment_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patient.patient_id"))
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctor.doctor_id"))
    appointment_date: Mapped[str] = mapped_column(String(10))
    appointment_time: Mapped[str] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(20))

    patient: Mapped["Patient"] = relationship(back_populates="appointments")
    doctor: Mapped["Doctor"] = relationship(back_populates="appointments")
    invoices: Mapped[list["Invoice"]] = relationship(back_populates="appointment")


class MedicalRecord(db.Model):
    __tablename__ = "medical_record"

    record_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patient.patient_id"))
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctor.doctor_id"))
    visit_date: Mapped[str] = mapped_column(String(10))
    diagnosis: Mapped[str] = mapped_column(String)
    notes: Mapped[str] = mapped_column(String)

    patient: Mapped["Patient"] = relationship(back_populates="records")
    doctor: Mapped["Doctor"] = relationship(back_populates="records")
    prescriptions: Mapped[list["Prescription"]] = relationship(back_populates="record")


class Prescription(db.Model):
    __tablename__ = "prescription"

    prescription_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    record_id: Mapped[int] = mapped_column(ForeignKey("medical_record.record_id"))
    medication_name: Mapped[str] = mapped_column(String(100))
    dosage: Mapped[str] = mapped_column(String(50))
    instructions: Mapped[str] = mapped_column(String)

    record: Mapped["MedicalRecord"] = relationship(back_populates="prescriptions")


class Service(db.Model):
    __tablename__ = "service"

    service_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String)
    fee: Mapped[str] = mapped_column(String(20))


class Invoice(db.Model):
    __tablename__ = "invoice"

    invoice_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    appointment_id: Mapped[int] = mapped_column(ForeignKey("appointment.appointment_id"))
    service_id: Mapped[int] = mapped_column(ForeignKey("service.service_id"))
    amount: Mapped[str] = mapped_column(String(20))
    payment_status: Mapped[str] = mapped_column(String(20))

    appointment: Mapped["Appointment"] = relationship(back_populates="invoices")
    service: Mapped["Service"] = relationship()


class Account(db.Model):
    __tablename__ = "account"
    account_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firstname: Mapped[str] = mapped_column(String(50), unique=True)
    lastname: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    phone: Mapped[str] = mapped_column(String(20))
    birthdate: Mapped[str] = mapped_column(String(10))
    password: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(20))

    patient = relationship("Patient", back_populates="account", uselist=False)
    doctor = relationship("Doctor", back_populates="account", uselist=False)

class User(db.Model):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True, autoincrement=True) 
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String(100))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Logged in successfully.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
            return render_template('admin/admin_login.html')
    return render_template('admin/admin_login.html')

@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        new_user = User(username=username, password=generate_password_hash(password, method='sha256'))
        db.session.add(new_user)
        db.session.commit()
        flash('Account created!', 'success')
        return redirect(url_for('admin_login'))
    return render_template('admin/admin_register.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        user = Account.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.account_id
            session['role'] = user.role
            if role == 'doctor':
                flash('Logged in successfully.', 'success')
                return redirect(url_for('doctor_dashboard'))
            elif role == 'patient':
                flash('Logged in successfully.', 'success')
                return redirect(url_for('patient_dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
            return render_template('login.html')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        phone = request.form['phone']
        birthdate = request.form['birthdate']
        password = request.form['password']
        role = request.form.get('role', 'patient')

        existing_user = Account.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists!", "danger")
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password)
        new_account = Account(firstname=firstname, lastname=lastname, email=email, phone=phone, birthdate=birthdate, password=hashed_pw, role=role)

        db.session.add(new_account)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin/admin_dashboard.html')

@app.route('/admin_doctors')
def admin_doctors():
    return render_template('admin/admin_doctors.html')

@app.route('/patients_list')
def patients_list():
    return render_template('admin/patients_list.html')

@app.route('/add_doctor', methods=['GET', 'POST'])
def add_doctor():
    doctors = Doctor.query.all()

    if request.method == 'POST':
        firstname = request.form['firstname']
        middlename = request.form['middlename']
        lastname = request.form['lastname']
        age = request.form['age']
        bloodtype = request.form['bloodtype']
        height = request.form['height']
        weight = request.form['weight']
        specialization = request.form['specialization']
        gender = request.form['gender']
        dob = request.form['dob']
        pob = request.form['pob']
        civilstatus = request.form.get('civilstatus')
        degree = request.form.get('degree')
        nationality = request.form['nationality']
        religion = request.form['religion']
        phone = request.form['phone']
        email = request.form['email']

        new_doctor = Doctor(firstname=firstname, 
                            middlename=middlename, 
                            lastname=lastname, 
                            age=age, 
                            bloodtype=bloodtype, 
                            height=height, 
                            weight=weight, 
                            specialization=specialization,
                            gender=gender, 
                            dob=dob, 
                            pob=pob, 
                            civilstatus=civilstatus, 
                            degree=degree, 
                            nationality=nationality, 
                            religion=religion, 
                            phone=phone, 
                            email=email
                        )
        db.session.add(new_doctor)
        db.session.commit()
    return render_template('admin/add_doctor.html', doctors=doctors)

@app.route('/admin_appointments')
def admin_appointments():
    return render_template('admin/admin_appointments.html')

@app.route('/admin_reports')
def admin_reports():
    return render_template('admin/admin_reports.html')

@app.route('/admin_settings')
def admin_settings():
    return render_template('admin/admin_settings.html')

@app.route('/settings/doctor/create_account', methods=['GET', 'POST'])
def create_doctor_account():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        phone = request.form['phone']
        birthdate = request.form['birthdate']
        password = request.form['password']
        role = request.form.get('role', 'doctor')

        existing_user = Account.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists!", "danger")
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password)
        new_account = Account(firstname=firstname, lastname=lastname, email=email, phone=phone, birthdate=birthdate, password=hashed_pw, role=role)

        db.session.add(new_account)
        db.session.commit()

        return redirect(url_for('create_doctor_account'))
    return render_template('admin/create_doctor_account.html')

@app.route('/doctor/dashboard')
def doctor_dashboard():
    if 'role' not in session or session['role'] != 'doctor':
        return redirect(url_for('unauthorized'))
    return render_template('doctor_dashboard.html')

@app.route('/patient/dashboard')
def patient_dashboard():
    return render_template('patient/patient_dashboard.html')

@app.route('/available_doctors')
def available_doctors():
    return render_template('patient/available_doctors.html')

@app.route('/doctors')
def doctors():
    return render_template('doctors.html')

@app.route('/patients')
def patients():
    return render_template('patients.html')

@app.route('/patient_appointment')
def patient_appointment():
    return render_template('patient/patient_appointment.html')

@app.route('/appointments')
def appointments():
    return render_template('appointments.html')

@app.route('/reports')
def reports():
    
    return render_template('reports.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/unauthorized')
def unauthorized():
    return "Unauthorized access", 403

@app.route('/profile/<int:user_id>', methods=['GET'])
def profile(user_id):
    user = User.query.get(user_id)
    return render_template('profile.html',user=user)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
