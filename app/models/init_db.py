from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from flask import current_app

def get_db():
   """데이터베이스 연결 객체 반환
   
   Returns:
       MongoDB database object
   """
   client = MongoClient(current_app.config['MONGODB_URI'])
   return client[current_app.config['DATABASE_NAME']]

def init_indexes(db):
   """데이터베이스 인덱스 초기화
   
   schemas.py에 정의된 모델 구조에 따라 필요한 인덱스를 생성합니다.
   
   Args:
       db: MongoDB database object
   """
   
   # Company 컬렉션 인덱스
   # 회사명은 유니크해야 하며, 크롤링시 중복 방지를 위해 사용
   db.companies.create_index([("name", ASCENDING)], unique=True)
   db.companies.create_index([("location", ASCENDING)])
   db.companies.create_index([("created_at", DESCENDING)])
   
   # JobPosting 컬렉션 인덱스
   # 회사ID와 공고 제목으로 복합 유니크 인덱스 생성
   db.job_postings.create_index([
       ("company_id", ASCENDING),
       ("title", ASCENDING)
   ], unique=True)
   
   # 검색 기능을 위한 텍스트 인덱스
   db.job_postings.create_index([
       ("title", TEXT),
       ("description", TEXT),
       ("sector", TEXT),
       ("tasks", TEXT),
       ("requirements", TEXT),
       ("preferred", TEXT),
       ("benefits", TEXT)
   ])
   
   # 필터링을 위한 인덱스들
   db.job_postings.create_index([("status", ASCENDING)])
   db.job_postings.create_index([("deadline", ASCENDING)])
   db.job_postings.create_index([("location", ASCENDING)])
   db.job_postings.create_index([("job_type", ASCENDING)])
   db.job_postings.create_index([("experience_level", ASCENDING)])
   db.job_postings.create_index([("education", ASCENDING)])
   db.job_postings.create_index([("skills", ASCENDING)])
   
   # 리스트 형태 필드들에 대한 개별 인덱스
   db.job_postings.create_index([("tasks", ASCENDING)])
   db.job_postings.create_index([("requirements", ASCENDING)])
   db.job_postings.create_index([("preferred", ASCENDING)])
   db.job_postings.create_index([("benefits", ASCENDING)])
   
   # 크롤링 데이터 관리를 위한 인덱스
   db.job_postings.create_index([("original_url", ASCENDING)], unique=True)
   db.job_postings.create_index([("updated_at", DESCENDING)])

def init_db():
   """데이터베이스 초기화
   
   데이터베이스 연결 및 인덱스를 초기화합니다.
   
   Returns:
       MongoDB database object
   """
   db = get_db()
   init_indexes(db)
   return db