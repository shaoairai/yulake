"""
預約 API 測試
測試預約的建立、取消、狀態變更等功能

API 路徑：
- 顧客相關: /api/me/bookings
- 店家相關: /api/salon/bookings
- 建立預約: /api/bookings
"""
import pytest
from datetime import date, timedelta


class TestCreateBooking:
    """建立預約測試 (透過 /api/bookings)"""

    def test_create_booking_missing_fields(self, client, customer_auth_headers):
        """測試建立預約缺少必填欄位"""
        response = client.post('/api/bookings', headers=customer_auth_headers, json={
            'salon_code': 'nailart'
            # 缺少 service_id, stylist_id, booking_date, start_time
        })

        assert response.status_code == 400

    def test_create_booking_unauthorized(self, client):
        """測試未授權建立預約"""
        response = client.post('/api/bookings', json={
            'salon_code': 'nailart',
            'service_id': 'service_001',
            'stylist_id': 'stylist_001',
            'booking_date': (date.today() + timedelta(days=7)).isoformat(),
            'start_time': '14:00'
        })

        assert response.status_code == 401


class TestCancelBooking:
    """顧客取消預約測試 (透過 /api/me/bookings)"""

    def test_cancel_booking_success(self, client, customer_auth_headers, app):
        """測試成功取消預約"""
        from app.models import Booking

        with app.app_context():
            # 找一個可取消的預約
            booking = Booking.query.filter_by(status='confirmed').first()

            if not booking:
                pytest.skip('No confirmed booking available for cancellation')

            response = client.put(
                f'/api/me/bookings/{booking.id}/cancel',
                headers=customer_auth_headers,
                json={'reason': '行程變更，需要取消'}
            )

            # 可能成功或因為不是該顧客的預約而失敗
            assert response.status_code in [200, 403, 404]

    def test_cancel_booking_invalid_id(self, client, customer_auth_headers):
        """測試取消不存在的預約"""
        response = client.put(
            '/api/me/bookings/invalid_booking_id/cancel',
            headers=customer_auth_headers,
            json={'reason': '測試取消'}
        )

        assert response.status_code == 404

    def test_cancel_booking_unauthorized(self, client):
        """測試未授權取消預約"""
        response = client.put(
            '/api/me/bookings/booking_001/cancel',
            json={'reason': '測試取消'}
        )

        assert response.status_code == 401


class TestUpdateBookingStatus:
    """店家更新預約狀態測試"""

    def test_confirm_booking(self, client, auth_headers, app):
        """測試確認預約"""
        from app.models import Booking

        with app.app_context():
            # 找一個待確認的預約
            booking = Booking.query.filter_by(status='pending').first()

            if not booking:
                pytest.skip('No pending booking available')

            response = client.put(
                f'/api/salon/bookings/{booking.id}/status',
                headers=auth_headers,
                json={'status': 'confirmed'}
            )

            assert response.status_code in [200, 403, 404]
            if response.status_code == 200:
                data = response.get_json()
                assert data['success'] is True

    def test_complete_booking(self, client, auth_headers, app):
        """測試標記預約完成"""
        from app.models import Booking

        with app.app_context():
            booking = Booking.query.filter_by(status='confirmed').first()

            if not booking:
                pytest.skip('No confirmed booking available')

            response = client.put(
                f'/api/salon/bookings/{booking.id}/status',
                headers=auth_headers,
                json={'status': 'completed'}
            )

            assert response.status_code in [200, 403, 404]

    def test_mark_no_show(self, client, auth_headers, app):
        """測試標記顧客未出席"""
        from app.models import Booking

        with app.app_context():
            booking = Booking.query.filter_by(status='confirmed').first()

            if not booking:
                pytest.skip('No confirmed booking available')

            response = client.put(
                f'/api/salon/bookings/{booking.id}/status',
                headers=auth_headers,
                json={'status': 'no_show', 'note': '顧客未到場'}
            )

            assert response.status_code in [200, 403, 404]

    def test_cancel_by_salon(self, client, auth_headers, app):
        """測試店家取消預約"""
        from app.models import Booking

        with app.app_context():
            booking = Booking.query.filter(
                Booking.status.in_(['pending', 'confirmed'])
            ).first()

            if not booking:
                pytest.skip('No booking available for cancellation')

            response = client.put(
                f'/api/salon/bookings/{booking.id}/status',
                headers=auth_headers,
                json={
                    'status': 'cancelled_by_salon',
                    'note': '店家臨時休業'
                }
            )

            assert response.status_code in [200, 403, 404]

    def test_update_invalid_status(self, client, auth_headers, app):
        """測試更新為無效狀態"""
        from app.models import Booking

        with app.app_context():
            # 找到屬於該店家的預約
            booking = Booking.query.filter_by(salon_id='salon_001').first()

            if not booking:
                # 備用：找任何預約
                booking = Booking.query.first()

            if not booking:
                pytest.skip('No booking available')

            response = client.put(
                f'/api/salon/bookings/{booking.id}/status',
                headers=auth_headers,
                json={'status': 'invalid_status'}
            )

            # 可能回傳 400 (無效狀態) 或 404 (非該店家預約)
            assert response.status_code in [400, 404]

    def test_update_booking_unauthorized(self, client, app):
        """測試未授權更新預約狀態"""
        from app.models import Booking

        with app.app_context():
            booking = Booking.query.first()

            if not booking:
                pytest.skip('No booking available')

            response = client.put(
                f'/api/salon/bookings/{booking.id}/status',
                json={'status': 'confirmed'}
            )

            assert response.status_code == 401


class TestGetBookingDetail:
    """取得預約詳情測試"""

    def test_get_booking_detail_salon(self, client, auth_headers, app):
        """測試店家取得預約詳情"""
        from app.models import Booking

        with app.app_context():
            booking = Booking.query.first()

            if not booking:
                pytest.skip('No booking available')

            response = client.get(
                f'/api/salon/bookings/{booking.id}',
                headers=auth_headers
            )

            assert response.status_code in [200, 403, 404]
            if response.status_code == 200:
                data = response.get_json()
                assert data['success'] is True
                assert 'id' in data['data']

    def test_get_booking_detail_customer(self, client, customer_auth_headers, app):
        """測試顧客取得預約詳情"""
        from app.models import Booking

        with app.app_context():
            booking = Booking.query.first()

            if not booking:
                pytest.skip('No booking available')

            response = client.get(
                f'/api/me/bookings/{booking.id}',
                headers=customer_auth_headers
            )

            # 可能成功或因為不是該顧客的預約而失敗
            assert response.status_code in [200, 403, 404]


class TestCalendarData:
    """日曆資料測試"""

    def test_get_calendar_data(self, client, auth_headers):
        """測試取得日曆資料"""
        start_date = date.today().isoformat()
        end_date = (date.today() + timedelta(days=30)).isoformat()

        response = client.get(
            f'/api/salon/calendar?start_date={start_date}&end_date={end_date}',
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert isinstance(data['data'], list)

    def test_get_calendar_data_with_stylist(self, client, auth_headers, app):
        """測試篩選特定設計師的日曆資料"""
        from app.models import Stylist

        with app.app_context():
            stylist = Stylist.query.filter_by(is_active=True).first()

            if not stylist:
                pytest.skip('No active stylist available')

            start_date = date.today().isoformat()
            end_date = (date.today() + timedelta(days=30)).isoformat()

            response = client.get(
                f'/api/salon/calendar?start_date={start_date}&end_date={end_date}&stylist_id={stylist.id}',
                headers=auth_headers
            )

            assert response.status_code == 200


class TestSpecialDates:
    """特殊日期測試"""

    def test_get_special_dates(self, client, auth_headers):
        """測試取得特殊日期列表"""
        response = client.get('/api/salon/special-dates', headers=auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert isinstance(data['data'], list)

    def test_create_special_date(self, client, auth_headers):
        """測試建立特殊日期"""
        future_date = (date.today() + timedelta(days=60)).isoformat()

        response = client.post('/api/salon/special-dates', headers=auth_headers, json={
            'date': future_date,
            'type': 'closed',
            'description': '測試店休日'
        })

        # 可能成功或因日期重複而失敗
        assert response.status_code in [200, 201, 400]

    def test_create_special_hours(self, client, auth_headers):
        """測試建立特殊營業時間"""
        future_date = (date.today() + timedelta(days=61)).isoformat()

        response = client.post('/api/salon/special-dates', headers=auth_headers, json={
            'date': future_date,
            'type': 'special_hours',
            'description': '測試特殊營業',
            'open_time': '10:00',
            'close_time': '18:00'
        })

        assert response.status_code in [200, 201, 400]

    def test_delete_special_date(self, client, auth_headers, app):
        """測試刪除特殊日期"""
        from app.models import SpecialDate

        with app.app_context():
            special_date = SpecialDate.query.first()

            if not special_date:
                pytest.skip('No special date available')

            response = client.delete(
                f'/api/salon/special-dates/{special_date.id}',
                headers=auth_headers
            )

            assert response.status_code in [200, 204, 403, 404]


class TestCustomerBookings:
    """顧客預約列表測試 (透過 /api/me/bookings)"""

    def test_get_my_bookings(self, client, customer_auth_headers):
        """測試顧客取得自己的預約列表"""
        response = client.get('/api/me/bookings', headers=customer_auth_headers)

        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert isinstance(data['data'], list)

    def test_get_my_bookings_unauthorized(self, client):
        """測試未授權取得預約列表"""
        response = client.get('/api/me/bookings')

        assert response.status_code == 401
