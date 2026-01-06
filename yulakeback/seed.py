"""
種子資料腳本 - 初始化測試資料

⚠️  警告：此腳本僅供「全新空資料庫」初始化使用！
⚠️  已有資料的資料庫執行此腳本會被安全機制阻擋。
⚠️  若需強制重建，請使用 --force 參數（會刪除所有資料！）

執行方式:
  python seed.py          # 僅在空資料庫時執行
  python seed.py --force  # 強制重建（危險！會刪除所有資料）
"""
import os
import sys
from datetime import datetime, time, date, timedelta
from werkzeug.security import generate_password_hash

# 設置環境變數
os.environ.setdefault('DATABASE_URL', 'postgresql://yulake:yulake@localhost:5432/yulake')

from app import create_app, db
from app.models import (
    Salon, SalonOwner, BusinessHour, BookingRule, SpecialDate,
    Stylist, StylistSchedule, StylistBreak,
    Service, ServiceStylist,
    Customer, SalonCustomer,
    Booking, CustomerStat,
    MembershipTier, CustomerMembership,
    EmailTemplate, AutoEmailRule
)


def check_database_has_data():
    """檢查資料庫是否已有資料"""
    # 檢查關鍵表是否有資料
    salon_count = Salon.query.count()
    customer_count = Customer.query.count()
    booking_count = Booking.query.count()
    return salon_count > 0 or customer_count > 0 or booking_count > 0


def seed_data(force=False):
    """
    建立測試資料

    Args:
        force: 若為 True，則強制重建資料庫（危險！）
    """
    app = create_app()

    with app.app_context():
        # ===== 安全檢查：防止誤刪現有資料 =====
        has_data = check_database_has_data()

        if has_data and not force:
            print("\n" + "=" * 60)
            print("❌ 安全檢查失敗：資料庫已有資料！")
            print("=" * 60)
            print("\n為保護現有資料，種子資料腳本已終止。")
            print("\n若您確定要刪除所有資料並重建，請使用：")
            print("  python seed.py --force")
            print("\n⚠️  警告：--force 會刪除所有現有資料，包括：")
            print("  - 所有店家資料")
            print("  - 所有顧客資料")
            print("  - 所有預約紀錄")
            print("  - 所有其他業務資料")
            print("\n此操作無法復原！\n")
            sys.exit(1)

        if has_data and force:
            print("\n" + "=" * 60)
            print("⚠️  警告：即將刪除所有資料！")
            print("=" * 60)
            print("\n偵測到 --force 參數，將清空並重建資料庫...")
            print("清空現有資料...")
            db.drop_all()
            db.create_all()
        else:
            print("\n偵測到空資料庫，開始初始化...")

        print("建立店家資料...")
        # ===== 建立店家 =====
        salon = Salon(
            id='salon_001',
            code='nailart',
            name='花漾美甲工作室',
            address='台北市大安區忠孝東路四段100號3樓',
            phone='02-2771-1234',
            line_id='@nailart',
            ig_account='nailart_studio',
            theme_color='#3F7C6A',
            is_active=True
        )
        db.session.add(salon)

        # ===== 建立店家管理員 =====
        print("建立店家管理員...")
        owner = SalonOwner(
            id='owner_001',
            salon_id='salon_001',
            name='林小美',
            email='admin@nailart.com',
            password_hash=generate_password_hash('password123'),
            phone='0912-345-678',
            role='owner',
            is_active=True
        )
        db.session.add(owner)

        # ===== 建立營業時間 =====
        print("建立營業時間...")
        for day in range(7):
            is_open = day not in [0]  # 週日公休
            bh = BusinessHour(
                salon_id='salon_001',
                day_of_week=day,
                is_open=is_open,
                open_time=time(10, 0) if is_open else None,
                close_time=time(21, 0) if is_open else None
            )
            db.session.add(bh)

        # ===== 建立預約規則 =====
        print("建立預約規則...")
        rule = BookingRule(
            salon_id='salon_001',
            slot_interval=30,
            min_advance_hours=2,
            max_advance_days=30,
            require_confirmation=True
        )
        db.session.add(rule)

        # ===== 建立特殊日期 =====
        print("建立特殊日期...")
        # 下週一公休
        next_monday = date.today() + timedelta(days=(7 - date.today().weekday()) % 7 + 7)
        special = SpecialDate(
            salon_id='salon_001',
            date=next_monday,
            type='closed',
            reason='員工旅遊'
        )
        db.session.add(special)

        # ===== 建立設計師 =====
        print("建立設計師...")
        stylists_data = [
            {
                'id': 'stylist_001',
                'name': '小花',
                'style': '日系、韓系',
                'introduction': '擅長日系清新風格與韓系時尚設計，擁有5年經驗。',
                'sort_order': 1
            },
            {
                'id': 'stylist_002',
                'name': '小雅',
                'style': '歐美、暈染',
                'introduction': '專精暈染技術與歐美華麗風格，讓您的指尖成為藝術品。',
                'sort_order': 2
            },
            {
                'id': 'stylist_003',
                'name': '小晴',
                'style': '法式、簡約',
                'introduction': '法式優雅風格專家，簡約而不簡單的美感。',
                'sort_order': 3
            }
        ]

        for data in stylists_data:
            stylist = Stylist(
                id=data['id'],
                salon_id='salon_001',
                name=data['name'],
                style=data['style'],
                introduction=data['introduction'],
                sort_order=data['sort_order'],
                is_active=True
            )
            db.session.add(stylist)

            # 建立設計師排班（週一至週六）
            for day in range(7):
                is_working = day not in [0]  # 週日休息
                schedule = StylistSchedule(
                    stylist_id=data['id'],
                    day_of_week=day,
                    is_working=is_working,
                    start_time=time(10, 0) if is_working else None,
                    end_time=time(21, 0) if is_working else None
                )
                db.session.add(schedule)

        # ===== 建立服務項目 =====
        print("建立服務項目...")
        services_data = [
            {
                'id': 'service_001',
                'name': '基礎凝膠美甲',
                'description': '包含修型、甘皮處理、單色凝膠上色',
                'duration': 60,
                'price': 800,
                'sort_order': 1
            },
            {
                'id': 'service_002',
                'name': '凝膠光療卸甲',
                'description': '溫和卸除舊的凝膠指甲',
                'duration': 30,
                'price': 300,
                'sort_order': 2
            },
            {
                'id': 'service_003',
                'name': '手繪設計款',
                'description': '客製化手繪設計，包含基礎美甲',
                'duration': 90,
                'price': 1500,
                'sort_order': 3
            },
            {
                'id': 'service_004',
                'name': '暈染設計款',
                'description': '暈染、大理石紋等特殊效果',
                'duration': 90,
                'price': 1300,
                'sort_order': 4
            },
            {
                'id': 'service_005',
                'name': '日式美睫',
                'description': '自然款日式單根嫁接，約100根',
                'duration': 90,
                'price': 1200,
                'sort_order': 5
            }
        ]

        for data in services_data:
            service = Service(
                id=data['id'],
                salon_id='salon_001',
                name=data['name'],
                description=data['description'],
                duration=data['duration'],
                price=data['price'],
                sort_order=data['sort_order'],
                is_active=True
            )
            db.session.add(service)

        # 建立服務-設計師關聯（所有設計師都能做所有服務）
        for service_id in ['service_001', 'service_002', 'service_003', 'service_004', 'service_005']:
            for stylist_id in ['stylist_001', 'stylist_002', 'stylist_003']:
                ss = ServiceStylist(
                    service_id=service_id,
                    stylist_id=stylist_id
                )
                db.session.add(ss)

        # ===== 建立顧客 =====
        print("建立顧客...")
        customers_data = [
            {
                'id': 'customer_001',
                'name': '王小明',
                'email': 'wang@example.com',
                'phone': '0911-111-111',
                'birthday': date(1990, 3, 15)
            },
            {
                'id': 'customer_002',
                'name': '李小華',
                'email': 'lee@example.com',
                'phone': '0922-222-222',
                'birthday': date(1995, 7, 20)
            },
            {
                'id': 'customer_003',
                'name': '張小美',
                'email': 'zhang@example.com',
                'phone': '0933-333-333',
                'birthday': date(1988, 11, 5)
            }
        ]

        for data in customers_data:
            customer = Customer(
                id=data['id'],
                name=data['name'],
                email=data['email'],
                password_hash=generate_password_hash('password123'),
                phone=data['phone'],
                birthday=data['birthday'],
                is_active=True
            )
            db.session.add(customer)

            # 建立店家-顧客關聯
            sc = SalonCustomer(
                salon_id='salon_001',
                customer_id=data['id'],
                first_visit_at=datetime.now() - timedelta(days=30)
            )
            db.session.add(sc)

        # ===== 建立預約 =====
        print("建立預約...")
        today = date.today()
        bookings_data = [
            # 今日預約
            {
                'id': 'booking_001',
                'customer_id': 'customer_001',
                'service_id': 'service_001',
                'stylist_id': 'stylist_001',
                'booking_date': today,
                'start_time': time(10, 0),
                'end_time': time(11, 0),
                'status': 'confirmed'
            },
            {
                'id': 'booking_002',
                'customer_id': 'customer_002',
                'service_id': 'service_003',
                'stylist_id': 'stylist_002',
                'booking_date': today,
                'start_time': time(14, 0),
                'end_time': time(15, 30),
                'status': 'pending'
            },
            # 明日預約
            {
                'id': 'booking_003',
                'customer_id': 'customer_003',
                'service_id': 'service_004',
                'stylist_id': 'stylist_001',
                'booking_date': today + timedelta(days=1),
                'start_time': time(11, 0),
                'end_time': time(12, 30),
                'status': 'confirmed'
            },
            # 後天預約
            {
                'id': 'booking_004',
                'customer_id': 'customer_001',
                'service_id': 'service_005',
                'stylist_id': 'stylist_003',
                'booking_date': today + timedelta(days=2),
                'start_time': time(15, 0),
                'end_time': time(16, 30),
                'status': 'pending'
            },
            # 過去已完成預約
            {
                'id': 'booking_005',
                'customer_id': 'customer_001',
                'service_id': 'service_001',
                'stylist_id': 'stylist_001',
                'booking_date': today - timedelta(days=7),
                'start_time': time(10, 0),
                'end_time': time(11, 0),
                'status': 'completed'
            },
            # 過去爽約
            {
                'id': 'booking_006',
                'customer_id': 'customer_002',
                'service_id': 'service_002',
                'stylist_id': 'stylist_002',
                'booking_date': today - timedelta(days=14),
                'start_time': time(14, 0),
                'end_time': time(14, 30),
                'status': 'no_show'
            }
        ]

        for data in bookings_data:
            booking = Booking(
                id=data['id'],
                salon_id='salon_001',
                customer_id=data['customer_id'],
                service_id=data['service_id'],
                stylist_id=data['stylist_id'],
                booking_date=data['booking_date'],
                start_time=data['start_time'],
                end_time=data['end_time'],
                status=data['status']
            )
            db.session.add(booking)

        # ===== 建立顧客統計 =====
        print("建立顧客統計...")
        stats_data = [
            {'customer_id': 'customer_001', 'total_bookings': 5, 'completed_bookings': 3, 'no_show_count': 0, 'total_spent': 4100},
            {'customer_id': 'customer_002', 'total_bookings': 3, 'completed_bookings': 1, 'no_show_count': 1, 'total_spent': 1500},
            {'customer_id': 'customer_003', 'total_bookings': 2, 'completed_bookings': 1, 'no_show_count': 0, 'total_spent': 1300}
        ]

        for data in stats_data:
            stat = CustomerStat(
                salon_id='salon_001',
                customer_id=data['customer_id'],
                total_bookings=data['total_bookings'],
                completed_bookings=data['completed_bookings'],
                no_show_count=data['no_show_count'],
                total_spent=data['total_spent']
            )
            db.session.add(stat)

        # ===== 建立會員等級 =====
        print("建立會員等級...")
        tiers_data = [
            {'id': 'tier_001', 'name': '一般會員', 'min_spent': 0, 'min_visits': 0, 'discount_percent': 0, 'color': '#9E9E9E', 'sort_order': 1},
            {'id': 'tier_002', 'name': '銀卡會員', 'min_spent': 3000, 'min_visits': 3, 'discount_percent': 5, 'color': '#B0BEC5', 'sort_order': 2},
            {'id': 'tier_003', 'name': '金卡會員', 'min_spent': 10000, 'min_visits': 10, 'discount_percent': 10, 'color': '#FFD54F', 'sort_order': 3},
            {'id': 'tier_004', 'name': 'VIP會員', 'min_spent': 30000, 'min_visits': 30, 'discount_percent': 15, 'color': '#3F7C6A', 'sort_order': 4}
        ]

        for data in tiers_data:
            tier = MembershipTier(
                id=data['id'],
                salon_id='salon_001',
                name=data['name'],
                min_spent=data['min_spent'],
                min_visits=data['min_visits'],
                discount_percent=data['discount_percent'],
                color=data['color'],
                sort_order=data['sort_order'],
                is_active=True
            )
            db.session.add(tier)

        # 設定顧客會員等級
        memberships_data = [
            {'customer_id': 'customer_001', 'tier_id': 'tier_002'},  # 銀卡
            {'customer_id': 'customer_002', 'tier_id': 'tier_001'},  # 一般
            {'customer_id': 'customer_003', 'tier_id': 'tier_001'}   # 一般
        ]

        for data in memberships_data:
            membership = CustomerMembership(
                salon_id='salon_001',
                customer_id=data['customer_id'],
                tier_id=data['tier_id']
            )
            db.session.add(membership)

        # ===== 建立 Email 範本 =====
        print("建立 Email 範本...")
        templates_data = [
            {
                'id': 'template_001',
                'type': 'booking_confirm',
                'name': '預約確認通知',
                'subject': '【{{salon_name}}】您的預約已確認',
                'body': '''親愛的 {{customer_name}} 您好：

您的預約已確認！

預約資訊：
- 服務項目：{{service_name}}
- 設計師：{{stylist_name}}
- 日期時間：{{booking_date}} {{start_time}}

如需更改或取消預約，請提前 24 小時告知。

{{salon_name}} 敬上'''
            },
            {
                'id': 'template_002',
                'type': 'booking_reminder',
                'name': '預約提醒',
                'subject': '【提醒】明天 {{start_time}} 有預約',
                'body': '''親愛的 {{customer_name}} 您好：

提醒您明天有預約：

- 服務項目：{{service_name}}
- 設計師：{{stylist_name}}
- 時間：{{start_time}}

期待為您服務！

{{salon_name}} 敬上'''
            },
            {
                'id': 'template_003',
                'type': 'birthday',
                'name': '生日祝福',
                'subject': '【{{salon_name}}】生日快樂！專屬優惠送給您',
                'body': '''親愛的 {{customer_name}} 您好：

祝您生日快樂！🎂

感謝您一直以來的支持，本月預約可享有專屬生日優惠！

歡迎來店預約，讓我們為您打造美麗造型。

{{salon_name}} 敬上'''
            }
        ]

        for data in templates_data:
            template = EmailTemplate(
                id=data['id'],
                salon_id='salon_001',
                type=data['type'],
                name=data['name'],
                subject=data['subject'],
                body=data['body'],
                is_active=True
            )
            db.session.add(template)

        # ===== 建立自動發信規則 =====
        print("建立自動發信規則...")
        auto_rules_data = [
            {'type': 'booking_confirm', 'template_id': 'template_001', 'config': '{}'},
            {'type': 'booking_reminder', 'template_id': 'template_002', 'config': '{"hours_before": 24}'},
            {'type': 'birthday', 'template_id': 'template_003', 'config': '{"days_before": 3}'}
        ]

        for data in auto_rules_data:
            rule = AutoEmailRule(
                salon_id='salon_001',
                type=data['type'],
                template_id=data['template_id'],
                config=data['config'],
                is_active=True
            )
            db.session.add(rule)

        # 提交所有變更
        db.session.commit()
        print("\n✅ 種子資料建立完成！")
        print("\n測試帳號：")
        print("  店家登入: admin@nailart.com / password123")
        print("  顧客登入: wang@example.com / password123")


if __name__ == '__main__':
    # 解析命令列參數
    force_mode = '--force' in sys.argv

    if force_mode:
        # 二次確認
        print("\n" + "!" * 60)
        print("!!! 危險操作：即將刪除所有資料庫資料 !!!")
        print("!" * 60)
        confirm = input("\n請輸入 'DELETE ALL DATA' 確認刪除所有資料: ")
        if confirm != 'DELETE ALL DATA':
            print("\n操作已取消。")
            sys.exit(0)

    seed_data(force=force_mode)
