from routes import abp
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

db = SQLAlchemy(abp)


class Base(DeclarativeBase):
    pass


class Patient(db.Model):
    __tablename__ = "patient"

    patient_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firstname: Mapped[str] = mapped_column(String(50))
    lastname: Mapped[str] = mapped_column(String(50))
    birthdate: Mapped[str] = mapped_column(String(10))
    gender: Mapped[str] = mapped_column(String(10))
    address: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(20))
    account_id: Mapped[int] = mapped_column(ForeignKey("account.account_id"), unique=True, nullable=False)

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
    doctor_schedule = relationship("Doctor_Schedule", back_populates="doctor")



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
    schedule_id: Mapped[int] = mapped_column(ForeignKey("doctor_schedule.doctor_schedule_id"))
    visit_date: Mapped[str] = mapped_column(String(10))
    diagnosis: Mapped[str] = mapped_column(String)
    notes: Mapped[str] = mapped_column(String)

    patient: Mapped["Patient"] = relationship(back_populates="records")
    doctor: Mapped["Doctor"] = relationship(back_populates="records")
    doctor_schedule: Mapped["Doctor_Schedule"] = relationship(back_populates="record")


class Doctor_Schedule(db.Model):
    __tablename__ = "doctor_schedule"

    doctor_schedule_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctor.doctor_id"))
    vacant_date: Mapped[str] = mapped_column(String(20))
    vacant_time: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20))

    doctor = relationship("Doctor", back_populates="doctor_schedule")
    record = relationship("MedicalRecord", back_populates="doctor_schedule")


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
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(20))

    patient = relationship("Patient", back_populates="account", uselist=False)
    doctor = relationship("Doctor", back_populates="account", uselist=False)

class User(db.Model, UserMixin):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True, autoincrement=True) 
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(20))