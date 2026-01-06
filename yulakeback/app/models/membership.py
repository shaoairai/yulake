# 會員等級相關資料表模型
import uuid
from datetime import datetime
from app import db


class MembershipTier(db.Model):
    """會員等級定義"""
    __tablename__ = 'membership_tiers'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    salon_id = db.Column(db.String(36), db.ForeignKey('salons.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)  # 等級名稱
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
