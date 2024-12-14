from flask import Flask
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from datetime import timedelta
import os
from dotenv import load_dotenv
from flasgger import Swagger

# Routes import 
from app.routes.auth_routes import auth_bp
from app.routes.job_routes import job_bp
from app.routes.application_routes import application_bp
from app.routes.bookmark_routes import bookmark_bp
from app.crawlers.saramin_crawler import SaraminCrawler
from flask_cors import CORS

# 환경변수 로드
load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)  # CORS 설정 추가

    # JWT 설정
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    jwt = JWTManager(app)

    # MongoDB 연결
    client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017'))
    db = client[os.getenv('DATABASE_NAME', 'job_portal')]
    
    # app 객체에 db 추가
    app.db = db

    # Swagger 설정
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs",
        "title": "Job Portal API",
        "openapi": "3.0.0",  # OpenAPI 버전 명시
        "uiversion": 3  # Swagger UI 버전
    }

    swagger_template = {
        "openapi": "3.0.0",
        "info": {
            "title": "Job Portal API",
            "version": "1.0.0",
            "description": "구인구직 백엔드 서버 API 문서"
        },
        "servers": [
            {
                "url": "https://113.198.66.75:13062",
                "description": "Production server"
            },
            {
                "url": "http://localhost:3000",
                "description": "Development server"
            }
        ],
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            },
            "schemas": {
                "Error": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "example": "error"},
                        "message": {"type": "string"}
                    }
                },
                "Pagination": {
                    "type": "object",
                    "properties": {
                        "currentPage": {"type": "integer"},
                        "totalPages": {"type": "integer"},
                        "totalItems": {"type": "integer"},
                        "perPage": {"type": "integer", "example": 20}
                    }
                }
            }
        },
        "security": [
            {"bearerAuth": []}
        ]
    }

    # Swagger 초기화
    swagger = Swagger(app, 
                     config=swagger_config, 
                     template=swagger_template,
                     parse=True)

    # Blueprint 등록
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(job_bp, url_prefix='/jobs')
    app.register_blueprint(application_bp, url_prefix='/applications')
    app.register_blueprint(bookmark_bp, url_prefix='/bookmarks')

    return app

def init_crawler():
    # MongoDB 연결
    client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017'))
    db = client[os.getenv('DATABASE_NAME', 'job_portal')]
    
    # 크롤러 실행
    crawler = SaraminCrawler(db)
    total_jobs = crawler.crawl()
    print(f"Total jobs collected: {total_jobs}")

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=3000)