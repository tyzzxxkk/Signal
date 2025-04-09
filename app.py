from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from config import Config
from extensions import db, mail, login_manager
from routes import main_bp  # 메인 라우터 블루프린트
from auth import auth_bp   # 인증 라우터 블루프린트
import os

# Flask 확장 모듈 초기화
db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 확장 모듈 등록
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    # 로그인 안한 사용자가 접근 시 리다이렉트할 페이지
    login_manager.login_view = 'auth.login'  # auth_bp 안의 login 함수로 연결

    # 로그인 유저 로드 함수
    from models import User, LoveHistory  # 모델 import

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 블루프린트 등록
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
