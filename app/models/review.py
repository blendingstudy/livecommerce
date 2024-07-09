from app import db
from datetime import datetime

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    live_stream_id = db.Column(db.Integer, db.ForeignKey('live_stream.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='reviews')
    live_stream = db.relationship('LiveStream', back_populates='reviews')

    def __init__(self, user_id, live_stream_id, rating, content):
        self.user_id = user_id
        self.live_stream_id = live_stream_id
        self.rating = rating
        self.content = content

    def __repr__(self):
        return f'<Review {self.id} by User {self.user_id} for LiveStream {self.live_stream_id}>'

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
    def get_reviews_for_stream(live_stream_id):
        return Review.query.filter_by(live_stream_id=live_stream_id).order_by(Review.created_at.desc()).all()

    @staticmethod
    def get_average_rating_for_stream(live_stream_id):
        reviews = Review.query.filter_by(live_stream_id=live_stream_id)
        if reviews.count() > 0:
            return sum(review.rating for review in reviews) / reviews.count()
        return 0