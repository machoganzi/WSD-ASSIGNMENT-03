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