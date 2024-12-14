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
               return False, "Password must be at least 8 characters long", None

           # 이메일 중복 확인
           if self.db.users.find_one({'email': user_data['email']}):
               return False, "Email already exists", None

           # 비밀번호 Base64 인코딩
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
           
           # 로그인 정보 업데이트
           self.db.users.update_one(
               {'_id': user['_id']},
               {
                   '$set': {
                       'last_login': datetime.utcnow(),
                       'refresh_token': tokens['refresh_token']
                   }
               }
           )
           
           return True, "Login successful", {
               'user_id': str(user['_id']),
               'email': user['email'],
               'access_token': tokens['access_token'],
               'refresh_token': tokens['refresh_token'],
               'token_type': 'Bearer'
           }

       except Exception as e:
           return False, str(e), None

   def get_profile(self, user_id: str) -> Tuple[bool, str, Optional[Dict]]:
       """사용자 프로필 조회"""
       try:
           user = self.db.users.find_one({'_id': ObjectId(user_id)})
           if not user:
               return False, "User not found", None
           
           user['_id'] = str(user['_id'])
           del user['password']  # 민감한 정보 제거
           if 'refresh_token' in user:
               del user['refresh_token']  # refresh token도 제거
           return True, "Profile retrieved successfully", user
           
       except Exception as e:
           return False, str(e), None

   def update_profile(self, user_id: str, update_data: Dict) -> Tuple[bool, str, Optional[Dict]]:
       """프로필 업데이트"""
       try:
           user = self.db.users.find_one({'_id': ObjectId(user_id)})
           if not user:
               return False, "User not found", None

           # 비밀번호 변경 처리
           if 'new_password' in update_data:
               # 현재 비밀번호 확인
               if 'current_password' not in update_data:
                   return False, "Current password is required", None
               
               if not self.auth_utils.verify_password(update_data['current_password'], user['password']):
                   return False, "Current password is incorrect", None
               
               if not self.auth_utils.validate_password(update_data['new_password']):
                   return False, "Invalid new password format", None
                   
               update_data['password'] = self.auth_utils.encode_password(update_data['new_password'])
               del update_data['current_password']
               del update_data['new_password']

           # 이메일 변경 처리
           if 'email' in update_data:
               if not self.auth_utils.validate_email(update_data['email']):
                   return False, "Invalid email format", None
               existing_user = self.db.users.find_one({'email': update_data['email']})
               if existing_user and str(existing_user['_id']) != user_id:
                   return False, "Email already exists", None

           update_data['updated_at'] = datetime.utcnow()

           result = self.db.users.update_one(
               {'_id': ObjectId(user_id)},
               {'$set': update_data}
           )

           if result.modified_count:
               updated_user = self.db.users.find_one({'_id': ObjectId(user_id)})
               updated_user['_id'] = str(updated_user['_id'])
               del updated_user['password']
               if 'refresh_token' in updated_user:
                   del updated_user['refresh_token']
               return True, "Profile updated successfully", updated_user

           return False, "No changes made", None

       except Exception as e:
           return False, str(e), None

   def deactivate_account(self, user_id: str, password: str) -> Tuple[bool, str, None]:
       """회원 탈퇴 처리"""
       try:
           # 사용자 조회 및 비밀번호 확인
           user = self.db.users.find_one({'_id': ObjectId(user_id)})
           if not user or not self.auth_utils.verify_password(password, user['password']):
               return False, "Invalid password", None

           result = self.db.users.update_one(
               {'_id': ObjectId(user_id)},
               {
                   '$set': {
                       'is_active': False,
                       'deactivated_at': datetime.utcnow()
                   }
               }
           )
           
           if result.modified_count:
               return True, "Account deactivated successfully", None
           return False, "User not found", None
           
       except Exception as e:
           return False, str(e), None

   def refresh_token(self, user_id: str, refresh_token: str) -> Tuple[bool, str, Optional[Dict]]:
       """Access Token 갱신"""
       try:
           # 사용자 조회 및 refresh token 확인
           user = self.db.users.find_one({
               '_id': ObjectId(user_id),
               'refresh_token': refresh_token,
               'is_active': True
           })
           if not user:
               return False, "Invalid refresh token or inactive user", None

           # 새로운 access token 생성
           tokens = self.auth_utils.create_tokens(str(user['_id']))
           
           return True, "Token refreshed successfully", {
               'access_token': tokens['access_token'],
               'token_type': 'Bearer'
           }

       except Exception as e:
           return False, str(e), None