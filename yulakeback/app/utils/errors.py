"""
錯誤碼定義與錯誤處理
"""
from enum import Enum


class ErrorCode(Enum):
    """API 錯誤碼定義"""
    # 認證相關 (401, 403)
    AUTH_INVALID_CREDENTIALS = ('AUTH_INVALID_CREDENTIALS', 401, '帳號或密碼錯誤')
    AUTH_EMAIL_EXISTS = ('AUTH_EMAIL_EXISTS', 400, 'Email 已被註冊')
    AUTH_TOKEN_EXPIRED = ('AUTH_TOKEN_EXPIRED', 401, 'Token 已過期')
    AUTH_TOKEN_INVALID = ('AUTH_TOKEN_INVALID', 401, 'Token 無效')
    AUTH_UNAUTHORIZED = ('AUTH_UNAUTHORIZED', 403, '無權限存取此資源')
    AUTH_REQUIRED = ('AUTH_REQUIRED', 401, '請先登入')

    # 預約相關 (400, 403)
    BOOKING_SLOT_UNAVAILABLE = ('BOOKING_SLOT_UNAVAILABLE', 400, '該時段已被預約')
    BOOKING_USER_BLACKLISTED = ('BOOKING_USER_BLACKLISTED', 403, '您已被此店家列入黑名單')
    BOOKING_INVALID_TIME = ('BOOKING_INVALID_TIME', 400, '預約時間不符合規則')
    BOOKING_CANNOT_CANCEL = ('BOOKING_CANNOT_CANCEL', 400, '此預約無法取消')
    BOOKING_NOT_FOUND = ('BOOKING_NOT_FOUND', 404, '預約不存在')

    # 資源不存在 (404)
    SALON_NOT_FOUND = ('SALON_NOT_FOUND', 404, '店家不存在')
    SERVICE_NOT_FOUND = ('SERVICE_NOT_FOUND', 404, '服務不存在')
    STYLIST_NOT_FOUND = ('STYLIST_NOT_FOUND', 404, '設計師不存在')
    CUSTOMER_NOT_FOUND = ('CUSTOMER_NOT_FOUND', 404, '顧客不存在')
    RESOURCE_NOT_FOUND = ('RESOURCE_NOT_FOUND', 404, '資源不存在')

    # 驗證相關 (400)
    VALIDATION_ERROR = ('VALIDATION_ERROR', 400, '欄位驗證失敗')
    INVALID_REQUEST = ('INVALID_REQUEST', 400, '請求格式錯誤')

    # 伺服器錯誤 (500)
    INTERNAL_ERROR = ('INTERNAL_ERROR', 500, '系統內部錯誤')
    DATABASE_ERROR = ('DATABASE_ERROR', 500, '資料庫錯誤')

    def __init__(self, code: str, status: int, message: str):
        self._code = code
        self._status = status
        self._message = message

    @property
    def code(self) -> str:
        return self._code

    @property
    def status(self) -> int:
        return self._status

    @property
    def message(self) -> str:
        return self._message


class ApiError(Exception):
    """API 錯誤例外類別"""

    def __init__(self, error_code: ErrorCode, message: str = None, details: dict = None):
        self.error_code = error_code
        self.message = message or error_code.message
        self.details = details
        super().__init__(self.message)

    def to_dict(self) -> dict:
        result = {
            'success': False,
            'error': {
                'code': self.error_code.code,
                'message': self.message
            }
        }
        if self.details:
            result['error']['details'] = self.details
        return result

    @property
    def status_code(self) -> int:
        return self.error_code.status
