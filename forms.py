from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Regexp('^[a-zA-Z0-9._%+-]+@e-mirim\\.hs\\.kr$', message='미림마이스터고등학교의 이메일만 가능합니다.')
    ])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('로그인')

class RegisterForm(FlaskForm):
    name = StringField('이름', validators=[DataRequired()])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Regexp('^[a-zA-Z0-9._%+-]+@e-mirim\\.hs\\.kr$', message='미림마이스터고등학교의 이메일만 가능합니다.')
    ])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='비밀번호가 일치하지 않습니다.')])
    submit = SubmitField('가입하기')

class LetterForm(FlaskForm):
    receiver_email = StringField('받는 사람 이메일', validators=[
        DataRequired(),
        Email(),
        Regexp('^[a-zA-Z0-9._%+-]+@e-mirim\\\\.hs\\\\.kr$', message='미림마이스터고등학교의 이메일만 가능합니다.')
    ])
    anonymous = BooleanField('익명으로 보내기')
    # name = StringField('보내는 사람(학번 이름)', validators=[DataRequired()]) 자동으로 설정되게 바꿨어염
    content = TextAreaField('내용', validators=[DataRequired()])
    submit = SubmitField('보내기')

class LoveForm(FlaskForm):
    name1 = StringField('당신의 이름', validators=[DataRequired()])
    name2 = StringField('상대 이름', validators=[DataRequired()])
    submit = SubmitField('테스트 시작')
