from flask import current_app
from flask_login import current_user
from app import socketio
from app import db
from app.controllers import discount_controller
from app.models.live_stream import LiveStream
from app.models.order import Order, OrderItem, Payment
from app.models.product import Product
from app.models.revenue import Revenue
from app.services.discount_service import finalize_coupon_usage
from app.services.iamport_service import IamportService
from datetime import datetime

def create_order(products):
    if not products:
        return None, "주문할 상품이 없습니다."

    total_price = 0
    order_items = []

    for item in products:
        try:
            product = Product.query.get(item['product_id'])
        except KeyError:
            product = Product.query.get(item['id'])

        print(product)
        if not product:
            return None, f"상품 ID {item['id']}를 찾을 수 없습니다."
        if product.stock < item['quantity']:
            return None, f"상품 {product.name}의 재고가 부족합니다."
        
        product.order_count += item['quantity']
        #price = product.price * item['quantity']
        discounted_price = discount_controller.apply_discount(product, item['quantity'])
        total_price += discounted_price
        order_items.append(OrderItem(product_id=product.id, quantity=item['quantity'], price=discounted_price))

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

    # 아임포트 API 호출 대신 항상 성공으로 처리
    payment_data = {
        'status': 'paid',
        'amount': order.total_price  # 주문 금액을 그대로 사용
    }

    if payment_data['status'] == 'paid':
        if order.total_price == payment_data['amount']:
            return process_payment(order_id, 'iamport', imp_uid)
        else:
            return False, "결제 금액이 일치하지 않습니다."
    else:
        return False, "결제에 실패했습니다."
    
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
            update_stock(product.id, item.quantity)

        # 결제 완료 후 쿠폰 사용 확정
        finalize_coupon_usage(order)

        db.session.add(payment)
        db.session.commit()

        # 수익 계산 및 생성
        calculate_and_create_revenue(order)
        
        # 결제 성공 후 실시간 알림 전송
        # 현재 라이브 중인 스트림 찾기
        live_stream = LiveStream.query.filter_by(seller_id=product.seller_id, is_live=True).first()
        print(live_stream)   
            
        if live_stream:
            order_info = {
                'product_name': product.name,
                'quantity': item.quantity,
                'total_price': item.price * item.quantity
            }
            socketio.emit('order_notification', {
                'streamId': live_stream.id,
                'orderInfo': order_info
            }, room=f'stream_{live_stream.id}')
            print('Order notification emitted')

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
        # 쿠폰 사용 취소
        if order.coupon:
            order.coupon.used_count -= 1
        
        order.status = 'cancelled'
        db.session.commit()
        return True, "주문이 성공적으로 취소되었습니다."
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"주문 취소 중 오류 발생: {str(e)}")
        return False, "주문 취소 중 오류가 발생했습니다."
    
def calculate_and_create_revenue(order):
    for item in order.items:
        product = item.product
        live_stream = LiveStream.query.filter_by(seller_id=product.seller_id, is_live=True).first()
        
        if live_stream:
            amount = item.price * item.quantity
            commission_rate = 0.1  # 10% 수수료, 필요에 따라 조정 가능
            
            revenue = Revenue(
                user_id=product.seller_id,
                live_stream_id=live_stream.id,
                amount=amount,
                commission_rate=commission_rate
            )
            
            db.session.add(revenue)
    
    db.session.commit()
    
def update_stock(product_id, quantity):
    product = Product.query.get(product_id)
    product.stock -= quantity
    if product.stock <= 5:
        notify_low_stock(product)
    db.session.commit()

def notify_low_stock(product):
    socketio.emit('low_stock_alert', {
        'product_id': product.id,
        'product_name': product.name,
        'current_stock': product.stock
    }, room=f'stream_{product.live_stream_id}')