from app.models import Coupon, Order
from datetime import datetime

def apply_product_discount(product):
    if product.discount and product.discount.is_active:
        now = datetime.utcnow()
        if product.discount.start_date <= now <= product.discount.end_date:
            if product.discount.discount_type == 'percentage':
                return product.price * (1 - product.discount.value / 100)
            elif product.discount.discount_type == 'fixed':
                return max(product.price - product.discount.value, 0)
    return product.price

def apply_coupon_to_order(order, coupon_code):
    coupon = Coupon.query.filter_by(code=coupon_code).first()
    if not coupon or coupon.used_count >= coupon.usage_limit or datetime.utcnow() > coupon.expiration_date:
        return False, "유효하지 않거나 만료된 쿠폰입니다."
    
    if coupon.discount_type == 'percentage':
        discount_amount = order.total_price * (coupon.discount_value / 100)
    elif coupon.discount_type == 'fixed':
        discount_amount = coupon.discount_value
    
    order.discount_amount = discount_amount
    final_price = max(order.total_price - discount_amount, 0)
    #order.total_price = final_price
    print(order.total_price)
    order.coupon = coupon
    # 여기서 used_count를 증가시키지 않습니다.
    return True, "쿠폰이 성공적으로 적용되었습니다.", discount_amount, final_price

def finalize_coupon_usage(order):
    if order.coupon:
        order.coupon.used_count += 1
        return True
    return False