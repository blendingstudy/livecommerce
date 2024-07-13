from app import db
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    image_url = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    view_count = db.Column(db.Integer, default=0)
    order_count = db.Column(db.Integer, default=0)
    
    # 판매자와의 관계 설정
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller = db.relationship('User', backref=db.backref('products', lazy=True))

    # 카테고리와의 관계 설정 (옵션)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    category = db.relationship('Category', backref=db.backref('products', lazy=True))
    favorited_by = db.relationship('User', secondary='user_favorite_products', back_populates='favorite_products')

    def __init__(self, name, description, price, stock, seller_id, image_url=None, category_id=None):
        self.name = name
        self.description = description
        self.price = price
        self.stock = stock
        self.seller_id = seller_id
        self.image_url = image_url
        self.category_id = category_id
        self.view_count = 0
        self.order_count = 0

    def __repr__(self):
        return f'<Product {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'stock': self.stock,
            'image_url': self.image_url,
            'seller_id': self.seller_id,
            'category_id': self.category_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
    @hybrid_property
    def popularity_score(self):
        return self.view_count + (self.order_count * 10)  # 주문 수에 더 높은 가중치 부여

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'<Category {self.name}>'