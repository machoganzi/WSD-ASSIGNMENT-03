const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const { User } = require('../models');
const { ValidationError, AuthenticationError } = require('../utils/errors');
const logger = require('../utils/logger');

class AuthController {
  // 토큰 생성 함수
  generateToken(userId) {
    return jwt.sign({ id: userId }, process.env.JWT_SECRET, {
      expiresIn: process.env.JWT_EXPIRES_IN
    });
  }

  // 회원가입
  async register(req, res, next) {
    try {
      const { email, password, name, phone } = req.body;

      // 이메일 형식 검증
      const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
      if (!emailRegex.test(email)) {
        throw new ValidationError('Invalid email format');
      }

      // 비밀번호 길이 검증
      if (password.length < 6) {
        throw new ValidationError('Password must be at least 6 characters long');
      }

      // 이메일 중복 체크
      const existingUser = await User.findOne({ email });
      if (existingUser) {
        throw new ValidationError('Email already exists');
      }

      // 비밀번호 해싱
      const hashedPassword = await bcrypt.hash(password, 10);

      // 사용자 생성
      const user = await User.create({
        email,
        password: hashedPassword,
        name,
        phone
      });

      // 토큰 생성
      const token = this.generateToken(user._id);

      logger.info('User registered successfully', { userId: user._id });

      res.status(201).json({
        status: 'success',
        data: {
          token,
          user: {
            id: user._id,
            email: user.email,
            name: user.name
          }
        }
      });
    } catch (error) {
      next(error);
    }
  }

  // 로그인
  async login(req, res, next) {
    try {
      const { email, password } = req.body;

      // 이메일과 비밀번호 필수 입력 확인
      if (!email || !password) {
        throw new ValidationError('Please provide email and password');
      }

      // 사용자 찾기
      const user = await User.findOne({ email }).select('+password');
      if (!user) {
        throw new AuthenticationError('Invalid email or password');
      }

      // 비밀번호 확인
      const isPasswordValid = await bcrypt.compare(password, user.password);
      if (!isPasswordValid) {
        throw new AuthenticationError('Invalid email or password');
      }

      // 토큰 생성
      const token = this.generateToken(user._id);

      logger.info('User logged in successfully', { userId: user._id });

      res.json({
        status: 'success',
        data: {
          token,
          user: {
            id: user._id,
            email: user.email,
            name: user.name
          }
        }
      });
    } catch (error) {
      next(error);
    }
  }

  // 내 정보 조회
  async getMe(req, res, next) {
    try {
      const user = await User.findById(req.user._id)
        .select('-password')
        .populate('applications')
        .populate('bookmarks');

      res.json({
        status: 'success',
        data: { user }
      });
    } catch (error) {
      next(error);
    }
  }

  // 내 정보 수정
  async updateMe(req, res, next) {
    try {
      const { name, phone } = req.body;
      const updatedUser = await User.findByIdAndUpdate(
        req.user._id,
        { name, phone },
        { new: true, runValidators: true }
      ).select('-password');

      logger.info('User profile updated', { userId: req.user._id });

      res.json({
        status: 'success',
        data: { user: updatedUser }
      });
    } catch (error) {
      next(error);
    }
  }

  // 비밀번호 변경
  async updatePassword(req, res, next) {
    try {
      const { currentPassword, newPassword } = req.body;

      // 현재 비밀번호 확인
      const user = await User.findById(req.user._id).select('+password');
      const isPasswordValid = await bcrypt.compare(currentPassword, user.password);
      
      if (!isPasswordValid) {
        throw new AuthenticationError('Current password is incorrect');
      }

      // 새 비밀번호 해싱
      if (newPassword.length < 6) {
        throw new ValidationError('New password must be at least 6 characters long');
      }
      
      const hashedPassword = await bcrypt.hash(newPassword, 10);
      user.password = hashedPassword;
      await user.save();

      logger.info('User password updated', { userId: user._id });

      res.json({
        status: 'success',
        message: 'Password updated successfully'
      });
    } catch (error) {
      next(error);
    }
  }
}

module.exports = new AuthController();