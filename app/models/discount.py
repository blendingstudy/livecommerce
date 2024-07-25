from app import db
from datetime import datetime

class Discount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    discount_type = db.Column(db.String(20), nullable=False)  # 'percentage' or 'fixed'
    value = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 추가된 부분

    seller = db.relationship('User', backref='discounts')  # 관계 추가

    def __repr__(self):
        return f'<Discount {self.name}>'