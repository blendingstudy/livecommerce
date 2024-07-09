from flask import current_app
from flask_login import current_user
from app import db
from app.models import User, Order, Review, LiveStream, Product, Revenue
from werkzeug.security import generate_password_hash

def get_user_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return None, "사용자를 찾을 수 없습니다."
    return user, None

def update_user_profile(user_id, data):
    user = User.query.get(user_id)
    if not user:
        return False, "사용자를 찾을 수 없습니다."
    
    try:
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.phone_number = data.get('phone_number', user.phone_number)
        user.address = data.get('address', user.address)
        
        if 'password' in data and data['password']:
            user.password_hash = generate_password_hash(data['password'])
        
        db.session.commit()
        return True, "프로필이 성공적으로 업데이트되었습니다."
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"프로필 업데이트 중 오류 발생: {str(e)}")
        return False, "프로필 업데이트 중 오류가 발생했습니다."

def get_purchase_history(user_id):
    user = User.query.get(user_id)
    if not user:
        return None, "사용자를 찾을 수 없습니다."
    return user.get_purchase_history(), None

def get_user_reviews(user_id):
    user = User.query.get(user_id)
    if not user:
        return None, "사용자를 찾을 수 없습니다."
    return user.get_reviews(), None

def add_to_favorites(user_id, item_type, item_id):
    user = User.query.get(user_id)
    if not user:
        return False, "사용자를 찾을 수 없습니다."
    
    if item_type == 'stream':
        item = LiveStream.query.get(item_id)
    elif item_type == 'product':
        item = Product.query.get(item_id)
    else:
        return False, "잘못된 항목 유형입니다."
    
    if not item:
        return False, "항목을 찾을 수 없습니다."
    
    try:
        user.add_to_favorites(item)
        db.session.commit()
        return True, "관심 목록에 추가되었습니다."
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"관심 목록 추가 중 오류 발생: {str(e)}")
        return False, "관심 목록 추가 중 오류가 발생했습니다."

def remove_from_favorites(user_id, item_type, item_id):
    user = User.query.get(user_id)
    if not user:
        return False, "사용자를 찾을 수 없습니다."
    
    if item_type == 'stream':
        item = LiveStream.query.get(item_id)
    elif item_type == 'product':
        item = Product.query.get(item_id)
    else:
        return False, "잘못된 항목 유형입니다."
    
    if not item:
        return False, "항목을 찾을 수 없습니다."
    
    try:
        user.remove_from_favorites(item)
        db.session.commit()
        return True, "관심 목록에서 제거되었습니다."
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"관심 목록 제거 중 오류 발생: {str(e)}")
        return False, "관심 목록 제거 중 오류가 발생했습니다."

def get_user_favorites(user_id):
    user = User.query.get(user_id)
    if not user:
        return None, "사용자를 찾을 수 없습니다."
    return {
        'streams': user.favorite_streams,
        'products': user.favorite_products
    }, None

def get_user_revenue(user_id):
    user = User.query.get(user_id)
    if not user:
        return None, "사용자를 찾을 수 없습니다."
    if not user.is_seller:
        return None, "판매자 계정만 수익 정보를 볼 수 있습니다."
    
    total_revenue = Revenue.get_total_revenue_for_user(user_id)
    recent_revenues = Revenue.get_revenues_for_user(user_id, status='paid')[:10]  # 최근 10개의 지급된 수익
    return {
        'total_revenue': total_revenue,
        'recent_revenues': recent_revenues
    }, None