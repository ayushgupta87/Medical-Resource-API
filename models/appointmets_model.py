import datetime

from db import db


class AppointmentModel(db.Model):
    __tablename__ = 'appointments_model'

    id = db.Column(db.Integer, primary_key=True)
    patient_username = db.Column(db.String(15), nullable=False)
    date = db.Column(db.String(15), nullable=False)
    time = db.Column(db.String(15), nullable=False)
    message = db.Column(db.String(80), nullable=False)
    sent_to = db.Column(db.String(15), nullable=False)
    accepted = db.Column(db.String(2), nullable=False, default='0')

    def __init__(self, patient_username, date, time, message, sent_to, accepted='0'):
        self.patient_username = patient_username
        self.date = date
        self.time = time
        self.message = message
        self.sent_to = sent_to
        self.accepted = accepted

    def appointment_json(self):
        return {
            'patient': self.patient_username,
            'appointmentDate': self.date,
            'appointmentTime': self.time,
            'message': self.message,
            'doctor': self.sent_to,
            'doctor_acceptance': self.accepted
        }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    @classmethod
    def find_all_approved_username(cls, sent_to):
        return cls.query.filter_by(sent_to=sent_to, accepted='1').all()

    @classmethod
    def find_all_not_approved_username(cls, sent_to):
        return cls.query.filter_by(sent_to=sent_to, accepted='0').all()

    @classmethod
    def find_by_patient_date_notAccepted_doctor(cls, patient_username, sent_to):
        return cls.query.filter_by(patient_username=patient_username, sent_to=sent_to).all()

    @classmethod
    def find_by_id_username_doctor(cls, id, sent_to):
        return cls.query.filter_by(id=id, sent_to=sent_to).first()
