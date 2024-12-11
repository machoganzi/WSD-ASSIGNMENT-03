from flask import Flask, send_from_directory
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from datetime import timedelta
import os
from dotenv import load_dotenv

# Routes import
from .routes.auth_routes import auth_bp
from .routes.job_routes import job_bp
from .routes.application_routes import application_bp
from .routes.bookmark_routes import bookmark_bp
from .swagger.swagger_config import swagger_ui_blueprint, SWAGGER_URL
from .crawlers.saramin_crawler import SaraminCrawler

# 환경변수 로드
load_dotenv()

def create_app():
    app = Flask(__name__)

    # JWT 설정
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    jwt = JWTManager(app)

    # MongoDB 연결
    client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017'))
    db = client[os.getenv('DATABASE_NAME', 'job_portal')]
    
    # app 객체에 db 추가
    app.db = db

    # Swagger UI 등록
    app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

    # Swagger JSON 파일을 서빙하기 위한 라우트
    @app.route('/static/swagger.json')
    def send_swagger_json():
        return send_from_directory('static', 'swagger.json')

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
    app.run(debug=True)