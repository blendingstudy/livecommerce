from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_cors import CORS

# 데이터베이스 객체 생성
db = SQLAlchemy()
# 로그인 매니저 객체 생성
login_manager = LoginManager()
# SocketIO 객체 생성 (실시간 통신을 위해)
socketio = SocketIO()

def create_app(config_name='development'):
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # 설정 로드
    if config_name == 'production':
        app.config.from_object('config.ProductionConfig')
    else:
        app.config.from_object('config.DevelopmentConfig')

    # 데이터베이스 초기화
    db.init_app(app)

    # 마이그레이션 설정
    Migrate(app, db)

    # 로그인 매니저 설정
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # SocketIO 초기화
    socketio.init_app(app, async_mode='eventlet', cors_allowed_origins="*")
    from app import socket_events

    # 블루프린트 등록
    from app.views import auth, product, live_stream#, cart, payment, user
    app.register_blueprint(auth.auth)
    #app.register_blueprint(user.bp)
    app.register_blueprint(product.product)
    app.register_blueprint(live_stream.live_stream)
    #app.register_blueprint(cart.bp)
    #app.register_blueprint(payment.bp)

    from app.models.user import User
    from app.models.product import Product
    from app.models.live_stream import LiveStream

    # 사용자 로더 콜백 설정
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @app.route('/')
    def index():
        products = Product.query.limit(8).all()
        print(products)
        #popular_products = Product.query.order_by(Product.sales_count.desc()).limit(4).all()
        #return render_template('index.html'""" , products=products, popular_products=popular_products """)
        return render_template('index.html', products=products)

    return app