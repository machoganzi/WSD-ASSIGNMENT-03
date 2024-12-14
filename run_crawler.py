from pymongo import MongoClient
from app.crawlers.saramin_crawler import SaraminCrawler
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        # MongoDB 연결
        client = MongoClient('mongodb://localhost:27017')
        db = client['job_portal']
        
        # 크롤러 초기화 및 실행
        crawler = SaraminCrawler(db)
        total_jobs = crawler.crawl()
        
        # 결과 확인
        jobs_count = db.job_postings.count_documents({})
        companies_count = db.companies.count_documents({})
        
        logger.info(f"크롤링 완료. 총 수집된 채용공고: {total_jobs}")
        logger.info(f"데이터베이스 내 총 채용공고 수: {jobs_count}")
        logger.info(f"데이터베이스 내 총 회사 수: {companies_count}")

    except Exception as e:
        logger.error(f"실행 중 오류 발생: {str(e)}")
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    main()