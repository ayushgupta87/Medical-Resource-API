import os
from datetime import timedelta

from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from werkzeug.serving import WSGIRequestHandler

from resources.appointment_resources import CreateNewAppointment, DoctorApproval, GetAllApprovedAppointments, \
    GetAllNonApprovedAppointments, GetMyAppointments, RequestedAppointments
from resources.user_resources import RegisterUser, LoginUser, RefreshToken, GetCurrentUserDetails

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///ayushApp.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=15)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = 'ayushApp'
api = Api(app)

jwt = JWTManager(app)


@app.before_first_request
def create_tables():
    db.create_all()


# user register, login, refresh token, current user details
api.add_resource(RegisterUser, '/api/signUp')
api.add_resource(LoginUser, '/api/login')
api.add_resource(RefreshToken, '/api/refreshToken')
api.add_resource(GetCurrentUserDetails, '/api/currentUser')

# for user, appointment
api.add_resource(CreateNewAppointment, '/api/requestAppointment')
api.add_resource(GetAllApprovedAppointments, '/api/myAppointments')
api.add_resource(GetAllNonApprovedAppointments, '/api/myNonApprovedAppointments')

# for doctors, approve requests
api.add_resource(DoctorApproval, '/api/requestAppointment/<string:id>')
api.add_resource(GetMyAppointments, '/api/myUpcomingAppointments')
api.add_resource(RequestedAppointments, '/api/requestedAppointments')

if __name__ == '__main__':
    from db import db

    db.init_app(app)
    # Flutter error of Connection closed while receiving data > windows OS
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    app.run(debug=True, port=5000)
