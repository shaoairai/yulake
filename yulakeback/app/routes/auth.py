"""
認證相關 API
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import Customer, SalonOwner, Salon
from app.utils.response import ApiResponse
from app.utils.errors import ApiError, ErrorCode
from app.utils.auth import create_token, customer_required, salon_required
from flask import g

auth_ns = Namespace('auth', description='認證相關 API')

# ===== 請求/回應模型定義 (for Swagger) =====

customer_register_model = auth_ns.model('CustomerRegister', {
    'name': fields.String(required=True, description='姓名', example='王小明'),
    'email': fields.String(required=True, description='Email', example='wang@example.com'),
    'password': fields.String(required=True, description='密碼', example='password123'),
    'phone': fields.String(description='手機（選填）', example='0912345678')
})

customer_login_model = auth_ns.model('CustomerLogin', {
    'email': fields.String(required=True, description='Email', example='wang@example.com'),
    'password': fields.String(required=True, description='密碼', example='password123')
})

salon_login_model = auth_ns.model('SalonLogin', {
    'email': fields.String(required=True, description='Email', example='admin@nailart.com'),
    'password': fields.String(required=True, description='密碼', example='password123')
})


# ===== 顧客認證 =====

@auth_ns.route('/customer/register')
class CustomerRegister(Resource):
    @auth_ns.doc('customer_register')
    @auth_ns.expect(customer_register_model)
    def post(self):
        """顧客註冊"""
        data = request.get_json()

        # 驗證必填欄位
        if not data.get('name') or not data.get('email') or not data.get('password'):
            raise ApiError(ErrorCode.VALIDATION_ERROR, '姓名、Email 和密碼為必填')

        # 檢查 Email 是否已存在
        if Customer.query.filter_by(email=data['email']).first():
            raise ApiError(ErrorCode.AUTH_EMAIL_EXISTS)

        # 建立顧客
        customer = Customer(
            name=data['name'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            phone=data.get('phone')
        )
        db.session.add(customer)
        db.session.commit()

        # 產生 Token
        token = create_token({
            'type': 'customer',
            'customer_id': customer.id
        })

        return ApiResponse.created({
            'token': token,
            'user': {
                'id': customer.id,
                'name': customer.name,
                'email': customer.email,
                'phone': customer.phone
            }
        }, '註冊成功')


@auth_ns.route('/customer/login')
class CustomerLogin(Resource):
    @auth_ns.doc('customer_login')
    @auth_ns.expect(customer_login_model)
    def post(self):
        """顧客登入"""
        data = request.get_json()

        if not data.get('email') or not data.get('password'):
            raise ApiError(ErrorCode.VALIDATION_ERROR, 'Email 和密碼為必填')

        # 查詢顧客
        customer = Customer.query.filter_by(email=data['email'], is_active=True).first()
        if not customer or not check_password_hash(customer.password_hash, data['password']):
            raise ApiError(ErrorCode.AUTH_INVALID_CREDENTIALS)

        # 產生 Token
        token = create_token({
            'type': 'customer',
            'customer_id': customer.id
        })

        return ApiResponse.success({
            'token': token,
            'user': {
                'id': customer.id,
                'name': customer.name,
                'email': customer.email,
                'phone': customer.phone
            }
        }, '登入成功')


@auth_ns.route('/customer/me')
class CustomerMe(Resource):
    @auth_ns.doc('customer_me', security='Bearer')
    @customer_required
    def get(self):
        """取得當前顧客資訊"""
        customer = Customer.query.get(g.customer_id)
        if not customer:
            raise ApiError(ErrorCode.CUSTOMER_NOT_FOUND)

        return ApiResponse.success({
            'id': customer.id,
            'name': customer.name,
            'email': customer.email,
            'phone': customer.phone,
            'birthday': customer.birthday.isoformat() if customer.birthday else None,
            'created_at': customer.created_at.isoformat()
        })


# ===== 店家認證 =====

@auth_ns.route('/salon/login')
class SalonLogin(Resource):
    @auth_ns.doc('salon_login')
    @auth_ns.expect(salon_login_model)
    def post(self):
        """店家登入"""
        data = request.get_json()

        if not data.get('email') or not data.get('password'):
            raise ApiError(ErrorCode.VALIDATION_ERROR, 'Email 和密碼為必填')

        # 查詢店家管理員
        owner = SalonOwner.query.filter_by(email=data['email'], is_active=True).first()
        if not owner or not check_password_hash(owner.password_hash, data['password']):
            raise ApiError(ErrorCode.AUTH_INVALID_CREDENTIALS)

        # 取得店家資訊
        salon = Salon.query.get(owner.salon_id)
        if not salon or not salon.is_active:
            raise ApiError(ErrorCode.SALON_NOT_FOUND, '店家不存在或已停用')

        # 產生 Token
        token = create_token({
            'type': 'salon',
            'salon_id': salon.id,
            'owner_id': owner.id,
            'role': owner.role
        })

        return ApiResponse.success({
            'token': token,
            'user': {
                'id': owner.id,
                'name': owner.name,
                'email': owner.email,
                'role': owner.role
            },
            'salon': {
                'id': salon.id,
                'code': salon.code,
                'name': salon.name
            }
        }, '登入成功')


@auth_ns.route('/salon/me')
class SalonMe(Resource):
    @auth_ns.doc('salon_me', security='Bearer')
    @salon_required
    def get(self):
        """取得當前店家資訊"""
        owner = SalonOwner.query.get(g.owner_id)
        salon = Salon.query.get(g.salon_id)

        if not owner or not salon:
            raise ApiError(ErrorCode.SALON_NOT_FOUND)

        return ApiResponse.success({
            'user': {
                'id': owner.id,
                'name': owner.name,
                'email': owner.email,
                'phone': owner.phone,
                'role': owner.role
            },
            'salon': {
                'id': salon.id,
                'code': salon.code,
                'name': salon.name,
                'address': salon.address,
                'phone': salon.phone,
                'theme_color': salon.theme_color,
                'logo_url': salon.logo_url
            }
        })
