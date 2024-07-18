from pytz import timezone
from app import db
from datetime import datetime

class LiveStream(db.Model):
    def get_local_time():
        seoul_tz = timezone('Asia/Seoul')  # 또는 해당하는 로컬 시간대
        return seoul_tz.localize(datetime.now())
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_time = db.Column(db.DateTime, default=get_local_time)
    end_time = db.Column(db.DateTime, nullable=True)
    is_live = db.Column(db.Boolean, default=True)
    viewer_count = db.Column(db.Integer, default=0)
    stream_url = db.Column(db.String(200), nullable=True)
    
    # 판매자와의 관계
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller = db.relationship('User', backref=db.backref('live_streams', lazy='dynamic'))

    # 라이브 스트림과 연관된 제품들
    products = db.relationship('Product', secondary='live_stream_products', backref=db.backref('live_streams', lazy='dynamic'))
    reviews = db.relationship('Review', back_populates='live_stream', lazy='dynamic')
    revenues = db.relationship('Revenue', back_populates='live_stream', lazy='dynamic')
    favorited_by = db.relationship('User', secondary='user_favorite_streams', back_populates='favorite_streams')

    def __init__(self, title, seller_id, description=None, stream_url=None, start_time=None, is_live=True):
        self.title = title
        self.seller_id = seller_id
        self.description = description
        self.stream_url = stream_url
        self.start_time = start_time
        self.is_live = is_live

    def __repr__(self):
        return f'<LiveStream {self.title}>'

    def end_stream(self):
        self.is_live = False
        self.end_time = datetime.utcnow()

    def add_product(self, product):
        if product not in self.products:
            self.products.append(product)

    def remove_product(self, product):
        if product in self.products:
            self.products.remove(product)

    def update_viewer_count(self, count):
        self.viewer_count = count

    @property
    def duration(self):
        if self.end_time:
            return self.end_time - self.start_time
        return datetime.utcnow() - self.start_time

# 라이브 스트림과 제품 간의 다대다 관계를 위한 연결 테이블
live_stream_products = db.Table('live_stream_products',
    db.Column('live_stream_id', db.Integer, db.ForeignKey('live_stream.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True)
)

class LiveStreamComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # 라이브 스트림과의 관계
    live_stream_id = db.Column(db.Integer, db.ForeignKey('live_stream.id'), nullable=False)
    live_stream = db.relationship('LiveStream', backref=db.backref('comments', lazy='dynamic'))

    # 댓글 작성자와의 관계
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('live_stream_comments', lazy='dynamic'))

    def __init__(self, content, live_stream_id, user_id):
        self.content = content
        self.live_stream_id = live_stream_id
        self.user_id = user_id

    def __repr__(self):
        return f'<LiveStreamComment {self.id}>'