from pymongo import ASCENDING, DESCENDING, TEXT

def init_indexes(db):
    """데이터베이스 인덱스 초기화"""
    
    # User 컬렉션 인덱스
    db.users.create_index([("email", ASCENDING)], unique=True)
    
    # JobPosting 컬렉션 인덱스
    db.job_postings.create_index([("company_id", ASCENDING)])
    db.job_postings.create_index([("status", ASCENDING)])
    db.job_postings.create_index([("title", TEXT), ("description", TEXT)])
    db.job_postings.create_index([("skills", ASCENDING)])
    db.job_postings.create_index([("deadline", ASCENDING)])
    
    # Application 컬렉션 인덱스
    db.applications.create_index([("user_id", ASCENDING), ("job_posting_id", ASCENDING)], unique=True)
    
    # Bookmark 컬렉션 인덱스
    db.bookmarks.create_index([("user_id", ASCENDING), ("job_posting_id", ASCENDING)], unique=True)
    
    # Company 컬렉션 인덱스
    db.companies.create_index([("name", TEXT)])
    
    # Skills 컬렉션 인덱스
    db.skills.create_index([("name", ASCENDING)], unique=True)
    
    # SearchHistory 컬렉션 인덱스
    db.search_history.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
    
    # CompanyReview 컬렉션 인덱스
    db.company_reviews.create_index([("company_id", ASCENDING)])
    db.company_reviews.create_index([("user_id", ASCENDING)])