from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User
from forms import LoginForm, RegisterForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash('가입되지 않은 이메일입니다.', 'danger')
        elif not check_password_hash(user.password, form.password.data):
            flash('비밀번호가 일치하지 않습니다.', 'danger')
        else:
            login_user(user)
            # flash('로그인 성공!', 'success')
            return redirect(url_for('main.home'))  # 로그인 후 홈으로 이동

    return render_template('login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('이미 존재하는 이메일입니다.', 'danger')
        elif form.password.data != form.confirm.data:
            flash('비밀번호가 일치하지 않습니다.', 'danger')
        else:
            hashed_pw = generate_password_hash(form.password.data)
            new_user = User(email=form.email.data, password=hashed_pw, name=form.name.data)
            db.session.add(new_user)
            db.session.commit()
            flash('회원가입 성공! 로그인 해주세요.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('로그아웃 되었습니다.', 'info')
    return redirect(url_for('auth.login'))
