# routes.py
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
                                  msg=msg,
                                  date=datetime.datetime.utcnow()) 
            db.session.add(history)
            db.session.commit()
            # flash('궁합 테스트 기록이 저장되었습니다!', 'success')
        except Exception as e:
            current_app.logger.error(f"Error saving love history: {e}")
            flash('기록 저장 중 오류가 발생했습니다.', 'danger')
            db.session.rollback()

    return render_template('love_test.html', form=form, result=result)

@main_bp.route('/history')
@login_required
def history():
    # 현재 로그인한 사용자의 궁합 테스트 기록
    love_histories = LoveHistory.query.filter_by(user_id=current_user.id).all()

    # 현재 로그인한 사용자가 보낸 쪽지 기록
    sent_letters = Letter.query.filter_by(sender_id=current_user.id).all()

    # 두 리스트를 합쳐서 시간순으로 정렬
    all_activities = []

    for h in love_histories:
        all_activities.append({
            'type': 'love_test',
            'id': h.id,
            'timestamp': h.date, 
            'name1': h.name1,
            'name2': h.name2,
            'score': h.score,
            'msg': h.msg,
            'display_text': f"'{h.name1}'와 '{h.name2}' 궁합 {h.score}%"
        })

    for l in sent_letters:
        all_activities.append({
            'type': 'sent_letter',
            'id': l.id,
            'timestamp': l.timestamp, 
            'sender_name': l.sender_name,
            'receiver_email': l.receiver_email,
            'content': l.content,
            'is_anonymous': l.is_anonymous,
            'display_text': f"쪽지 발송: {l.receiver_email}에게 '{l.content[:15]}...' (익명: {l.is_anonymous})"
        })

    all_activities.sort(key=lambda x: x['timestamp'], reverse=True)

    return render_template('history.html', activities=all_activities)

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


# routes.py

# ... (기존 import 문은 그대로 유지)

@main_bp.route('/send_letter', methods=['GET', 'POST'])
@login_required
def send_letter():
    form = LetterForm()
    if form.validate_on_submit():
        # form.receiver_email.data 에는 이제 '이름'이 들어옵니다.
        # 이 이름으로 실제 사용자 이메일을 찾아야 합니다.
        receiver_name_or_email_input = form.receiver_email.data
        content = form.content.data
        is_anonymous = form.anonymous.data

        # 이름으로 사용자 찾기
        receiver_user = User.query.filter_by(name=receiver_name_or_email_input).first()

        # 만약 이름으로 찾지 못했다면, 이메일로 다시 시도해볼 수 있습니다.
        # (혹시 사용자가 자동완성을 사용하지 않고 직접 이메일을 입력한 경우를 대비)
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

    # GET 요청이거나 폼 유효성 검사 실패 시
    return render_template('send_letter.html', form=form)

@main_bp.route('/search_user_email', methods=['GET'])
@login_required # 로그인된 사용자만 검색 가능하도록
def search_user_email():
    query = request.args.get('query', '').strip()
    if not query:
        return jsonify([])

    # 쿼리가 '@'를 포함하면 이메일로 검색, 아니면 이름으로 검색
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
    # 받은 쪽지 또는 보낸 쪽지 중 본인의 쪽지만 삭제 가능하도록 권한 확인 필요
    if letter.receiver_email != current_user.email and letter.sender_id != current_user.id:
        flash('삭제 권한이 없습니다.', 'danger')
        return redirect(url_for('main.letter')) # 또는 history
    try:
        db.session.delete(letter)
        db.session.commit()
        flash('쪽지가 삭제되었습니다.', 'success')
    except Exception as e:
        current_app.logger.error(f"Error deleting letter: {e}")
        flash('쪽지 삭제 중 오류가 발생했습니다.', 'danger')
        db.session.rollback()
    return redirect(url_for('main.letter')) # 또는 history