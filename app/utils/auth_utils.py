import base64
from flask_jwt_extended import create_access_token
from datetime import datetime, timedelta
import re

class AuthUtils:
    @staticmethod
    def encode_password(password: str) -> str:
        """비밀번호 Base64 인코딩"""
        return base64.b64encode(password.encode()).decode()

    @staticmethod
    def verify_password(input_password: str, stored_password: str) -> bool:
        """비밀번호 검증"""
        encoded_input = base64.b64encode(input_password.encode()).decode()
        return encoded_input == stored_password

    @staticmethod
    def validate_email(email: str) -> bool:
        """이메일 형식 검증"""
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_password(password: str) -> bool:
        """비밀번호 유효성 검증"""
        # 최소 8자, 최대 20자
        # 최소 하나의 문자 및 숫자 포함
        if len(password) < 8 or len(password) > 20:
            return False
        if not re.search(r'[A-Za-z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        return True

    @staticmethod
    def create_tokens(user_id: str) -> dict:
        """Access Token 생성"""
        access_token = create_access_token(identity=user_id)
        return {
            'access_token': access_token
        }