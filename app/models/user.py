from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from datetime import datetime

from app.models.live_stream import LiveStream
from app.models.order import Order
from app.models.product import Product
from app.models.review import Review

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_seller = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    phone_number = db.Column(db.String(20))
    address = db.Column(db.String(200))
    profile_image = db.Column(db.String(200))  # 프로필 이미지 URL
    
    # 관계 설정
    #products = db.relationship('Product', backref='seller', lazy='dynamic')
    #orders = db.relationship('Order', backref='buyer', lazy='dynamic')
    #cart_items = db.relationship('CartItem', backref='user', lazy='dynamic')
    cart = db.relationship('Cart', back_populates='user', uselist=False)
    reviews = db.relationship('Review', back_populates='user', lazy='dynamic')
    favorite_streams = db.relationship('LiveStream', secondary='user_favorite_streams', back_populates='favorited_by')
    favorite_products = db.relationship('Product', secondary='user_favorite_products', back_populates='favorited_by')
    revenues = db.relationship('Revenue', back_populates='user', lazy='dynamic')

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

    def add_to_favorites(self, item):
        if isinstance(item, LiveStream):
            if item not in self.favorite_streams:
                self.favorite_streams.append(item)
        elif isinstance(item, Product):
            if item not in self.favorite_products:
                self.favorite_products.append(item)

    def remove_from_favorites(self, item):
        if isinstance(item, LiveStream):
            if item in self.favorite_streams:
                self.favorite_streams.remove(item)
        elif isinstance(item, Product):
            if item in self.favorite_products:
                self.favorite_products.remove(item)

    def get_purchase_history(self):
        return self.orders.order_by(Order.created_at.desc()).all()

    def get_reviews(self):
        return self.reviews.order_by(Review.created_at.desc()).all()

# 중간 테이블: 사용자와 좋아하는 라이브 스트림
user_favorite_streams = db.Table('user_favorite_streams',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('stream_id', db.Integer, db.ForeignKey('live_stream.id'), primary_key=True)
)

# 중간 테이블: 사용자와 좋아하는 상품
user_favorite_products = db.Table('user_favorite_products',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
)