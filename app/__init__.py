import socket
import ssl
import dns
from flask import Flask, render_template
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
import requests
from flask_apscheduler import APScheduler

# 데이터베이스 객체 생성
db = SQLAlchemy()
# 로그인 매니저 객체 생성
login_manager = LoginManager()
# SocketIO 객체 생성 (실시간 통신을 위해)
socketio = SocketIO()
csrf = CSRFProtect()
scheduler = APScheduler()
mail = Mail()

def create_app(config_name='development'):
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # 설정 로드
    if config_name == 'production':
        app.config.from_object('config.ProductionConfig')
    else:
        app.config.from_object('config.DevelopmentConfig')

    csrf.init_app(app)

    # 데이터베이스 초기화
    db.init_app(app)
    mail.init_app(app)
    # APScheduler 설정
    app.config['SCHEDULER_API_ENABLED'] = True
    scheduler.init_app(app)

    # 마이그레이션 설정
    Migrate(app, db)

    # 로그인 매니저 설정
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # SocketIO 초기화
    socketio.init_app(app, async_mode='eventlet', cors_allowed_origins="*")
    from app import socket_events

    # 블루프린트 등록
    from app.views import auth, product, live_stream, payment, cart, user, host, discount
    app.register_blueprint(auth.auth)
    app.register_blueprint(user.user)
    app.register_blueprint(product.product)
    app.register_blueprint(live_stream.live_stream)
    app.register_blueprint(cart.cart)
    app.register_blueprint(payment.payment)
    app.register_blueprint(host.host)
    app.register_blueprint(discount.discount)

    from app.models.user import User
    from app.models.product import Product
    from app.models.live_stream import LiveStream
    from app.models.order import Order, OrderItem
    from app.models.cart import Cart, CartItem
    from app.models.review import Review
    from app.models.revenue import Revenue
    from app.models.coupon import Coupon
    from app.models.discount import Discount

    # 사용자 로더 콜백 설정
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @app.route('/')
    def index():
        products = Product.query.limit(8).all()
        print(products)
        popular_products = Product.query.order_by(Product.popularity_score.desc()).limit(3).all()
        return render_template('index.html', products=products, popular_products=popular_products)
    
    @app.template_filter('format_currency')
    def format_currency(value):
        return f"₩{value:,.0f}"
    
    # 템플릿 필터 정의
    @app.template_filter('status_color')
    def status_color(status):
        colors = {
            'pending': 'warning',
            'paid': 'info',
            'shipped': 'primary',
            'delivered': 'success',
            'cancelled': 'danger'
        }
        return colors.get(status, 'secondary')

    @app.template_filter('status_display')
    def status_display(status):
        displays = {
            'pending': '대기 중',
            'paid': '결제 완료',
            'shipped': '배송 중',
            'delivered': '배송 완료',
            'cancelled': '취소됨'
        }
        return displays.get(status, status)

    from app import tasks

    # 스케줄러 작업 등록
    @scheduler.task('cron', id='check_upcoming_streams', minute='*')
    def scheduled_task():
        with app.app_context():
            tasks.check_upcoming_streams()

    #scheduler.start()
    
    return app