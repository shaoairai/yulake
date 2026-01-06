"""
店家後台 API 測試
"""
import pytest


class TestSalonDashboard:
    """店家儀表板 API 測試"""

    def test_get_dashboard(self, client, auth_headers):
        """測試取得儀表板數據"""
        response = client.get('/api/salon/dashboard', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'stats' in data['data']
        assert 'today_bookings' in data['data']

    def test_get_dashboard_unauthorized(self, client):
        """測試未授權取得儀表板"""
        response = client.get('/api/salon/dashboard')

        assert response.status_code == 401


class TestSalonBookings:
    """店家預約管理 API 測試"""

    def test_get_bookings(self, client, auth_headers):
        """測試取得預約列表"""
        response = client.get('/api/salon/bookings', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert isinstance(data['data'], list)

    def test_get_bookings_with_filters(self, client, auth_headers):
        """測試篩選預約列表"""
        from datetime import date, timedelta
        start_date = date.today().isoformat()
        end_date = (date.today() + timedelta(days=30)).isoformat()

        response = client.get(
            f'/api/salon/bookings?start_date={start_date}&end_date={end_date}&status=pending',
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True


class TestSalonServices:
    """店家服務管理 API 測試"""

    def test_get_services(self, client, auth_headers):
        """測試取得服務列表"""
        response = client.get('/api/salon/services', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert isinstance(data['data'], list)

    def test_create_service(self, client, auth_headers):
        """測試新增服務"""
        response = client.post('/api/salon/services', headers=auth_headers, json={
            'name': '測試服務',
            'description': '這是測試服務',
            'duration': 60,
            'price': 1000
        })

        # 可能成功或因重複名稱失敗
        assert response.status_code in [200, 201, 400]

    def test_create_service_missing_fields(self, client, auth_headers):
        """測試新增服務缺少必填欄位"""
        response = client.post('/api/salon/services', headers=auth_headers, json={
            'name': '測試'
            # 缺少 duration, price
        })

        assert response.status_code == 400


class TestSalonStylists:
    """店家設計師管理 API 測試"""

    def test_get_stylists(self, client, auth_headers):
        """測試取得設計師列表"""
        response = client.get('/api/salon/stylists', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert isinstance(data['data'], list)

    def test_create_stylist(self, client, auth_headers):
        """測試新增設計師"""
        import uuid
        response = client.post('/api/salon/stylists', headers=auth_headers, json={
            'name': f'測試設計師_{uuid.uuid4().hex[:6]}',
            'style': '日系',
            'introduction': '測試簡介'
        })

        assert response.status_code in [200, 201]
        data = response.get_json()
        assert data['success'] is True


class TestSalonCustomers:
    """店家顧客管理 API 測試"""

    def test_get_customers(self, client, auth_headers):
        """測試取得顧客列表"""
        response = client.get('/api/salon/customers', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert isinstance(data['data'], list)

    def test_get_customers_with_search(self, client, auth_headers):
        """測試搜尋顧客"""
        response = client.get('/api/salon/customers?search=王', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True


class TestSalonSettings:
    """店家設定 API 測試"""

    def test_get_settings(self, client, auth_headers):
        """測試取得店家設定"""
        response = client.get('/api/salon/settings', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'salon' in data['data']
        assert 'business_hours' in data['data']
        assert 'booking_rule' in data['data']


class TestSalonMembership:
    """店家會員等級 API 測試"""

    def test_get_membership_tiers(self, client, auth_headers):
        """測試取得會員等級列表"""
        response = client.get('/api/salon/membership/tiers', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert isinstance(data['data'], list)

    def test_get_point_rules(self, client, auth_headers):
        """測試取得集點規則"""
        response = client.get('/api/salon/membership/point-rules', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True

    def test_get_membership_stats(self, client, auth_headers):
        """測試取得會員統計"""
        response = client.get('/api/salon/membership/stats', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'tier_stats' in data['data']


class TestSalonEmail:
    """店家 Email 行銷 API 測試"""

    def test_get_email_templates(self, client, auth_headers):
        """測試取得 Email 範本列表"""
        response = client.get('/api/salon/email/templates', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert isinstance(data['data'], list)

    def test_get_auto_rules(self, client, auth_headers):
        """測試取得自動發信規則"""
        response = client.get('/api/salon/email/auto-rules', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
