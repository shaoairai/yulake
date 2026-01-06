"""
公開 API（顧客預約前台）
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from datetime import datetime, date, time, timedelta
from app import db
from app.models import (
    Salon, Service, Stylist, ServiceStylist,
    BusinessHour, BookingRule, SpecialDate,
    StylistSchedule, StylistBreak, Booking
)
from app.utils.response import ApiResponse
from app.utils.errors import ApiError, ErrorCode

public_ns = Namespace('public', description='公開 API（顧客端）')


# ===== 店家資訊 =====

@public_ns.route('/<string:code>')
class SalonInfo(Resource):
    @public_ns.doc('get_salon_info')
    def get(self, code):
        """根據 code 取得店家資訊"""
        salon = Salon.query.filter_by(code=code, is_active=True).first()
        if not salon:
            raise ApiError(ErrorCode.SALON_NOT_FOUND)

        # 取得營業時間
        business_hours = BusinessHour.query.filter_by(salon_id=salon.id).order_by(BusinessHour.day_of_week).all()

        # 取得預約規則
        booking_rule = BookingRule.query.filter_by(salon_id=salon.id).first()

        return ApiResponse.success({
            'id': salon.id,
            'code': salon.code,
            'name': salon.name,
            'address': salon.address,
            'phone': salon.phone,
            'line_id': salon.line_id,
            'ig_account': salon.ig_account,
            'website': salon.website,
            'logo_url': salon.logo_url,
            'theme_color': salon.theme_color,
            'booking_url': salon.booking_url,
            'business_hours': [{
                'day_of_week': bh.day_of_week,
                'is_open': bh.is_open,
                'open_time': bh.open_time.strftime('%H:%M') if bh.open_time else None,
                'close_time': bh.close_time.strftime('%H:%M') if bh.close_time else None
            } for bh in business_hours],
            'booking_rule': {
                'slot_interval': booking_rule.slot_interval if booking_rule else 30,
                'min_advance_hours': booking_rule.min_advance_hours if booking_rule else 2,
                'max_advance_days': booking_rule.max_advance_days if booking_rule else 30,
                'require_confirmation': booking_rule.require_confirmation if booking_rule else True
            } if booking_rule else None
        })


# ===== 服務列表 =====

@public_ns.route('/<string:code>/services')
class SalonServices(Resource):
    @public_ns.doc('get_salon_services')
    def get(self, code):
        """取得店家服務列表"""
        salon = Salon.query.filter_by(code=code, is_active=True).first()
        if not salon:
            raise ApiError(ErrorCode.SALON_NOT_FOUND)

        services = Service.query.filter_by(
            salon_id=salon.id,
            is_active=True
        ).order_by(Service.sort_order).all()

        return ApiResponse.success([{
            'id': s.id,
            'name': s.name,
            'description': s.description,
            'duration': s.duration,
            'price': s.price,
            'image_url': s.image_url
        } for s in services])


# ===== 設計師列表 =====

@public_ns.route('/<string:code>/stylists')
class SalonStylists(Resource):
    @public_ns.doc('get_salon_stylists')
    def get(self, code):
        """取得店家設計師列表"""
        salon = Salon.query.filter_by(code=code, is_active=True).first()
        if not salon:
            raise ApiError(ErrorCode.SALON_NOT_FOUND)

        # 可選：依服務篩選
        service_id = request.args.get('service_id')

        query = Stylist.query.filter_by(salon_id=salon.id, is_active=True)

        if service_id:
            # 篩選可服務該項目的設計師
            query = query.join(ServiceStylist).filter(ServiceStylist.service_id == service_id)

        stylists = query.order_by(Stylist.sort_order).all()

        return ApiResponse.success([{
            'id': st.id,
            'name': st.name,
            'style': st.style,
            'introduction': st.introduction,
            'avatar_url': st.avatar_url
        } for st in stylists])


# ===== 可用時段 =====

@public_ns.route('/<string:code>/available-slots')
class AvailableSlots(Resource):
    @public_ns.doc('get_available_slots')
    def get(self, code):
        """取得可預約時段"""
        salon = Salon.query.filter_by(code=code, is_active=True).first()
        if not salon:
            raise ApiError(ErrorCode.SALON_NOT_FOUND)

        # 必要參數
        stylist_id = request.args.get('stylist_id')
        date_str = request.args.get('date')
        service_id = request.args.get('service_id')

        if not stylist_id or not date_str or not service_id:
            raise ApiError(ErrorCode.VALIDATION_ERROR, '需要 stylist_id, date, service_id 參數')

        # 解析日期
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            raise ApiError(ErrorCode.VALIDATION_ERROR, '日期格式錯誤，請使用 YYYY-MM-DD')

        # 驗證設計師
        stylist = Stylist.query.filter_by(id=stylist_id, salon_id=salon.id, is_active=True).first()
        if not stylist:
            raise ApiError(ErrorCode.STYLIST_NOT_FOUND)

        # 驗證服務
        service = Service.query.filter_by(id=service_id, salon_id=salon.id, is_active=True).first()
        if not service:
            raise ApiError(ErrorCode.SERVICE_NOT_FOUND)

        # 取得預約規則
        booking_rule = BookingRule.query.filter_by(salon_id=salon.id).first()
        slot_interval = booking_rule.slot_interval if booking_rule else 30
        min_advance_hours = booking_rule.min_advance_hours if booking_rule else 2

        # 計算可用時段
        available_slots = calculate_available_slots(
            salon_id=salon.id,
            stylist_id=stylist_id,
            target_date=target_date,
            service_duration=service.duration,
            slot_interval=slot_interval,
            min_advance_hours=min_advance_hours
        )

        return ApiResponse.success({
            'date': date_str,
            'stylist': {
                'id': stylist.id,
                'name': stylist.name
            },
            'service': {
                'id': service.id,
                'name': service.name,
                'duration': service.duration
            },
            'slots': available_slots
        })


def calculate_available_slots(
    salon_id: str,
    stylist_id: str,
    target_date: date,
    service_duration: int,
    slot_interval: int,
    min_advance_hours: int
) -> list:
    """
    計算可用時段

    Returns:
        list: [{'start_time': '10:00', 'end_time': '11:00'}, ...]
    """
    day_of_week = target_date.weekday()  # 0=Monday, 6=Sunday
    # 轉換為我們的格式 (0=Sunday)
    day_of_week = (day_of_week + 1) % 7

    # 1. 檢查是否為特殊日期（公休）
    special_date = SpecialDate.query.filter_by(
        salon_id=salon_id,
        date=target_date
    ).first()

    if special_date and special_date.type == 'closed':
        return []  # 公休日無可用時段

    # 2. 取得營業時間
    if special_date and special_date.type == 'special_hours':
        open_time = special_date.open_time
        close_time = special_date.close_time
    else:
        business_hour = BusinessHour.query.filter_by(
            salon_id=salon_id,
            day_of_week=day_of_week
        ).first()

        if not business_hour or not business_hour.is_open:
            return []  # 當日不營業

        open_time = business_hour.open_time
        close_time = business_hour.close_time

    # 3. 取得設計師排班
    stylist_schedule = StylistSchedule.query.filter_by(
        stylist_id=stylist_id,
        day_of_week=day_of_week
    ).first()

    if not stylist_schedule or not stylist_schedule.is_working:
        return []  # 設計師當日不上班

    # 設計師工作時段
    work_start = max(open_time, stylist_schedule.start_time)
    work_end = min(close_time, stylist_schedule.end_time)

    # 4. 取得設計師休息時間
    stylist_breaks = StylistBreak.query.filter_by(
        stylist_id=stylist_id,
        date=target_date
    ).all()

    # 5. 取得已有預約
    existing_bookings = Booking.query.filter(
        Booking.stylist_id == stylist_id,
        Booking.booking_date == target_date,
        Booking.status.in_(['pending', 'confirmed'])
    ).all()

    # 6. 產生時段
    slots = []
    current_time = datetime.combine(target_date, work_start)
    end_datetime = datetime.combine(target_date, work_end)
    now = datetime.now()
    min_booking_time = now + timedelta(hours=min_advance_hours)

    while current_time + timedelta(minutes=service_duration) <= end_datetime:
        slot_start = current_time.time()
        slot_end = (current_time + timedelta(minutes=service_duration)).time()

        # 檢查是否已過最晚預約時間
        if current_time < min_booking_time:
            current_time += timedelta(minutes=slot_interval)
            continue

        # 檢查是否與休息時間衝突
        is_break = False
        for brk in stylist_breaks:
            if not (slot_end <= brk.start_time or slot_start >= brk.end_time):
                is_break = True
                break

        if is_break:
            current_time += timedelta(minutes=slot_interval)
            continue

        # 檢查是否與現有預約衝突
        is_booked = False
        for booking in existing_bookings:
            if not (slot_end <= booking.start_time or slot_start >= booking.end_time):
                is_booked = True
                break

        if not is_booked:
            slots.append({
                'start_time': slot_start.strftime('%H:%M'),
                'end_time': slot_end.strftime('%H:%M')
            })

        current_time += timedelta(minutes=slot_interval)

    return slots
