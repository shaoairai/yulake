# 會員等級相關資料表模型
import uuid
from datetime import datetime
from app import db


class MembershipTier(db.Model):
    """會員等級定義（每店家最多 10 等級）"""
    __tablename__ = 'membership_tiers'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    salon_id = db.Column(db.String(36), db.ForeignKey('salons.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)  # 等級名稱
    level = db.Column(db.Integer, default=1)  # 等級編號 (1-10)
    min_points = db.Column(db.Integer, default=0)  # 最低累積點數（升級門檻）
    min_spent = db.Column(db.Integer, default=0)  # 最低累積消費金額
    min_visits = db.Column(db.Integer, default=0)  # 最低來店次數
    discount_percent = db.Column(db.Integer, default=0)  # 折扣百分比（5 表示 95 折）
    benefits = db.Column(db.Text)  # 等級福利說明（JSON 或文字）
    color = db.Column(db.String(7), default='#3F7C6A')  # 等級顯示顏色
    sort_order = db.Column(db.Integer, default=0)  # 排序順序
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    salon = db.relationship('Salon')
    customer_memberships = db.relationship('CustomerMembership', back_populates='tier', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'salon_id': self.salon_id,
            'name': self.name,
            'level': self.level,
            'min_points': self.min_points,
            'min_spent': self.min_spent,
            'min_visits': self.min_visits,
            'discount_percent': self.discount_percent,
            'benefits': self.benefits,
            'color': self.color,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class CustomerMembership(db.Model):
    """顧客會員等級"""
    __tablename__ = 'customer_memberships'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    salon_id = db.Column(db.String(36), db.ForeignKey('salons.id'), nullable=False)
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.id'), nullable=False)
    tier_id = db.Column(db.String(36), db.ForeignKey('membership_tiers.id'), nullable=False)
    upgraded_at = db.Column(db.DateTime, default=datetime.utcnow)  # 升級時間
    expires_at = db.Column(db.DateTime)  # 等級到期時間（可選，用於限時等級）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 唯一約束
    __table_args__ = (
        db.UniqueConstraint('salon_id', 'customer_id', name='uq_customer_membership'),
    )

    # 關聯
    salon = db.relationship('Salon')
    customer = db.relationship('Customer', back_populates='customer_memberships')
    tier = db.relationship('MembershipTier', back_populates='customer_memberships')

    def to_dict(self):
        return {
            'id': self.id,
            'salon_id': self.salon_id,
            'customer_id': self.customer_id,
            'tier_id': self.tier_id,
            'upgraded_at': self.upgraded_at.isoformat() if self.upgraded_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PointRule(db.Model):
    """集點規則設定（每店家一組規則）"""
    __tablename__ = 'point_rules'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    salon_id = db.Column(db.String(36), db.ForeignKey('salons.id'), nullable=False, unique=True)

    # 集點方式
    points_per_visit = db.Column(db.Integer, default=1)  # 每次消費獲得點數
    points_per_amount = db.Column(db.Integer, default=0)  # 每消費 N 元獲得 1 點（0=不啟用）
    bonus_birthday_points = db.Column(db.Integer, default=0)  # 生日當月額外點數

    # 升級規則類型: points / spent / visits / combined
    upgrade_rule_type = db.Column(db.String(20), default='points')

    # 點數有效期（月），0=永久
    points_expiry_months = db.Column(db.Integer, default=0)

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    salon = db.relationship('Salon')

    def to_dict(self):
        return {
            'id': self.id,
            'salon_id': self.salon_id,
            'points_per_visit': self.points_per_visit,
            'points_per_amount': self.points_per_amount,
            'bonus_birthday_points': self.bonus_birthday_points,
            'upgrade_rule_type': self.upgrade_rule_type,
            'points_expiry_months': self.points_expiry_months,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class CustomerPoints(db.Model):
    """顧客點數"""
    __tablename__ = 'customer_points'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    salon_id = db.Column(db.String(36), db.ForeignKey('salons.id'), nullable=False)
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.id'), nullable=False)
    total_points = db.Column(db.Integer, default=0)  # 目前累積點數
    lifetime_points = db.Column(db.Integer, default=0)  # 歷史累積總點數
    used_points = db.Column(db.Integer, default=0)  # 已使用點數
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 唯一約束
    __table_args__ = (
        db.UniqueConstraint('salon_id', 'customer_id', name='uq_customer_points'),
    )

    # 關聯
    salon = db.relationship('Salon')
    customer = db.relationship('Customer')

    def to_dict(self):
        return {
            'id': self.id,
            'salon_id': self.salon_id,
            'customer_id': self.customer_id,
            'total_points': self.total_points,
            'lifetime_points': self.lifetime_points,
            'used_points': self.used_points,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PointTransaction(db.Model):
    """點數交易紀錄"""
    __tablename__ = 'point_transactions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    salon_id = db.Column(db.String(36), db.ForeignKey('salons.id'), nullable=False)
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.id'), nullable=False)
    booking_id = db.Column(db.String(36), db.ForeignKey('bookings.id'))  # 關聯預約（可選）

    # 交易類型: earn / use / expire / adjust（手動調整）
    transaction_type = db.Column(db.String(20), nullable=False)
    points = db.Column(db.Integer, nullable=False)  # 正數=獲得，負數=使用/過期
    balance_after = db.Column(db.Integer, nullable=False)  # 交易後餘額
    description = db.Column(db.String(255))  # 說明
    created_by = db.Column(db.String(36))  # 操作者（店家手動調整時記錄）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 關聯
    salon = db.relationship('Salon')
    customer = db.relationship('Customer')

    def to_dict(self):
        return {
            'id': self.id,
            'salon_id': self.salon_id,
            'customer_id': self.customer_id,
            'booking_id': self.booking_id,
            'transaction_type': self.transaction_type,
            'points': self.points,
            'balance_after': self.balance_after,
            'description': self.description,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
