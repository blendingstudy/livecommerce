from datetime import datetime
from flask import jsonify
from flask_login import current_user
from app import db
from app.models import Discount, Coupon
from app.models.order import Order
from app.services.discount_service import apply_coupon_to_order

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

def update_coupon(coupon_id, data):
    coupon = Coupon.query.get(coupon_id)
    if not coupon or coupon.seller_id != current_user.id:
        return jsonify({"error": "쿠폰을 찾을 수 없습니다."}), 404
    
    coupon.code = data['code']
    coupon.discount_type = data['discount_type']
    coupon.discount_value = float(data['discount_value'])
    coupon.usage_limit = int(data['usage_limit'])
    coupon.expiration_date = datetime.strptime(data['expiration_date'], '%Y-%m-%d')

    try:
        db.session.commit()
        return jsonify({"message": "쿠폰이 성공적으로 업데이트되었습니다."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

def delete_coupon(coupon_id):
    coupon = Coupon.query.get(coupon_id)
    if not coupon or coupon.seller_id != current_user.id:
        return False, "쿠폰을 찾을 수 없습니다."

    try:
        db.session.delete(coupon)
        db.session.commit()
        return True, "쿠폰이 성공적으로 삭제되었습니다."
    except Exception as e:
        db.session.rollback()
        return False, str(e)
    
def update_discount(discount_id, data):
    discount = Discount.query.get(discount_id)
    if not discount or discount.seller_id != current_user.id:
        return None

    discount.name = data['name']
    discount.description = data['description']
    discount.discount_type = data['discount_type']
    discount.value = data['value']
    discount.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
    discount.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
    discount.is_active = data['is_active']

    try:
        db.session.commit()
        return discount
    except Exception as e:
        db.session.rollback()
        return None

def delete_discount(discount_id):
    discount = Discount.query.get(discount_id)
    if not discount or discount.seller_id != current_user.id:
        return False

    try:
        db.session.delete(discount)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        return False
    
def create_discount(data):
    new_discount = Discount(
        name=data['name'],
        description=data['description'],
        discount_type=data['discount_type'],
        value=data['value'],
        start_date=datetime.strptime(data['start_date'], '%Y-%m-%d'),
        end_date=datetime.strptime(data['end_date'], '%Y-%m-%d'),
        is_active=data['is_active'],
        seller_id=data['seller_id'],
        product_id=data['product_id']
    )
    db.session.add(new_discount)
    db.session.commit()
    return new_discount

def get_product_discount(product_id):
    now = datetime.utcnow()
    return Discount.query.filter(
        Discount.product_id == product_id,
        Discount.start_date <= now,
        Discount.end_date >= now,
        Discount.is_active == True
    ).order_by(Discount.value.desc()).first()

def apply_discount(product, quantity):
    discount = get_product_discount(product.id)
    if not discount:
        return product.price * quantity

    if discount.discount_type == 'percentage':
        discounted_price = product.price * (1 - discount.value / 100)
    else:  # fixed amount
        discounted_price = max(product.price - discount.value, 0)

    return discounted_price * quantity