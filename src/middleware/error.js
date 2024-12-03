const logger = require('../utils/logger');
const { AppError } = require('../utils/errors');

// 개발 환경용 에러 응답
const sendErrorDev = (err, res) => {
  res.status(err.statusCode).json({
    status: err.status,
    error: err,
    message: err.message,
    code: err.errorCode,
    stack: err.stack
  });
};

// 운영 환경용 에러 응답
const sendErrorProd = (err, res) => {
  // Operational, trusted error: send message to client
  if (err.isOperational) {
    res.status(err.statusCode).json({
      status: err.status,
      message: err.message,
      code: err.errorCode
    });
  } 
  // Programming or other unknown error: don't leak error details
  else {
    logger.error('ERROR 💥', err);
    res.status(500).json({
      status: 'error',
      message: 'Something went very wrong!',
      code: 'INTERNAL_SERVER_ERROR'
    });
  }
};

// 몽구스 에러 처리
const handleMongooseError = err => {
  if (err.name === 'CastError') {
    return new AppError(`Invalid ${err.path}: ${err.value}`, 400, 'INVALID_INPUT');
  }
  if (err.name === 'ValidationError') {
    const errors = Object.values(err.errors).map(el => el.message);
    return new AppError(`Invalid input data. ${errors.join('. ')}`, 400, 'VALIDATION_ERROR');
  }
  if (err.code === 11000) {
    const value = err.errmsg.match(/(["'])(\\?.)*?\1/)[0];
    return new AppError(`Duplicate field value: ${value}`, 409, 'DUPLICATE_ERROR');
  }
  return err;
};

// 글로벌 에러 핸들링 미들웨어
const errorHandler = (err, req, res, next) => {
  err.statusCode = err.statusCode || 500;
  err.status = err.status || 'error';

  // 에러 로깅
  logger.error(err.message, {
    error: err,
    path: req.path,
    method: req.method,
    ip: req.ip,
    userId: req.user?.id
  });

  if (process.env.NODE_ENV === 'development') {
    sendErrorDev(err, res);
  } else {
    let error = { ...err };
    error.message = err.message;
    
    error = handleMongooseError(error);
    sendErrorProd(error, res);
  }
};

module.exports = errorHandler;