const express = require('express');
const authRoutes = require('./auth.routes');
const jobRoutes = require('./job.routes');
const applicationRoutes = require('./application.routes');
const bookmarkRoutes = require('./bookmark.routes');
const companyRoutes = require('./company.routes');
const categoryRoutes = require('./category.routes');
const skillRoutes = require('./skill.routes');
const searchRoutes = require('./search.routes');

const router = express.Router();

// Health check
router.get('/health', (req, res) => {
  res.status(200).json({
    status: 'success',
    message: 'API is working'
  });
});

// API 라우트
router.use('/auth', authRoutes);
router.use('/jobs', jobRoutes);
router.use('/applications', applicationRoutes);
router.use('/bookmarks', bookmarkRoutes);
router.use('/companies', companyRoutes);
router.use('/categories', categoryRoutes);
router.use('/skills', skillRoutes);
router.use('/search', searchRoutes);

// 404 처리
router.use('*', (req, res) => {
  res.status(404).json({
    status: 'error',
    message: 'Endpoint not found',
    code: 'NOT_FOUND'
  });
});

module.exports = router;