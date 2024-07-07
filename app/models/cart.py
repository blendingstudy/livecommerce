from app import db
from datetime import datetime

class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='cart')
    items = db.relationship('CartItem', back_populates='cart', cascade='all, delete-orphan')

    def __init__(self, user_id):
        self.user_id = user_id

    def add_item(self, product_id, quantity):
        item = CartItem.query.filter_by(cart_id=self.id, product_id=product_id).first()
        if item:
            item.quantity += quantity
        else:
            item = CartItem(cart_id=self.id, product_id=product_id, quantity=quantity)
            self.items.append(item)
        db.session.commit()

    def remove_item(self, product_id):
        item = CartItem.query.filter_by(cart_id=self.id, product_id=product_id).first()
        if item:
            db.session.delete(item)
            db.session.commit()

    def update_item_quantity(self, product_id, quantity):
        item = CartItem.query.filter_by(cart_id=self.id, product_id=product_id).first()
        if item:
            item.quantity = quantity
            db.session.commit()

    def clear(self):
        for item in self.items:
            db.session.delete(item)
        db.session.commit()

    def get_total_price(self):
        return sum(item.get_subtotal() for item in self.items)

    def __repr__(self):
        return f'<Cart {self.id}>'

class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    cart = db.relationship('Cart', back_populates='items')
    product = db.relationship('Product')

    def get_subtotal(self):
        return self.product.price * self.quantity

    def __repr__(self):
        return f'<CartItem {self.id}>'