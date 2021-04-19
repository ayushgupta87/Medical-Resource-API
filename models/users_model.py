from db import db


class UsersModel(db.Model):
    __tablename__ = 'users_table'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(15), nullable=False)
    email_address = db.Column(db.String(25), nullable=False, unique=True)
    password = db.Column(db.String(15), nullable=False)
    role = db.Column(db.String(10), nullable=False)

    def __init__(self, name, username, email_address,password, role):
        self.name = name
        self.username = username
        self.email_address = email_address
        self.password=password
        self.role = role

    def user_json(self):
        return {
            'name': self.name,
            'username': self.username,
            'emailAddress': self.email_address,
            'role': self.role
        }

    @classmethod
    def find_all(cls):
        return cls.query.all()

    @classmethod
    def find_all_doctors(cls):
        return cls.query.filter_by(role='Doctor').all()

    @classmethod
    def find_all_patients(cls):
        return cls.query.filter_by(role='Patient').all()

    @classmethod
    def find_by_role(cls, role):
        return cls.query.filter_by(role=role).all()

    @classmethod
    def find_by_email_address(cls, email_address):
        return cls.query.filter_by(email_address=email_address).first()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_username_role(cls, username, role):
        return cls.query.filter_by(username=username, role=role).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
