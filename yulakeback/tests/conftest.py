"""
測試配置
"""
import pytest
import os
import sys

# 確保可以 import app 模組
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import (
    Salon, SalonOwner, Service, Stylist, ServiceStylist,
    Customer, Booking, BusinessHour, BookingRule
)
from werkzeug.security import generate_password_hash


@pytest.fixture(scope='session')
def app():
    """建立測試用 Flask 應用程式"""
    # 使用測試設定 - 在 Docker 容器內使用 db 作為主機
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': os.getenv(
            'DATABASE_URL',
            'postgresql://yulake:yulake@db:5432/yulake'
        ),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JWT_SECRET': 'test-secret-key'
    }

    app = create_app(test_config)
    yield app


@pytest.fixture(scope='function')
def client(app):
    """建立測試用 HTTP 客戶端"""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """建立測試用資料庫 session"""
    with app.app_context():
        yield db.session
        db.session.rollback()


@pytest.fixture
def sample_salon(app):
    """建立測試用店家資料"""
    with app.app_context():
        salon = Salon.query.filter_by(code='test_salon').first()
        if not salon:
            salon = Salon(
                id='test_salon_001',
                code='test_salon',
                name='測試店家',
                address='測試地址',
                phone='02-1234-5678'
            )
            db.session.add(salon)
            db.session.commit()
        return {
            'id': salon.id,
            'code': salon.code,
            'name': salon.name
        }


@pytest.fixture
def sample_owner(app, sample_salon):
    """建立測試用店家管理員"""
    with app.app_context():
        owner = SalonOwner.query.filter_by(email='test_owner@test.com').first()
        if not owner:
            owner = SalonOwner(
                id='test_owner_001',
                salon_id=sample_salon['id'],
                name='測試管理員',
                email='test_owner@test.com',
                password_hash=generate_password_hash('test123'),
                role='owner'
            )
            db.session.add(owner)
            db.session.commit()
        return {
            'id': owner.id,
            'email': 'test_owner@test.com',
            'password': 'test123',
            'salon_id': sample_salon['id']
        }


@pytest.fixture
def sample_customer(app):
    """建立測試用顧客"""
    with app.app_context():
        customer = Customer.query.filter_by(email='test_customer@test.com').first()
        if not customer:
            customer = Customer(
                id='test_customer_001',
                name='測試顧客',
                email='test_customer@test.com',
                password_hash=generate_password_hash('test123'),
                phone='0911-111-111'
            )
            db.session.add(customer)
            db.session.commit()
        return {
            'id': customer.id,
            'email': 'test_customer@test.com',
            'password': 'test123'
        }


@pytest.fixture
def salon_token(client, sample_owner):
    """取得店家登入 Token"""
    response = client.post('/api/auth/salon/login', json={
        'email': sample_owner['email'],
        'password': sample_owner['password']
    })
    data = response.get_json()
    return data['data']['token']


@pytest.fixture
def customer_token(client, sample_customer):
    """取得顧客登入 Token"""
    response = client.post('/api/auth/customer/login', json={
        'email': sample_customer['email'],
        'password': sample_customer['password']
    })
    data = response.get_json()
    return data['data']['token']


@pytest.fixture
def auth_headers(salon_token):
    """店家認證 headers"""
    return {'Authorization': f'Bearer {salon_token}'}


@pytest.fixture
def customer_auth_headers(customer_token):
    """顧客認證 headers"""
    return {'Authorization': f'Bearer {customer_token}'}
