from app import db
from app.models import Discount, Coupon
from app.models.order import Order
from app.services.discount_service import apply_coupon_to_order

def create_discount(data):
    new_discount = Discount(**data)
    db.session.add(new_discount)
    db.session.commit()
    return new_discount

def create_coupon(data):
    new_coupon = Coupon(**data)
    db.session.add(new_coupon)
    db.session.commit()
    return new_coupon

def apply_coupon(order_id, coupon_code):
    order = Order.query.get(order_id)
    if not order:
        return False, "Order not found"
    
    success, message, discount_amount, final_price = apply_coupon_to_order(order, coupon_code)
    if success:
        db.session.commit()
    return success, message, discount_amount, final_price