from typing import Dict, Tuple, Optional
from datetime import datetime
from bson import ObjectId

class BookmarkService:
    def __init__(self, db):
        self.db = db
        self.ITEMS_PER_PAGE = 20

    def toggle_bookmark(self, user_id: str, job_id: str) -> Tuple[bool, str, str]:
        """북마크 추가/제거"""
        try:
            # 채용공고 존재 확인
            job = self.db.job_postings.find_one({
                '_id': ObjectId(job_id),
                'status': 'active'
            })
            
            if not job:
                return False, "채용공고를 찾을 수 없거나 비활성화되었습니다", None

            # 기존 북마크 확인
            existing_bookmark = self.db.bookmarks.find_one({
                'user_id': user_id,
                'job_posting_id': job_id
            })
            
            if existing_bookmark:
                # 북마크 제거
                self.db.bookmarks.delete_one({'_id': existing_bookmark['_id']})
                return True, "북마크가 성공적으로 제거되었습니다", "removed"
            else:
                # 북마크 추가
                bookmark_data = {
                    'user_id': user_id,
                    'job_posting_id': job_id,
                    'created_at': datetime.utcnow()
                }
                self.db.bookmarks.insert_one(bookmark_data)
                return True, "북마크가 성공적으로 추가되었습니다", "added"

        except Exception as e:
            return False, str(e), None

    def get_user_bookmarks(self, user_id: str, page: int = 1) -> Dict:
        """사용자의 북마크 목록 조회"""
        try:
            query = {'user_id': user_id}
            
            # 페이지네이션
            total_items = self.db.bookmarks.count_documents(query)
            total_pages = (total_items + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE
            
            skip = (page - 1) * self.ITEMS_PER_PAGE
            
            bookmarks = list(self.db.bookmarks.find(query)
                           .sort('created_at', -1)
                           .skip(skip)
                           .limit(self.ITEMS_PER_PAGE))

            # 북마크한 채용공고 정보 추가
            for bookmark in bookmarks:
                bookmark['_id'] = str(bookmark['_id'])
                job = self.db.job_postings.find_one({'_id': ObjectId(bookmark['job_posting_id'])})
                if job:
                    job['_id'] = str(job['_id'])
                    bookmark['job_posting'] = job

            return {
                'status': 'success',
                'data': bookmarks,
                'pagination': {
                    'currentPage': page,
                    'totalPages': total_pages,
                    'totalItems': total_items,
                    'perPage': self.ITEMS_PER_PAGE  # 추가
                }
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }