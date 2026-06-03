"""SQLAlchemy ORM models. Import all model modules here so Alembic autogenerate sees them."""

from app.models.c_user import User, Address, UserPref, Design, CartItem  # noqa: F401
from app.models.coupon import Coupon, UserCoupon  # noqa: F401
from app.models.catalog import (  # noqa: F401
    ProductCategory,
    Product,
    ProductSku,
    PatternCategory,
    Pattern,
    Topic,
    Banner,
    FileRecord,
    CulturalElement,
    CityIp,
    CityIpItem,
    CityIpStyleWeight,
)
from app.models.order import Order, OrderItem, OrderStatusLog  # noqa: F401
from app.models.ai import ModelChannel, AiGeneration, AiPreprocessLog  # noqa: F401
from app.models.b_user import (  # noqa: F401
    AdminUser,
    Partner,
    Store,
    StoreStaff,
    Device,
    DeviceStatusLog,
)
from app.models.b_ops import QrCode, PushMessage, SystemConfig  # noqa: F401
from app.models.b_finance import (  # noqa: F401
    PayoutRecord,
    SettleRecord,
    Withdrawal,
    Reconciliation,
)
