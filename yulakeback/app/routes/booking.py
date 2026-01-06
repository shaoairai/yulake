"""
預約相關 API（建立預約）
"""
from flask import request, g
from flask_restx import Namespace, Resource, fields
from datetime import datetime, date, time, timedelta
from app import db
from app.models import (
    Salon, Service, Stylist, Booking, Customer,
    SalonCustomer, CustomerStat, BookingRule,
    BusinessHour, SpecialDate, StylistSchedule, StylistBreak
)
from app.utils.response import ApiResponse
from app.utils.errors import ApiError, ErrorCode
from app.utils.auth import customer_required

booking_ns = Namespace('booking', description='預約 API')

# ===== 請求模型 =====
create_booking_model = booking_ns.model('CreateBooking', {
    'salon_code': fields.String(required=True, description='店家代碼', example='nailart'),
    'service_id': fields.String(required=True, description='服務 ID'),
    'stylist_id': fields.String(required=True, description='設計師 ID'),
    'booking_date': fields.String(required=True, description='預約日期', example='2026-01-10'),
    'start_time': fields.String(required=True, description='開始時間', example='14:00'),
    'customer_note': fields.String(description='顧客備註')
})


@booking_ns.route('')
class CreateBooking(Resource):
    @booking_ns.doc('create_booking', security='Bearer')
    @booking_ns.expect(create_booking_model)
    @customer_required
    def post(self):
        """建立預約"""
        data = request.get_json()
        customer_id = g.customer_id

        # 驗證必填欄位
        required_fields = ['salon_code', 'service_id', 'stylist_id', 'booking_date', 'start_time']
        for field in required_fields:
            if not data.get(field):
                raise ApiError(ErrorCode.VALIDATION_ERROR, f'{field} 為必填')

        # 取得店家
        salon = Salon.query.filter_by(code=data['salon_code'], is_active=True).first()
        if not salon:
            raise ApiError(ErrorCode.SALON_NOT_FOUND)

        # 取得服務
        service = Service.query.filter_by(
            id=data['service_id'],
            salon_id=salon.id,
            is_active=True
        ).first()
        if not service:
            raise ApiError(ErrorCode.SERVICE_NOT_FOUND)

        # 取得設計師
        stylist = Stylist.query.filter_by(
            id=data['stylist_id'],
            salon_id=salon.id,
            is_active=True
        ).first()
        if not stylist:
            raise ApiError(ErrorCode.STYLIST_NOT_FOUND)

        # 解析日期時間
        try:
            booking_date = datetime.strptime(data['booking_date'], '%Y-%m-%d').date()
            start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        except ValueError:
            raise ApiError(ErrorCode.VALIDATION_ERROR, '日期或時間格式錯誤')

        # 計算結束時間
        start_datetime = datetime.combine(booking_date, start_time)
        end_datetime = start_datetime + timedelta(minutes=service.duration)
        end_time = end_datetime.time()

        # 檢查顧客是否在黑名單
        salon_customer = SalonCustomer.query.filter_by(
            salon_id=salon.id,
            customer_id=customer_id
        ).first()

        if salon_customer and salon_customer.is_blacklisted:
            raise ApiError(ErrorCode.BOOKING_USER_BLACKLISTED)

        # 取得預約規則
        booking_rule = BookingRule.query.filter_by(salon_id=salon.id).first()
        min_advance_hours = booking_rule.min_advance_hours if booking_rule else 2
        max_advance_days = booking_rule.max_advance_days if booking_rule else 30

        # 檢查預約時間是否符合規則
        now = datetime.now()
        min_booking_time = now + timedelta(hours=min_advance_hours)
        max_booking_date = now.date() + timedelta(days=max_advance_days)

        if start_datetime < min_booking_time:
            raise ApiError(
                ErrorCode.BOOKING_INVALID_TIME,
                f'需提前至少 {min_advance_hours} 小時預約'
            )

        if booking_date > max_booking_date:
            raise ApiError(
                ErrorCode.BOOKING_INVALID_TIME,
                f'最多只能預約 {max_advance_days} 天內的時段'
            )

        # 檢查時段是否可用（防止併發衝突）
        if not is_slot_available(salon.id, stylist.id, booking_date, start_time, end_time):
            raise ApiError(ErrorCode.BOOKING_SLOT_UNAVAILABLE)

        # 建立預約
        booking = Booking(
            salon_id=salon.id,
            customer_id=customer_id,
            service_id=service.id,
            stylist_id=stylist.id,
            booking_date=booking_date,
            start_time=start_time,
            end_time=end_time,
            status='pending' if (booking_rule and booking_rule.require_confirmation) else 'confirmed',
            customer_note=data.get('customer_note')
        )
        db.session.add(booking)

        # 更新或建立 salon_customer 記錄
        if not salon_customer:
            salon_customer = SalonCustomer(
                salon_id=salon.id,
                customer_id=customer_id,
                first_visit_at=datetime.now()
            )
            db.session.add(salon_customer)

            # 建立顧客統計
            customer_stat = CustomerStat(
                salon_id=salon.id,
                customer_id=customer_id,
                total_bookings=1
            )
            db.session.add(customer_stat)
        else:
            # 更新統計
            stat = CustomerStat.query.filter_by(
                salon_id=salon.id,
                customer_id=customer_id
            ).first()
            if stat:
                stat.total_bookings += 1

        db.session.commit()

        return ApiResponse.created({
            'id': booking.id,
            'salon': {
                'code': salon.code,
                'name': salon.name
            },
            'service': {
                'name': service.name,
                'duration': service.duration,
                'price': service.price
            },
            'stylist': {
                'name': stylist.name
            },
            'booking_date': booking.booking_date.isoformat(),
            'start_time': booking.start_time.strftime('%H:%M'),
            'end_time': booking.end_time.strftime('%H:%M'),
            'status': booking.status
        }, '預約建立成功')


def is_slot_available(
    salon_id: str,
    stylist_id: str,
    booking_date: date,
    start_time: time,
    end_time: time
) -> bool:
    """
    檢查時段是否可用
    """
    day_of_week = (booking_date.weekday() + 1) % 7  # 轉換為 0=Sunday

    # 1. 檢查是否為公休日
    special_date = SpecialDate.query.filter_by(
        salon_id=salon_id,
        date=booking_date
    ).first()

    if special_date and special_date.type == 'closed':
        return False

    # 2. 檢查營業時間
    if special_date and special_date.type == 'special_hours':
        open_time = special_date.open_time
        close_time = special_date.close_time
    else:
        business_hour = BusinessHour.query.filter_by(
            salon_id=salon_id,
            day_of_week=day_of_week
        ).first()

        if not business_hour or not business_hour.is_open:
            return False

        open_time = business_hour.open_time
        close_time = business_hour.close_time

    # 檢查是否在營業時間內
    if start_time < open_time or end_time > close_time:
        return False

    # 3. 檢查設計師排班
    stylist_schedule = StylistSchedule.query.filter_by(
        stylist_id=stylist_id,
        day_of_week=day_of_week
    ).first()

    if not stylist_schedule or not stylist_schedule.is_working:
        return False

    if start_time < stylist_schedule.start_time or end_time > stylist_schedule.end_time:
        return False

    # 4. 檢查設計師休息時間
    stylist_breaks = StylistBreak.query.filter_by(
        stylist_id=stylist_id,
        date=booking_date
    ).all()

    for brk in stylist_breaks:
        if not (end_time <= brk.start_time or start_time >= brk.end_time):
            return False

    # 5. 檢查是否與現有預約衝突
    existing_bookings = Booking.query.filter(
        Booking.stylist_id == stylist_id,
        Booking.booking_date == booking_date,
        Booking.status.in_(['pending', 'confirmed'])
    ).all()

    for booking in existing_bookings:
        if not (end_time <= booking.start_time or start_time >= booking.end_time):
            return False

    return True
