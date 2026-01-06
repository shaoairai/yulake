# 服務相關資料表模型
import uuid
from datetime import datetime
from app import db


class Service(db.Model):
    """服務項目"""
    __tablename__ = 'services'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    salon_id = db.Column(db.String(36), db.ForeignKey('salons.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)  # 服務說明
    duration = db.Column(db.Integer, nullable=False)  # 所需時間（分鐘）
    price = db.Column(db.Integer, nullable=False)  # 價格
    image_url = db.Column(db.String(255))  # 服務圖片 URL
    sort_order = db.Column(db.Integer, default=0)  # 排序順序
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    salon = db.relationship('Salon', back_populates='services')
    service_stylists = db.relationship('ServiceStylist', back_populates='service', lazy='dynamic')
    bookings = db.relationship('Booking', back_populates='service', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'salon_id': self.salon_id,
            'name': self.name,
            'description': self.description,
            'duration': self.duration,
            'price': self.price,
            'image_url': self.image_url,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ServiceStylist(db.Model):
    """服務-設計師關聯"""
    __tablename__ = 'service_stylists'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    service_id = db.Column(db.String(36), db.ForeignKey('services.id'), nullable=False)
    stylist_id = db.Column(db.String(36), db.ForeignKey('stylists.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 唯一約束
    __table_args__ = (
        db.UniqueConstraint('service_id', 'stylist_id', name='uq_service_stylist'),
    )

    # 關聯
    service = db.relationship('Service', back_populates='service_stylists')
    stylist = db.relationship('Stylist', back_populates='service_stylists')

    def to_dict(self):
        return {
            'id': self.id,
            'service_id': self.service_id,
            'stylist_id': self.stylist_id
        }
