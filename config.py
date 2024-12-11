import os
from datetime import timedelta

class Config:
    # Flask 앱 기본 설정
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')  # 실제 배포시에는 환경변수로 관리
    DEBUG = False
    
    # 데이터베이스 설정
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql://username:password@localhost/db_name')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT 설정
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # 페이지네이션 설정
    PER_PAGE = 20
    
    # CORS 설정
    CORS_HEADERS = 'Content-Type'
    
    # Swagger 설정
    SWAGGER = {
        'title': 'Job Search API',
        'uiversion': 3,
        'version': '1.0.0',
        'description': 'API for job search application',
        'security': [{'Bearer': []}],
        'securityDefinitions': {
            'Bearer': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description': 'JWT Authorization header using the Bearer scheme. Example: "Bearer {token}"'
            }
        }
    }

class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    
# 환경별 설정 선택
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    env = os.getenv('FLASK_ENV', 'default')
    return config[env]