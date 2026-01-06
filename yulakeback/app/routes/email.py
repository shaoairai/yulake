"""
Email 行銷管理 API
"""
import json
import re
from flask import request, g
from flask_restx import Namespace, Resource
from datetime import datetime
from app import db
from app.models import (
    EmailTemplate, EmailCampaign, EmailLog, AutoEmailRule,
    Customer, SalonCustomer, CustomerMembership, MembershipTier
)
from app.utils.response import ApiResponse
from app.utils.errors import ApiError, ErrorCode
from app.utils.auth import salon_required

email_ns = Namespace('email', description='Email 行銷管理 API')

# Email 範本變數說明
TEMPLATE_VARIABLES = {
    '{{customer_name}}': '顧客姓名',
    '{{salon_name}}': '店家名稱',
    '{{booking_date}}': '預約日期',
    '{{booking_time}}': '預約時間',
    '{{service_name}}': '服務名稱',
    '{{stylist_name}}': '設計師姓名',
    '{{booking_url}}': '預約連結'
}


# ===== Email 範本管理 =====

@email_ns.route('/templates')
class EmailTemplateList(Resource):
    @email_ns.doc('get_email_templates', security='Bearer')
    @salon_required
    def get(self):
        """取得 Email 範本列表"""
        template_type = request.args.get('type')

        # 查詢店家範本和系統範本
        query = EmailTemplate.query.filter(
            db.or_(
                EmailTemplate.salon_id == g.salon_id,
                EmailTemplate.salon_id.is_(None)  # 系統範本
            )
        )

        if template_type:
            query = query.filter(EmailTemplate.type == template_type)

        templates = query.order_by(
            EmailTemplate.salon_id.desc(),  # 店家範本優先
            EmailTemplate.type,
            EmailTemplate.name
        ).all()

        return ApiResponse.success([{
            **t.to_dict(),
            'is_system_template': t.salon_id is None
        } for t in templates])

    @email_ns.doc('create_email_template', security='Bearer')
    @salon_required
    def post(self):
        """新增 Email 範本"""
        data = request.get_json()

        required_fields = ['type', 'name', 'subject', 'body']
        for field in required_fields:
            if not data.get(field):
                raise ApiError(ErrorCode.VALIDATION_ERROR, f'{field} 為必填')

        valid_types = [
            'booking_confirm', 'booking_reminder',
            'birthday', 'revisit', 'promotion'
        ]
        if data['type'] not in valid_types:
            raise ApiError(
                ErrorCode.VALIDATION_ERROR,
                f'範本類型無效，可選: {", ".join(valid_types)}'
            )

        template = EmailTemplate(
            salon_id=g.salon_id,
            type=data['type'],
            name=data['name'],
            subject=data['subject'],
            body=data['body'],
            is_active=data.get('is_active', True)
        )

        db.session.add(template)
        db.session.commit()

        return ApiResponse.created(template.to_dict())


@email_ns.route('/templates/<string:template_id>')
class EmailTemplateDetail(Resource):
    @email_ns.doc('get_email_template', security='Bearer')
    @salon_required
    def get(self, template_id):
        """取得 Email 範本詳情"""
        template = EmailTemplate.query.filter(
            EmailTemplate.id == template_id,
            db.or_(
                EmailTemplate.salon_id == g.salon_id,
                EmailTemplate.salon_id.is_(None)
            )
        ).first()

        if not template:
            raise ApiError(ErrorCode.RESOURCE_NOT_FOUND, '找不到此範本')

        result = template.to_dict()
        result['is_system_template'] = template.salon_id is None
        result['available_variables'] = TEMPLATE_VARIABLES

        return ApiResponse.success(result)

    @email_ns.doc('update_email_template', security='Bearer')
    @salon_required
    def put(self, template_id):
        """更新 Email 範本"""
        template = EmailTemplate.query.filter_by(
            id=template_id,
            salon_id=g.salon_id
        ).first()

        if not template:
            raise ApiError(ErrorCode.RESOURCE_NOT_FOUND, '找不到此範本或無法編輯系統範本')

        data = request.get_json()

        if 'name' in data:
            template.name = data['name']
        if 'subject' in data:
            template.subject = data['subject']
        if 'body' in data:
            template.body = data['body']
        if 'is_active' in data:
            template.is_active = data['is_active']

        db.session.commit()

        return ApiResponse.success(template.to_dict(), '更新成功')

    @email_ns.doc('delete_email_template', security='Bearer')
    @salon_required
    def delete(self, template_id):
        """刪除 Email 範本"""
        template = EmailTemplate.query.filter_by(
            id=template_id,
            salon_id=g.salon_id
        ).first()

        if not template:
            raise ApiError(ErrorCode.RESOURCE_NOT_FOUND, '找不到此範本或無法刪除系統範本')

        # 檢查是否有活動使用此範本
        campaign_count = EmailCampaign.query.filter_by(
            template_id=template_id
        ).count()

        if campaign_count > 0:
            raise ApiError(
                ErrorCode.VALIDATION_ERROR,
                f'此範本有 {campaign_count} 個行銷活動使用中，無法刪除'
            )

        db.session.delete(template)
        db.session.commit()

        return ApiResponse.success(message='刪除成功')


@email_ns.route('/templates/<string:template_id>/preview')
class EmailTemplatePreview(Resource):
    @email_ns.doc('preview_email_template', security='Bearer')
    @salon_required
    def post(self, template_id):
        """預覽 Email 範本"""
        template = EmailTemplate.query.filter(
            EmailTemplate.id == template_id,
            db.or_(
                EmailTemplate.salon_id == g.salon_id,
                EmailTemplate.salon_id.is_(None)
            )
        ).first()

        if not template:
            raise ApiError(ErrorCode.RESOURCE_NOT_FOUND, '找不到此範本')

        data = request.get_json() or {}
        test_data = data.get('test_data', {})

        # 預設測試資料
        default_data = {
            'customer_name': '王小明',
            'salon_name': '測試店家',
            'booking_date': '2025-01-15',
            'booking_time': '14:00',
            'service_name': '剪髮',
            'stylist_name': 'Amy',
            'booking_url': 'https://example.com/booking'
        }
        default_data.update(test_data)

        # 替換變數
        subject = template.subject
        body = template.body

        for var, value in default_data.items():
            subject = subject.replace(f'{{{{{var}}}}}', str(value))
            body = body.replace(f'{{{{{var}}}}}', str(value))

        return ApiResponse.success({
            'subject': subject,
            'body': body,
            'original_subject': template.subject,
            'original_body': template.body
        })


# ===== Email 行銷活動管理 =====

@email_ns.route('/campaigns')
class EmailCampaignList(Resource):
    @email_ns.doc('get_email_campaigns', security='Bearer')
    @salon_required
    def get(self):
        """取得行銷活動列表"""
        status = request.args.get('status')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        query = EmailCampaign.query.filter_by(salon_id=g.salon_id)

        if status:
            query = query.filter(EmailCampaign.status == status)

        query = query.order_by(EmailCampaign.created_at.desc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        items = []
        for campaign in pagination.items:
            item = campaign.to_dict()
            item['template_name'] = campaign.template.name if campaign.template else None
            items.append(item)

        return ApiResponse.success(
            data=items,
            meta={
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'total_pages': pagination.pages
                }
            }
        )

    @email_ns.doc('create_email_campaign', security='Bearer')
    @salon_required
    def post(self):
        """建立行銷活動"""
        data = request.get_json()

        required_fields = ['name', 'template_id', 'target_type']
        for field in required_fields:
            if not data.get(field):
                raise ApiError(ErrorCode.VALIDATION_ERROR, f'{field} 為必填')

        # 驗證範本存在
        template = EmailTemplate.query.filter(
            EmailTemplate.id == data['template_id'],
            db.or_(
                EmailTemplate.salon_id == g.salon_id,
                EmailTemplate.salon_id.is_(None)
            )
        ).first()

        if not template:
            raise ApiError(ErrorCode.RESOURCE_NOT_FOUND, '找不到指定範本')

        # 驗證目標類型
        valid_target_types = ['all', 'tier', 'inactive', 'birthday_month', 'custom']
        if data['target_type'] not in valid_target_types:
            raise ApiError(
                ErrorCode.VALIDATION_ERROR,
                f'目標類型無效，可選: {", ".join(valid_target_types)}'
            )

        campaign = EmailCampaign(
            salon_id=g.salon_id,
            name=data['name'],
            template_id=data['template_id'],
            target_type=data['target_type'],
            target_config=json.dumps(data.get('target_config', {})),
            status='draft'
        )

        # 設定排程時間
        if data.get('scheduled_at'):
            try:
                campaign.scheduled_at = datetime.strptime(
                    data['scheduled_at'], '%Y-%m-%d %H:%M'
                )
                campaign.status = 'scheduled'
            except ValueError:
                raise ApiError(ErrorCode.VALIDATION_ERROR, '排程時間格式錯誤')

        db.session.add(campaign)
        db.session.commit()

        return ApiResponse.created(campaign.to_dict())


@email_ns.route('/campaigns/<string:campaign_id>')
class EmailCampaignDetail(Resource):
    @email_ns.doc('get_email_campaign', security='Bearer')
    @salon_required
    def get(self, campaign_id):
        """取得行銷活動詳情"""
        campaign = EmailCampaign.query.filter_by(
            id=campaign_id,
            salon_id=g.salon_id
        ).first()

        if not campaign:
            raise ApiError(ErrorCode.RESOURCE_NOT_FOUND, '找不到此活動')

        result = campaign.to_dict()
        result['template'] = campaign.template.to_dict() if campaign.template else None

        # 計算開啟率和點擊率
        if campaign.sent_count > 0:
            result['open_rate'] = round(campaign.open_count / campaign.sent_count * 100, 2)
            result['click_rate'] = round(campaign.click_count / campaign.sent_count * 100, 2)
        else:
            result['open_rate'] = 0
            result['click_rate'] = 0

        return ApiResponse.success(result)

    @email_ns.doc('update_email_campaign', security='Bearer')
    @salon_required
    def put(self, campaign_id):
        """更新行銷活動"""
        campaign = EmailCampaign.query.filter_by(
            id=campaign_id,
            salon_id=g.salon_id
        ).first()

        if not campaign:
            raise ApiError(ErrorCode.RESOURCE_NOT_FOUND, '找不到此活動')

        if campaign.status not in ['draft', 'scheduled']:
            raise ApiError(ErrorCode.VALIDATION_ERROR, '只能編輯草稿或排程中的活動')

        data = request.get_json()

        if 'name' in data:
            campaign.name = data['name']
        if 'template_id' in data:
            # 驗證範本存在
            template = EmailTemplate.query.filter(
                EmailTemplate.id == data['template_id'],
                db.or_(
                    EmailTemplate.salon_id == g.salon_id,
                    EmailTemplate.salon_id.is_(None)
                )
            ).first()
            if not template:
                raise ApiError(ErrorCode.RESOURCE_NOT_FOUND, '找不到指定範本')
            campaign.template_id = data['template_id']
        if 'target_type' in data:
            campaign.target_type = data['target_type']
        if 'target_config' in data:
            campaign.target_config = json.dumps(data['target_config'])
        if 'scheduled_at' in data:
            if data['scheduled_at']:
                try:
                    campaign.scheduled_at = datetime.strptime(
                        data['scheduled_at'], '%Y-%m-%d %H:%M'
                    )
                    campaign.status = 'scheduled'
                except ValueError:
                    raise ApiError(ErrorCode.VALIDATION_ERROR, '排程時間格式錯誤')
            else:
                campaign.scheduled_at = None
                campaign.status = 'draft'

        db.session.commit()

        return ApiResponse.success(campaign.to_dict(), '更新成功')

    @email_ns.doc('delete_email_campaign', security='Bearer')
    @salon_required
    def delete(self, campaign_id):
        """刪除行銷活動"""
        campaign = EmailCampaign.query.filter_by(
            id=campaign_id,
            salon_id=g.salon_id
        ).first()

        if not campaign:
            raise ApiError(ErrorCode.RESOURCE_NOT_FOUND, '找不到此活動')

        if campaign.status in ['sending', 'sent']:
            raise ApiError(ErrorCode.VALIDATION_ERROR, '發送中或已發送的活動無法刪除')

        # 刪除相關的發送紀錄
        EmailLog.query.filter_by(campaign_id=campaign_id).delete()

        db.session.delete(campaign)
        db.session.commit()

        return ApiResponse.success(message='刪除成功')


@email_ns.route('/campaigns/<string:campaign_id>/send')
class EmailCampaignSend(Resource):
    @email_ns.doc('send_email_campaign', security='Bearer')
    @salon_required
    def post(self, campaign_id):
        """立即發送活動"""
        campaign = EmailCampaign.query.filter_by(
            id=campaign_id,
            salon_id=g.salon_id
        ).first()

        if not campaign:
            raise ApiError(ErrorCode.RESOURCE_NOT_FOUND, '找不到此活動')

        if campaign.status not in ['draft', 'scheduled']:
            raise ApiError(
                ErrorCode.VALIDATION_ERROR,
                f'此活動狀態為 {campaign.status}，無法發送'
            )

        # 計算收件人
        recipients = get_campaign_recipients(campaign)

        if not recipients:
            raise ApiError(ErrorCode.VALIDATION_ERROR, '沒有符合條件的收件人')

        # 更新活動狀態
        campaign.status = 'sending'
        campaign.total_recipients = len(recipients)
        campaign.sent_at = datetime.utcnow()

        # 在實際環境中，這裡應該使用背景任務來發送郵件
        # 目前僅模擬發送成功
        campaign.sent_count = len(recipients)
        campaign.status = 'sent'

        db.session.commit()

        return ApiResponse.success({
            'campaign_id': campaign.id,
            'status': campaign.status,
            'total_recipients': campaign.total_recipients,
            'sent_count': campaign.sent_count
        }, '活動已發送')


@email_ns.route('/campaigns/<string:campaign_id>/cancel')
class EmailCampaignCancel(Resource):
    @email_ns.doc('cancel_email_campaign', security='Bearer')
    @salon_required
    def post(self, campaign_id):
        """取消排程活動"""
        campaign = EmailCampaign.query.filter_by(
            id=campaign_id,
            salon_id=g.salon_id
        ).first()

        if not campaign:
            raise ApiError(ErrorCode.RESOURCE_NOT_FOUND, '找不到此活動')

        if campaign.status != 'scheduled':
            raise ApiError(ErrorCode.VALIDATION_ERROR, '只能取消排程中的活動')

        campaign.status = 'cancelled'
        db.session.commit()

        return ApiResponse.success(campaign.to_dict(), '活動已取消')


@email_ns.route('/campaigns/<string:campaign_id>/recipients')
class EmailCampaignRecipients(Resource):
    @email_ns.doc('preview_campaign_recipients', security='Bearer')
    @salon_required
    def get(self, campaign_id):
        """預覽收件人列表"""
        campaign = EmailCampaign.query.filter_by(
            id=campaign_id,
            salon_id=g.salon_id
        ).first()

        if not campaign:
            raise ApiError(ErrorCode.RESOURCE_NOT_FOUND, '找不到此活動')

        recipients = get_campaign_recipients(campaign)

        # 只回傳前 50 筆作為預覽
        preview_recipients = [{
            'id': c.id,
            'name': c.name,
            'email': c.email
        } for c in recipients[:50]]

        return ApiResponse.success({
            'total_count': len(recipients),
            'preview': preview_recipients,
            'has_more': len(recipients) > 50
        })


def get_campaign_recipients(campaign):
    """根據活動設定取得收件人列表"""
    target_config = json.loads(campaign.target_config) if campaign.target_config else {}

    # 基本查詢：店家的顧客
    query = Customer.query.join(SalonCustomer).filter(
        SalonCustomer.salon_id == campaign.salon_id,
        SalonCustomer.is_blacklisted == False,
        Customer.is_active == True
    )

    if campaign.target_type == 'all':
        pass  # 所有顧客
    elif campaign.target_type == 'tier':
        # 指定等級
        tier_ids = target_config.get('tier_ids', [])
        if tier_ids:
            query = query.join(CustomerMembership).filter(
                CustomerMembership.tier_id.in_(tier_ids),
                CustomerMembership.salon_id == campaign.salon_id
            )
    elif campaign.target_type == 'inactive':
        # 不活躍顧客（N 天未消費）
        inactive_days = target_config.get('inactive_days', 60)
        cutoff_date = datetime.utcnow()
        # 這裡需要更複雜的查詢，暫時簡化
        pass
    elif campaign.target_type == 'birthday_month':
        # 生日月份
        current_month = datetime.utcnow().month
        target_month = target_config.get('month', current_month)
        query = query.filter(
            db.extract('month', Customer.birthday) == target_month
        )

    return query.all()


# ===== 自動發信規則 =====

@email_ns.route('/auto-rules')
class AutoEmailRuleList(Resource):
    @email_ns.doc('get_auto_email_rules', security='Bearer')
    @salon_required
    def get(self):
        """取得自動發信規則"""
        rules = AutoEmailRule.query.filter_by(
            salon_id=g.salon_id
        ).all()

        result = []
        for rule in rules:
            item = rule.to_dict()
            item['template'] = rule.template.to_dict() if rule.template else None
            result.append(item)

        return ApiResponse.success(result)


@email_ns.route('/auto-rules/<string:rule_type>')
class AutoEmailRuleDetail(Resource):
    @email_ns.doc('get_auto_email_rule', security='Bearer')
    @salon_required
    def get(self, rule_type):
        """取得特定類型的自動發信規則"""
        rule = AutoEmailRule.query.filter_by(
            salon_id=g.salon_id,
            type=rule_type
        ).first()

        if not rule:
            return ApiResponse.success({
                'type': rule_type,
                'template_id': None,
                'config': None,
                'is_active': False,
                'message': '尚未設定此規則'
            })

        result = rule.to_dict()
        result['template'] = rule.template.to_dict() if rule.template else None

        return ApiResponse.success(result)

    @email_ns.doc('update_auto_email_rule', security='Bearer')
    @salon_required
    def put(self, rule_type):
        """更新自動發信規則"""
        valid_types = [
            'booking_confirm', 'booking_reminder',
            'birthday', 'revisit', 'no_show_warning'
        ]
        if rule_type not in valid_types:
            raise ApiError(
                ErrorCode.VALIDATION_ERROR,
                f'規則類型無效，可選: {", ".join(valid_types)}'
            )

        data = request.get_json()

        rule = AutoEmailRule.query.filter_by(
            salon_id=g.salon_id,
            type=rule_type
        ).first()

        if not rule:
            # 新增規則
            if not data.get('template_id'):
                raise ApiError(ErrorCode.VALIDATION_ERROR, 'template_id 為必填')

            rule = AutoEmailRule(
                salon_id=g.salon_id,
                type=rule_type,
                template_id=data['template_id']
            )
            db.session.add(rule)

        if 'template_id' in data:
            # 驗證範本存在
            template = EmailTemplate.query.filter(
                EmailTemplate.id == data['template_id'],
                db.or_(
                    EmailTemplate.salon_id == g.salon_id,
                    EmailTemplate.salon_id.is_(None)
                )
            ).first()
            if not template:
                raise ApiError(ErrorCode.RESOURCE_NOT_FOUND, '找不到指定範本')
            rule.template_id = data['template_id']

        if 'config' in data:
            rule.config = json.dumps(data['config'])

        if 'is_active' in data:
            rule.is_active = data['is_active']

        db.session.commit()

        result = rule.to_dict()
        result['template'] = rule.template.to_dict() if rule.template else None

        return ApiResponse.success(result, '規則已更新')


# ===== Email 發送紀錄 =====

@email_ns.route('/logs')
class EmailLogList(Resource):
    @email_ns.doc('get_email_logs', security='Bearer')
    @salon_required
    def get(self):
        """取得發送紀錄"""
        customer_id = request.args.get('customer_id')
        email_type = request.args.get('type')
        status = request.args.get('status')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        query = EmailLog.query.filter_by(salon_id=g.salon_id)

        if customer_id:
            query = query.filter(EmailLog.customer_id == customer_id)
        if email_type:
            query = query.filter(EmailLog.type == email_type)
        if status:
            query = query.filter(EmailLog.status == status)
        if date_from:
            try:
                date_from_dt = datetime.strptime(date_from, '%Y-%m-%d')
                query = query.filter(EmailLog.created_at >= date_from_dt)
            except ValueError:
                pass
        if date_to:
            try:
                date_to_dt = datetime.strptime(date_to, '%Y-%m-%d')
                query = query.filter(EmailLog.created_at <= date_to_dt)
            except ValueError:
                pass

        query = query.order_by(EmailLog.created_at.desc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        items = []
        for log in pagination.items:
            item = log.to_dict()
            item['customer_name'] = log.customer.name if log.customer else None
            items.append(item)

        return ApiResponse.success(
            data=items,
            meta={
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'total_pages': pagination.pages
                }
            }
        )
