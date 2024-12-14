from base64 import b64encode, b64decode
import re
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional
from .config import Config

class AuthUtils:
    def __init__(self):
        self.JWT_SECRET_KEY = Config.JWT_SECRET_KEY  # 실제로는 환경변수에서 가져와야 합니다
        self.JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
        self.JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=14)

    def encode_password(self, password: str) -> str:
        """비밀번호를 Base64로 인코딩합니다."""
        if not password:
            raise ValueError("Password cannot be empty")
        return b64encode(password.encode()).decode()

    def verify_password(self, plain_password: str, encoded_password: str) -> bool:
        """인코딩된 비밀번호와 일반 비밀번호를 비교합니다."""
        return self.encode_password(plain_password) == encoded_password

    def validate_email(self, email: str) -> bool:
        """이메일 형식을 검증합니다."""
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        return bool(email_pattern.match(email))

    def validate_password(self, password: str) -> bool:
        """비밀번호 형식을 검증합니다."""
        return len(password) >= 8  # 기본적인 길이 검증

    def create_tokens(self, user_id: str) -> Dict[str, str]:
        """Access Token과 Refresh Token을 생성합니다."""
        access_token = jwt.encode(
            {
                'user_id': user_id,
                'exp': datetime.utcnow() + self.JWT_ACCESS_TOKEN_EXPIRES,
                'type': 'access'
            },
            self.JWT_SECRET_KEY,
            algorithm='HS256'
        )

        refresh_token = jwt.encode(
            {
                'user_id': user_id,
                'exp': datetime.utcnow() + self.JWT_REFRESH_TOKEN_EXPIRES,
                'type': 'refresh'
            },
            self.JWT_SECRET_KEY,
            algorithm='HS256'
        )

        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }