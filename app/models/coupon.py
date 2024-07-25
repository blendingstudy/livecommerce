from app import db
from datetime import datetime

class Coupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    discount_type = db.Column(db.String(20), nullable=False)  # 'percentage' or 'fixed'
    discount_value = db.Column(db.Float, nullable=False)
    usage_limit = db.Column(db.Integer, default=1)
    used_count = db.Column(db.Integer, default=0)
    expiration_date = db.Column(db.DateTime, nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    seller = db.relationship('User', backref='coupons')

    def __repr__(self):
        return f'<Coupon {self.code}>'