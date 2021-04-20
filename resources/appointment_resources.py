import datetime
import time

from flask_jwt_extended import jwt_required
from flask_restful import Resource, reqparse

from models.appointmets_model import AppointmentModel
from models.users_model import UsersModel
from resources.user_resources import GetCurrentUserDetails

_appointment_parser = reqparse.RequestParser()
_appointment_parser.add_argument('date',
                                 type=str,
                                 required=True,
                                 help='Date is required')
_appointment_parser.add_argument('time',
                                 type=str,
                                 required=True,
                                 help='Time is required')
_appointment_parser.add_argument('message',
                                 type=str,
                                 required=False)
_appointment_parser.add_argument('sent_to',
                                 type=str,
                                 required=True,
                                 help='Doctor name is required')


class CreateNewAppointment(Resource):
    @jwt_required()
    def post(self):
        fetchUserDetail = GetCurrentUserDetails.get(self)
        user_verify = fetchUserDetail[0]
        if not user_verify['role'] == 'Patient':
            return {'message': 'Only patient can create new appointments'}, 401
        print(user_verify['username'])

        data = _appointment_parser.parse_args()

        checkDoctor = UsersModel.find_by_username_role(str(data['sent_to']).lower().strip(), 'Doctor')

        if not checkDoctor:
            return {'message': 'Requested Doctor not found'}, 400

        try:
            userDate = datetime.datetime.strptime(str(data['date']).strip(), "%Y-%m-%d")
            if userDate.date() < datetime.date.today():
                return {'message': 'Appointment date must be greater than today\'s date'}, 400
        except ValueError as e:
            return {'message': 'Date should be in format YYYY-MM-DD'}, 400

        try:
            time.strptime(str(data['time']).strip(), "%H:%M")
        except ValueError as e:
            return {'message': 'Time should be in format HH:MM'}, 400

        todayDateTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        userDateTime = f'{userDate.date()} {str(data["time"]).strip()}'
        if userDateTime <= todayDateTime:
            return {'message': 'Appointment date and time must be greater than today\'s date and current time'}, 400

        checkOldRequest = AppointmentModel.find_by_patient_date_notAccepted_doctor(
            str(user_verify['username']).lower().strip(), str(data['sent_to']).lower().strip())

        users = list(map(lambda x: x.appointment_json(), checkOldRequest))
        for user in users:
            if datetime.datetime.strptime(str(user['appointmentDate']).strip(),
                                          "%Y-%m-%d").date() > datetime.date.today():
                return {'message': 'You already sent appointment to the doctor'}, 400

        try:
            new_appointment = AppointmentModel(
                str(user_verify['username']).lower().strip(),
                str(data['date']).strip(),
                str(data['time']).strip(),
                str(data['message']).capitalize().lower(),
                str(data['sent_to']).lower().strip()
            )
            new_appointment.save_to_db()
            return {'message': f'Your appointment sent to doctor {checkDoctor.name}'}, 200
        except Exception as e:
            print(f'Exception while creating new appointment {e}')
            return {'message': 'Something went wrong'}, 400


class DoctorApproval(Resource):
    @jwt_required()
    def put(self, id):
        fetchUserDetail = GetCurrentUserDetails.get(self)
        user_verify = fetchUserDetail[0]
        if not user_verify['role'] == 'Doctor':
            return {'message': 'Only doctors can do this task'}, 401
        print(user_verify['username'])

        if id.isnumeric():
            print(True)
        else:
            print(False)

        checkAppointment = AppointmentModel.find_by_id_username_doctor(id, user_verify['username'])

        if checkAppointment:
            if checkAppointment.accepted == '1':
                return {'message': f'Patient "{checkAppointment.patient_username}" appointment already accepted'}, 400
            if datetime.datetime.strptime(checkAppointment.date, "%Y-%m-%d").date() < datetime.date.today():
                return {'message': 'Appointment expired'}, 400
            try:
                checkAppointment.accepted = '1'
                checkAppointment.save_to_db()
                return {'message': f'Appointment accepted for patient {checkAppointment.patient_username}'}, 200
            except Exception as e:
                print(f'Exception while accepting patient appointment {e}')
                return {'message': 'Something went wrong'}, 500
        return {'message': 'Requested id not found'}, 400


class GetAllApprovedAppointments(Resource):
    @jwt_required()
    def get(self):
        fetchUserDetail = GetCurrentUserDetails.get(self)
        user_verify = fetchUserDetail[0]
        if not user_verify['role'] == 'Patient':
            return {'message': 'Only doctors can do this task'}, 401
        print(user_verify['username'])

        getAppointments = AppointmentModel.find_all_approved_appointments(user_verify['username'])

        if not getAppointments:
            return {'message': 'Your no appointments approved'}, 400

        return {'appointments': list(map(lambda x: x.appointment_patients_json(), getAppointments))}, 200


class GetAllNonApprovedAppointments(Resource):
    @jwt_required()
    def get(self):
        fetchUserDetail = GetCurrentUserDetails.get(self)
        user_verify = fetchUserDetail[0]
        if not user_verify['role'] == 'Patient':
            return {'message': 'Only doctors can do this task'}, 401
        print(user_verify['username'])

        getAppointments = AppointmentModel.find_all_non_approved_appointments(user_verify['username'])

        if not getAppointments:
            return {'message': 'No appointments'}, 400

        return {'appointments': list(map(lambda x: x.appointment_patients_json(), getAppointments))}, 200


class GetMyAppointments(Resource):
    @jwt_required()
    def get(self):
        fetchUserDetail = GetCurrentUserDetails.get(self)
        user_verify = fetchUserDetail[0]
        if not user_verify['role'] == 'Doctor':
            return {'message': 'Only doctors can do this task'}, 401
        print(user_verify['username'])

        getMyAppointments = AppointmentModel.find_all_doctor_appointments(user_verify['username'])

        if not getMyAppointments:
            return {'message': 'No appointments pending'}, 400

        return {'appointments': list(map(lambda x: x.appointment_doctor_json(), getMyAppointments))}, 200


class RequestedAppointments(Resource):
    @jwt_required()
    def get(self):
        fetchUserDetail = GetCurrentUserDetails.get(self)
        user_verify = fetchUserDetail[0]
        if not user_verify['role'] == 'Doctor':
            return {'message': 'Only doctors can do this task'}, 401
        print(user_verify['username'])

        getMyAppointments = AppointmentModel.find_all_appointments(user_verify['username'])

        if not getMyAppointments:
            return {'message': 'No appointments'}, 400

        return {'appointments': list(map(lambda x: x.appointment_doctor_json_2(), getMyAppointments))}, 200
