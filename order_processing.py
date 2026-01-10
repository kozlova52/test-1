"""
Модуль обработки заказов после рефакторинга
"""
DEFAULT_CURRENCY = "USD"
TAX_RATE = 0.21
MIN_PRICE = 0
MIN_QTY = 0
MIN_SUBTOTAL_FOR_DISCOUNT = 200
VIP_DISCOUNT_THRESHOLD = 100
MIN_TOTAL_AFTER_DISCOUNT = 0

COUPON_DISCOUNTS = {
    "SAVE10": 0.10,
    "SAVE20": {"min_subtotal": 200, "discount_rate": 0.20, "fallback_rate": 0.05},
    "VIP": {"threshold": 100, "high_discount": 50, "low_discount": 10}
}

def parse_request(request: dict):
    return (
        request.get("user_id"),
        request.get("items"),
        request.get("coupon"),
        request.get("currency")
    )

def validate_user_id(user_id):
    if user_id is None:
        raise ValueError("user_id is required")

def validate_items(items):
    if items is None:
        raise ValueError("items is required")
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    if len(items) == 0:
        raise ValueError("items must not be empty")

def validate_item(item):
    if "price" not in item or "qty" not in item:
        raise ValueError("item must have price and qty")
    if item["price"] <= MIN_PRICE:
        raise ValueError("price must be positive")
    if item["qty"] <= MIN_QTY:
        raise ValueError("qty must be positive")

def validate_request(user_id, items):
    validate_user_id(user_id)
    validate_items(items)
    for item in items:
        validate_item(item)

def calculate_subtotal(items):
    return sum(item["price"] * item["qty"] for item in items)

def calculate_discount(subtotal, coupon):
    if not coupon:
        return 0
    if coupon not in COUPON_DISCOUNTS:
        raise ValueError("unknown coupon")
    if coupon == "SAVE10":
        return int(subtotal * COUPON_DISCOUNTS["SAVE10"])
    elif coupon == "SAVE20":
        coupon_data = COUPON_DISCOUNTS["SAVE20"]
        if subtotal >= coupon_data["min_subtotal"]:
            return int(subtotal * coupon_data["discount_rate"])
        else:
            return int(subtotal * coupon_data["fallback_rate"])
    elif coupon == "VIP":
        coupon_data = COUPON_DISCOUNTS["VIP"]
        return coupon_data["high_discount"] if subtotal >= coupon_data["threshold"] else coupon_data["low_discount"]
    return 0

def calculate_tax(amount):
    return int(amount * TAX_RATE)

def generate_order_id(user_id, items_count):
    return f"{user_id}-{items_count}-X"

def process_checkout(request: dict) -> dict:
    user_id, items, coupon, currency = parse_request(request)
    validate_request(user_id, items)
    if currency is None:
        currency = DEFAULT_CURRENCY
    subtotal = calculate_subtotal(items)
    discount = calculate_discount(subtotal, coupon)
    total_after_discount = max(subtotal - discount, 0)
    tax = calculate_tax(total_after_discount)
    total = total_after_discount + tax
    order_id = generate_order_id(user_id, len(items))
    return {
        "order_id": order_id,
        "user_id": user_id,
        "currency": currency,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": total,
        "items_count": len(items),
    }
