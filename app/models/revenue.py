from app import db
from datetime import datetime

class Revenue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    live_stream_id = db.Column(db.Integer, db.ForeignKey('live_stream.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    commission_rate = db.Column(db.Float, nullable=False, default=0.1)  # 10% 기본 수수료
    net_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, paid, cancelled

    # Relationships
    user = db.relationship('User', back_populates='revenues')
    live_stream = db.relationship('LiveStream', back_populates='revenues')

    def __init__(self, user_id, live_stream_id, amount, commission_rate=0.1):
        self.user_id = user_id
        self.live_stream_id = live_stream_id
        self.amount = amount
        self.commission_rate = commission_rate
        self.calculate_net_amount()

    def __repr__(self):
        return f'<Revenue {self.id} for User {self.user_id} from LiveStream {self.live_stream_id}>'

    def calculate_net_amount(self):
        self.net_amount = self.amount * (1 - self.commission_rate)

    def update_status(self, new_status):
        if new_status in ['pending', 'paid', 'cancelled']:
            self.status = new_status
        else:
            raise ValueError("Invalid status. Must be 'pending', 'paid', or 'cancelled'.")

    @property
    def formatted_created_at(self):
        return self.created_at.strftime('%Y-%m-%d %H:%M:%S')

    @classmethod
    def get_total_revenue_for_user(cls, user_id):
        return db.session.query(db.func.sum(cls.net_amount)).filter_by(user_id=user_id, status='paid').scalar() or 0

    @classmethod
    def get_revenues_for_user(cls, user_id, status=None):
        query = cls.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(cls.created_at.desc()).all()

    @classmethod
    def get_revenues_for_stream(cls, live_stream_id):
        return cls.query.filter_by(live_stream_id=live_stream_id).order_by(cls.created_at.desc()).all()