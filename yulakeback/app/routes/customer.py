"""
顧客 API（我的預約）
"""
from flask import request, g
from flask_restx import Namespace, Resource
from datetime import datetime
from app import db
from app.models import Booking, Customer
from app.utils.response import ApiResponse
from app.utils.errors import ApiError, ErrorCode
from app.utils.auth import customer_required
from app.utils.pagination import get_pagination_params

customer_ns = Namespace('customer', description='顧客 API')


@customer_ns.route('/bookings')
class MyBookings(Resource):
    @customer_ns.doc('get_my_bookings', security='Bearer')
    @customer_required
    def get(self):
        """取得我的預約列表"""
        customer_id = g.customer_id

        # 查詢參數
        status = request.args.get('status')

        query = Booking.query.filter_by(customer_id=customer_id)

        if status:
            query = query.filter(Booking.status == status)

        query = query.order_by(Booking.booking_date.desc(), Booking.start_time.desc())

        # 分頁
        page, per_page = get_pagination_params()
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        items = [{
            'id': b.id,
            'salon': {
                'id': b.salon.id,
                'code': b.salon.code,
                'name': b.salon.name,
                'address': b.salon.address,
                'phone': b.salon.phone
            } if b.salon else None,
            'service': {
                'id': b.service.id,
                'name': b.service.name,
                'duration': b.service.duration,
                'price': b.service.price
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
            'created_at': b.created_at.isoformat()
        } for b in pagination.items]

        return ApiResponse.paginated(items, page, per_page, pagination.total)


@customer_ns.route('/bookings/<string:booking_id>')
class MyBookingDetail(Resource):
    @customer_ns.doc('get_my_booking', security='Bearer')
    @customer_required
    def get(self, booking_id):
        """取得預約詳情"""
        booking = Booking.query.filter_by(
            id=booking_id,
            customer_id=g.customer_id
        ).first()

        if not booking:
            raise ApiError(ErrorCode.BOOKING_NOT_FOUND)

        return ApiResponse.success({
            'id': booking.id,
            'salon': {
                'id': booking.salon.id,
                'code': booking.salon.code,
                'name': booking.salon.name,
                'address': booking.salon.address,
                'phone': booking.salon.phone,
                'theme_color': booking.salon.theme_color
            } if booking.salon else None,
            'service': {
                'id': booking.service.id,
                'name': booking.service.name,
                'description': booking.service.description,
                'duration': booking.service.duration,
                'price': booking.service.price
            } if booking.service else None,
            'stylist': {
                'id': booking.stylist.id,
                'name': booking.stylist.name,
                'avatar_url': booking.stylist.avatar_url
            } if booking.stylist else None,
            'booking_date': booking.booking_date.isoformat(),
            'start_time': booking.start_time.strftime('%H:%M'),
            'end_time': booking.end_time.strftime('%H:%M'),
            'status': booking.status,
            'customer_note': booking.customer_note,
            'cancelled_at': booking.cancelled_at.isoformat() if booking.cancelled_at else None,
            'cancel_reason': booking.cancel_reason,
            'created_at': booking.created_at.isoformat()
        })


@customer_ns.route('/bookings/<string:booking_id>/cancel')
class CancelMyBooking(Resource):
    @customer_ns.doc('cancel_my_booking', security='Bearer')
    @customer_required
    def put(self, booking_id):
        """取消預約"""
        booking = Booking.query.filter_by(
            id=booking_id,
            customer_id=g.customer_id
        ).first()

        if not booking:
            raise ApiError(ErrorCode.BOOKING_NOT_FOUND)

        # 檢查狀態是否可取消
        if booking.status not in ['pending', 'confirmed']:
            raise ApiError(ErrorCode.BOOKING_CANNOT_CANCEL, '此預約狀態無法取消')

        # 檢查是否已過預約時間
        booking_datetime = datetime.combine(booking.booking_date, booking.start_time)
        if booking_datetime < datetime.now():
            raise ApiError(ErrorCode.BOOKING_CANNOT_CANCEL, '預約時間已過，無法取消')

        data = request.get_json() or {}

        booking.status = 'cancelled_by_customer'
        booking.cancelled_at = datetime.now()
        booking.cancel_reason = data.get('reason')

        db.session.commit()

        return ApiResponse.success({
            'id': booking.id,
            'status': booking.status,
            'cancelled_at': booking.cancelled_at.isoformat()
        }, '預約已取消')


@customer_ns.route('/profile')
class CustomerProfile(Resource):
    @customer_ns.doc('get_profile', security='Bearer')
    @customer_required
    def get(self):
        """取得個人資料"""
        customer = Customer.query.get(g.customer_id)
        if not customer:
            raise ApiError(ErrorCode.CUSTOMER_NOT_FOUND)

        return ApiResponse.success({
            'id': customer.id,
            'name': customer.name,
            'email': customer.email,
            'phone': customer.phone,
            'birthday': customer.birthday.isoformat() if customer.birthday else None,
            'created_at': customer.created_at.isoformat()
        })

    @customer_ns.doc('update_profile', security='Bearer')
    @customer_required
    def put(self):
        """更新個人資料"""
        customer = Customer.query.get(g.customer_id)
        if not customer:
            raise ApiError(ErrorCode.CUSTOMER_NOT_FOUND)

        data = request.get_json()

        if 'name' in data:
            customer.name = data['name']
        if 'phone' in data:
            customer.phone = data['phone']
        if 'birthday' in data:
            if data['birthday']:
                try:
                    customer.birthday = datetime.strptime(data['birthday'], '%Y-%m-%d').date()
                except ValueError:
                    raise ApiError(ErrorCode.VALIDATION_ERROR, '生日格式錯誤')
            else:
                customer.birthday = None

        db.session.commit()

        return ApiResponse.success({
            'id': customer.id,
            'name': customer.name,
            'phone': customer.phone,
            'birthday': customer.birthday.isoformat() if customer.birthday else None
        }, '資料更新成功')
