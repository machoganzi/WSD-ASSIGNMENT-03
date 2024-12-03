const express = require('express');
const searchController = require('../controllers/search.controller');
const { optionalAuth } = require('../middleware/auth');

const router = express.Router();

// 선택적 인증 적용 (인증된 사용자는 더 많은 결과를 볼 수 있음)
router.use(optionalAuth);

// 검색 라우트
router.get('/', searchController.searchAll);
router.get('/advanced', searchController.advancedSearch);
router.get('/suggestions', searchController.getSuggestions);

module.exports = router;