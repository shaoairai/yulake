# Email 行銷相關資料表模型
import uuid
from datetime import datetime
from app import db


class EmailTemplate(db.Model):
    """Email 範本"""
    __tablename__ = 'email_templates'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    salon_id = db.Column(db.String(36), db.ForeignKey('salons.id'))  # NULL 表示系統範本
    # 範本類型：booking_confirm/booking_reminder/birthday/revisit/promotion
    type = db.Column(db.String(30), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # 範本名稱
    subject = db.Column(db.String(200), nullable=False)  # 信件主旨
    body = db.Column(db.Text, nullable=False)  # 信件內容（支援變數替換）
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    salon = db.relationship('Salon')
    campaigns = db.relationship('EmailCampaign', back_populates='template', lazy='dynamic')
    auto_rules = db.relationship('AutoEmailRule', back_populates='template', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'salon_id': self.salon_id,
            'type': self.type,
            'name': self.name,
            'subject': self.subject,
            'body': self.body,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class EmailCampaign(db.Model):
    """Email 行銷活動"""
    __tablename__ = 'email_campaigns'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    salon_id = db.Column(db.String(36), db.ForeignKey('salons.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # 活動名稱
    template_id = db.Column(db.String(36), db.ForeignKey('email_templates.id'), nullable=False)
    # 目標客群：all/tier/inactive/birthday_month/custom
    target_type = db.Column(db.String(30), nullable=False)
    target_config = db.Column(db.Text)  # 目標設定（JSON）
    scheduled_at = db.Column(db.DateTime)  # 排程發送時間
    sent_at = db.Column(db.DateTime)  # 實際發送時間
    # 狀態：draft/scheduled/sending/sent/cancelled
    status = db.Column(db.String(20), default='draft')
    total_recipients = db.Column(db.Integer, default=0)  # 總收件人數
    sent_count = db.Column(db.Integer, default=0)  # 已發送數
    open_count = db.Column(db.Integer, default=0)  # 開啟數
    click_count = db.Column(db.Integer, default=0)  # 點擊數
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    salon = db.relationship('Salon')
    template = db.relationship('EmailTemplate', back_populates='campaigns')
    logs = db.relationship('EmailLog', back_populates='campaign', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'salon_id': self.salon_id,
            'name': self.name,
            'template_id': self.template_id,
            'target_type': self.target_type,
            'target_config': self.target_config,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'status': self.status,
            'total_recipients': self.total_recipients,
            'sent_count': self.sent_count,
            'open_count': self.open_count,
            'click_count': self.click_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class EmailLog(db.Model):
    """Email 發送紀錄"""
    __tablename__ = 'email_logs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = db.Column(db.String(36), db.ForeignKey('email_campaigns.id'))  # 可 NULL
    salon_id = db.Column(db.String(36), db.ForeignKey('salons.id'), nullable=False)
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.id'), nullable=False)
    email = db.Column(db.String(100), nullable=False)  # 收件 Email
    # 類型：campaign/booking_confirm/booking_reminder/birthday/revisit
    type = db.Column(db.String(30), nullable=False)
    subject = db.Column(db.String(200), nullable=False)  # 實際主旨
    # 狀態：pending/sent/failed/bounced
    status = db.Column(db.String(20), default='pending')
    sent_at = db.Column(db.DateTime)  # 發送時間
    opened_at = db.Column(db.DateTime)  # 開啟時間
    clicked_at = db.Column(db.DateTime)  # 點擊時間
    error_message = db.Column(db.Text)  # 錯誤訊息
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 關聯
    campaign = db.relationship('EmailCampaign', back_populates='logs')
    salon = db.relationship('Salon')
    customer = db.relationship('Customer', back_populates='email_logs')

    def to_dict(self):
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'salon_id': self.salon_id,
            'customer_id': self.customer_id,
            'email': self.email,
            'type': self.type,
            'subject': self.subject,
            'status': self.status,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'opened_at': self.opened_at.isoformat() if self.opened_at else None,
            'clicked_at': self.clicked_at.isoformat() if self.clicked_at else None,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class AutoEmailRule(db.Model):
    """自動發信規則"""
    __tablename__ = 'auto_email_rules'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    salon_id = db.Column(db.String(36), db.ForeignKey('salons.id'), nullable=False)
    # 規則類型：booking_confirm/booking_reminder/birthday/revisit/no_show_warning
    type = db.Column(db.String(30), nullable=False)
    template_id = db.Column(db.String(36), db.ForeignKey('email_templates.id'), nullable=False)
    config = db.Column(db.Text)  # 規則設定（JSON）
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 關聯
    salon = db.relationship('Salon')
    template = db.relationship('EmailTemplate', back_populates='auto_rules')

    def to_dict(self):
        return {
            'id': self.id,
            'salon_id': self.salon_id,
            'type': self.type,
            'template_id': self.template_id,
            'config': self.config,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
