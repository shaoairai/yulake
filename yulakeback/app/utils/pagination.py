"""
分頁查詢工具
"""
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.query import Query


def paginate(query: Query, schema=None, default_per_page: int = 20, max_per_page: int = 100) -> dict:
    """
    對查詢結果進行分頁

    Args:
        query: SQLAlchemy Query 物件
        schema: 序列化用的 schema（可選，需實作 dump 方法）
        default_per_page: 預設每頁數量
        max_per_page: 最大每頁數量

    Returns:
        dict: {
            'items': 資料列表,
            'page': 當前頁碼,
            'per_page': 每頁數量,
            'total': 總筆數,
            'total_pages': 總頁數,
            'has_next': 是否有下一頁,
            'has_prev': 是否有上一頁
        }
    """
    # 從 query string 取得分頁參數
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', default_per_page, type=int)

    # 限制範圍
    page = max(1, page)
    per_page = min(max(1, per_page), max_per_page)

    # 執行分頁查詢
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # 序列化資料
    if schema:
        items = schema.dump(pagination.items, many=True)
    else:
        items = pagination.items

    return {
        'items': items,
        'page': page,
        'per_page': per_page,
        'total': pagination.total,
        'total_pages': pagination.pages,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }


def get_pagination_params(default_per_page: int = 20, max_per_page: int = 100) -> tuple:
    """
    取得分頁參數

    Args:
        default_per_page: 預設每頁數量
        max_per_page: 最大每頁數量

    Returns:
        tuple: (page, per_page)
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', default_per_page, type=int)

    page = max(1, page)
    per_page = min(max(1, per_page), max_per_page)

    return page, per_page
