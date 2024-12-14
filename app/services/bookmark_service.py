from typing import Dict, Tuple, Optional, List
from datetime import datetime
from bson import ObjectId

class BookmarkService:
    def __init__(self, db):
        self.db = db
        self.ITEMS_PER_PAGE = 20

    def toggle_bookmark(self, user_id: str, job_id: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        채용공고를 북마크에 추가하거나 제거합니다.
        
        Parameters:
            user_id (str): 사용자 ID
            job_id (str): 채용공고 ID
            
        Returns:
            Tuple[bool, str, Optional[Dict]]: 성공 여부, 메시지, 북마크 데이터
        """
        try:
            # 채용공고 존재 여부와 상태를 확인합니다
            job = self.db.job_postings.find_one({
                '_id': ObjectId(job_id),
                'status': 'active'
            })
            
            if not job:
                return False, "채용공고를 찾을 수 없거나 비활성화되었습니다", None

            # 기존 북마크를 확인합니다
            existing_bookmark = self.db.bookmarks.find_one({
                'user_id': user_id,
                'job_posting_id': job_id
            })
            
            if existing_bookmark:
                # 북마크가 이미 존재하면 제거합니다
                self.db.bookmarks.delete_one({'_id': existing_bookmark['_id']})
                return True, "북마크가 성공적으로 제거되었습니다", {
                    'action': 'removed',
                    'bookmark_id': str(existing_bookmark['_id'])
                }
            else:
                # 새로운 북마크를 추가합니다
                bookmark_data = {
                    'user_id': user_id,
                    'job_posting_id': job_id,
                    'created_at': datetime.utcnow(),
                    'job_category': job.get('category'),  # 필터링을 위한 추가 정보
                    'company_id': job.get('company_id')
                }
                result = self.db.bookmarks.insert_one(bookmark_data)
                bookmark_data['_id'] = str(result.inserted_id)
                return True, "북마크가 성공적으로 추가되었습니다", {
                    'action': 'added',
                    'bookmark': bookmark_data
                }

        except Exception as e:
            return False, f"북마크 처리 중 오류가 발생했습니다: {str(e)}", None

    def get_user_bookmarks(
        self,
        user_id: str,
        page: int = 1,
        sort_by: str = 'created_at',
        sort_order: int = -1,
        category: str = None,
        company_id: str = None
    ) -> Dict:
        """
        사용자의 북마크 목록을 조회합니다.
        
        Parameters:
            user_id (str): 사용자 ID
            page (int): 페이지 번호
            sort_by (str): 정렬 기준 필드
            sort_order (int): 정렬 순서 (1: 오름차순, -1: 내림차순)
            category (str): 채용공고 카테고리 필터
            company_id (str): 회사 ID 필터
            
        Returns:
            Dict: 북마크 목록과 페이지네이션 정보
        """
        try:
            # 기본 쿼리 조건을 설정합니다
            query = {'user_id': user_id}
            
            # 필터링 조건을 추가합니다
            if category:
                query['job_category'] = category
            if company_id:
                query['company_id'] = company_id

            # 유효한 정렬 필드를 정의합니다
            valid_sort_fields = {
                'created_at': 'created_at',
                'company': 'company_id',
                'category': 'job_category'
            }
            sort_field = valid_sort_fields.get(sort_by, 'created_at')

            # 전체 아이템 수를 계산합니다
            total_items = self.db.bookmarks.count_documents(query)
            total_pages = (total_items + self.ITEMS_PER_PAGE - 1) // self.ITEMS_PER_PAGE
            
            # 페이지네이션을 적용합니다
            skip = (page - 1) * self.ITEMS_PER_PAGE
            
            # 북마크 목록을 조회합니다
            bookmarks = list(self.db.bookmarks.find(query)
                           .sort(sort_field, sort_order)
                           .skip(skip)
                           .limit(self.ITEMS_PER_PAGE))

            # 채용공고 정보를 포함시킵니다
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
                    'perPage': self.ITEMS_PER_PAGE
                },
                'filters': {
                    'category': category,
                    'company_id': company_id
                },
                'sorting': {
                    'field': sort_by,
                    'order': 'desc' if sort_order == -1 else 'asc'
                }
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f"북마크 목록 조회 중 오류가 발생했습니다: {str(e)}"
            }