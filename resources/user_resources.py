from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jti
from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
import re

from models.users_model import UsersModel

_user_parser = reqparse.RequestParser()
_user_parser.add_argument('name',
                          type=str,
                          required=True,
                          help='Name is required')
_user_parser.add_argument('username',
                          type=str,
                          required=True,
                          help='Username is required')
_user_parser.add_argument('email_address',
                          type=str,
                          required=True,
                          help='Email Address is required')
_user_parser.add_argument('password',
                          type=str,
                          required=True,
                          help='Password is required')
_user_parser.add_argument('confirm_password',
                          type=str,
                          required=True,
                          help='Confirm Password is required')
_user_parser.add_argument('role',
                          type=str,
                          required=True,
                          choices=['Doctor', 'Patient'])


class RegisterUser(Resource):
    def post(self):

        data = _user_parser.parse_args()

        if UsersModel.find_by_username(str(data['username']).lower().strip()):
            return {'message': 'Username already exists, try another'}, 400

        if UsersModel.find_by_email_address(str(data['email_address']).lower().strip()):
            return {'message': 'Email Address already registered, try another'}, 400

        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        if not re.search(regex, str(data['email_address']).lower().strip()):
            return {'message': 'Email id seems invalid, please check it!'}, 400

        if len(str(data['password'])) > 16:
            return {'message': 'Password length exceeds'}, 400
        if len(str(data['password'])) < 6:
            return {'message': 'Password must be six or more than six characters'}, 400

        if data['password'] !=data['confirm_password']:
            return {'message': 'Password and confirm password not matching'}, 400

        try:
            new_user = UsersModel(
                str(data['name']).title().strip(),
                str(data['username']).lower().strip(),
                str(data['email_address']).lower().strip(),
                data['password'],
                data['role']
            )
            new_user.save_to_db()
            access_token = create_access_token(identity=str(data['username']).lower().strip(), fresh=True)
            refresh_token = create_refresh_token(str(data['username']).lower().strip())
            return {
                       'access_token': access_token,
                       'refresh_token': refresh_token
                   }, 200
        except Exception as e:
            print(f'Error while saving new user {e}')
            return {'message': 'Something went wrong'}, 500


class LoginUser(Resource):
    def post(self):
        _user_login_parser = reqparse.RequestParser()
        _user_login_parser.add_argument('username',
                                        type=str,
                                        required=True,
                                        help='Username is required')
        _user_login_parser.add_argument('password',
                                        type=str,
                                        required=True,
                                        help='Password is required')
        _user_login_parser.add_argument('role',
                                  type=str,
                                  required=True,
                                  choices=['Doctor', 'Patient'])
        data = _user_login_parser.parse_args()

        checkUser = UsersModel.find_by_username_role(str(data['username']).lower().strip(), str(data['role']).title().strip())

        if not checkUser:
            return {'message': 'Invalid Details'}, 400

        if checkUser and safe_str_cmp(checkUser.password, data['password']):
            access_token = create_access_token(identity=checkUser.username, fresh=True)
            refresh_token = create_refresh_token(checkUser.username)
            return {
                       'access_token': access_token,
                       'refresh_token': refresh_token
                   }, 200
        return {'message': 'Invalid credentials'}, 400


class RefreshToken(Resource):
    @jwt_required(refresh=True)
    def post(self):
        checkUser = UsersModel.find_by_username(get_jwt_identity())
        if not checkUser:
            return {'message': 'Login Required'}, 400
        new_access_token = create_access_token(identity=get_jwt_identity(), fresh=True)
        return {'access_token': new_access_token}, 200


class GetCurrentUserDetails(Resource):
    @jwt_required()
    def get(self):
        customer_details = UsersModel.find_by_username(get_jwt_identity())
        if not customer_details:
            return {'username': 'None', 'role': 'None'}, 401
        current_user_customer = get_jwt_identity()
        current_user_role = customer_details.role
        return {'username': current_user_customer, 'role': current_user_role}, 200
