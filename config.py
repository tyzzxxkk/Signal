import os

class Config:
    SECRET_KEY = 'signel_super_secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///signel.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your_email@gmail.com'
    MAIL_PASSWORD = 'your_app_password'
