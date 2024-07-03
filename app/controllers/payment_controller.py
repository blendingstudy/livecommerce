from flask import current_app
from flask_login import current_user
from app import db
from app.models.order import Order, OrderItem, Payment
from app.models.product import Product
from app.services.iamport_service import IamportService
from datetime import datetime

def create_order(products):
    if not products:
        return None, "주문할 상품이 없습니다."

    total_price = 0
    order_items = []

    for item in products:
        product = Product.query.get(item['id'])
        if not product:
            return None, f"상품 ID {item['id']}를 찾을 수 없습니다."
        if product.stock < item['quantity']:
            return None, f"상품 {product.name}의 재고가 부족합니다."
        
        price = product.price * item['quantity']
        total_price += price
        order_items.append(OrderItem(product_id=product.id, quantity=item['quantity'], price=price))

    order = Order(user_id=current_user.id, total_price=total_price, status='pending')
    order.items = order_items

    try:
        db.session.add(order)
        db.session.commit()
        return order, None
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"주문 생성 중 오류 발생: {str(e)}")
        return None, "주문 생성 중 오류가 발생했습니다."

def get_order_for_checkout(order_id, user_id):
    order = Order.query.get(order_id)
    if not order:
        return None, "주문을 찾을 수 없습니다."
    if order.user_id != user_id:
        return None, "접근 권한이 없습니다."
    return order, None

def verify_payment(order_id, imp_uid, merchant_uid):
    order, error = get_order_for_checkout(order_id, current_user.id)
    if error:
        return False, error

    iamport_service = IamportService()
    try:
        payment_data = iamport_service.find_payment(imp_uid)
        print(payment_data['status'])
        if payment_data['status'] == 'paid':
            if order.total_price == payment_data['amount']:
                return process_payment(order_id, 'iamport', imp_uid)
            else:
                return False, "결제 금액이 일치하지 않습니다."
        else:
            return False, "결제에 실패했습니다."
    except Exception as e:
        current_app.logger.error(f"Payment verification error: {str(e)}")
        return False, "결제 검증 중 오류가 발생했습니다."

def process_payment(order_id, payment_method, transaction_id):
    order = Order.query.get(order_id)
    
    if not order:
        return False, "주문을 찾을 수 없습니다."

    if order.status != 'pending':
        return False, "이미 처리된 주문입니다."

    try:
        payment = Payment(
            order_id=order.id,
            amount=order.total_price,
            payment_method=payment_method,
            transaction_id=transaction_id,
            status='completed'
        )

        order.status = 'paid'
        
        # 재고 감소
        for item in order.items:
            product = item.product
            product.stock -= item.quantity

        db.session.add(payment)
        db.session.commit()
        return True, "결제가 성공적으로 처리되었습니다."
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"결제 처리 중 오류 발생: {str(e)}")
        return False, "결제 처리 중 오류가 발생했습니다."

def get_order_status(order_id):
    order = Order.query.get(order_id)
    
    if not order:
        return None, "주문을 찾을 수 없습니다."

    if order.user_id != current_user.id:
        return None, "권한이 없습니다."

    return order, None

def get_user_order_history():
    return Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()

def cancel_order(order_id):
    order = Order.query.get(order_id)
    
    if not order:
        return False, "주문을 찾을 수 없습니다."

    if order.user_id != current_user.id:
        return False, "권한이 없습니다."

    if order.status != 'pending':
        return False, "취소할 수 없는 주문 상태입니다."

    try:
        order.status = 'cancelled'
        db.session.commit()
        return True, "주문이 성공적으로 취소되었습니다."
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"주문 취소 중 오류 발생: {str(e)}")
        return False, "주문 취소 중 오류가 발생했습니다."