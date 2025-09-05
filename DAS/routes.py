from flask import Blueprint, render_template, request, redirect, url_for, flash
from functools import wraps
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

# from datetime import datetime
# from collections import Counter

from .models import db, Appointment, Doctor, User, Account, Patient, Doctor_Schedule, MedicalRecord

abp = Blueprint("abp", __name__)

def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        @login_required
        def decorated_view(*args, **kwargs):
            if current_user.role not in roles:
                flash("You do not have permission to access this page.", "danger")
                return redirect(url_for("index"))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

# def calculate_appointment_statistics():
#     appointments = db.session.query(Appointment).all()

#     if not appointments:
#         return {
#             'total_appointments': 0,
#             'monthly_counts': {},
#             'status_counts': {},
#             'average_appointments_per_day': 0,
#             'busiest_day_of_week': None
#         }

#     appointment_datetimes = np.array([
#         datetime.strptime(f"{appt.appointment_date} {appt.appointment_time}", '%Y-%m-%d %H:%M')
#         for appt in appointments
#     ])

#     # Total number of appointments
#     total_appointments = len(appointments)

#     # Monthly appointment counts
#     months = [date.strftime('%Y-%m') for date in appointment_datetimes]
#     monthly_counts = Counter(months)

#     # Appointment status counts
#     statuses = [appt.status for appt in appointments]
#     status_counts = Counter(statuses)

#     # Average appointments per day
#     if appointment_datetimes.size > 0:
#         unique_days = np.unique(appointment_datetimes.astype('datetime64[D]'))
#         average_appointments_per_day = total_appointments / len(unique_days)
#     else:
#         average_appointments_per_day = 0

#     # Busiest day of the week
#     if appointment_datetimes.size > 0:
#         days_of_week = [date.strftime('%A') for date in appointment_datetimes]
#         day_counts = Counter(days_of_week)
#         busiest_day = day_counts.most_common(1)[0][0]
#     else:
#         busiest_day = None

#     return {
#         'total_appointments': total_appointments,
#         'monthly_counts': dict(monthly_counts),
#         'status_counts': dict(status_counts),
#         'average_appointments_per_day': round(average_appointments_per_day, 2),
#         'busiest_day_of_week': busiest_day
#     }

@abp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        print(f"Login attempt - Username: {username}")
        print(f"Password received: {'Yes' if password else 'No'}")
        
        user = User.query.filter_by(username=username).first()
        print(f"User found: {user is not None}")
        
        if user:
            print(f"User ID: {user.id}")
            print(f"Stored password hash: {user.password}")
            password_check = check_password_hash(user.password, password)
            print(f"Password check result: {password_check}")
        
        if user and check_password_hash(user.password, password):
            print("Password check passed")
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('abp.admin_dashboard'))
        else:
            print("Login failed")
            flash('Login unsuccessful. Please check username and password.', 'danger')

    return render_template('admin/admin_login.html')

@abp.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        new_user = User(username=username, password=generate_password_hash(password, method='sha256'))
        db.session.add(new_user)
        db.session.commit()
        flash('Account created!', 'success')
        return redirect(url_for('abp.admin_login'))
    return render_template('admin/admin_register.html')

@abp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # check if existing
        user = Account.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)

            # redirect based on role
            if user.role == "doctor":
                flash("Logged in successfully.", "success")
                return redirect(url_for("doctor_dashboard"))

            elif user.role == "patient":
                flash("Logged in successfully.", "success")
                patient_profile = Patient.query.filter_by(account_id=user.account_id).first()
                if patient_profile:
                    return redirect(url_for("abp.patient_dashboard"))
                else:
                    return redirect(url_for("abp.create_profile"))

        else:
            flash("Login Unsuccessful. Please check email and password", "danger")

    return render_template("login.html")


@abp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'patient')

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('abp.register'))

        existing_user = Account.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists!", "danger")
            return redirect(url_for('abp.register'))

        hashed_pw = generate_password_hash(password, method='scrypt')
        new_account = Account(email=email, password=hashed_pw, role=role)

        db.session.add(new_account)
        db.session.commit()

        flash("Account created successfully!", "success")
        return redirect(url_for('abp.login'))

    return render_template('abp.register.html')

@abp.route('/admin/dashboard')
@login_required
@role_required("admin")
def admin_dashboard():
    # statistics = calculate_appointment_statistics()
    return render_template('admin/admin_dashboard.html')

@abp.route('/admin_doctors')
@login_required
@role_required("admin")
def admin_doctors():
    doctors = Doctor.query.all()
    return render_template('admin/admin_doctors.html', doctors=doctors)

@abp.route('/patients_list')
@login_required
@role_required("admin")
def patients_list():
    patients = Patient.query.all()
    return render_template('admin/patients_list.html', patients=patients)

@abp.route('/add_doctor', methods=['GET', 'POST'])
@login_required
@role_required("admin")
def add_doctor():
    accounts = (
    db.session.query(Account)
    .outerjoin(Doctor, Doctor.account_id == Account.account_id)
    .filter(Account.role == 'doctor', Doctor.account_id.is_(None))
    .all()
    )

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
        account_id = request.form['account_id']

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
                            email=email,
                            account_id=account_id
                        )
        db.session.add(new_doctor)
        db.session.commit()

        return redirect(url_for('abp.admin_doctors'))
    return render_template('admin/add_doctor.html', accounts=accounts)

@abp.route('/admin_appointments')
@login_required
@role_required("admin")
def admin_appointments():
    appointments = Appointment.query.all()
    return render_template('admin/admin_appointments.html', appointments=appointments)  

@abp.route('/admin_reports')
@login_required
@role_required("admin")
def admin_reports():
    return render_template('admin/admin_reports.html')

@abp.route('/admin_settings')
@login_required
@role_required("admin")
def admin_settings():
    return render_template('admin/admin_settings.html')

# Doctor's Account Creation
@abp.route('/settings/doctor/create_account', methods=['GET', 'POST'])
@login_required
@role_required("admin")
def create_doctor_account():
    doctors = Doctor.query.all()

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'doctor')

        existing_user = Account.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists!", "danger")
            return redirect(url_for('abp.register'))

        hashed_pw = generate_password_hash(password)
        new_account = Account(email=email, password=hashed_pw, role=role)

        db.session.add(new_account)
        db.session.commit()

        return redirect(url_for('abp.create_doctor_account'))
    return render_template('admin/create_doctor_account.html',doctors=doctors)

# Doctor dashboard
@abp.route("/doctor/dashboard")
@login_required
def doctor_dashboard():
    if current_user.role != "doctor":
        flash("Access denied!", "danger")
        return redirect(url_for("abp.unauthorized"))
    return render_template("doctor/doctor_dashboard.html")


# Doctor's patients
@abp.route("/doctors/patients")
@login_required
def doctors_patient():
    if current_user.role != "doctor":
        flash("Access denied!", "danger")
        return redirect(url_for("abp.unauthorized"))

    # use current_user.id (Flask-Login user id, tied to Account.account_id)
    patients = (
        db.session.query(Patient)
        .join(Appointment)
        .filter(Appointment.doctor_id == current_user.account_id,
                Appointment.status == "Accepted")
        .all()
    )
    return render_template("doctor/doctor_patients.html", patients=patients)


# Doctor's appointments
@abp.route("/doctors/appointment")
@login_required
def doctors_appointment():
    if current_user.role != "doctor":
        flash("Access denied!", "danger")
        return redirect(url_for("abp.unauthorized"))

    appointments = Appointment.query.filter_by(
        doctor_id=current_user.account_id
    ).all()

    return render_template("doctor/doctor_appointment.html", appointments=appointments)

@abp.route('/doctors/schedule', methods=['GET', 'POST'])
@login_required
def doctors_schedule():
    if current_user.role != "doctor":
        flash("Access denied!", "danger")
        return redirect(url_for("abp.unauthorized"))

    doctor_id = current_user.account_id

    if request.method == "POST":
        preferred_date = request.form["preferred_date"]
        preferred_time = request.form["preferred_time"]

        new_schedule = Doctor_Schedule(
            doctor_id=doctor_id,
            vacant_date=preferred_date,
            vacant_time=preferred_time,
            status="Available"
        )
        db.session.add(new_schedule)
        db.session.commit()

        flash("Schedule added successfully!", "success")
        return redirect(url_for("abp.doctors_schedule"))

    schedules = Doctor_Schedule.query.filter_by(doctor_id=doctor_id).all()

    return render_template("doctor/open_schedule.html", schedules=schedules)

@abp.route('/available_doctors')
@login_required
@role_required("patient")
def available_doctors():
    doctors = Doctor.query.all()
    return render_template('patient/available_doctors.html', doctors=doctors)

@abp.route("/doctors/profile")
@login_required
@role_required("doctor")
def doctors_profile():
    if current_user.role != "doctor":
        flash("Access denied!", "danger")
        return redirect(url_for("abp.unauthorized"))

    doctor = Doctor.query.filter_by(account_id=current_user.account_id).first()

    return render_template("doctor/doctor_profile.html", doctor=doctor)

@abp.route('/doctors/accept_appointment/<int:appointment_id>', methods=['POST'])
@login_required
@role_required("doctor")
def accept_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return redirect(url_for('abp.doctors_appointment'))
    appointment.status = 'Accepted'
    db.session.commit()
    return redirect(url_for('abp.doctors_appointment'))

@abp.route('/doctors/reject_appointment/<int:appointment_id>', methods=['POST'])
@login_required
@role_required("doctor")
def reject_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return redirect(url_for('abp.doctors_appointment'))
    appointment.status = 'Rejected'
    db.session.commit()
    return redirect(url_for('abp.doctors_appointment'))

@abp.route('/doctors/done_appointment/<int:appointment_id>', methods=['POST'])
@login_required
@role_required("doctor")
def done_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return redirect(url_for('abp.doctors_appointment'))
    appointment.status = 'Done'
    db.session.commit()
    return redirect(url_for('abp.doctors_appointment'))

@abp.route('/doctors/delete_schedule/<int:doctor_schedule_id>', methods=['POST'])
@login_required
@role_required("doctor", "admin")
def delete_doctor_schedule(doctor_schedule_id):
    schedule = Doctor_Schedule.query.get(doctor_schedule_id)
    if not schedule:
        return redirect(url_for('abp.doctors_schedule'))
    db.session.delete(schedule)
    db.session.commit()
    return redirect(url_for('abp.doctors_schedule'))

@abp.route('/medical_records', methods=['GET','POST'])
def medical_records():
    pass

# Patient's Dashboard
@abp.route("/patient/dashboard")
@role_required("patient", "admin") 
@login_required
def patient_dashboard():
    profile = Patient.query.filter_by(account_id=current_user.account_id).first()

    if not profile:
        return redirect(url_for("abp.create_profile"))

    appointments = Appointment.query.filter_by(patient_id=current_user.account_id).all()

    return render_template(
        "patient/patient_dashboard.html",
        profile=profile,
        appointments=appointments
    )

@abp.route("/medical_record/<int:patient_id>")
def medical_record(patient_id):
    record = MedicalRecord.query.filter_by(account_id=current_user.account_id).first()
    if patient_id is not MedicalRecord:
        return redirect(url_for("abp.submit_medical_form"))
    return render_template("patient/medical_record.html", record=record)

@abp.route('/submit-medical-form', methods=['GET', 'POST'])
@login_required
@role_required("patient", "admin")
def submit_medical_form():
    if request.method == "GET":
        # Render the medical form template
        return render_template("patient/medical_form.html")
    
    if request.method == "POST":
        # Extract personal information
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        phone = request.form.get("phone")
        
        # Construct birthdate from separate fields
        birth_month = request.form.get("birth_month")
        birth_day = request.form.get("birth_day")
        birth_year = request.form.get("birth_year")
        
        birthdate = None
        if birth_month and birth_day and birth_year:
            try:
                birthdate = f"{birth_year}-{birth_month.zfill(2)}-{birth_day.zfill(2)}"
            except:
                flash("Invalid birth date format", "error")
                return render_template("patient/medical_form.html")
        
        # Address information
        street_address = request.form.get("street_address")
        street_address_2 = request.form.get("street_address_2")
        city = request.form.get("city")
        state = request.form.get("state")
        
        # Combine address fields
        address_parts = [part for part in [street_address, street_address_2, city, state] if part]
        address = ", ".join(address_parts) if address_parts else None
        
        # Basic measurements
        weight = request.form.get("weight")
        height = request.form.get("height")
        
        # Emergency contact information
        emergency_first_name = request.form.get("emergency_first_name")
        emergency_last_name = request.form.get("emergency_last_name")
        emergency_name = f"{emergency_first_name} {emergency_last_name}".strip() if emergency_first_name or emergency_last_name else None
        
        emergency_street = request.form.get("emergency_street")
        emergency_street_2 = request.form.get("emergency_street_2")
        emergency_city = request.form.get("emergency_city")
        emergency_state = request.form.get("emergency_state")
        
        emergency_address_parts = [part for part in [emergency_street, emergency_street_2, emergency_city, emergency_state] if part]
        emergency_address = ", ".join(emergency_address_parts) if emergency_address_parts else None
        
        emergency_home_phone = request.form.get("emergency_home_phone")
        emergency_work_phone = request.form.get("emergency_work_phone")
        
        # Medical history information
        hepatitis_b = request.form.get("hepatitis_b")
        emergency_info = request.form.get("emergency_info")
        
        # Chronic conditions
        chronic_flu_smoking = request.form.get("chronic_flu_smoking") == "on"
        chronic_flu_not_smoking = request.form.get("chronic_flu_not_smoking") == "on"
        drinking_smoking = request.form.get("drinking_smoking") == "on"
        drinking_not_smoking = request.form.get("drinking_not_smoking") == "on"
        
        medical_history = request.form.get("medical_history")
        medical_problems = request.form.get("medical_problems")
        medications = request.form.get("medications")
        allergies = request.form.get("allergies")
        
        # Insurance information
        has_insurance = request.form.get("has_insurance")
        insurance_company = request.form.get("insurance_company")
        
        insurance_street = request.form.get("insurance_street")
        insurance_street_2 = request.form.get("insurance_street_2")
        insurance_city = request.form.get("insurance_city")
        insurance_state = request.form.get("insurance_state")
        
        insurance_address_parts = [part for part in [insurance_street, insurance_street_2, insurance_city, insurance_state] if part]
        insurance_address = ", ".join(insurance_address_parts) if insurance_address_parts else None
        
        policy_number = request.form.get("policy_number")
        
        # Insurance expiry date
        expiry_month = request.form.get("expiry_month")
        expiry_day = request.form.get("expiry_day")
        expiry_year = request.form.get("expiry_year")
        
        insurance_expiry = None
        if expiry_month and expiry_day and expiry_year:
            try:
                insurance_expiry = f"{expiry_year}-{expiry_month.zfill(2)}-{expiry_day.zfill(2)}"
            except:
                flash("Invalid insurance expiry date format", "error")
                return render_template("patient/PatientMedicalRecord.html")
        
        try:
            # Check if patient profile already exists
            existing_patient = Patient.query.filter_by(account_id=current_user.account_id).first()
            
            if existing_patient:
                # Update existing patient record
                existing_patient.firstname = first_name or existing_patient.firstname
                existing_patient.lastname = last_name or existing_patient.lastname
                existing_patient.phone = phone or existing_patient.phone
                if birthdate:
                    existing_patient.birthdate = birthdate
                existing_patient.address = address or existing_patient.address
                
                # Add new fields to existing patient (you may need to add these columns to your Patient model)
                if hasattr(existing_patient, 'weight'):
                    existing_patient.weight = weight
                if hasattr(existing_patient, 'height'):
                    existing_patient.height = height
                if hasattr(existing_patient, 'emergency_contact_name'):
                    existing_patient.emergency_contact_name = emergency_name
                if hasattr(existing_patient, 'emergency_contact_address'):
                    existing_patient.emergency_contact_address = emergency_address
                if hasattr(existing_patient, 'emergency_home_phone'):
                    existing_patient.emergency_home_phone = emergency_home_phone
                if hasattr(existing_patient, 'emergency_work_phone'):
                    existing_patient.emergency_work_phone = emergency_work_phone
                if hasattr(existing_patient, 'hepatitis_b_vaccination'):
                    existing_patient.hepatitis_b_vaccination = hepatitis_b
                if hasattr(existing_patient, 'medical_history'):
                    existing_patient.medical_history = medical_history
                if hasattr(existing_patient, 'medical_problems'):
                    existing_patient.medical_problems = medical_problems
                if hasattr(existing_patient, 'current_medications'):
                    existing_patient.current_medications = medications
                if hasattr(existing_patient, 'allergies'):
                    existing_patient.allergies = allergies
                if hasattr(existing_patient, 'has_insurance'):
                    existing_patient.has_insurance = has_insurance == "yes"
                if hasattr(existing_patient, 'insurance_company'):
                    existing_patient.insurance_company = insurance_company
                if hasattr(existing_patient, 'insurance_address'):
                    existing_patient.insurance_address = insurance_address
                if hasattr(existing_patient, 'policy_number'):
                    existing_patient.policy_number = policy_number
                if hasattr(existing_patient, 'insurance_expiry'):
                    existing_patient.insurance_expiry = insurance_expiry
                
                flash("Medical information updated successfully!", "success")
            else:
                # Create new patient record with all medical information
                patient = Patient(
                    firstname=first_name,
                    lastname=last_name,
                    phone=phone,
                    birthdate=birthdate,
                    address=address,
                    account_id=current_user.account_id
                    # Add additional fields if they exist in your model
                    # weight=weight,
                    # height=height,
                    # emergency_contact_name=emergency_name,
                    # emergency_contact_address=emergency_address,
                    # emergency_home_phone=emergency_home_phone,
                    # emergency_work_phone=emergency_work_phone,
                    # hepatitis_b_vaccination=hepatitis_b,
                    # medical_history=medical_history,
                    # medical_problems=medical_problems,
                    # current_medications=medications,
                    # allergies=allergies,
                    # has_insurance=has_insurance == "yes",
                    # insurance_company=insurance_company,
                    # insurance_address=insurance_address,
                    # policy_number=policy_number,
                    # insurance_expiry=insurance_expiry
                )
                
                db.session.add(patient)
                flash("Medical profile created successfully!", "success")
            
            db.session.commit()
            return redirect(url_for("abp.patient_dashboard"))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error processing medical form: {str(e)}", "error")
            return render_template("patient/medical_form.html")
    
    return render_template("patient/medical_form.html")

# Create profile
@abp.route("/create_profile", methods=["GET", "POST"])
@login_required
@role_required("patient", "admin")
def create_profile():
    if request.method == "POST":
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        phone = request.form["phone"]
        birthdate = request.form["birthdate"]
        gender = request.form["gender"]
        address = request.form["address"]

        patient = Patient(
            firstname=firstname,
            lastname=lastname,
            phone=phone,
            birthdate=birthdate,
            gender=gender,
            address=address,
            account_id=current_user.account_id
        )

        db.session.add(patient)
        db.session.commit()

        flash("Profile created successfully!", "success")
        return redirect(url_for("abp.patient_dashboard"))

    return render_template("patient/create_profile.html")

# Patient Profile
@abp.route("/patient_profile")
@login_required
@role_required("patient", "admin")
def patient_profile():
    profile = Patient.query.filter_by(account_id=current_user.account_id).first()
    if not profile:
        return redirect(url_for("abp.create_profile"))
    return render_template("patient/patient_profile.html", profile=profile)

# Patient Appointments
@abp.route("/patient/appointment", methods=["GET", "POST"])
@login_required
@role_required("patient")
def patient_appointment():
    appointments = Appointment.query.filter_by(patient_id=current_user.account_id).all()
    return render_template("patient/patient_appointment.html", appointments=appointments)

# View Doctor's Available Time
@abp.route("/doctors/view_available/time_for_<int:doctor_id>")
@login_required
@role_required("patient")
def view_available_time(doctor_id):
    schedules = Doctor_Schedule.query.filter_by(doctor_id=doctor_id, status="Available").all()
    return render_template("patient/view_available_time.html", schedules=schedules)

# Book Appointment
@abp.route("/book_appointment/<int:doctor_schedule_id>", methods=["GET", "POST"])
@login_required
@role_required("patient")
def book_appointment(doctor_schedule_id):
    schedule = Doctor_Schedule.query.get_or_404(doctor_schedule_id)

    if not schedule:
        flash('Schedule not found.', 'error')
        return redirect(url_for('abp.patient_appointment'))

    if request.method == 'POST':
        patient_id = current_user.account_id,
        preferred_date = request.form['vacant_date']
        preferred_time = request.form['vacant_time']
        doctor_id = request.form['doctor_id']
        status = 'Pending'

        # Create appointment
        new_appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_date=preferred_date,
            appointment_time=preferred_time,
            status=status
        )
        db.session.add(new_appointment)

        schedule.status = 'Booked'
        print("Before Commit:", schedule.status)
        db.session.commit()
        print("Before Commit:", schedule.status)
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('abp.patient_appointment'))

    return render_template('patient/book_appointment.html')

from flask_login import login_required, current_user

@abp.route('/patient/reschedule_appointment/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
@role_required("patient")
def reschedule_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)

    # Ensure the appointment belongs to the logged-in patient
    if appointment.patient_id != current_user.account_id:
        flash("You are not authorized to reschedule this appointment.", "danger")
        return redirect(url_for("abp.unauthorized"))

    if request.method == 'POST':
        preferred_date = request.form.get('preferred_date')
        preferred_time = request.form.get('preferred_time')

        if not preferred_date or not preferred_time:
            flash("Missing date or time.", "danger")
            return redirect(url_for("abp.reschedule_appointment", appointment_id=appointment_id))

        # Update appointment
        appointment.appointment_date = preferred_date
        appointment.appointment_time = preferred_time
        db.session.commit()

        flash("Appointment rescheduled successfully!", "success")
        return redirect(url_for('abp.patient_appointment'))

    return render_template('patient/reschedule_appointment.html', appointment=appointment)

@abp.route('/patient/cancel_appointment/<int:appointment_id>', methods=['POST'])
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return redirect(url_for('abp.patient_appointment'))

    appointment.status = 'Cancelled'
    db.session.commit()

    return redirect(url_for('abp.patient_appointment'))

from flask_login import login_required, current_user

@abp.route('/create_appointment', methods=['GET', 'POST'])
@login_required
@role_required("patient")
def create_appointment():
    doctors = Doctor.query.all()

    if request.method == 'POST':
        appointment_date = request.form.get('preferred_date')
        appointment_time = request.form.get('preferred_time')
        doctor_id = request.form.get('doctor_id')
        status = 'Pending'

        if not appointment_date or not appointment_time or not doctor_id:
            flash("All fields are required.", "danger")
            return redirect(url_for("abp.create_appointment"))

        new_appointment = Appointment(
            patient_id=current_user.account_id,  # 🔑 patient comes from logged-in user
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status=status
        )

        db.session.add(new_appointment)
        db.session.commit()

        flash("Appointment request submitted successfully!", "success")
        return redirect(url_for('abp.patient_appointment'))

    return render_template('patient/create_appointment.html', doctors=doctors)

@abp.route('/reports')
def reports():
    return render_template('reports.html')

@abp.route('/settings')
def settings():
    return render_template('settings.html')

@abp.route('/unauthorized')
def unauthorized():
    return "Unauthorized access", 403

@abp.route('/profile/<int:user_id>', methods=['GET'])
def profile(user_id):
    user = User.query.get(user_id)
    return render_template('profile.html',user=user)

@abp.route("/search")
def search():
    q = request.args.get("q")
    print(q)

    if q:
        results = Doctor.query.filter(Doctor.firstname.icontains(q) | Doctor.lastname.icontains(q)) \
        .order_by(Doctor.specialization.asc()).limit(100).all()
    else:
        results = []

    return render_template("search_results.html", results=results)

@abp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('abp.login'))

@abp.route('/.well-known/appspecific/com.chrome.devtools.json')
def chrome_devtools_probe():
    return {}, 200