"""
統一 API 回應格式工具

flask-restx 會自動將 dict 轉為 JSON 回應，
所以這裡直接回傳 dict 和 status code 的 tuple
"""
from typing import Any
from app.utils.errors import ApiError, ErrorCode


class ApiResponse:
    """統一 API 回應格式"""

    @staticmethod
    def success(data: Any = None, message: str = None, meta: dict = None) -> tuple:
        """
        成功回應

        Args:
            data: 回應資料
            message: 成功訊息
            meta: 額外元資料（如分頁資訊）

        Returns:
            tuple: (response_dict, status_code)
        """
        response = {'success': True}

        if message:
            response['message'] = message

        if data is not None:
            response['data'] = data

        if meta:
            response['meta'] = meta

        return response, 200

    @staticmethod
    def created(data: Any = None, message: str = '建立成功') -> tuple:
        """建立成功回應 (201)"""
        response = {
            'success': True,
            'message': message
        }
        if data is not None:
            response['data'] = data
        return response, 201

    @staticmethod
    def no_content() -> tuple:
        """無內容回應 (204)"""
        return '', 204

    @staticmethod
    def error(error_code: ErrorCode, message: str = None, details: dict = None) -> tuple:
        """
        錯誤回應

        Args:
            error_code: 錯誤碼 (ErrorCode enum)
            message: 自訂錯誤訊息
            details: 錯誤詳情

        Returns:
            tuple: (response_dict, status_code)
        """
        response = {
            'success': False,
            'error': {
                'code': error_code.code,
                'message': message or error_code.message
            }
        }
        if details:
            response['error']['details'] = details
        return response, error_code.status

    @staticmethod
    def from_exception(error: ApiError) -> tuple:
        """從 ApiError 例外建立回應"""
        return error.to_dict(), error.status_code

    @staticmethod
    def paginated(items: list, page: int, per_page: int, total: int) -> tuple:
        """
        分頁回應

        Args:
            items: 資料列表
            page: 當前頁碼
            per_page: 每頁數量
            total: 總筆數

        Returns:
            tuple: (response_dict, status_code)
        """
        total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0

        return ApiResponse.success(
            data=items,
            meta={
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': total,
                    'total_pages': total_pages,
                    'has_next': page < total_pages,
                    'has_prev': page > 1
                }
            }
        )


def api_error(error_code: ErrorCode, message: str = None, details: dict = None) -> tuple:
    """快速建立錯誤回應的便捷函式"""
    return ApiResponse.error(error_code, message, details)
