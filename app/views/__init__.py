
from .auth import auth as auth_bp
#from .user import bp as user_bp
from .product import product as product_bp
from .live_stream import live_stream as live_stream_bp
#from .cart import bp as cart_bp
from .payment import payment as payment_bp

# 필요한 경우 추가 블루프린트를 여기에 임포트합니다.

# 모든 블루프린트를 다른 모듈에서 쉽게 임포트할 수 있도록 __all__ 리스트를 정의합니다.
__all__ = [
    'auth_bp',
    #'user_bp',
    'product_bp',
    #'live_stream_bp',
    #'cart_bp',
    #'payment_bp'
]

# 블루프린트 리스트
blueprints = [
    auth_bp,
    #user_bp,
    product_bp,
    #live_stream_bp,
    #cart_bp,
    #payment_bp
]