const express = require('express');
const bookmarkController = require('../controllers/bookmark.controller');
const { auth } = require('../middleware/auth');

const router = express.Router();

// 모든 라우트에 인증 필요
router.use(auth);

// 북마크 관리
router.get('/', bookmarkController.getBookmarks);
router.post('/jobs/:jobId', bookmarkController.toggleBookmark);
router.get('/jobs/:jobId/status', bookmarkController.checkBookmarkStatus);
router.patch('/:id/note', bookmarkController.updateBookmarkNote);
router.patch('/:id/tags', bookmarkController.updateBookmarkTags);
router.delete('/', bookmarkController.deleteBookmarks);

module.exports = router;