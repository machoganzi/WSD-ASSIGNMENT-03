/**
 * @swagger
 * tags:
 *   name: Applications
 *   description: 채용공고 지원 관리 API
 */

/**
 * @swagger
 * /applications/jobs/{jobId}:
 *   post:
 *     tags: [Applications]
 *     summary: 채용공고 지원하기
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: jobId
 *         required: true
 *         schema:
 *           type: string
 *         description: 채용공고 ID
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - coverLetter
 *             properties:
 *               coverLetter:
 *                 type: string
 *                 description: 자기소개서
 *               answers:
 *                 type: array
 *                 items:
 *                   type: object
 *                   properties:
 *                     question:
 *                       type: string
 *                     answer:
 *                       type: string
 *     responses:
 *       201:
 *         description: 지원 성공
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
 *                     application:
 *                       $ref: '#/components/schemas/Application'
 *
 * /applications/me:
 *   get:
 *     tags: [Applications]
 *     summary: 내 지원 목록 조회
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: query
 *         name: status
 *         schema:
 *           type: string
 *           enum: [pending, reviewing, accepted, rejected, withdrawn]
 *         description: 지원 상태 필터
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
 *           default: 10
 *         description: 페이지당 항목 수
 *       - in: query
 *         name: sort
 *         schema:
 *           type: string
 *           default: -appliedAt
 *         description: 정렬 기준
 *     responses:
 *       200:
 *         description: 내 지원 목록 조회 성공
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
 *                     applications:
 *                       type: array
 *                       items:
 *                         $ref: '#/components/schemas/Application'
 *                     pagination:
 *                       $ref: '#/components/schemas/Pagination'
 *
 * /applications/{id}:
 *   get:
 *     tags: [Applications]
 *     summary: 지원서 상세 조회
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *         description: 지원서 ID
 *     responses:
 *       200:
 *         description: 지원서 상세 조회 성공
 *
 *   patch:
 *     tags: [Applications]
 *     summary: 지원서 수정
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *         description: 지원서 ID
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               coverLetter:
 *                 type: string
 *               answers:
 *                 type: array
 *                 items:
 *                   type: object
 *                   properties:
 *                     question:
 *                       type: string
 *                     answer:
 *                       type: string
 *     responses:
 *       200:
 *         description: 지원서 수정 성공
 *
 *   delete:
 *     tags: [Applications]
 *     summary: 지원 취소
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *         description: 지원서 ID
 *     responses:
 *       200:
 *         description: 지원 취소 성공
 *
 * /applications/{id}/status:
 *   patch:
 *     tags: [Applications]
 *     summary: 지원 상태 변경 (관리자용)
 *     security:
 *       - bearerAuth: []
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: string
 *         description: 지원서 ID
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - status
 *             properties:
 *               status:
 *                 type: string
 *                 enum: [pending, reviewing, accepted, rejected]
 *               note:
 *                 type: string
 *     responses:
 *       200:
 *         description: 상태 변경 성공
 */

const express = require('express');
const applicationController = require('../controllers/application.controller');
const { auth, adminAuth } = require('../middleware/auth');

const router = express.Router();

// 모든 라우트에 인증 필요
router.use(auth);

// 일반 사용자 라우트
router.get('/me', applicationController.getMyApplications);
router.get('/:id', applicationController.getApplication);
router.post('/jobs/:jobId', applicationController.apply);
router.patch('/:id', applicationController.updateApplication);
router.delete('/:id', applicationController.withdrawApplication);

// 관리자 라우트
router.patch('/:id/status', adminAuth, applicationController.updateApplicationStatus);

module.exports = router;