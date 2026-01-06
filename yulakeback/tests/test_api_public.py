"""
公開 API 測試（不需認證）
"""
import pytest


class TestPublicSalonApi:
    """公開店家資訊 API 測試"""

    def test_get_salon_info_success(self, client):
        """測試取得店家資訊成功"""
        response = client.get('/api/salons/nailart')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['code'] == 'nailart'
        assert 'name' in data['data']
        assert 'business_hours' in data['data']

    def test_get_salon_info_not_found(self, client):
        """測試取得不存在的店家"""
        response = client.get('/api/salons/nonexistent_salon_code')

        assert response.status_code == 404
        data = response.get_json()
        assert data['success'] is False

    def test_get_salon_services(self, client):
        """測試取得店家服務列表"""
        response = client.get('/api/salons/nailart/services')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert isinstance(data['data'], list)
        if len(data['data']) > 0:
            service = data['data'][0]
            assert 'id' in service
            assert 'name' in service
            assert 'duration' in service
            assert 'price' in service

    def test_get_salon_stylists(self, client):
        """測試取得店家設計師列表"""
        response = client.get('/api/salons/nailart/stylists')

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert isinstance(data['data'], list)
        if len(data['data']) > 0:
            stylist = data['data'][0]
            assert 'id' in stylist
            assert 'name' in stylist

    def test_get_available_slots_missing_params(self, client):
        """測試取得可用時段缺少參數"""
        response = client.get('/api/salons/nailart/available-slots')

        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False

    def test_get_available_slots_success(self, client):
        """測試取得可用時段成功"""
        # 先取得服務和設計師 ID
        services_response = client.get('/api/salons/nailart/services')
        stylists_response = client.get('/api/salons/nailart/stylists')

        services = services_response.get_json()['data']
        stylists = stylists_response.get_json()['data']

        if len(services) == 0 or len(stylists) == 0:
            pytest.skip('沒有可用的服務或設計師')

        service_id = services[0]['id']
        stylist_id = stylists[0]['id']

        # 取得未來日期的可用時段
        from datetime import date, timedelta
        future_date = (date.today() + timedelta(days=7)).isoformat()

        response = client.get(
            f'/api/salons/nailart/available-slots'
            f'?date={future_date}&service_id={service_id}&stylist_id={stylist_id}'
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'slots' in data['data']
        assert isinstance(data['data']['slots'], list)


class TestHealthCheck:
    """健康檢查 API 測試"""

    def test_health_check(self, client):
        """測試健康檢查端點"""
        response = client.get('/api/health')

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
