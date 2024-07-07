from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_seller = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 관계 설정
    #products = db.relationship('Product', backref='seller', lazy='dynamic')
    """orders = db.relationship('Order', backref='buyer', lazy='dynamic')
    cart_items = db.relationship('CartItem', backref='user', lazy='dynamic') """
    cart = db.relationship('Cart', back_populates='user', uselist=False)

    def __init__(self, username, email, password, is_seller=False):
        self.username = username
        self.email = email
        self.set_password(password)
        self.is_seller = is_seller

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

    # 판매자 권한 확인
    def check_is_seller(self):
        return self.is_seller

    """ # 장바구니에 상품 추가
    def add_to_cart(self, product, quantity=1):
        cart_item = CartItem.query.filter_by(user_id=self.id, product_id=product.id).first()
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(user_id=self.id, product_id=product.id, quantity=quantity)
            db.session.add(cart_item)
        db.session.commit()

    # 장바구니에서 상품 제거
    def remove_from_cart(self, product):
        cart_item = CartItem.query.filter_by(user_id=self.id, product_id=product.id).first()
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()

    # 장바구니 조회
    def get_cart(self):
        return CartItem.query.filter_by(user_id=self.id).all()

    # 주문 생성
    def create_order(self, cart_items):
        total = sum(item.product.price * item.quantity for item in cart_items)
        order = Order(user_id=self.id, total_price=total)
        for item in cart_items:
            order_item = OrderItem(order=order, product=item.product, quantity=item.quantity)
            db.session.add(order_item)
            db.session.delete(item)  # 장바구니에서 제거
        db.session.add(order)
        db.session.commit()
        return order
 """
""" # 장바구니 아이템 모델
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    
    product = db.relationship('Product')

# 주문 모델
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    items = db.relationship('OrderItem', backref='order', lazy='dynamic')

# 주문 아이템 모델
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    
    product = db.relationship('Product') """