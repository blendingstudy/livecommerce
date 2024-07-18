from flask import current_app, jsonify
from sqlalchemy import func
from app import db
from app.models import User, LiveStream, Product, Revenue, Order
from datetime import datetime

from app.models.order import OrderItem

def get_host_profile(user_id):
    host = User.query.filter_by(id=user_id, is_seller=True).first()
    if not host:
        return None, "호스트를 찾을 수 없습니다."
    return host, None

def get_host_streams(user_id):
    host = User.query.filter_by(id=user_id, is_seller=True).first()
    if not host:
        return None, "호스트를 찾을 수 없습니다."
    
    now = datetime.utcnow()
    
    upcoming_streams = LiveStream.query.filter_by(seller_id=user_id, is_live=False).filter(LiveStream.start_time > now).order_by(LiveStream.start_time).all()
    print(now)
    past_streams = LiveStream.query.filter_by(seller_id=user_id, is_live=False).filter(LiveStream.start_time <= now).order_by(LiveStream.start_time.desc()).all()
    
    return {
        'upcoming': upcoming_streams,
        'past': past_streams
    }, None

def get_host_products(user_id):
    host = User.query.filter_by(id=user_id, is_seller=True).first()
    if not host:
        return None, "호스트를 찾을 수 없습니다."
    
    try:
        products_query = Product.query.filter_by(seller_id=user_id)
        return products_query, None
    except Exception as e:
        return None, str(e)

def create_product(user_id, product_data):
    host = User.query.filter_by(id=user_id, is_seller=True).first()
    if not host:
        return None, "호스트를 찾을 수 없습니다."
    
    try:
        new_product = Product(
            name=product_data['name'],
            description=product_data['description'],
            price=product_data['price'],
            stock=product_data['stock'],
            seller_id=user_id
        )
        db.session.add(new_product)
        db.session.commit()
        return new_product, None
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"제품 생성 중 오류 발생: {str(e)}")
        return None, "제품 생성 중 오류가 발생했습니다."

def update_product(user_id, product_id, product_data):
    host = User.query.filter_by(id=user_id, is_seller=True).first()
    if not host:
        return False, "호스트를 찾을 수 없습니다."
    
    product = Product.query.filter_by(id=product_id, seller_id=user_id).first()
    if not product:
        return False, "제품을 찾을 수 없습니다."
    
    try:
        product.name = product_data.get('name', product.name)
        product.description = product_data.get('description', product.description)
        product.price = product_data.get('price', product.price)
        product.stock = product_data.get('stock', product.stock)
        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"제품 업데이트 중 오류 발생: {str(e)}")
        return False, "제품 업데이트 중 오류가 발생했습니다."

def delete_product(user_id, product_id):
    host = User.query.filter_by(id=user_id, is_seller=True).first()
    if not host:
        return False, "호스트를 찾을 수 없습니다."
    
    product = Product.query.filter_by(id=product_id, seller_id=user_id).first()
    if not product:
        return False, "제품을 찾을 수 없습니다."
    
    try:
        db.session.delete(product)
        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"제품 삭제 중 오류 발생: {str(e)}")
        return False, "제품 삭제 중 오류가 발생했습니다."

def get_host_revenue(user_id, period='all'):
    host = User.query.filter_by(id=user_id, is_seller=True).first()
    if not host:
        return None, "호스트를 찾을 수 없습니다."
    
    query = Revenue.query.filter_by(user_id=user_id)
    
    if period == 'daily':
        query = query.filter(Revenue.created_at >= datetime.utcnow().date())
    elif period == 'weekly':
        query = query.filter(Revenue.created_at >= datetime.utcnow().date() - timedelta(days=7))
    elif period == 'monthly':
        query = query.filter(Revenue.created_at >= datetime.utcnow().date().replace(day=1))
    
    total_revenue = query.with_entities(db.func.sum(Revenue.net_amount)).scalar() or 0
    revenue_list = query.order_by(Revenue.created_at.desc()).all()
    
    return {'total': total_revenue, 'list': revenue_list}, None

def get_host_orders(user_id, status='all', page=1, per_page=10):
    host = User.query.filter_by(id=user_id, is_seller=True).first()
    if not host:
        return None, "호스트를 찾을 수 없습니다."
    
    query = Order.query.join(OrderItem).join(Product).filter(Product.seller_id == user_id)
    
    if status != 'all':
        query = query.filter(Order.status == status)
    
    if page and per_page:
        pagination = query.order_by(Order.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
        return pagination, None
    else:
        orders = query.order_by(Order.created_at.desc()).all()
        return orders, None

def get_stream_stats(user_id, stream_id):
    stream = LiveStream.query.filter_by(id=stream_id, seller_id=user_id).first()
    if not stream:
        return None, "스트림을 찾을 수 없습니다."

    # 총 시청자 수
    total_viewers = stream.viewer_count

    # 최대 동시 시청자 수 (이 정보를 저장하고 있다고 가정)
    max_concurrent_viewers = stream.max_concurrent_viewers if hasattr(stream, 'max_concurrent_viewers') else 0

    # 스트림 지속 시간
    duration = (stream.end_time - stream.start_time).total_seconds() / 60 if stream.end_time else 0

    # 총 매출액
    total_revenue = db.session.query(func.sum(OrderItem.price * OrderItem.quantity)).join(Order).filter(
        Order.created_at.between(stream.start_time, stream.end_time or datetime.utcnow()),
        OrderItem.product_id.in_([p.id for p in stream.products])
    ).scalar() or 0

    # 판매된 상품 정보
    sold_products = db.session.query(
        OrderItem.product_id,
        func.sum(OrderItem.quantity).label('total_quantity'),
        func.sum(OrderItem.price * OrderItem.quantity).label('total_sales')
    ).join(Order).filter(
        Order.created_at.between(stream.start_time, stream.end_time or datetime.utcnow()),
        OrderItem.product_id.in_([p.id for p in stream.products])
    ).group_by(OrderItem.product_id).all()

    sold_products_info = []
    for product_id, quantity, sales in sold_products:
        product = next((p for p in stream.products if p.id == product_id), None)
        if product:
            sold_products_info.append({
                'name': product.name,
                'quantity': quantity,
                'sales': sales
            })

    stats = {
        'stream_title': stream.title,
        'start_time': stream.start_time,
        'end_time': stream.end_time,
        'total_viewers': total_viewers,
        'max_concurrent_viewers': max_concurrent_viewers,
        'duration': duration,
        'total_revenue': total_revenue,
        'sold_products': sold_products_info
    }

    return stats, None

def update_order_status(user_id, order_id, new_status):
    host = User.query.filter_by(id=user_id, is_seller=True).first()
    if not host:
        return jsonify({'success': False, 'error': '호스트를 찾을 수 없습니다.'}), 404

    order = Order.query.get(order_id)
    if not order:
        return jsonify({'success': False, 'error': '주문을 찾을 수 없습니다.'}), 404

    # 호스트가 이 주문의 판매자인지 확인
    if not any(item.product.seller_id == user_id for item in order.items):
        return jsonify({'success': False, 'error': '이 주문을 수정할 권한이 없습니다.'}), 403

    # 상태 업데이트
    if new_status not in ['pending', 'paid', 'shipped', 'delivered', 'cancelled']:
        return jsonify({'success': False, 'error': '유효하지 않은 주문 상태입니다.'}), 400

    order.status = new_status
    db.session.commit()

    return jsonify({'success': True, 'message': '주문 상태가 성공적으로 업데이트되었습니다.'}), 200