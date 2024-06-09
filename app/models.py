# models.py

from flask_login import UserMixin
# from .db import get_user_credential

class User(UserMixin):
    def __init__(self, id, email, password):
        self.email = email
        self.password = password

    def get_id(self):
        return self.username

class Agent(UserMixin):
    def __init__(self, name, password, role):
        self.name = name
        self.password = password
        self.role = role

    def get_id(self):
        return self.name