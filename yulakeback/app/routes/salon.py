"""
店家後台 API
"""
from flask import request, g
from flask_restx import Namespace, Resource, fields
from datetime import datetime, date, timedelta
from app import db
from app.models import (
    Salon, Booking, Customer, SalonCustomer, CustomerStat,
    Service, Stylist, ServiceStylist, BusinessHour, BookingRule
)
from app.utils.response import ApiResponse
from app.utils.errors import ApiError, ErrorCode
from app.utils.auth import salon_required
from app.utils.pagination import paginate, get_pagination_params

salon_ns = Namespace('salon', description='店家後台 API')


# ===== Dashboard =====

@salon_ns.route('/dashboard')
class Dashboard(Resource):
    @salon_ns.doc('get_dashboard', security='Bearer')
    @salon_required
    def get(self):
        """取得總覽數據"""
        salon_id = g.salon_id
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        last_week_start = week_start - timedelta(days=7)
        last_week_end = week_start - timedelta(days=1)

        # 本週預約數
        this_week_bookings = Booking.query.filter(
            Booking.salon_id == salon_id,
            Booking.booking_date >= week_start,
            Booking.booking_date <= week_end
        ).count()

        # 上週預約數
        last_week_bookings = Booking.query.filter(
            Booking.salon_id == salon_id,
            Booking.booking_date >= last_week_start,
            Booking.booking_date <= last_week_end
        ).count()

        # 本週爽約數
        this_week_no_shows = Booking.query.filter(
            Booking.salon_id == salon_id,
            Booking.booking_date >= week_start,
            Booking.booking_date <= week_end,
            Booking.status == 'no_show'
        ).count()

        # 上週爽約數
        last_week_no_shows = Booking.query.filter(
            Booking.salon_id == salon_id,
            Booking.booking_date >= last_week_start,
            Booking.booking_date <= last_week_end,
            Booking.status == 'no_show'
        ).count()

        # 本週新顧客數
        this_week_new_customers = SalonCustomer.query.filter(
            SalonCustomer.salon_id == salon_id,
            SalonCustomer.first_visit_at >= datetime.combine(week_start, datetime.min.time()),
            SalonCustomer.first_visit_at <= datetime.combine(week_end, datetime.max.time())
        ).count()

        # 上週新顧客數
        last_week_new_customers = SalonCustomer.query.filter(
            SalonCustomer.salon_id == salon_id,
            SalonCustomer.first_visit_at >= datetime.combine(last_week_start, datetime.min.time()),
            SalonCustomer.first_visit_at <= datetime.combine(last_week_end, datetime.max.time())
        ).count()

        # 今日預約列表
        today_bookings = Booking.query.filter(
            Booking.salon_id == salon_id,
            Booking.booking_date == today
        ).order_by(Booking.start_time).all()

        # 計算變化百分比
        def calc_change(current, previous):
            if previous == 0:
                return 100 if current > 0 else 0
            return round((current - previous) / previous * 100, 1)

        return ApiResponse.success({
            'stats': {
                'bookings': {
                    'count': this_week_bookings,
                    'change': calc_change(this_week_bookings, last_week_bookings)
                },
                'no_shows': {
                    'count': this_week_no_shows,
                    'change': calc_change(this_week_no_shows, last_week_no_shows)
                },
                'new_customers': {
                    'count': this_week_new_customers,
                    'change': calc_change(this_week_new_customers, last_week_new_customers)
                }
            },
            'today_bookings': [{
                'id': b.id,
                'customer_name': b.customer.name if b.customer else '未知',
                'service_name': b.service.name if b.service else '未知',
                'stylist_name': b.stylist.name if b.stylist else '未知',
                'start_time': b.start_time.strftime('%H:%M'),
                'end_time': b.end_time.strftime('%H:%M'),
                'status': b.status
            } for b in today_bookings]
        })


# ===== 預約管理 =====

@salon_ns.route('/bookings')
class BookingList(Resource):
    @salon_ns.doc('get_bookings', security='Bearer')
    @salon_required
    def get(self):
        """取得預約列表"""
        salon_id = g.salon_id

        # 查詢參數
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        stylist_id = request.args.get('stylist_id')
        status = request.args.get('status')

        query = Booking.query.filter_by(salon_id=salon_id)

        if date_from:
            query = query.filter(Booking.booking_date >= date_from)
        if date_to:
            query = query.filter(Booking.booking_date <= date_to)
        if stylist_id:
            query = query.filter(Booking.stylist_id == stylist_id)
        if status:
            query = query.filter(Booking.status == status)

        query = query.order_by(Booking.booking_date.desc(), Booking.start_time)

        # 分頁
        page, per_page = get_pagination_params()
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        items = [{
            'id': b.id,
            'customer': {
                'id': b.customer.id,
                'name': b.customer.name,
                'phone': b.customer.phone
            } if b.customer else None,
            'service': {
                'id': b.service.id,
                'name': b.service.name
            } if b.service else None,
            'stylist': {
                'id': b.stylist.id,
                'name': b.stylist.name
            } if b.stylist else None,
            'booking_date': b.booking_date.isoformat(),
            'start_time': b.start_time.strftime('%H:%M'),
            'end_time': b.end_time.strftime('%H:%M'),
            'status': b.status,
            'customer_note': b.customer_note,
            'salon_note': b.salon_note,
            'created_at': b.created_at.isoformat()
        } for b in pagination.items]

        return ApiResponse.paginated(items, page, per_page, pagination.total)


@salon_ns.route('/bookings/<string:booking_id>')
class BookingDetail(Resource):
    @salon_ns.doc('get_booking', security='Bearer')
    @salon_required
    def get(self, booking_id):
        """取得預約詳情"""
        booking = Booking.query.filter_by(id=booking_id, salon_id=g.salon_id).first()
        if not booking:
            raise ApiError(ErrorCode.BOOKING_NOT_FOUND)

        return ApiResponse.success({
            'id': booking.id,
            'customer': {
                'id': booking.customer.id,
                'name': booking.customer.name,
                'email': booking.customer.email,
                'phone': booking.customer.phone
            } if booking.customer else None,
            'service': {
                'id': booking.service.id,
                'name': booking.service.name,
                'duration': booking.service.duration,
                'price': booking.service.price
            } if booking.service else None,
            'stylist': {
                'id': booking.stylist.id,
                'name': booking.stylist.name
            } if booking.stylist else None,
            'booking_date': booking.booking_date.isoformat(),
            'start_time': booking.start_time.strftime('%H:%M'),
            'end_time': booking.end_time.strftime('%H:%M'),
            'status': booking.status,
            'customer_note': booking.customer_note,
            'salon_note': booking.salon_note,
            'cancelled_at': booking.cancelled_at.isoformat() if booking.cancelled_at else None,
            'cancel_reason': booking.cancel_reason,
            'created_at': booking.created_at.isoformat()
        })


@salon_ns.route('/bookings/<string:booking_id>/status')
class BookingStatus(Resource):
    @salon_ns.doc('update_booking_status', security='Bearer')
    @salon_required
    def put(self, booking_id):
        """更新預約狀態"""
        booking = Booking.query.filter_by(id=booking_id, salon_id=g.salon_id).first()
        if not booking:
            raise ApiError(ErrorCode.BOOKING_NOT_FOUND)

        data = request.get_json()
        new_status = data.get('status')
        note = data.get('note')

        valid_statuses = ['pending', 'confirmed', 'completed', 'cancelled_by_salon', 'no_show']
        if new_status not in valid_statuses:
            raise ApiError(ErrorCode.VALIDATION_ERROR, f'無效的狀態: {new_status}')

        # 更新狀態
        old_status = booking.status
        booking.status = new_status

        if note:
            booking.salon_note = note

        if new_status in ['cancelled_by_salon', 'cancelled_by_customer']:
            booking.cancelled_at = datetime.now()
            booking.cancel_reason = note

        # 更新顧客統計
        if booking.customer_id:
            stat = CustomerStat.query.filter_by(
                salon_id=g.salon_id,
                customer_id=booking.customer_id
            ).first()

            if stat:
                if new_status == 'completed' and old_status != 'completed':
                    stat.completed_bookings += 1
                    if booking.service:
                        stat.total_spent += booking.service.price or 0
                elif new_status == 'no_show' and old_status != 'no_show':
                    stat.no_show_count += 1

        db.session.commit()

        return ApiResponse.success({
            'id': booking.id,
            'status': booking.status
        }, '狀態更新成功')


# ===== 顧客管理 =====

@salon_ns.route('/customers')
class CustomerList(Resource):
    @salon_ns.doc('get_customers', security='Bearer')
    @salon_required
    def get(self):
        """取得顧客列表"""
        salon_id = g.salon_id

        # 查詢參數
        search = request.args.get('search')
        is_blacklisted = request.args.get('is_blacklisted')

        query = db.session.query(Customer, SalonCustomer, CustomerStat).join(
            SalonCustomer, (Customer.id == SalonCustomer.customer_id) & (SalonCustomer.salon_id == salon_id)
        ).outerjoin(
            CustomerStat, (Customer.id == CustomerStat.customer_id) & (CustomerStat.salon_id == salon_id)
        )

        if search:
            query = query.filter(
                (Customer.name.ilike(f'%{search}%')) |
                (Customer.phone.ilike(f'%{search}%')) |
                (Customer.email.ilike(f'%{search}%'))
            )

        if is_blacklisted == 'true':
            query = query.filter(SalonCustomer.is_blacklisted == True)
        elif is_blacklisted == 'false':
            query = query.filter(SalonCustomer.is_blacklisted == False)

        query = query.order_by(SalonCustomer.last_visit_at.desc())

        # 分頁
        page, per_page = get_pagination_params()
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        items = [{
            'id': customer.id,
            'name': customer.name,
            'email': customer.email,
            'phone': customer.phone,
            'note': salon_customer.note if salon_customer else None,
            'is_blacklisted': salon_customer.is_blacklisted if salon_customer else False,
            'first_visit_at': salon_customer.first_visit_at.isoformat() if salon_customer and salon_customer.first_visit_at else None,
            'last_visit_at': salon_customer.last_visit_at.isoformat() if salon_customer and salon_customer.last_visit_at else None,
            'stats': {
                'total_bookings': stat.total_bookings if stat else 0,
                'completed_bookings': stat.completed_bookings if stat else 0,
                'no_show_count': stat.no_show_count if stat else 0,
                'total_spent': stat.total_spent if stat else 0
            }
        } for customer, salon_customer, stat in pagination.items]

        return ApiResponse.paginated(items, page, per_page, pagination.total)


@salon_ns.route('/customers/<string:customer_id>')
class CustomerDetail(Resource):
    @salon_ns.doc('get_customer', security='Bearer')
    @salon_required
    def get(self, customer_id):
        """取得顧客詳情"""
        salon_id = g.salon_id

        customer = Customer.query.get(customer_id)
        if not customer:
            raise ApiError(ErrorCode.CUSTOMER_NOT_FOUND)

        salon_customer = SalonCustomer.query.filter_by(
            salon_id=salon_id,
            customer_id=customer_id
        ).first()

        stat = CustomerStat.query.filter_by(
            salon_id=salon_id,
            customer_id=customer_id
        ).first()

        # 預約歷史
        bookings = Booking.query.filter_by(
            salon_id=salon_id,
            customer_id=customer_id
        ).order_by(Booking.booking_date.desc()).limit(10).all()

        return ApiResponse.success({
            'id': customer.id,
            'name': customer.name,
            'email': customer.email,
            'phone': customer.phone,
            'birthday': customer.birthday.isoformat() if customer.birthday else None,
            'note': salon_customer.note if salon_customer else None,
            'is_blacklisted': salon_customer.is_blacklisted if salon_customer else False,
            'blacklist_reason': salon_customer.blacklist_reason if salon_customer else None,
            'first_visit_at': salon_customer.first_visit_at.isoformat() if salon_customer and salon_customer.first_visit_at else None,
            'last_visit_at': salon_customer.last_visit_at.isoformat() if salon_customer and salon_customer.last_visit_at else None,
            'stats': {
                'total_bookings': stat.total_bookings if stat else 0,
                'completed_bookings': stat.completed_bookings if stat else 0,
                'no_show_count': stat.no_show_count if stat else 0,
                'total_spent': stat.total_spent if stat else 0
            },
            'recent_bookings': [{
                'id': b.id,
                'service_name': b.service.name if b.service else None,
                'stylist_name': b.stylist.name if b.stylist else None,
                'booking_date': b.booking_date.isoformat(),
                'status': b.status
            } for b in bookings]
        })


@salon_ns.route('/customers/<string:customer_id>/note')
class CustomerNote(Resource):
    @salon_ns.doc('update_customer_note', security='Bearer')
    @salon_required
    def put(self, customer_id):
        """更新顧客備註"""
        salon_customer = SalonCustomer.query.filter_by(
            salon_id=g.salon_id,
            customer_id=customer_id
        ).first()

        if not salon_customer:
            raise ApiError(ErrorCode.CUSTOMER_NOT_FOUND)

        data = request.get_json()
        salon_customer.note = data.get('note', '')
        db.session.commit()

        return ApiResponse.success({'note': salon_customer.note}, '備註更新成功')


@salon_ns.route('/customers/<string:customer_id>/blacklist')
class CustomerBlacklist(Resource):
    @salon_ns.doc('add_to_blacklist', security='Bearer')
    @salon_required
    def post(self, customer_id):
        """加入黑名單"""
        salon_customer = SalonCustomer.query.filter_by(
            salon_id=g.salon_id,
            customer_id=customer_id
        ).first()

        if not salon_customer:
            raise ApiError(ErrorCode.CUSTOMER_NOT_FOUND)

        data = request.get_json() or {}
        salon_customer.is_blacklisted = True
        salon_customer.blacklist_reason = data.get('reason')
        salon_customer.blacklisted_at = datetime.now()
        db.session.commit()

        return ApiResponse.success({'is_blacklisted': True}, '已加入黑名單')

    @salon_ns.doc('remove_from_blacklist', security='Bearer')
    @salon_required
    def delete(self, customer_id):
        """解除黑名單"""
        salon_customer = SalonCustomer.query.filter_by(
            salon_id=g.salon_id,
            customer_id=customer_id
        ).first()

        if not salon_customer:
            raise ApiError(ErrorCode.CUSTOMER_NOT_FOUND)

        salon_customer.is_blacklisted = False
        salon_customer.blacklist_reason = None
        salon_customer.blacklisted_at = None
        db.session.commit()

        return ApiResponse.success({'is_blacklisted': False}, '已解除黑名單')


# ===== 服務管理 =====

@salon_ns.route('/services')
class ServiceList(Resource):
    @salon_ns.doc('get_services', security='Bearer')
    @salon_required
    def get(self):
        """取得服務列表"""
        services = Service.query.filter_by(salon_id=g.salon_id).order_by(Service.sort_order).all()

        return ApiResponse.success([{
            'id': s.id,
            'name': s.name,
            'description': s.description,
            'duration': s.duration,
            'price': s.price,
            'image_url': s.image_url,
            'sort_order': s.sort_order,
            'is_active': s.is_active,
            'stylists': [{
                'id': ss.stylist.id,
                'name': ss.stylist.name
            } for ss in s.service_stylists]
        } for s in services])

    @salon_ns.doc('create_service', security='Bearer')
    @salon_required
    def post(self):
        """新增服務"""
        data = request.get_json()

        if not data.get('name') or not data.get('duration') or data.get('price') is None:
            raise ApiError(ErrorCode.VALIDATION_ERROR, '名稱、時長和價格為必填')

        service = Service(
            salon_id=g.salon_id,
            name=data['name'],
            description=data.get('description'),
            duration=data['duration'],
            price=data['price'],
            image_url=data.get('image_url'),
            is_active=data.get('is_active', True)
        )
        db.session.add(service)
        db.session.flush()

        # 關聯設計師
        stylist_ids = data.get('stylist_ids', [])
        for stylist_id in stylist_ids:
            service_stylist = ServiceStylist(
                service_id=service.id,
                stylist_id=stylist_id
            )
            db.session.add(service_stylist)

        db.session.commit()

        return ApiResponse.created({
            'id': service.id,
            'name': service.name
        })


@salon_ns.route('/services/<string:service_id>')
class ServiceDetail(Resource):
    @salon_ns.doc('update_service', security='Bearer')
    @salon_required
    def put(self, service_id):
        """更新服務"""
        service = Service.query.filter_by(id=service_id, salon_id=g.salon_id).first()
        if not service:
            raise ApiError(ErrorCode.SERVICE_NOT_FOUND)

        data = request.get_json()

        if 'name' in data:
            service.name = data['name']
        if 'description' in data:
            service.description = data['description']
        if 'duration' in data:
            service.duration = data['duration']
        if 'price' in data:
            service.price = data['price']
        if 'image_url' in data:
            service.image_url = data['image_url']
        if 'is_active' in data:
            service.is_active = data['is_active']

        # 更新設計師關聯
        if 'stylist_ids' in data:
            ServiceStylist.query.filter_by(service_id=service_id).delete()
            for stylist_id in data['stylist_ids']:
                service_stylist = ServiceStylist(
                    service_id=service_id,
                    stylist_id=stylist_id
                )
                db.session.add(service_stylist)

        db.session.commit()

        return ApiResponse.success({'id': service.id}, '更新成功')

    @salon_ns.doc('delete_service', security='Bearer')
    @salon_required
    def delete(self, service_id):
        """刪除服務"""
        service = Service.query.filter_by(id=service_id, salon_id=g.salon_id).first()
        if not service:
            raise ApiError(ErrorCode.SERVICE_NOT_FOUND)

        # 檢查是否有進行中的預約
        pending_bookings = Booking.query.filter(
            Booking.service_id == service_id,
            Booking.status.in_(['pending', 'confirmed'])
        ).count()

        if pending_bookings > 0:
            raise ApiError(ErrorCode.VALIDATION_ERROR, f'尚有 {pending_bookings} 筆進行中的預約使用此服務')

        db.session.delete(service)
        db.session.commit()

        return ApiResponse.success(message='刪除成功')


# ===== 設計師管理 =====

@salon_ns.route('/stylists')
class StylistList(Resource):
    @salon_ns.doc('get_stylists', security='Bearer')
    @salon_required
    def get(self):
        """取得設計師列表"""
        stylists = Stylist.query.filter_by(salon_id=g.salon_id).order_by(Stylist.sort_order).all()

        return ApiResponse.success([{
            'id': st.id,
            'name': st.name,
            'style': st.style,
            'introduction': st.introduction,
            'avatar_url': st.avatar_url,
            'sort_order': st.sort_order,
            'is_active': st.is_active
        } for st in stylists])

    @salon_ns.doc('create_stylist', security='Bearer')
    @salon_required
    def post(self):
        """新增設計師"""
        data = request.get_json()

        if not data.get('name'):
            raise ApiError(ErrorCode.VALIDATION_ERROR, '姓名為必填')

        stylist = Stylist(
            salon_id=g.salon_id,
            name=data['name'],
            style=data.get('style'),
            introduction=data.get('introduction'),
            avatar_url=data.get('avatar_url'),
            is_active=data.get('is_active', True)
        )
        db.session.add(stylist)
        db.session.commit()

        return ApiResponse.created({
            'id': stylist.id,
            'name': stylist.name
        })


@salon_ns.route('/stylists/<string:stylist_id>')
class StylistDetail(Resource):
    @salon_ns.doc('update_stylist', security='Bearer')
    @salon_required
    def put(self, stylist_id):
        """更新設計師"""
        stylist = Stylist.query.filter_by(id=stylist_id, salon_id=g.salon_id).first()
        if not stylist:
            raise ApiError(ErrorCode.STYLIST_NOT_FOUND)

        data = request.get_json()

        if 'name' in data:
            stylist.name = data['name']
        if 'style' in data:
            stylist.style = data['style']
        if 'introduction' in data:
            stylist.introduction = data['introduction']
        if 'avatar_url' in data:
            stylist.avatar_url = data['avatar_url']
        if 'is_active' in data:
            stylist.is_active = data['is_active']

        db.session.commit()

        return ApiResponse.success({'id': stylist.id}, '更新成功')

    @salon_ns.doc('delete_stylist', security='Bearer')
    @salon_required
    def delete(self, stylist_id):
        """刪除設計師"""
        stylist = Stylist.query.filter_by(id=stylist_id, salon_id=g.salon_id).first()
        if not stylist:
            raise ApiError(ErrorCode.STYLIST_NOT_FOUND)

        # 檢查是否有進行中的預約
        pending_bookings = Booking.query.filter(
            Booking.stylist_id == stylist_id,
            Booking.status.in_(['pending', 'confirmed'])
        ).count()

        if pending_bookings > 0:
            raise ApiError(ErrorCode.VALIDATION_ERROR, f'尚有 {pending_bookings} 筆進行中的預約指派此設計師')

        db.session.delete(stylist)
        db.session.commit()

        return ApiResponse.success(message='刪除成功')


# ===== 日曆 API =====

@salon_ns.route('/calendar')
class Calendar(Resource):
    @salon_ns.doc('get_calendar', security='Bearer')
    @salon_required
    def get(self):
        """取得日曆資料"""
        salon_id = g.salon_id

        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        stylist_id = request.args.get('stylist_id')

        if not start_date or not end_date:
            raise ApiError(ErrorCode.VALIDATION_ERROR, '需要 start_date 和 end_date 參數')

        query = Booking.query.filter(
            Booking.salon_id == salon_id,
            Booking.booking_date >= start_date,
            Booking.booking_date <= end_date
        )

        if stylist_id:
            query = query.filter(Booking.stylist_id == stylist_id)

        bookings = query.order_by(Booking.booking_date, Booking.start_time).all()

        return ApiResponse.success([{
            'id': b.id,
            'title': f'{b.customer.name if b.customer else "未知"} - {b.service.name if b.service else "未知"}',
            'customer': {
                'id': b.customer.id,
                'name': b.customer.name
            } if b.customer else None,
            'service': {
                'id': b.service.id,
                'name': b.service.name
            } if b.service else None,
            'stylist': {
                'id': b.stylist.id,
                'name': b.stylist.name
            } if b.stylist else None,
            'date': b.booking_date.isoformat(),
            'start_time': b.start_time.strftime('%H:%M'),
            'end_time': b.end_time.strftime('%H:%M'),
            'status': b.status
        } for b in bookings])
