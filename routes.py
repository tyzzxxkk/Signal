from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from models import LoveHistory
from extensions import db
from love_test import love_result_message
from mail_sender import send_letter_mail
from filters import filter_bad_words
import random
import string
import datetime
from forms import LoveForm # LoveForm을 import 합니다.

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    if current_user.is_authenticated:
        email_name = current_user.email.split('@')[0]
        return render_template('home.html', user_name=email_name)
    return render_template('index.html')

@main_bp.route('/guest_home')
def guest_home():
    return render_template('guest_home.html')

@main_bp.route('/love_test', methods=['GET', 'POST'])
# @login_required 
def love_test():
    form = LoveForm() 
    result = None
    if form.validate_on_submit(): 
        name1 = form.name1.data
        name2 = form.name2.data 

        score, msg = love_result_message(name1, name2)
        result = {'name1': name1, 'name2': name2, 'score': score, 'msg': msg}

        if current_user.is_authenticated:
            history = LoveHistory(user_id=current_user.id,
                                  name1=name1,
                                  name2=name2,
                                  score=score,
                                  msg=msg,
                                  date=datetime.datetime.now(datetime.timezone.utc))
            db.session.add(history)
            db.session.commit()
        else:
            flash('로그인하시면 궁합 테스트 기록을 저장할 수 있습니다.', 'info')

    return render_template('love_test.html', form=form, result=result) 


@main_bp.route('/history')
@login_required
def history():
    histories = LoveHistory.query.filter_by(user_id=current_user.id).all()
    return render_template('history.html', histories=histories)


@main_bp.route('/send_letter', methods=['GET', 'POST'])
@login_required
def send_letter():
    form = LetterForm() 
    if form.validate_on_submit():
        receiver_email = request.form.get('receiver')
        sender_name = form.name.data
        content = form.content.data
        subject = "SIGNAL에서 온 쪽지" 

        if not receiver_email or not sender_name or not content:
            flash('모든 항목을 입력해주세요.', 'warning')
            return redirect(url_for('main.send_letter'))

        if not receiver_email.endswith('@e-mirim.hs.kr'):
            flash('학교 이메일만 입력 가능합니다.', 'danger')
            return redirect(url_for('main.send_letter'))

        send_letter_mail(receiver_email, subject, sender_name, content)
        flash('편지가 성공적으로 전송되었습니다!', 'success')
        return redirect(url_for('main.home'))
    return render_template('send_letter.html', form=form) 