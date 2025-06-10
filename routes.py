from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from flask_login import login_required, current_user
from models import LoveHistory, User, Letter 
from extensions import db
from love_test import love_result_message
from mail_sender import send_letter_mail
from filters import filter_bad_words
import datetime
from forms import LoveForm, LetterForm
from smtplib import SMTPException 

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
        is_anonymous = form.anonymous.data 

        # 1. @e-mirim.hs.kr 도메인 검사 먼저 수행 
        if not receiver_email.endswith('@e-mirim.hs.kr'):
            flash('학교 이메일만 입력 가능합니다.', 'danger')
            return render_template('send_letter.html', form=form) 

        # 2. 받는 사람 이메일로 User 검색 
        receiver_user = User.query.filter_by(email=receiver_email).first()
        if not receiver_user:
            flash('존재하지 않는 사용자 이메일이거나, 유효하지 않은 이메일 형식입니다.', 'danger')
            return render_template('send_letter.html', form=form) # 사용자 없으면 폼 유지

        # 익명 여부에 따라 보내는 사람 이름 설정
        if is_anonymous:
            sender_name = "익명"

        # 욕설 필터링
        filtered_content = filter_bad_words(content)

        # Letter 모델에 편지 저장
        new_letter = Letter(
            sender_id=current_user.id, # 로그인된 사용자 ID를 sender_id로 저장
            receiver_email=receiver_email,
            sender_name=sender_name,
            content=filtered_content,
            is_anonymous=is_anonymous # 익명 여부 저장
        )
        db.session.add(new_letter)

        try:
            db.session.commit() # 편지 저장 먼저 커밋
            send_letter_mail(receiver_email, "SIGNAL로부터 온 편지", sender_name, filtered_content)
            flash('편지가 성공적으로 전송되었습니다!', 'success')
            return redirect(url_for('main.home'))
        except SMTPException as e: # 메일 서버 관련 구체적인 예외 처리
            current_app.logger.error(f"SMTP Error sending email to {receiver_email}: {e}")
            flash(f'메일 발송에 실패했습니다. (메일 서버 오류: {e})', 'danger')
            db.session.rollback() # 오류 발생 시 DB 변경사항 롤백
            return render_template('send_letter.html', form=form) # 오류 발생 시 폼 유지
        except Exception as e: # 그 외 모든 예외 처리
            current_app.logger.error(f"Unexpected error sending email to {receiver_email}: {e}")
            flash(f'메일 발송 중 알 수 없는 오류가 발생했습니다: {e}', 'danger')
            db.session.rollback() # 오류 발생 시 DB 변경사항 롤백
            return render_template('send_letter.html', form=form) # 오류 발생 시 폼 유지

    # GET 요청 시 또는 폼 유효성 검사 실패 시 (post 요청에서 유효성 검사 통과 못했을 때)
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
        # 이름으로 검색 (대소문자 구분 없음)
        users = User.query.filter(User.name.ilike(f'%{query}%')).limit(10).all()

    results = []
    for user in users:
        # 이름 필드가 없거나 비어있을 경우 이메일의 로컬 파트 사용 (예: "test@e-mirim.hs.kr" -> "test")
        display_name = user.name if user.name else user.email.split('@')[0]
        results.append({'email': user.email, 'name': display_name})

    return jsonify(results)

@main_bp.route('/letter')
@login_required
def letter_inbox():
    user_email = current_user.email
    received_letters = Letter.query.filter_by(receiver_email=user_email).order_by(Letter.timestamp.desc()).all()
    return render_template('letter.html', letters=received_letters)