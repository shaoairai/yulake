"""
認證 API 測試
"""
import pytest


class TestCustomerAuth:
    """顧客認證測試"""

    def test_customer_register_success(self, client):
        """測試顧客註冊成功"""
        response = client.post('/api/auth/customer/register', json={
            'name': '新顧客',
            'email': f'new_customer_{pytest.importorskip("uuid").uuid4().hex[:8]}@test.com',
            'password': 'newpassword123',
            'phone': '0922-222-222'
        })

        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'token' in data['data']
        assert data['data']['user']['name'] == '新顧客'

    def test_customer_register_missing_fields(self, client):
        """測試顧客註冊缺少必填欄位"""
        response = client.post('/api/auth/customer/register', json={
            'name': '測試',
            'email': 'test@test.com'
            # 缺少 password
        })

        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False

    def test_customer_register_duplicate_email(self, client, sample_customer):
        """測試顧客註冊重複 Email"""
        response = client.post('/api/auth/customer/register', json={
            'name': '另一個顧客',
            'email': sample_customer['email'],  # 已存在的 Email
            'password': 'password123'
        })

        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert data['error']['code'] == 'AUTH_EMAIL_EXISTS'

    def test_customer_login_success(self, client, sample_customer):
        """測試顧客登入成功"""
        response = client.post('/api/auth/customer/login', json={
            'email': sample_customer['email'],
            'password': sample_customer['password']
        })

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'token' in data['data']
        assert data['data']['user']['email'] == sample_customer['email']

    def test_customer_login_wrong_password(self, client, sample_customer):
        """測試顧客登入密碼錯誤"""
        response = client.post('/api/auth/customer/login', json={
            'email': sample_customer['email'],
            'password': 'wrong_password'
        })

        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False
        assert data['error']['code'] == 'AUTH_INVALID_CREDENTIALS'

    def test_customer_login_nonexistent_email(self, client):
        """測試顧客登入帳號不存在"""
        response = client.post('/api/auth/customer/login', json={
            'email': 'nonexistent@test.com',
            'password': 'anypassword'
        })

        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False

    def test_customer_get_me_with_token(self, client, customer_token):
        """測試取得當前顧客資訊"""
        response = client.get('/api/auth/customer/me',
                              headers={'Authorization': f'Bearer {customer_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'id' in data['data']

    def test_customer_get_me_without_token(self, client):
        """測試無 Token 取得顧客資訊"""
        response = client.get('/api/auth/customer/me')

        assert response.status_code == 401


class TestSalonAuth:
    """店家認證測試"""

    def test_salon_login_success(self, client, sample_owner):
        """測試店家登入成功"""
        response = client.post('/api/auth/salon/login', json={
            'email': sample_owner['email'],
            'password': sample_owner['password']
        })

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'token' in data['data']
        assert 'salon' in data['data']

    def test_salon_login_wrong_password(self, client, sample_owner):
        """測試店家登入密碼錯誤"""
        response = client.post('/api/auth/salon/login', json={
            'email': sample_owner['email'],
            'password': 'wrong_password'
        })

        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] is False

    def test_salon_get_me_with_token(self, client, salon_token):
        """測試取得當前店家資訊"""
        response = client.get('/api/auth/salon/me',
                              headers={'Authorization': f'Bearer {salon_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'user' in data['data']
        assert 'salon' in data['data']

    def test_salon_get_me_without_token(self, client):
        """測試無 Token 取得店家資訊"""
        response = client.get('/api/auth/salon/me')

        assert response.status_code == 401

    def test_invalid_token_format(self, client):
        """測試無效 Token 格式"""
        response = client.get('/api/auth/salon/me',
                              headers={'Authorization': 'InvalidFormat token123'})

        assert response.status_code == 401
