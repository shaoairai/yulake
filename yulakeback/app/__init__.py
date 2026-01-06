from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api
import os

db = SQLAlchemy()

# Swagger API 設定
api = Api(
    title='Yulake API',
    version='1.0',
    description='約來客預約系統 API 文件',
    doc='/docs',  # Swagger UI 路徑
    authorizations={
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': '輸入: Bearer <token>'
        }
    },
    security='Bearer'
)


def create_app(test_config=None):
    app = Flask(__name__)

    # CORS 設定
    CORS(app)

    # 應用程式設定
    if test_config:
        app.config.update(test_config)
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
            'DATABASE_URL',
            'postgresql://yulake:yulake@localhost:5432/yulake'
        )
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['JWT_SECRET'] = os.getenv('JWT_SECRET', 'yulake-dev-secret-key-change-in-production')
        app.config['RESTX_MASK_SWAGGER'] = False  # 不隱藏 X-Fields header

    # 初始化資料庫
    db.init_app(app)

    # 載入所有資料模型（確保建表時能找到所有模型）
    from app import models  # noqa: F401

    # 初始化 API (Swagger)
    api.init_app(app)

    # 註冊 API 命名空間
    from app.routes.health import health_ns
    from app.routes.auth import auth_ns
    from app.routes.public import public_ns
    from app.routes.salon import salon_ns
    from app.routes.booking import booking_ns
    from app.routes.customer import customer_ns
    from app.routes.membership import membership_ns
    from app.routes.email import email_ns

    api.add_namespace(health_ns, path='/api')
    api.add_namespace(auth_ns, path='/api/auth')
    api.add_namespace(public_ns, path='/api/salons')
    api.add_namespace(salon_ns, path='/api/salon')
    api.add_namespace(booking_ns, path='/api/bookings')
    api.add_namespace(customer_ns, path='/api/me')
    api.add_namespace(membership_ns, path='/api/salon/membership')
    api.add_namespace(email_ns, path='/api/salon/email')

    # 全域錯誤處理
    @app.errorhandler(Exception)
    def handle_exception(error):
        from app.utils.errors import ApiError
        if isinstance(error, ApiError):
            return jsonify(error.to_dict()), error.status_code
        # 非預期錯誤
        app.logger.error(f'Unhandled exception: {error}')
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '系統內部錯誤'
            }
        }), 500

    # 建立資料表
    with app.app_context():
        db.create_all()

    return app
