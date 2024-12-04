/**
 * @swagger
 * tags:
 *   name: Bookmarks
 *   description: 채용공고 북마크 관리 API
 */

/**
 * @swagger
 * /bookmarks:
 *   get:
 *     tags: [Bookmarks]
 *     summary: 북마크 목록 조회
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: page
 *         schema:
 *           type: integer
 *           default: 1
 *         description: 페이지 번호
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 20
 *         description: 페이지당 항목 수
 *       - in: query
 *         name: sort
 *         schema:
 *           type: string
 *           default: -bookmarkedAt
 *         description: 정렬 기준
 *     responses:
 *       200:
 *         description: 북마크 목록 조회 성공
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 status:
 *                   type: string
 *                   enum: [success]
 *                 data:
 *                   type: object
 *                   properties:
 *                     bookmarks:
 *                       type: array
 *                       items:
 *                         $ref: '#/components/schemas/Bookmark'
 *                     pagination:
 *                       $ref: '#/components/schemas/Pagination'
 *
 *   delete:
 *     tags: [Bookmarks]
 *     summary: 북마크 일괄 삭제
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - bookmarkIds
 *             properties:
 *               bookmarkIds:
 *                 type: array
 *                 items:
 *                   type: string
 *     responses:
 *       200:
 *         description: 북마크 삭제 성공
 *
 * /bookmarks/jobs/{jobId}:
 *   post:
 *     tags: [Bookmarks]
 *     summary: 채용공고 북마크 토글
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: jobId
 *         required: true
 *         schema:
 *           type: string
 *         description: 채용공고 ID
 *     responses:
 *       200:
 *         description: 북마크 토글 성공
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 status:
 *                   type: string
 *                   enum: [success]
 *                 data:
 *                   type: object
 *                   properties:
 *                     isBookmarked:
 *                       type: boolean
 *                     bookmark:
 *                       $ref: '#/components/schemas/Bookmark'
 *
 * /bookmarks/jobs/{jobId}/status:
 *   get:
 *     tags: [Bookmarks]
 *     summary: 채용공고 북마크 상태 확인
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: jobId
 *         required: true
 *         schema:
 *           type: string
 *         description: 채용공고 ID
 *     responses:
 *       200:
 *         description: 북마크 상태 확인 성공
 *
 * /bookmarks/{id}/note:
 *   patch:
 *     tags: [Bookmarks]
 *     summary: 북마크 메모 수정
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *         description: 북마크 ID
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - note
 *             properties:
 *               note:
 *                 type: string
 *     responses:
 *       200:
 *         description: 메모 수정 성공
 *
 * /bookmarks/{id}/tags:
 *   patch:
 *     tags: [Bookmarks]
 *     summary: 북마크 태그 수정
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *         description: 북마크 ID
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - tags
 *             properties:
 *               tags:
 *                 type: array
 *                 items:
 *                   type: string
 *     responses:
 *       200:
 *         description: 태그 수정 성공
 */

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