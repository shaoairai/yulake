# 店家相關資料表模型
import uuid
from datetime import datetime
from app import db


class Salon(db.Model):
    """店家"""
    __tablename__ = 'salons'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)  # 用於 URL
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    line_id = db.Column(db.String(50))
    ig_account = db.Column(db.String(50))
    website = db.Column(db.String(255))
    logo_url = db.Column(db.String(255))
    theme_color = db.Column(db.String(7), default='#3F7C6A')  # 霧感莫蘭迪綠
    booking_url = db.Column(db.String(255))  # 自動產生的預約連結
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    owners = db.relationship('SalonOwner', back_populates='salon', lazy='dynamic')
    business_hours = db.relationship('BusinessHour', back_populates='salon', lazy='dynamic')
    booking_rules = db.relationship('BookingRule', back_populates='salon', uselist=False)
    special_dates = db.relationship('SpecialDate', back_populates='salon', lazy='dynamic')
    stylists = db.relationship('Stylist', back_populates='salon', lazy='dynamic')
    services = db.relationship('Service', back_populates='salon', lazy='dynamic')
    bookings = db.relationship('Booking', back_populates='salon', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'line_id': self.line_id,
            'ig_account': self.ig_account,
            'website': self.website,
            'logo_url': self.logo_url,
            'theme_color': self.theme_color,
            'booking_url': self.booking_url,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class SalonOwner(db.Model):
    """店家管理員"""
    __tablename__ = 'salon_owners'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    salon_id = db.Column(db.String(36), db.ForeignKey('salons.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default='staff')  # owner / staff
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    salon = db.relationship('Salon', back_populates='owners')

    def to_dict(self):
        return {
            'id': self.id,
            'salon_id': self.salon_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class BusinessHour(db.Model):
    """營業時間"""
    __tablename__ = 'business_hours'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    salon_id = db.Column(db.String(36), db.ForeignKey('salons.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0-6，0=週日
    is_open = db.Column(db.Boolean, default=True)
    open_time = db.Column(db.Time)
    close_time = db.Column(db.Time)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    salon = db.relationship('Salon', back_populates='business_hours')

    def to_dict(self):
        return {
            'id': self.id,
            'salon_id': self.salon_id,
            'day_of_week': self.day_of_week,
            'is_open': self.is_open,
            'open_time': self.open_time.strftime('%H:%M') if self.open_time else None,
            'close_time': self.close_time.strftime('%H:%M') if self.close_time else None
        }


class BookingRule(db.Model):
    """預約規則"""
    __tablename__ = 'booking_rules'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    salon_id = db.Column(db.String(36), db.ForeignKey('salons.id'), unique=True, nullable=False)
    slot_interval = db.Column(db.Integer, default=30)  # 預約時段間隔（分鐘）
    min_advance_hours = db.Column(db.Integer, default=1)  # 最少提前預約小時數
    max_advance_days = db.Column(db.Integer, default=30)  # 最多可預約天數
    require_confirmation = db.Column(db.Boolean, default=True)  # 是否需要店家確認
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    salon = db.relationship('Salon', back_populates='booking_rules')

    def to_dict(self):
        return {
            'id': self.id,
            'salon_id': self.salon_id,
            'slot_interval': self.slot_interval,
            'min_advance_hours': self.min_advance_hours,
            'max_advance_days': self.max_advance_days,
            'require_confirmation': self.require_confirmation
        }


class SpecialDate(db.Model):
    """特殊日期設定（公休/特殊營業時間）"""
    __tablename__ = 'special_dates'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    salon_id = db.Column(db.String(36), db.ForeignKey('salons.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # closed / special_hours
    open_time = db.Column(db.Time)  # type=special_hours 時使用
    close_time = db.Column(db.Time)  # type=special_hours 時使用
    reason = db.Column(db.String(100))  # 原因/說明
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 唯一約束
    __table_args__ = (
        db.UniqueConstraint('salon_id', 'date', name='uq_salon_special_date'),
    )

    # 關聯
    salon = db.relationship('Salon', back_populates='special_dates')

    def to_dict(self):
        return {
            'id': self.id,
            'salon_id': self.salon_id,
            'date': self.date.isoformat() if self.date else None,
            'type': self.type,
            'open_time': self.open_time.strftime('%H:%M') if self.open_time else None,
            'close_time': self.close_time.strftime('%H:%M') if self.close_time else None,
            'reason': self.reason
        }
