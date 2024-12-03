const jwt = require('jsonwebtoken');
const { AuthenticationError } = require('../utils/errors');
const { User } = require('../models');
const logger = require('../utils/logger');

const auth = async (req, res, next) => {
  try {
    // 토큰 확인
    const authHeader = req.headers.authorization;
    if (!authHeader?.startsWith('Bearer ')) {
      throw new AuthenticationError('No token provided');
    }

    // 토큰 검증
    const token = authHeader.split(' ')[1];
    const decoded = jwt.verify(token, process.env.JWT_SECRET);

    // 사용자 확인
    const user = await User.findById(decoded.id).select('-password');
    if (!user) {
      throw new AuthenticationError('User not found');
    }

    // request 객체에 사용자 정보 추가
    req.user = user;
    next();
  } catch (error) {
    if (error.name === 'JsonWebTokenError') {
      next(new AuthenticationError('Invalid token'));
    } else if (error.name === 'TokenExpiredError') {
      next(new AuthenticationError('Token expired'));
    } else {
      next(error);
    }
  }
};

// 선택적 인증 미들웨어 (토큰이 있으면 검증, 없어도 됨)
const optionalAuth = async (req, res, next) => {
  try {
    const authHeader = req.headers.authorization;
    if (!authHeader?.startsWith('Bearer ')) {
      return next();
    }

    const token = authHeader.split(' ')[1];
    const decoded = jwt.verify(token, process.env.JWT_SECRET);

    const user = await User.findById(decoded.id).select('-password');
    if (user) {
      req.user = user;
    }
    next();
  } catch (error) {
    // 토큰이 유효하지 않아도 다음 미들웨어로 진행
    next();
  }
};

// 관리자 권한 확인 미들웨어
const adminAuth = async (req, res, next) => {
  try {
    if (!req.user || req.user.role !== 'admin') {
      throw new AuthenticationError('Admin access required');
    }
    next();
  } catch (error) {
    next(error);
  }
};

module.exports = {
  auth,
  optionalAuth,
  adminAuth
};