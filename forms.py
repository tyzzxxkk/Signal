from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Regexp('^[a-zA-Z0-9._%+-]+@e-mirim\\.hs\\.kr$', message='미림 이메일만 가능')
    ])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('로그인')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Regexp('^[a-zA-Z0-9._%+-]+@e-mirim\\.hs\\.kr$', message='미림 이메일만 가능')
    ])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('가입하기')

class LetterForm(FlaskForm):
    anonymous = BooleanField('익명 여부')
    name = StringField('보내는 사람(학번 이름)', validators=[DataRequired()])
    content = TextAreaField('내용', validators=[DataRequired()])
    submit = SubmitField('보내기')

class LoveForm(FlaskForm):
    name1 = StringField('당신의 이름', validators=[DataRequired()])
    name2 = StringField('상대 이름', validators=[DataRequired()])
    submit = SubmitField('테스트 시작')
