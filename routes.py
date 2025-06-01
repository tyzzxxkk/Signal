from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app # current_app 추가
from flask_login import login_required, current_user
from models import LoveHistory
from extensions import db
from love_test import love_result_message
from mail_sender import send_letter_mail
from filters import filter_bad_words
import random
import string
import datetime
from forms import LoveForm, LetterForm

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
@login_required
def love_test():
    form = LoveForm()
    result = None
    if form.validate_on_submit():
        name1 = form.name1.data
        name2 = form.name2.data

        score, msg = love_result_message(name1, name2)
        result = {'name1': name1, 'name2': name2, 'score': score, 'msg': msg}

        history = LoveHistory(user_id=current_user.id,
                              name1=name1,
                              name2=name2,
                              score=score,
                              msg=msg,
                              date=datetime.datetime.now(datetime.timezone.utc))
        db.session.add(history)
        db.session.commit()
    return render_template('love_test.html', form=form, result=result)


@main_bp.route('/history')
@login_required
def history():
    histories = LoveHistory.query.filter_by(user_id=current_user.id).order_by(LoveHistory.date.desc()).all()
    return render_template('history.html', histories=histories)

@main_bp.route('/delete_history/<int:history_id>', methods=['POST'])
@login_required
def delete_history(history_id):
    history_to_delete = LoveHistory.query.get_or_404(history_id)

    db.session.delete(history_to_delete)
    db.session.commit()
    # flash('기록이 성공적으로 삭제되었습니다.', 'success')  
    return redirect(url_for('main.history'))


@main_bp.route('/send_letter', methods=['GET', 'POST'])
@login_required
def send_letter():
    form = LetterForm()
    if form.validate_on_submit():
        receiver_email = form.receiver_email.data
        sender_name = form.name.data
        content = form.content.data
        anonymous = form.anonymous.data

        if anonymous:
            sender_name = "익명"

        subject = "SIGNAL로부터 온 편지"

        if not receiver_email.endswith('@e-mirim.hs.kr'):
            flash('학교 이메일만 입력 가능합니다.', 'danger')
            return redirect(url_for('main.send_letter'))

        try:
            send_letter_mail(receiver_email, subject, sender_name, content)
            flash('편지가 성공적으로 전송되었습니다!', 'success')
            return redirect(url_for('main.home'))
        except Exception as e:
            flash(f'편지 전송에 실패했습니다: {e}', 'danger')
            current_app.logger.error(f"Error sending email: {e}")
            return redirect(url_for('main.send_letter'))

    return render_template('send_letter.html', form=form)