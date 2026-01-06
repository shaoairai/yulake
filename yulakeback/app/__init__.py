from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # CORS 設定
    CORS(app)

    # 資料庫設定
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'postgresql://yulake:yulake@localhost:5432/yulake'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 初始化資料庫
    db.init_app(app)

    # 載入所有資料模型（確保建表時能找到所有模型）
    from app import models  # noqa: F401

    # 註冊路由
    from app.routes import main
    app.register_blueprint(main.bp)

    # 建立資料表
    with app.app_context():
        db.create_all()

    return app
