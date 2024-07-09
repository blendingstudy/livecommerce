from flask import current_app
from app import db
from app.models import User, LiveStream, Product, Revenue, Order
from datetime import datetime

def get_host_profile(user_id):
    host = User.query.filter_by(id=user_id, is_seller=True).first()
    if not host:
        return None, "호스트를 찾을 수 없습니다."
    return host, None

def get_host_streams(user_id, status='all'):
    host = User.query.filter_by(id=user_id, is_seller=True).first()
    if not host:
        return None, "호스트를 찾을 수 없습니다."
    
    """ if status == 'upcoming':
        streams = LiveStream.query.filter_by(seller_id=user_id, is_live=False).filter(LiveStream.scheduled_start_time > datetime.utcnow()).order_by(LiveStream.scheduled_start_time).all()
    elif status == 'past':
        streams = LiveStream.query.filter_by(seller_id=user_id, is_live=False).filter(LiveStream.scheduled_start_time <= datetime.utcnow()).order_by(LiveStream.scheduled_start_time.desc()).all()
    elif status == 'live':
        streams = LiveStream.query.filter_by(seller_id=user_id, is_live=True).all()
    else:  # 'all'
        streams = LiveStream.query.filter_by(seller_id=user_id).order_by(LiveStream.scheduled_start_time.desc()).all() """
        
    streams = LiveStream.query.filter_by(seller_id=user_id).order_by(LiveStream.start_time.desc()).all()
    
    return streams, None

def get_host_products(user_id):
    host = User.query.filter_by(id=user_id, is_seller=True).first()
    if not host:
        return None, "호스트를 찾을 수 없습니다."
    
    products = Product.query.filter_by(seller_id=user_id).order_by(Product.created_at.desc()).all()
    return products, None

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

def get_host_orders(user_id, status='all'):
    host = User.query.filter_by(id=user_id, is_seller=True).first()
    if not host:
        return None, "호스트를 찾을 수 없습니다."
    
    query = Order.query.join(Order.items).join(Product).filter(Product.seller_id == user_id)
    
    if status != 'all':
        query = query.filter(Order.status == status)
    
    orders = query.order_by(Order.created_at.desc()).all()
    return orders, None