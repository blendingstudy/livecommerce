from app import db
from datetime import datetime

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    image_url = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 판매자와의 관계 설정
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller = db.relationship('User', backref=db.backref('products', lazy=True))

    # 카테고리와의 관계 설정 (옵션)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    category = db.relationship('Category', backref=db.backref('products', lazy=True))

    def __init__(self, name, description, price, stock, seller_id, image_url=None, category_id=None):
        self.name = name
        self.description = description
        self.price = price
        self.stock = stock
        self.seller_id = seller_id
        self.image_url = image_url
        self.category_id = category_id

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

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'<Category {self.name}>'