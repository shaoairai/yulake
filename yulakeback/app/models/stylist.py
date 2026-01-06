# 設計師相關資料表模型
import uuid
from datetime import datetime
from app import db


class Stylist(db.Model):
    """設計師"""
    __tablename__ = 'stylists'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    salon_id = db.Column(db.String(36), db.ForeignKey('salons.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    style = db.Column(db.String(100))  # 擅長風格
    introduction = db.Column(db.Text)  # 簡介
    avatar_url = db.Column(db.String(255))  # 頭像 URL
    sort_order = db.Column(db.Integer, default=0)  # 排序順序
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    salon = db.relationship('Salon', back_populates='stylists')
    schedules = db.relationship('StylistSchedule', back_populates='stylist', lazy='dynamic')
    breaks = db.relationship('StylistBreak', back_populates='stylist', lazy='dynamic')
    service_stylists = db.relationship('ServiceStylist', back_populates='stylist', lazy='dynamic')
    bookings = db.relationship('Booking', back_populates='stylist', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'salon_id': self.salon_id,
            'name': self.name,
            'style': self.style,
            'introduction': self.introduction,
            'avatar_url': self.avatar_url,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class StylistSchedule(db.Model):
    """設計師排班"""
    __tablename__ = 'stylist_schedules'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    stylist_id = db.Column(db.String(36), db.ForeignKey('stylists.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0-6，0=週日
    is_working = db.Column(db.Boolean, default=True)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    stylist = db.relationship('Stylist', back_populates='schedules')

    def to_dict(self):
        return {
            'id': self.id,
            'stylist_id': self.stylist_id,
            'day_of_week': self.day_of_week,
            'is_working': self.is_working,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None
        }


class StylistBreak(db.Model):
    """設計師休息時間/特殊休假"""
    __tablename__ = 'stylist_breaks'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    stylist_id = db.Column(db.String(36), db.ForeignKey('stylists.id'), nullable=False)
    date = db.Column(db.Date)  # 特定日期休假用
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    reason = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 關聯
    stylist = db.relationship('Stylist', back_populates='breaks')

    def to_dict(self):
        return {
            'id': self.id,
            'stylist_id': self.stylist_id,
            'date': self.date.isoformat() if self.date else None,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'reason': self.reason
        }
