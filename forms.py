from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField, HiddenField # HiddenField 추가
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp, ValidationError # ValidationError 추가

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
        Email(message='유효한 이메일 주소가 아닙니다.'), 
        Regexp('^[a-zA-Z0-9._%+-]+@e-mirim\\.hs\\.kr$', message='미림마이스터고등학교의 이메일만 가능합니다.')
    ])
    
    content = TextAreaField('내용', validators=[DataRequired(), Length(min=1, max=500, message='내용은 1자 이상 500자 이하로 작성해주세요.')])
    anonymous = BooleanField('익명으로 보내기')
    submit = SubmitField('보내기')

    def validate_receiver_display_name(self, field):
        if not self.receiver_email.data:
            raise ValidationError('받는 사람을 정확히 선택하거나 유효한 이메일 주소를 입력해주세요.')