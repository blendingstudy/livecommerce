from flask import current_app
from flask_login import current_user
from app import db
from app.models.cart import Cart, CartItem
from app.models.product import Product

def get_or_create_cart():
    if current_user.is_authenticated:
        cart = Cart.query.filter_by(user_id=current_user.id).first()
        if not cart:
            cart = Cart(user_id=current_user.id)
            db.session.add(cart)
            db.session.commit()
        return cart
    return None

def add_to_cart(product_id, quantity):
    cart = get_or_create_cart()
    if not cart:
        return False, "로그인이 필요합니다."

    product = Product.query.get(product_id)
    if not product:
        return False, "상품을 찾을 수 없습니다."

    if product.stock < quantity:
        return False, "재고가 부족합니다."

    try:
        cart.add_item(product_id, quantity)
        return True, "상품이 장바구니에 추가되었습니다."
    except Exception as e:
        current_app.logger.error(f"장바구니 추가 중 오류 발생: {str(e)}")
        db.session.rollback()
        return False, "장바구니에 추가하는 중 오류가 발생했습니다."

def remove_from_cart(product_id):
    cart = get_or_create_cart()
    if not cart:
        return False, "로그인이 필요합니다."

    try:
        cart.remove_item(product_id)
        return True, "상품이 장바구니에서 제거되었습니다."
    except Exception as e:
        current_app.logger.error(f"장바구니 제거 중 오류 발생: {str(e)}")
        db.session.rollback()
        return False, "장바구니에서 제거하는 중 오류가 발생했습니다."

def update_cart_item(product_id, quantity):
    cart = get_or_create_cart()
    if not cart:
        return False, "로그인이 필요합니다."

    product = Product.query.get(product_id)
    if not product:
        return False, "상품을 찾을 수 없습니다."

    if product.stock < quantity:
        return False, "재고가 부족합니다."

    try:
        cart.update_item_quantity(product_id, quantity)
        return True, "장바구니가 업데이트되었습니다."
    except Exception as e:
        current_app.logger.error(f"장바구니 업데이트 중 오류 발생: {str(e)}")
        db.session.rollback()
        return False, "장바구니 업데이트 중 오류가 발생했습니다."

def clear_cart():
    cart = get_or_create_cart()
    if not cart:
        return False, "로그인이 필요합니다."

    try:
        cart.clear()
        return True, "장바구니가 비워졌습니다."
    except Exception as e:
        current_app.logger.error(f"장바구니 비우기 중 오류 발생: {str(e)}")
        db.session.rollback()
        return False, "장바구니를 비우는 중 오류가 발생했습니다."

def get_cart_items():
    cart = get_or_create_cart()
    if not cart:
        return []
    cart_items = []
    
    for item in cart.items:
        product = Product.query.get(item.product_id)
        cart_items.append({
            'id': item.id,
            'product_id': item.product_id,
            'product_name': product.name,
            'price': product.price,
            'quantity': item.quantity,
            'subtotal': item.quantity * product.price,
            'product': product  # 전체 product 객체를 추가
        })
    
    return cart_items

def get_cart_total():
    cart = get_or_create_cart()
    if not cart:
        return 0

    return cart.get_total_price()