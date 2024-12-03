class AppError extends Error {
    constructor(message, statusCode = 500, errorCode = 'INTERNAL_SERVER_ERROR') {
      super(message);
      this.statusCode = statusCode;
      this.errorCode = errorCode;
      this.status = `${statusCode}`.startsWith('4') ? 'fail' : 'error';
      this.isOperational = true;
  
      Error.captureStackTrace(this, this.constructor);
    }
  }
  
  class ValidationError extends AppError {
    constructor(message) {
      super(message, 400, 'VALIDATION_ERROR');
    }
  }
  
  class AuthenticationError extends AppError {
    constructor(message = 'Authentication failed') {
      super(message, 401, 'AUTHENTICATION_ERROR');
    }
  }
  
  class AuthorizationError extends AppError {
    constructor(message = 'Not authorized') {
      super(message, 403, 'AUTHORIZATION_ERROR');
    }
  }
  
  class NotFoundError extends AppError {
    constructor(message = 'Resource not found') {
      super(message, 404, 'NOT_FOUND_ERROR');
    }
  }
  
  class DuplicateError extends AppError {
    constructor(message = 'Duplicate resource') {
      super(message, 409, 'DUPLICATE_ERROR');
    }
  }
  
  class CrawlerError extends AppError {
    constructor(message, metadata = {}) {
      super(message, 500, 'CRAWLER_ERROR');
      this.metadata = metadata;
    }
  }
  
  class DatabaseError extends AppError {
    constructor(message, originalError = null) {
      super(message, 500, 'DATABASE_ERROR');
      this.originalError = originalError;
    }
  }
  
  module.exports = {
    AppError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    DuplicateError,
    CrawlerError,
    DatabaseError
  };