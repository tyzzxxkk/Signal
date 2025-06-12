from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from models import LoveHistory, User, Letter 
from extensions import db
from love_test import love_result_message
import datetime
from forms import LoveForm, LetterForm
from filters import filter_bad_words 

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    if current_user.is_authenticated:
        user_name = current_user.email.split('@')[0]
        if hasattr(current_user, 'name') and current_user.name:
            user_name = current_user.name
        return render_template('home.html', user_name=user_name)
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

        try:
            history = LoveHistory(user_id=current_user.id,
                                  name1=name1,
                                  name2=name2,
                                  score=score,
                                  message=msg, 
                                  timestamp=datetime.datetime.utcnow())
            db.session.add(history)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f"기록 저장 중 오류가 발생했습니다: {e}", 'danger')
            current_app.logger.error(f"Error saving love history: {e}")

    return render_template('love_test.html', form=form, result=result)

@main_bp.route('/history')
@login_required
def history():
    love_histories = LoveHistory.query.filter_by(user_id=current_user.id).order_by(LoveHistory.timestamp.desc()).all()
    sent_letters = Letter.query.filter_by(sender_id=current_user.id).order_by(Letter.timestamp.desc()).all()

    all_activities = []
    for lh in love_histories:
        all_activities.append({
            'type': 'love_test',
            'id': lh.id,
            'name1': lh.name1,
            'name2': lh.name2,
            'score': lh.score,
            'message': lh.message, 
            'timestamp': lh.timestamp
        })
    for sl in sent_letters:
        receiver_user = User.query.filter_by(email=sl.receiver_email).first()
        receiver_name = sl.receiver_email.split('@')[0] 
        if receiver_user and receiver_user.name:
            receiver_name = receiver_user.name 

        all_activities.append({
            'type': 'sent_letter',
            'id': sl.id, 
            'receiver_email': sl.receiver_email, 
            'receiver_name': receiver_name, 
            'sender_name': '익명' if sl.is_anonymous else current_user.name,
            'content': sl.content,
            'timestamp': sl.timestamp,
            'is_anonymous': sl.is_anonymous
        })
    all_activities.sort(key=lambda x: x['timestamp'], reverse=True)

    return render_template('history.html', all_activities=all_activities)

@main_bp.route('/delete_history/<int:history_id>', methods=['POST'])
@login_required
def delete_history(history_id):
    history = LoveHistory.query.get_or_404(history_id)
    if history.user_id != current_user.id:
        flash('삭제 권한이 없습니다.', 'danger')
        return redirect(url_for('main.history'))

    try:
        db.session.delete(history)
        db.session.commit()
        flash('궁합 테스트 기록이 삭제되었습니다.', 'success')
    except Exception as e:
        current_app.logger.error(f"Error deleting love history: {e}")
        flash('기록 삭제 중 오류가 발생했습니다.', 'danger')
        db.session.rollback()
    return redirect(url_for('main.history'))

@main_bp.route('/letter')
@login_required
def letter():
    received_letters = Letter.query.filter_by(receiver_email=current_user.email).order_by(Letter.timestamp.desc()).all()
    return render_template('letter.html', letters=received_letters)


@main_bp.route('/send_letter', methods=['GET', 'POST'])
@login_required
def send_letter():
    form = LetterForm()
    if form.validate_on_submit():
        receiver_name_or_email_input = form.receiver_email.data
        content = form.content.data
        is_anonymous = form.anonymous.data

        receiver_user = User.query.filter_by(name=receiver_name_or_email_input).first()

        if not receiver_user:
            receiver_user = User.query.filter_by(email=receiver_name_or_email_input).first()

        if not receiver_user:
            flash('존재하지 않는 사용자입니다. 이름을 다시 확인해주세요.', 'danger')
            return render_template('send_letter.html', form=form)

        # 찾은 사용자의 실제 이메일 주소
        receiver_email = receiver_user.email

        # 자신에게 쪽지 보내기 방지 (이제 정확한 이메일로 비교)
        if receiver_email == current_user.email:
            flash('자신에게는 쪽지를 보낼 수 없습니다.', 'danger')
            return render_template('send_letter.html', form=form)

        # 욕설 필터링
        filtered_content = filter_bad_words(content)

        # 보낸 사람 이름 설정
        sender_name = "익명" if is_anonymous else current_user.name

        try:
            new_letter = Letter(
                sender_id=current_user.id,
                receiver_email=receiver_email,
                sender_name=sender_name,
                content=filtered_content,
                is_anonymous=is_anonymous,
                timestamp=datetime.datetime.utcnow()
            )
            db.session.add(new_letter)
            db.session.commit()
            flash('쪽지가 성공적으로 발송되었습니다!', 'success')
            return render_template('send_letter.html', form=LetterForm()) 
        except Exception as e:
            db.session.rollback()
            flash(f'쪽지 발송 중 오류가 발생했습니다: {e}', 'danger')
            current_app.logger.error(f"Error sending letter: {e}")

    return render_template('send_letter.html', form=form)

@main_bp.route('/search_user_email', methods=['GET'])
@login_required 
def search_user_email():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify([])

    if '@' in query:
        # 이메일 전체 또는 부분 일치 검색
        users = User.query.filter(User.email.ilike(f'%{query}%')).limit(10).all()
    else:
        # 이름으로 검색 
        users = User.query.filter(User.name.ilike(f'%{query}%')).limit(10).all()

    results = []
    for user in users:
        display_name = user.name if user.name else user.email.split('@')[0]
        results.append({'email': user.email, 'display_name': display_name})
    return jsonify(results)

@main_bp.route('/delete_letter/<int:letter_id>', methods=['POST'])
@login_required
def delete_letter(letter_id):
    letter = Letter.query.get_or_404(letter_id)
    if letter.receiver_email != current_user.email and letter.sender_id != current_user.id:
        flash('삭제 권한이 없습니다.', 'danger')
        return redirect(url_for('main.history')) 
    try:
        db.session.delete(letter)
        db.session.commit()
        flash('쪽지가 삭제되었습니다.', 'success')
    except Exception as e:
        current_app.logger.error(f"Error deleting letter: {e}")
        flash('쪽지 삭제 중 오류가 발생했습니다.', 'danger')
        db.session.rollback()
    return redirect(url_for('main.history')) 