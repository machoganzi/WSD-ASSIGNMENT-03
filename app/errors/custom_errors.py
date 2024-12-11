class CustomError(Exception):
    """기본 커스텀 에러 클래스"""
    def __init__(self, message: str, code: str = 'UNKNOWN_ERROR'):
        self.message = message
        self.code = code
        super().__init__(self.message)

class AuthenticationError(CustomError):
    """인증 관련 에러"""
    def __init__(self, message: str = "인증 오류가 발생했습니다"):
        super().__init__(message, code='AUTHENTICATION_ERROR')

class DataFormatError(CustomError):
    """데이터 형식 관련 에러"""
    def __init__(self, message: str = "데이터 형식이 올바르지 않습니다"):
        super().__init__(message, code='DATA_FORMAT_ERROR')