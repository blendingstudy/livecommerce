# config.py

import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

class Config:
    """기본 설정"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://kyounje:9350/live_commerce'
    
    # 이메일 설정 (필요한 경우)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # 파일 업로드 설정
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # 페이지네이션 설정
    ITEMS_PER_PAGE = 10
    
    IAMPORT_API_KEY = '0054575041252252'
    IAMPORT_API_SECRET = '4y5PCQ5KoXFWRL7UltBruL2pvSnux1jjVFwo2L5hFqCNYH4AJGjXsCPbmGezWzwnWkHNP7Uv4ApDwb4w'
    
    SCHEDULER_TIMEZONE = "Asia/Seoul"  # 또는 해당하는 로컬 시간대

class DevelopmentConfig(Config):
    """개발 환경 설정"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://kyounje:9350@localhost/live_commerce'

class TestingConfig(Config):
    """테스트 환경 설정"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'postgresql://localhost/live_commerce_test'

class ProductionConfig(Config):
    """운영 환경 설정"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://localhost/live_commerce_prod'

# 환경 설정 딕셔너리
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}