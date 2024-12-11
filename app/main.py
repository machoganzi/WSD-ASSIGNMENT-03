from flask import Flask
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from datetime import timedelta
import os
from dotenv import load_dotenv
from .routes.auth_routes import auth_bp
from .routes.application_routes import application_bp
from .routes.bookmark_routes import bookmark_bp
from .swagger.swagger_config import swagger_ui_blueprint, SWAGGER_URL
from pymongo import MongoClient

# MongoDB 연결
client = MongoClient('mongodb://localhost:27017')
db = client['job_portal']

# 크롤러 실행
crawler = SaraminCrawler(db)
total_jobs = crawler.crawl()
print(f"Total jobs collected: {total_jobs}")
# Swagger UI 등록
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

# Swagger JSON 파일을 서빙하기 위한 라우트
@app.route('/static/swagger.json')
def send_swagger_json():
    return send_from_directory('static', 'swagger.json')

app.register_blueprint(application_bp, url_prefix='/applications')
app.register_blueprint(bookmark_bp, url_prefix='/bookmarks')
# Blueprint 등록
app.register_blueprint(auth_bp, url_prefix='/auth')
load_dotenv()

app = Flask(__name__)

# JWT 설정
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
jwt = JWTManager(app)

# MongoDB 연결
client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017'))
db = client['job_portal']

# 라우트 등록은 나중에 추가

if __name__ == '__main__':
    app.run(debug=True)