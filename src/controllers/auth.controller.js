const jwt = require('jsonwebtoken');
const User = require('../models/user.model');

class AuthController {
  // 회원가입
  async register(req, res) {
    try {
      const { email, password, name } = req.body;

      // 이메일 중복 체크
      const existingUser = await User.findOne({ email });
      if (existingUser) {
        return res.status(400).json({
          status: 'error',
          message: 'Email already exists',
          code: 'EMAIL_EXISTS'
        });
      }

      const user = new User({
        email,
        password,
        name
      });

      await user.save();

      const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET, {
        expiresIn: process.env.JWT_EXPIRES_IN
      });

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
      res.status(400).json({
        status: 'error',
        message: error.message,
        code: 'REGISTRATION_FAILED'
      });
    }
  }

  // 로그인
  async login(req, res) {
    try {
      const { email, password } = req.body;

      // 사용자 찾기
      const user = await User.findOne({ email });
      if (!user || !(await user.comparePassword(password))) {
        return res.status(401).json({
          status: 'error',
          message: 'Invalid email or password',
          code: 'INVALID_CREDENTIALS'
        });
      }

      // JWT 토큰 생성
      const token = jwt.sign({ id: user._id }, process.env.JWT_SECRET, {
        expiresIn: process.env.JWT_EXPIRES_IN
      });

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
      res.status(400).json({
        status: 'error',
        message: error.message,
        code: 'LOGIN_FAILED'
      });
    }
  }

  // 내 정보 조회
  async getMe(req, res) {
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
      res.status(400).json({
        status: 'error',
        message: error.message,
        code: 'FETCH_PROFILE_FAILED'
      });
    }
  }
}

module.exports = new AuthController();