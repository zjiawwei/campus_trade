# Product condition choices
PRODUCT_CONDITIONS = {
    "brand_new": "全新",
    "like_new": "几乎全新",
    "used": "使用过",
    "defective": "有瑕疵",
}

# Product status choices
PRODUCT_STATUSES = {
    "active": "在售",
    "reserved": "已预定",
    "sold": "已售出",
    "withdrawn": "已下架",
}

# Order status choices
ORDER_STATUSES = {
    "pending": "待确认",
    "confirmed": "已确认",
    "completed": "已完成",
    "cancelled": "已取消",
}

# User roles
ROLE_USER = "user"
ROLE_ADMIN = "admin"

# Rating range
RATING_MIN = 1
RATING_MAX = 5

# Pagination
ITEMS_PER_PAGE = 12

# Image upload
ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_IMAGES_PER_PRODUCT = 6
