from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    get_jwt_identity,
    verify_jwt_in_request,
    decode_token
)
from datetime import datetime, timedelta
import base64
import re
from typing import Optional, Dict, Tuple

class AuthUtils:
    """인증 관련 유틸리티 클래스
    
    JWT 토큰 생성/검증, 비밀번호 암호화/검증, 입력값 검증 등
    인증 관련 핵심 기능들을 제공합니다.
    """
    
    @staticmethod
    def encode_password(password: str) -> str:
        """비밀번호 Base64 인코딩
        
        Args:
            password (str): 원본 비밀번호
            
        Returns:
            str: Base64로 인코딩된 비밀번호
        """
        return base64.b64encode(password.encode()).decode()

    @staticmethod
    def verify_password(input_password: str, stored_password: str) -> bool:
        """비밀번호 검증
        
        Args:
            input_password (str): 입력된 비밀번호
            stored_password (str): 저장된 인코딩된 비밀번호
            
        Returns:
            bool: 비밀번호 일치 여부
        """
        encoded_input = base64.b64encode(input_password.encode()).decode()
        return encoded_input == stored_password

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """이메일 형식 검증
        
        Args:
            email (str): 검증할 이메일 주소
            
        Returns:
            Tuple[bool, Optional[str]]: (유효성 여부, 에러 메시지)
        """
        if not email:
            return False, "이메일은 필수 입력항목입니다."
            
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(pattern, email):
            return False, "유효하지 않은 이메일 형식입니다."
            
        return True, None

    @staticmethod
    def validate_password(password: str) -> Tuple[bool, Optional[str]]:
        """비밀번호 유효성 검증
        
        Args:
            password (str): 검증할 비밀번호
            
        Returns:
            Tuple[bool, Optional[str]]: (유효성 여부, 에러 메시지)
        """
        if not password:
            return False, "비밀번호는 필수 입력항목입니다."
            
        if len(password) < 8 or len(password) > 20:
            return False, "비밀번호는 8~20자 사이여야 합니다."
            
        if not re.search(r'[A-Za-z]', password):
            return False, "비밀번호는 최소 1개의 문자를 포함해야 합니다."
            
        if not re.search(r'\d', password):
            return False, "비밀번호는 최소 1개의 숫자를 포함해야 합니다."
            
        return True, None

    @staticmethod
    def create_tokens(user_id: str) -> Dict[str, str]:
        """Access Token과 Refresh Token 생성
        
        Args:
            user_id (str): 사용자 식별자
            
        Returns:
            Dict[str, str]: access_token과 refresh_token을 포함한 딕셔너리
        """
        access_token = create_access_token(
            identity=user_id,
            expires_delta=timedelta(hours=1)  # Access Token 1시간 유효
        )
        
        refresh_token = create_refresh_token(
            identity=user_id,
            expires_delta=timedelta(days=14)  # Refresh Token 14일 유효
        )
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 3600  # 1시간 (초 단위)
        }

    @staticmethod
    def refresh_access_token() -> Dict[str, str]:
        """Refresh Token을 사용하여 새로운 Access Token 발급
        
        현재 요청의 Refresh Token을 검증하고 새로운 Access Token을 발급합니다.
        
        Returns:
            Dict[str, str]: 새로운 access_token을 포함한 딕셔너리
            
        Raises:
            InvalidTokenError: 유효하지 않은 토큰
        """
        verify_jwt_in_request(refresh=True)
        current_user = get_jwt_identity()
        
        new_access_token = create_access_token(
            identity=current_user,
            expires_delta=timedelta(hours=1)
        )
        
        return {
            'access_token': new_access_token,
            'token_type': 'Bearer',
            'expires_in': 3600
        }

    @staticmethod
    def verify_token(token: str) -> Tuple[bool, Optional[str]]:
        """토큰 유효성 검증
        
        Args:
            token (str): 검증할 JWT 토큰
            
        Returns:
            Tuple[bool, Optional[str]]: (유효성 여부, 에러 메시지)
        """
        try:
            decode_token(token)
            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_token_user() -> Optional[str]:
        """현재 인증된 사용자의 ID 반환
        
        Returns:
            Optional[str]: 인증된 사용자 ID 또는 None
        """
        try:
            verify_jwt_in_request()
            return get_jwt_identity()
        except:
            return None