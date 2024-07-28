from app import db
from datetime import datetime

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='reviews')
    product = db.relationship('Product', back_populates='reviews')

    def __init__(self, user_id, product_id, rating, content):
        self.user_id = user_id
        self.product_id = product_id
        self.rating = rating
        self.content = content

    def __repr__(self):
        return f'<Review {self.id} by User {self.user_id} for Product {self.product_id}>'

    @property
    def formatted_created_at(self):
        return self.created_at.strftime('%Y-%m-%d %H:%M:%S')

    @property
    def formatted_updated_at(self):
        return self.updated_at.strftime('%Y-%m-%d %H:%M:%S')

    def update(self, rating, content):
        self.rating = rating
        self.content = content
        self.updated_at = datetime.utcnow()

    @staticmethod
    def get_reviews_for_product(product_id):
        return Review.query.filter_by(product_id=product_id).order_by(Review.created_at.desc()).all()

    @staticmethod
    def get_average_rating_for_product(product_id):
        reviews = Review.query.filter_by(product_id=product_id)
        if reviews.count() > 0:
            return sum(review.rating for review in reviews) / reviews.count()
        return 0