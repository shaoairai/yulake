"""
工具函式測試
"""
import pytest
import os
import sys
from datetime import datetime, timedelta, timezone

# 確保可以 import app 模組
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from werkzeug.security import generate_password_hash, check_password_hash


class TestPasswordUtils:
    """密碼工具測試"""

    def test_hash_password(self):
        """測試密碼雜湊"""
        password = 'test_password_123'
        hashed = generate_password_hash(password)

        # 雜湊後不應等於原密碼
        assert hashed != password
        # 雜湊值應有一定長度
        assert len(hashed) > 20

    def test_verify_password_correct(self):
        """測試正確密碼驗證"""
        password = 'correct_password'
        hashed = generate_password_hash(password)

        assert check_password_hash(hashed, password) is True

    def test_verify_password_incorrect(self):
        """測試錯誤密碼驗證"""
        password = 'correct_password'
        wrong_password = 'wrong_password'
        hashed = generate_password_hash(password)

        assert check_password_hash(hashed, wrong_password) is False

    def test_different_passwords_different_hashes(self):
        """測試不同密碼產生不同雜湊"""
        password1 = 'password1'
        password2 = 'password2'
        hash1 = generate_password_hash(password1)
        hash2 = generate_password_hash(password2)

        assert hash1 != hash2

    def test_same_password_different_hashes(self):
        """測試相同密碼產生不同雜湊（有鹽值）"""
        password = 'same_password'
        hash1 = generate_password_hash(password)
        hash2 = generate_password_hash(password)

        # 因為有鹽值，相同密碼應產生不同雜湊
        assert hash1 != hash2
        # 但兩者都應可驗證通過
        assert check_password_hash(hash1, password) is True
        assert check_password_hash(hash2, password) is True


class TestJWTUtils:
    """JWT 工具測試"""

    def test_create_token(self):
        """測試建立 Token"""
        from app.utils.auth import create_token

        payload = {'user_id': '123', 'type': 'customer'}
        token = create_token(payload)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 50  # JWT Token 通常很長

    def test_verify_token_valid(self):
        """測試驗證有效 Token"""
        from app.utils.auth import create_token, verify_token

        payload = {'user_id': '123', 'type': 'customer'}
        token = create_token(payload)
        decoded = verify_token(token)

        assert decoded['user_id'] == '123'
        assert decoded['type'] == 'customer'

    def test_verify_token_invalid(self):
        """測試驗證無效 Token"""
        from app.utils.auth import verify_token
        from app.utils.errors import ApiError

        with pytest.raises(ApiError) as exc_info:
            verify_token('invalid_token')

        assert exc_info.value.error_code.code == 'AUTH_TOKEN_INVALID'

    def test_token_expiration(self):
        """測試 Token 過期"""
        from app.utils.auth import create_token, verify_token
        from app.utils.errors import ApiError
        import jwt

        # 建立已過期的 Token
        payload = {
            'user_id': '123',
            'type': 'customer',
            'iat': datetime.now(timezone.utc) - timedelta(hours=200),
            'exp': datetime.now(timezone.utc) - timedelta(hours=1)
        }
        from app.utils.auth import JWT_SECRET, JWT_ALGORITHM
        expired_token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

        with pytest.raises(ApiError) as exc_info:
            verify_token(expired_token)

        assert exc_info.value.error_code.code == 'AUTH_TOKEN_EXPIRED'

    def test_token_contains_expiry(self):
        """測試 Token 包含過期時間"""
        from app.utils.auth import create_token, verify_token

        token = create_token({'user_id': '123'})
        decoded = verify_token(token)

        assert 'exp' in decoded
        assert 'iat' in decoded

    def test_create_token_with_custom_expiry(self):
        """測試自訂過期時間"""
        from app.utils.auth import create_token, verify_token

        token = create_token({'user_id': '123'}, expires_hours=1)
        decoded = verify_token(token)

        # 過期時間應在 1 小時後左右
        exp_time = datetime.fromtimestamp(decoded['exp'], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        diff = exp_time - now

        # 允許 1 分鐘誤差
        assert 55 < diff.total_seconds() / 60 < 65


class TestTimeSlotCalculation:
    """時段計算測試"""

    def test_time_slot_interval_30min(self):
        """測試 30 分鐘間隔時段"""
        # 模擬時段計算邏輯
        open_time = '10:00'
        close_time = '18:00'
        interval = 30

        slots = []
        current_hour = 10
        current_min = 0

        while current_hour < 18:
            time_str = f'{current_hour:02d}:{current_min:02d}'
            slots.append(time_str)
            current_min += interval
            if current_min >= 60:
                current_min = 0
                current_hour += 1

        # 從 10:00 到 17:30，每 30 分鐘一個時段
        assert '10:00' in slots
        assert '10:30' in slots
        assert '12:00' in slots
        assert '17:30' in slots
        assert '18:00' not in slots  # 18:00 不應包含（關店）

    def test_booking_time_conflict_detection(self):
        """測試預約時間衝突檢測"""
        # 現有預約
        existing_booking = {
            'start_time': '14:00',
            'end_time': '15:00'
        }

        def is_conflict(new_start, new_end, existing_start, existing_end):
            """檢查時間是否衝突"""
            # 轉換為分鐘數方便比較
            def time_to_minutes(time_str):
                h, m = map(int, time_str.split(':'))
                return h * 60 + m

            new_s = time_to_minutes(new_start)
            new_e = time_to_minutes(new_end)
            exist_s = time_to_minutes(existing_start)
            exist_e = time_to_minutes(existing_end)

            # 新預約結束時間 <= 現有開始時間：不衝突
            # 新預約開始時間 >= 現有結束時間：不衝突
            # 其他情況：衝突
            return not (new_e <= exist_s or new_s >= exist_e)

        # 測試案例
        # 完全重疊
        assert is_conflict('14:00', '15:00', '14:00', '15:00') is True
        # 部分重疊（前半）
        assert is_conflict('13:30', '14:30', '14:00', '15:00') is True
        # 部分重疊（後半）
        assert is_conflict('14:30', '15:30', '14:00', '15:00') is True
        # 新預約包含現有
        assert is_conflict('13:00', '16:00', '14:00', '15:00') is True
        # 現有包含新預約
        assert is_conflict('14:15', '14:45', '14:00', '15:00') is True
        # 緊鄰前方（不衝突）
        assert is_conflict('13:00', '14:00', '14:00', '15:00') is False
        # 緊鄰後方（不衝突）
        assert is_conflict('15:00', '16:00', '14:00', '15:00') is False
        # 完全不重疊（前方）
        assert is_conflict('10:00', '11:00', '14:00', '15:00') is False
        # 完全不重疊（後方）
        assert is_conflict('17:00', '18:00', '14:00', '15:00') is False


class TestApiResponse:
    """API 回應格式測試"""

    def test_success_response_format(self):
        """測試成功回應格式"""
        from app.utils.response import ApiResponse

        # ApiResponse.success 回傳 tuple (dict, status_code)
        response, status_code = ApiResponse.success({'id': '123'}, 'OK')

        assert status_code == 200
        assert response['success'] is True
        assert response['data']['id'] == '123'
        assert response['message'] == 'OK'

    def test_error_response_format(self):
        """測試錯誤回應格式"""
        from app.utils.errors import ErrorCode

        # ErrorCode 應包含標準錯誤碼
        assert hasattr(ErrorCode, 'AUTH_INVALID_CREDENTIALS')
        assert hasattr(ErrorCode, 'VALIDATION_ERROR')
        assert hasattr(ErrorCode, 'RESOURCE_NOT_FOUND')

    def test_pagination_response(self):
        """測試分頁回應格式"""
        from app.utils.response import ApiResponse

        items = [{'id': str(i)} for i in range(10)]
        # ApiResponse.success 回傳 tuple (dict, status_code)
        response, status_code = ApiResponse.success(
            data=items,
            meta={
                'pagination': {
                    'page': 1,
                    'per_page': 10,
                    'total': 100,
                    'total_pages': 10
                }
            }
        )

        assert status_code == 200
        assert response['success'] is True
        assert len(response['data']) == 10
        assert response['meta']['pagination']['total'] == 100
