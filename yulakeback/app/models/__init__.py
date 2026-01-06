# Models package
from app import db

# 店家相關
from app.models.salon import (
    Salon,
    SalonOwner,
    BusinessHour,
    BookingRule,
    SpecialDate
)

# 設計師相關
from app.models.stylist import (
    Stylist,
    StylistSchedule,
    StylistBreak
)

# 服務相關
from app.models.service import (
    Service,
    ServiceStylist
)

# 顧客相關
from app.models.customer import (
    Customer,
    SalonCustomer
)

# 預約與統計
from app.models.booking import (
    Booking,
    CustomerStat
)

# 會員等級
from app.models.membership import (
    MembershipTier,
    CustomerMembership
)

# Email 行銷
from app.models.email import (
    EmailTemplate,
    EmailCampaign,
    EmailLog,
    AutoEmailRule
)

__all__ = [
    'db',
    # 店家
    'Salon',
    'SalonOwner',
    'BusinessHour',
    'BookingRule',
    'SpecialDate',
    # 設計師
    'Stylist',
    'StylistSchedule',
    'StylistBreak',
    # 服務
    'Service',
    'ServiceStylist',
    # 顧客
    'Customer',
    'SalonCustomer',
    # 預約與統計
    'Booking',
    'CustomerStat',
    # 會員等級
    'MembershipTier',
    'CustomerMembership',
    # Email 行銷
    'EmailTemplate',
    'EmailCampaign',
    'EmailLog',
    'AutoEmailRule'
]
