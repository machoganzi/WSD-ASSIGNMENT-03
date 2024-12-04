/**
 * @swagger
 * tags:
 *   name: Search
 *   description: 통합 검색 API
 */

/**
 * @swagger
 * /search:
 *   get:
 *     tags: [Search]
 *     summary: 통합 검색
 *     description: 채용공고, 회사, 기술스택에 대한 통합 검색을 수행합니다.
 *     parameters:
 *       - in: query
 *         name: q
 *         required: true
 *         schema:
 *           type: string
 *         description: 검색어
 *       - in: query
 *         name: type
 *         schema:
 *           type: string
 *           enum: [jobs, companies, skills, all]
 *         description: 검색 대상 타입 (기본값: all)
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
 *         description: 페이지당 결과 수
 *     responses:
 *       200:
 *         description: 검색 성공
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
 *                     results:
 *                       type: object
 *                       properties:
 *                         jobs:
 *                           type: array
 *                           items:
 *                             $ref: '#/components/schemas/Job'
 *                         companies:
 *                           type: array
 *                           items:
 *                             $ref: '#/components/schemas/Company'
 *                         skills:
 *                           type: array
 *                           items:
 *                             $ref: '#/components/schemas/Skill'
 *                     pagination:
 *                       $ref: '#/components/schemas/Pagination'
 *
 * /search/advanced:
 *   get:
 *     tags: [Search]
 *     summary: 고급 검색
 *     description: 다양한 필터를 적용한 채용공고 검색을 수행합니다.
 *     parameters:
 *       - in: query
 *         name: keyword
 *         schema:
 *           type: string
 *         description: 검색어
 *       - in: query
 *         name: location
 *         schema:
 *           type: string
 *         description: 지역
 *       - in: query
 *         name: jobType
 *         schema:
 *           type: string
 *           enum: [full-time, part-time, contract, internship]
 *         description: 고용형태
 *       - in: query
 *         name: experienceLevel
 *         schema:
 *           type: string
 *         description: 경력 수준
 *       - in: query
 *         name: skills
 *         schema:
 *           type: array
 *           items:
 *             type: string
 *         description: 기술스택 (콤마로 구분)
 *       - in: query
 *         name: salary
 *         schema:
 *           type: string
 *         description: 연봉 범위 (예: 3000-5000)
 *       - in: query
 *         name: company
 *         schema:
 *           type: string
 *         description: 회사명
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
 *         description: 페이지당 결과 수
 *     responses:
 *       200:
 *         description: 검색 성공
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
 *                     jobs:
 *                       type: array
 *                       items:
 *                         $ref: '#/components/schemas/Job'
 *                     pagination:
 *                       $ref: '#/components/schemas/Pagination'
 *
 * /search/suggestions:
 *   get:
 *     tags: [Search]
 *     summary: 검색어 자동완성
 *     parameters:
 *       - in: query
 *         name: q
 *         required: true
 *         schema:
 *           type: string
 *         description: 검색어
 *       - in: query
 *         name: type
 *         schema:
 *           type: string
 *           enum: [jobs, companies, skills, all]
 *         description: 제안 타입 (기본값: all)
 *     responses:
 *       200:
 *         description: 검색어 제안 조회 성공
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
 *                     suggestions:
 *                       type: object
 *                       properties:
 *                         jobs:
 *                           type: array
 *                           items:
 *                             type: object
 *                             properties:
 *                               title:
 *                                 type: string
 *                         companies:
 *                           type: array
 *                           items:
 *                             type: object
 *                             properties:
 *                               name:
 *                                 type: string
 *                         skills:
 *                           type: array
 *                           items:
 *                             type: object
 *                             properties:
 *                               name:
 *                                 type: string
 */

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