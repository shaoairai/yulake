# 預約與統計相關資料表模型
import uuid
from datetime import datetime
from app import db


class Booking(db.Model):
    """預約"""
    __tablename__ = 'bookings'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    salon_id = db.Column(db.String(36), db.ForeignKey('salons.id'), nullable=False)
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.id'), nullable=False)
    service_id = db.Column(db.String(36), db.ForeignKey('services.id'), nullable=False)
    stylist_id = db.Column(db.String(36), db.ForeignKey('stylists.id'), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    # 狀態：pending/confirmed/completed/cancelled_by_customer/cancelled_by_salon/no_show
    status = db.Column(db.String(30), default='pending')
    customer_note = db.Column(db.Text)  # 顧客備註
    salon_note = db.Column(db.Text)  # 店家備註
    cancelled_at = db.Column(db.DateTime)  # 取消時間
    cancel_reason = db.Column(db.String(255))  # 取消原因
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 索引
    __table_args__ = (
        db.Index('ix_booking_salon_date', 'salon_id', 'booking_date'),
        db.Index('ix_booking_stylist_date', 'stylist_id', 'booking_date'),
        db.Index('ix_booking_customer', 'customer_id'),
    )

    # 關聯
    salon = db.relationship('Salon', back_populates='bookings')
    customer = db.relationship('Customer', back_populates='bookings')
    service = db.relationship('Service', back_populates='bookings')
    stylist = db.relationship('Stylist', back_populates='bookings')

    def to_dict(self):
        return {
            'id': self.id,
            'salon_id': self.salon_id,
            'customer_id': self.customer_id,
            'service_id': self.service_id,
            'stylist_id': self.stylist_id,
            'booking_date': self.booking_date.isoformat() if self.booking_date else None,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'status': self.status,
            'customer_note': self.customer_note,
            'salon_note': self.salon_note,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'cancel_reason': self.cancel_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def to_dict_with_relations(self):
        """包含關聯資料的字典"""
        data = self.to_dict()
        data['customer'] = self.customer.to_dict() if self.customer else None
        data['service'] = self.service.to_dict() if self.service else None
        data['stylist'] = self.stylist.to_dict() if self.stylist else None
        return data


class CustomerStat(db.Model):
    """顧客統計快取"""
    __tablename__ = 'customer_stats'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    salon_id = db.Column(db.String(36), db.ForeignKey('salons.id'), nullable=False)
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.id'), nullable=False)
    total_bookings = db.Column(db.Integer, default=0)  # 總預約次數
    completed_bookings = db.Column(db.Integer, default=0)  # 已完成次數
    no_show_count = db.Column(db.Integer, default=0)  # 爽約次數
    total_spent = db.Column(db.Integer, default=0)  # 累積消費金額
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 唯一約束
    __table_args__ = (
        db.UniqueConstraint('salon_id', 'customer_id', name='uq_customer_stat'),
    )

    # 關聯
    salon = db.relationship('Salon')
    customer = db.relationship('Customer', back_populates='customer_stats')

    def to_dict(self):
        return {
            'id': self.id,
            'salon_id': self.salon_id,
            'customer_id': self.customer_id,
            'total_bookings': self.total_bookings,
            'completed_bookings': self.completed_bookings,
            'no_show_count': self.no_show_count,
            'total_spent': self.total_spent,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
