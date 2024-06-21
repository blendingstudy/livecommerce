# app/controllers/__init__.py

from .auth_controller import register_user, login_user, logout_user
from .user_controller import get_user_profile, update_user_profile
from .product_controller import create_product, get_product, update_product, delete_product
from .live_stream_controller import create_live_stream, start_live_stream, end_live_stream, join_live_stream
from .cart_controller import add_to_cart, remove_from_cart, get_cart
from .payment_controller import create_order, process_payment

# 필요한 경우 추가 컨트롤러 함수를 여기에 임포트합니다.

# 모든 컨트롤러 함수를 다른 모듈에서 쉽게 임포트할 수 있도록 __all__ 리스트를 정의합니다.
__all__ = [
    # Auth
    'register_user', 'login_user', 'logout_user',
    
    # User
    'get_user_profile', 'update_user_profile',
    
    # Product
    'create_product', 'get_product', 'update_product', 'delete_product',
    
    # Live Stream
    'create_live_stream', 'start_live_stream', 'end_live_stream', 'join_live_stream',
    
    # Cart
    'add_to_cart', 'remove_from_cart', 'get_cart',
    
    # Payment
    'create_order', 'process_payment'
]

# 추가적인 초기화가 필요한 경우 여기에 함수를 정의할 수 있습니다.
def init_app(app):
    """
    애플리케이션에 컨트롤러 관련 설정을 초기화합니다.
    현재는 특별한 초기화가 필요 없지만, 필요시 이 함수를 확장할 수 있습니다.
    """
    pass