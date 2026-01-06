"""
會員等級與集點管理 API
"""
from flask import request, g
from flask_restx import Namespace, Resource
from datetime import datetime
from app import db
from app.models import (
    MembershipTier, CustomerMembership, PointRule,
    CustomerPoints, PointTransaction, Customer, CustomerStat
)
from app.utils.response import ApiResponse
from app.utils.errors import ApiError, ErrorCode
from app.utils.auth import salon_required

membership_ns = Namespace('membership', description='會員等級與集點管理 API')

MAX_TIERS = 10  # 每店家最多 10 個等級


# ===== 會員等級管理 =====

@membership_ns.route('/tiers')
class MembershipTierList(Resource):
    @membership_ns.doc('get_membership_tiers', security='Bearer')
    @salon_required
    def get(self):
        """取得會員等級列表"""
        tiers = MembershipTier.query.filter_by(
            salon_id=g.salon_id
        ).order_by(MembershipTier.level).all()

        return ApiResponse.success([tier.to_dict() for tier in tiers])

    @membership_ns.doc('create_membership_tier', security='Bearer')
    @salon_required
    def post(self):
        """新增會員等級"""
        # 檢查等級數量上限
        current_count = MembershipTier.query.filter_by(
            salon_id=g.salon_id
        ).count()

        if current_count >= MAX_TIERS:
            raise ApiError(
                ErrorCode.VALIDATION_ERROR,
                f'會員等級已達上限 {MAX_TIERS} 個'
            )

        data = request.get_json()

        if not data.get('name'):
            raise ApiError(ErrorCode.VALIDATION_ERROR, '等級名稱為必填')

        # 檢查 level 範圍
        level = data.get('level', current_count + 1)
        if level < 1 or level > MAX_TIERS:
            raise ApiError(
                ErrorCode.VALIDATION_ERROR,
                f'等級編號需在 1-{MAX_TIERS} 之間'
            )

        tier = MembershipTier(
            salon_id=g.salon_id,
            name=data['name'],
            level=level,
            min_points=data.get('min_points', 0),
            min_spent=data.get('min_spent', 0),
            min_visits=data.get('min_visits', 0),
            discount_percent=data.get('discount_percent', 0),
            benefits=data.get('benefits'),
            color=data.get('color', '#3F7C6A'),
            sort_order=data.get('sort_order', level)
        )

        db.session.add(tier)
        db.session.commit()

        return ApiResponse.created(tier.to_dict())


@membership_ns.route('/tiers/<string:tier_id>')
class MembershipTierDetail(Resource):
    @membership_ns.doc('get_membership_tier', security='Bearer')
    @salon_required
    def get(self, tier_id):
        """取得會員等級詳情"""
        tier = MembershipTier.query.filter_by(
            id=tier_id,
            salon_id=g.salon_id
        ).first()

        if not tier:
            raise ApiError(ErrorCode.RESOURCE_NOT_FOUND, '找不到此會員等級')

        # 統計使用此等級的顧客數
        member_count = CustomerMembership.query.filter_by(
            tier_id=tier_id,
            salon_id=g.salon_id
        ).count()

        result = tier.to_dict()
        result['member_count'] = member_count

        return ApiResponse.success(result)

    @membership_ns.doc('update_membership_tier', security='Bearer')
    @salon_required
    def put(self, tier_id):
        """更新會員等級"""
        tier = MembershipTier.query.filter_by(
            id=tier_id,
            salon_id=g.salon_id
        ).first()

        if not tier:
            raise ApiError(ErrorCode.RESOURCE_NOT_FOUND, '找不到此會員等級')

        data = request.get_json()

        if 'name' in data:
            tier.name = data['name']
        if 'level' in data:
            level = data['level']
            if level < 1 or level > MAX_TIERS:
                raise ApiError(
                    ErrorCode.VALIDATION_ERROR,
                    f'等級編號需在 1-{MAX_TIERS} 之間'
                )
            tier.level = level
        if 'min_points' in data:
            tier.min_points = data['min_points']
        if 'min_spent' in data:
            tier.min_spent = data['min_spent']
        if 'min_visits' in data:
            tier.min_visits = data['min_visits']
        if 'discount_percent' in data:
            tier.discount_percent = data['discount_percent']
        if 'benefits' in data:
            tier.benefits = data['benefits']
        if 'color' in data:
            tier.color = data['color']
        if 'sort_order' in data:
            tier.sort_order = data['sort_order']
        if 'is_active' in data:
            tier.is_active = data['is_active']

        db.session.commit()

        return ApiResponse.success(tier.to_dict(), '更新成功')

    @membership_ns.doc('delete_membership_tier', security='Bearer')
    @salon_required
    def delete(self, tier_id):
        """刪除會員等級"""
        tier = MembershipTier.query.filter_by(
            id=tier_id,
            salon_id=g.salon_id
        ).first()

        if not tier:
            raise ApiError(ErrorCode.RESOURCE_NOT_FOUND, '找不到此會員等級')

        # 檢查是否有顧客使用此等級
        member_count = CustomerMembership.query.filter_by(
            tier_id=tier_id
        ).count()

        if member_count > 0:
            raise ApiError(
                ErrorCode.VALIDATION_ERROR,
                f'此等級有 {member_count} 位顧客使用中，無法刪除'
            )

        db.session.delete(tier)
        db.session.commit()

        return ApiResponse.success(message='刪除成功')


# ===== 顧客等級調整 =====

@membership_ns.route('/customers/<string:customer_id>/tier')
class CustomerTier(Resource):
    @membership_ns.doc('get_customer_tier', security='Bearer')
    @salon_required
    def get(self, customer_id):
        """取得顧客目前等級"""
        membership = CustomerMembership.query.filter_by(
            salon_id=g.salon_id,
            customer_id=customer_id
        ).first()

        if not membership:
            return ApiResponse.success({
                'customer_id': customer_id,
                'tier': None,
                'message': '尚未設定會員等級'
            })

        result = membership.to_dict()
        result['tier'] = membership.tier.to_dict() if membership.tier else None

        return ApiResponse.success(result)

    @membership_ns.doc('set_customer_tier', security='Bearer')
    @salon_required
    def put(self, customer_id):
        """手動調整顧客等級"""
        data = request.get_json()
        tier_id = data.get('tier_id')

        if not tier_id:
            raise ApiError(ErrorCode.VALIDATION_ERROR, 'tier_id 為必填')

        # 驗證等級存在
        tier = MembershipTier.query.filter_by(
            id=tier_id,
            salon_id=g.salon_id,
            is_active=True
        ).first()

        if not tier:
            raise ApiError(ErrorCode.RESOURCE_NOT_FOUND, '找不到此會員等級')

        # 驗證顧客存在
        customer = Customer.query.get(customer_id)
        if not customer:
            raise ApiError(ErrorCode.CUSTOMER_NOT_FOUND)

        # 更新或新增會員資格
        membership = CustomerMembership.query.filter_by(
            salon_id=g.salon_id,
            customer_id=customer_id
        ).first()

        if membership:
            membership.tier_id = tier_id
            membership.upgraded_at = datetime.utcnow()
        else:
            membership = CustomerMembership(
                salon_id=g.salon_id,
                customer_id=customer_id,
                tier_id=tier_id
            )
            db.session.add(membership)

        # 設定到期時間（如果有指定）
        if 'expires_at' in data:
            if data['expires_at']:
                try:
                    membership.expires_at = datetime.strptime(
                        data['expires_at'], '%Y-%m-%d'
                    )
                except ValueError:
                    raise ApiError(ErrorCode.VALIDATION_ERROR, '到期日期格式錯誤')
            else:
                membership.expires_at = None

        db.session.commit()

        result = membership.to_dict()
        result['tier'] = tier.to_dict()

        return ApiResponse.success(result, '會員等級已更新')


# ===== 集點規則管理 =====

@membership_ns.route('/point-rules')
class PointRuleSettings(Resource):
    @membership_ns.doc('get_point_rules', security='Bearer')
    @salon_required
    def get(self):
        """取得集點規則"""
        rule = PointRule.query.filter_by(salon_id=g.salon_id).first()

        if not rule:
            # 回傳預設值
            return ApiResponse.success({
                'points_per_visit': 1,
                'points_per_amount': 0,
                'bonus_birthday_points': 0,
                'upgrade_rule_type': 'points',
                'points_expiry_months': 0,
                'is_active': False
            })

        return ApiResponse.success(rule.to_dict())

    @membership_ns.doc('update_point_rules', security='Bearer')
    @salon_required
    def put(self):
        """更新集點規則"""
        data = request.get_json()

        rule = PointRule.query.filter_by(salon_id=g.salon_id).first()

        if not rule:
            rule = PointRule(salon_id=g.salon_id)
            db.session.add(rule)

        if 'points_per_visit' in data:
            rule.points_per_visit = data['points_per_visit']
        if 'points_per_amount' in data:
            rule.points_per_amount = data['points_per_amount']
        if 'bonus_birthday_points' in data:
            rule.bonus_birthday_points = data['bonus_birthday_points']
        if 'upgrade_rule_type' in data:
            if data['upgrade_rule_type'] not in ['points', 'spent', 'visits', 'combined']:
                raise ApiError(
                    ErrorCode.VALIDATION_ERROR,
                    '升級規則類型無效，可選: points, spent, visits, combined'
                )
            rule.upgrade_rule_type = data['upgrade_rule_type']
        if 'points_expiry_months' in data:
            rule.points_expiry_months = data['points_expiry_months']
        if 'is_active' in data:
            rule.is_active = data['is_active']

        db.session.commit()

        return ApiResponse.success(rule.to_dict(), '集點規則已更新')


# ===== 顧客點數管理 =====

@membership_ns.route('/customers/<string:customer_id>/points')
class CustomerPointsResource(Resource):
    @membership_ns.doc('get_customer_points', security='Bearer')
    @salon_required
    def get(self, customer_id):
        """取得顧客點數"""
        points = CustomerPoints.query.filter_by(
            salon_id=g.salon_id,
            customer_id=customer_id
        ).first()

        if not points:
            return ApiResponse.success({
                'customer_id': customer_id,
                'total_points': 0,
                'lifetime_points': 0,
                'used_points': 0
            })

        return ApiResponse.success(points.to_dict())

    @membership_ns.doc('adjust_customer_points', security='Bearer')
    @salon_required
    def post(self, customer_id):
        """手動調整顧客點數"""
        data = request.get_json()

        adjustment = data.get('points')
        if adjustment is None:
            raise ApiError(ErrorCode.VALIDATION_ERROR, 'points 為必填')

        description = data.get('description', '手動調整')

        # 驗證顧客存在
        customer = Customer.query.get(customer_id)
        if not customer:
            raise ApiError(ErrorCode.CUSTOMER_NOT_FOUND)

        # 取得或建立顧客點數記錄
        points = CustomerPoints.query.filter_by(
            salon_id=g.salon_id,
            customer_id=customer_id
        ).first()

        if not points:
            points = CustomerPoints(
                salon_id=g.salon_id,
                customer_id=customer_id,
                total_points=0,
                lifetime_points=0,
                used_points=0
            )
            db.session.add(points)

        # 更新點數
        current_total = points.total_points or 0
        current_lifetime = points.lifetime_points or 0
        new_total = current_total + adjustment
        if new_total < 0:
            raise ApiError(
                ErrorCode.VALIDATION_ERROR,
                f'點數不足，目前點數: {points.total_points}'
            )

        points.total_points = new_total
        if adjustment > 0:
            points.lifetime_points = current_lifetime + adjustment

        # 記錄交易
        transaction = PointTransaction(
            salon_id=g.salon_id,
            customer_id=customer_id,
            transaction_type='adjust',
            points=adjustment,
            balance_after=new_total,
            description=description,
            created_by=g.owner_id
        )
        db.session.add(transaction)

        db.session.commit()

        return ApiResponse.success({
            'customer_id': customer_id,
            'adjustment': adjustment,
            'new_balance': new_total,
            'description': description
        }, '點數已調整')


@membership_ns.route('/customers/<string:customer_id>/points/history')
class CustomerPointHistory(Resource):
    @membership_ns.doc('get_customer_point_history', security='Bearer')
    @salon_required
    def get(self, customer_id):
        """取得顧客點數交易紀錄"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        query = PointTransaction.query.filter_by(
            salon_id=g.salon_id,
            customer_id=customer_id
        ).order_by(PointTransaction.created_at.desc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        items = [tx.to_dict() for tx in pagination.items]

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


# ===== 會員統計 =====

@membership_ns.route('/stats')
class MembershipStats(Resource):
    @membership_ns.doc('get_membership_stats', security='Bearer')
    @salon_required
    def get(self):
        """取得會員等級統計"""
        tiers = MembershipTier.query.filter_by(
            salon_id=g.salon_id,
            is_active=True
        ).order_by(MembershipTier.level).all()

        stats = []
        for tier in tiers:
            count = CustomerMembership.query.filter_by(
                salon_id=g.salon_id,
                tier_id=tier.id
            ).count()
            stats.append({
                'tier_id': tier.id,
                'tier_name': tier.name,
                'level': tier.level,
                'color': tier.color,
                'member_count': count
            })

        # 計算沒有等級的顧客數
        total_with_tier = sum(s['member_count'] for s in stats)
        total_customers = CustomerStat.query.filter_by(
            salon_id=g.salon_id
        ).count()

        return ApiResponse.success({
            'tier_stats': stats,
            'total_with_tier': total_with_tier,
            'total_without_tier': max(0, total_customers - total_with_tier),
            'total_customers': total_customers
        })
