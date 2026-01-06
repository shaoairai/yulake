# 顧客相關資料表模型
import uuid
from datetime import datetime
from app import db


class Customer(db.Model):
    """顧客"""
    __tablename__ = 'customers'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)  # 登入用
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))  # 選填，聯絡用
    birthday = db.Column(db.Date)  # 選填
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    salon_customers = db.relationship('SalonCustomer', back_populates='customer', lazy='dynamic')
    bookings = db.relationship('Booking', back_populates='customer', lazy='dynamic')
    customer_stats = db.relationship('CustomerStat', back_populates='customer', lazy='dynamic')
    customer_memberships = db.relationship('CustomerMembership', back_populates='customer', lazy='dynamic')
    email_logs = db.relationship('EmailLog', back_populates='customer', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'birthday': self.birthday.isoformat() if self.birthday else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class SalonCustomer(db.Model):
    """店家-顧客關聯與備註"""
    __tablename__ = 'salon_customers'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    salon_id = db.Column(db.String(36), db.ForeignKey('salons.id'), nullable=False)
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.id'), nullable=False)
    note = db.Column(db.Text)  # 店家備註
    is_blacklisted = db.Column(db.Boolean, default=False)
    blacklist_reason = db.Column(db.String(255))
    blacklisted_at = db.Column(db.DateTime)
    first_visit_at = db.Column(db.DateTime)  # 首次預約時間
    last_visit_at = db.Column(db.DateTime)  # 最後預約時間
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 唯一約束
    __table_args__ = (
        db.UniqueConstraint('salon_id', 'customer_id', name='uq_salon_customer'),
    )

    # 關聯
    salon = db.relationship('Salon')
    customer = db.relationship('Customer', back_populates='salon_customers')

    def to_dict(self):
        return {
            'id': self.id,
            'salon_id': self.salon_id,
            'customer_id': self.customer_id,
            'note': self.note,
            'is_blacklisted': self.is_blacklisted,
            'blacklist_reason': self.blacklist_reason,
            'blacklisted_at': self.blacklisted_at.isoformat() if self.blacklisted_at else None,
            'first_visit_at': self.first_visit_at.isoformat() if self.first_visit_at else None,
            'last_visit_at': self.last_visit_at.isoformat() if self.last_visit_at else None
        }
