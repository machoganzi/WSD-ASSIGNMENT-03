from datetime import datetime
from typing import Dict, Optional, Tuple
from bson import ObjectId
from ..utils.auth_utils import AuthUtils

class AuthService:
    def __init__(self, db):
        self.db = db
        self.auth_utils = AuthUtils()

    def register(self, user_data: Dict) -> Tuple[bool, str, Optional[Dict]]:
        """사용자 등록"""
        try:
            # 이메일 검증
            if not self.auth_utils.validate_email(user_data['email']):
                return False, "Invalid email format", None

            # 비밀번호 검증
            if not self.auth_utils.validate_password(user_data['password']):
                return False, "Invalid password format", None

            # 이메일 중복 확인
            if self.db.users.find_one({'email': user_data['email']}):
                return False, "Email already exists", None

            # 비밀번호 인코딩
            user_data['password'] = self.auth_utils.encode_password(user_data['password'])
            
            # 생성 시간 추가
            user_data['created_at'] = datetime.utcnow()
            user_data['updated_at'] = datetime.utcnow()
            user_data['is_active'] = True

            # 사용자 저장
            result = self.db.users.insert_one(user_data)
            user_data['_id'] = str(result.inserted_id)
            
            return True, "User registered successfully", user_data

        except Exception as e:
            return False, str(e), None

    def login(self, email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """사용자 로그인"""
        try:
            # 사용자 조회
            user = self.db.users.find_one({'email': email})
            if not user:
                return False, "Invalid email or password", None

            # 비밀번호 검증
            if not self.auth_utils.verify_password(password, user['password']):
                return False, "Invalid email or password", None

            # 계정 활성화 상태 확인
            if not user.get('is_active', True):
                return False, "Account is deactivated", None

            # 토큰 생성
            tokens = self.auth_utils.create_tokens(str(user['_id']))
            
            return True, "Login successful", {
                'user_id': str(user['_id']),
                'email': user['email'],
                'tokens': tokens
            }

        except Exception as e:
            return False, str(e), None

    def update_profile(self, user_id: str, update_data: Dict) -> Tuple[bool, str, Optional[Dict]]:
        """프로필 업데이트"""
        try:
            # 비밀번호 변경 처리
            if 'password' in update_data:
                if not self.auth_utils.validate_password(update_data['password']):
                    return False, "Invalid password format", None
                update_data['password'] = self.auth_utils.encode_password(update_data['password'])

            # 이메일 변경 처리
            if 'email' in update_data:
                if not self.auth_utils.validate_email(update_data['email']):
                    return False, "Invalid email format", None
                # 이메일 중복 확인
                existing_user = self.db.users.find_one({'email': update_data['email']})
                if existing_user and str(existing_user['_id']) != user_id:
                    return False, "Email already exists", None

            update_data['updated_at'] = datetime.utcnow()

            # 프로필 업데이트
            result = self.db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )

            if result.modified_count:
                updated_user = self.db.users.find_one({'_id': ObjectId(user_id)})
                updated_user['_id'] = str(updated_user['_id'])
                return True, "Profile updated successfully", updated_user

            return False, "No changes made", None

        except Exception as e:
            return False, str(e), None