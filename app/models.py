# models.py
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, email, password):
        self.email = email
        self.password = password

    def get_id(self):
        return self.email

class Agent(UserMixin):
    def __init__(self, name, password, role):
        self.name = name
        self.password = password
        self.role = role

    def get_id(self):
        return self.name