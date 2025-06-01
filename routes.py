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
# @login_required  # 이 줄을 주석 처리하거나 제거합니다.
def love_test():
    form = LoveForm() # LoveForm 인스턴스를 생성합니다.
    result = None
    if form.validate_on_submit(): # request.method == 'POST' 대신 form.validate_on_submit() 사용
        name1 = form.name1.data # 폼에서 데이터 가져오기
        name2 = form.name2.data # 폼에서 데이터 가져오기

        score, msg = love_result_message(name1, name2)
        result = {'name1': name1, 'name2': name2, 'score': score, 'msg': msg}

        # 로그인된 사용자일 경우에만 LoveHistory에 저장
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

    return render_template('love_test.html', form=form, result=result) # form을 템플릿으로 전달합니다.


@main_bp.route('/history')
@login_required
def history():
    histories = LoveHistory.query.filter_by(user_id=current_user.id).all()
    # history.html 템플릿의 변수명 불일치 수정 (history -> histories)
    return render_template('history.html', histories=histories)


@main_bp.route('/send_letter', methods=['GET', 'POST'])
@login_required
def send_letter():
    form = LetterForm() # LetterForm을 import 하고 인스턴스 생성
    if form.validate_on_submit():
        # receiver_email 필드가 폼에 직접 정의되어 있지 않으므로, 임시로 request.form.get 사용
        # forms.py의 LetterForm에 receiver_email 필드를 추가하거나,
        # 프론트엔드에서 hidden input 등으로 receiver_email을 전달해야 합니다.
        # 여기서는 임시로 'receiver_email'이라는 필드명으로 request.form.get을 사용합니다.
        # 만약 LetterForm에 receiver 필드를 추가한다면 form.receiver.data로 변경해야 합니다.
        receiver_email = request.form.get('receiver') # forms.py의 LetterForm에 'receiver' 필드 추가를 권장합니다.
        sender_name = form.name.data
        content = form.content.data
        subject = "SIGNAL 쪽지" # 기본 제목 설정

        if not receiver_email or not sender_name or not content:
            flash('모든 항목을 입력해주세요.', 'warning')
            return redirect(url_for('main.send_letter'))

        if not receiver_email.endswith('@e-mirim.hs.kr'):
            flash('학교 이메일만 입력 가능합니다.', 'danger')
            return redirect(url_for('main.send_letter'))

        send_letter_mail(receiver_email, subject, sender_name, content)
        flash('편지가 성공적으로 전송되었습니다!', 'success')
        return redirect(url_for('main.home'))
    return render_template('send_letter.html', form=form) # form을 템플릿으로 전달합니다.