from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, ForeignKey, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'wowixczzzzz'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fernandez_clinic.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


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
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    specialization: Mapped[str] = mapped_column(String(100))
    contact_number: Mapped[str] = mapped_column(String(20))
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
    account_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    firstname: Mapped[str] = mapped_column(String(50), unique=True)
    lastname: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    phone: Mapped[str] = mapped_column(String(20))
    birthdate: Mapped[str] = mapped_column(String(10))
    password: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(20)) 

    patient = relationship("Patient", back_populates="account", uselist=False)
    doctor = relationship("Doctor", back_populates="account", uselist=False)
    
    def get_id(self):
        return str(self.account_id)

@login_manager.user_loader
def load_user(user_id):
    return Account.query.get(int(user_id))

@app.route('/', methods=['GET', 'POST'])
def login():
    print(request.form)
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        user = Account.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == 'admin':
                flash('Logged in successfully.','success')
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'doctor':
                flash('Logged in successfully.','success')
                return redirect(url_for('doctor_dashboard'))
            elif user.role == 'patient':
                flash('Logged in successfully.','success')
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
            flash("Username already exists!", "danger")
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password)
        new_account = Account(firstname=firstname, lastname=lastname, email=email, phone=phone, birthdate=birthdate, password=hashed_pw, role=role)
        
        db.session.add(new_account)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('unauthorized'))
    return render_template('admin_dashboard.html')


@app.route('/doctor/dashboard')
@login_required
def doctor_dashboard():
    if current_user.role != 'doctor':
        return redirect(url_for('unauthorized'))
    return render_template('doctor_dashboard.html')


@app.route('/patient/dashboard')
@login_required
def patient_dashboard():
    if current_user.role != 'patient':
        return redirect(url_for('unauthorized'))
    return render_template('patient_dashboard.html')


@app.route('/unauthorized')
def unauthorized():
    return "Unauthorized access", 403


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
