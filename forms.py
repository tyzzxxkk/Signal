from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField, HiddenField 
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, ValidationError 

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

class LoveForm(FlaskForm):
    name1 = StringField('이름 1', validators=[DataRequired(), Length(min=1, max=50)])
    name2 = StringField('이름 2', validators=[DataRequired(), Length(min=1, max=50)])
    submit = SubmitField('궁합 보기')

class LetterForm(FlaskForm):
    receiver_display_name = StringField('받는 사람', validators=[DataRequired()])

    receiver_email = HiddenField('받는 사람 이메일', validators=[
        DataRequired(),
        Email()
    ])

    def validate_receiver_email(self, field):
        from models import User 

        user = User.query.filter_by(email=field.data).first()
        if not user:
            raise ValidationError('가입하지 않은 사용자입니다.')
    
    content = TextAreaField('내용', validators=[DataRequired(), Length(min=1, max=500, message='내용은 1자 이상 500자 이하로 작성해주세요.')])
    anonymous = BooleanField('익명으로 보내기')
    submit = SubmitField('보내기')