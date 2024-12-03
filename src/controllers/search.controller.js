const { Job, Company, Skill } = require('../models');
const { ValidationError } = require('../utils/errors');
const logger = require('../utils/logger');

class SearchController {
  // 통합 검색 (채용공고, 회사, 기술스택)
  async searchAll(req, res, next) {
    try {
      const { q: query, type, page = 1, limit = 20 } = req.query;
      
      if (!query) {
        throw new ValidationError('Search query is required');
      }

      const skip = (page - 1) * limit;
      let results = {};
      let total = 0;

      const searchQuery = { $text: { $search: query } };
      const searchOptions = {
        score: { $meta: 'textScore' }
      };

      switch (type) {
        case 'jobs':
          [results.jobs, total] = await Promise.all([
            Job.find(searchQuery, searchOptions)
              .sort({ score: { $meta: 'textScore' } })
              .skip(skip)
              .limit(parseInt(limit))
              .populate('company', 'name location')
              .populate('skills', 'name'),
            Job.countDocuments(searchQuery)
          ]);
          break;

        case 'companies':
          [results.companies, total] = await Promise.all([
            Company.find(searchQuery, searchOptions)
              .sort({ score: { $meta: 'textScore' } })
              .skip(skip)
              .limit(parseInt(limit)),
            Company.countDocuments(searchQuery)
          ]);
          break;

        case 'skills':
          [results.skills, total] = await Promise.all([
            Skill.find(searchQuery, searchOptions)
              .sort({ score: { $meta: 'textScore' } })
              .skip(skip)
              .limit(parseInt(limit)),
            Skill.countDocuments(searchQuery)
          ]);
          break;

        default:
          // 전체 검색
          const [jobs, companies, skills] = await Promise.all([
            Job.find(searchQuery, searchOptions)
              .sort({ score: { $meta: 'textScore' } })
              .limit(5)
              .populate('company', 'name location'),
            Company.find(searchQuery, searchOptions)
              .sort({ score: { $meta: 'textScore' } })
              .limit(5),
            Skill.find(searchQuery, searchOptions)
              .sort({ score: { $meta: 'textScore' } })
              .limit(5)
          ]);

          results = { jobs, companies, skills };
          total = jobs.length + companies.length + skills.length;
      }

      logger.info('Search performed', { 
        query, 
        type, 
        totalResults: total 
      });

      res.json({
        status: 'success',
        data: {
          results,
          pagination: type ? {
            currentPage: parseInt(page),
            totalPages: Math.ceil(total / limit),
            totalItems: total,
            itemsPerPage: parseInt(limit)
          } : null
        }
      });
    } catch (error) {
      next(error);
    }
  }

  // 필터 기반 고급 검색
  async advancedSearch(req, res, next) {
    try {
      const {
        keyword,
        location,
        jobType,
        experienceLevel,
        skills,
        salary,
        company,
        page = 1,
        limit = 20,
        sort = '-createdAt'
      } = req.query;

      const query = {};

      // 키워드 검색
      if (keyword) {
        query.$or = [
          { title: new RegExp(keyword, 'i') },
          { description: new RegExp(keyword, 'i') }
        ];
      }

      // 위치 필터
      if (location) {
        query.location = new RegExp(location, 'i');
      }

      // 직무 유형 필터
      if (jobType) {
        query.jobType = jobType;
      }

      // 경력 수준 필터
      if (experienceLevel) {
        query.experience = experienceLevel;
      }

      // 기술 스택 필터
      if (skills) {
        const skillArray = Array.isArray(skills) ? skills : skills.split(',');
        query.skills = { $all: skillArray };
      }

      // 연봉 범위 필터
      if (salary) {
        const [min, max] = salary.split('-').map(Number);
        query.salary = {
          $gte: min,
          ...(max && { $lte: max })
        };
      }

      // 회사 필터
      if (company) {
        const companyDoc = await Company.findOne({ 
          name: new RegExp(company, 'i') 
        });
        if (companyDoc) {
          query.company = companyDoc._id;
        }
      }

      const [jobs, total] = await Promise.all([
        Job.find(query)
          .sort(sort)
          .skip((page - 1) * limit)
          .limit(parseInt(limit))
          .populate('company', 'name location')
          .populate('skills', 'name'),
        Job.countDocuments(query)
      ]);

      logger.info('Advanced search performed', { 
        filters: req.query, 
        totalResults: total 
      });

      res.json({
        status: 'success',
        data: {
          jobs,
          pagination: {
            currentPage: parseInt(page),
            totalPages: Math.ceil(total / limit),
            totalItems: total,
            itemsPerPage: parseInt(limit)
          }
        }
      });
    } catch (error) {
      next(error);
    }
  }

  // 자동완성 검색 제안
  async getSuggestions(req, res, next) {
    try {
      const { q: query, type = 'all' } = req.query;

      if (!query || query.length < 2) {
        return res.json({
          status: 'success',
          data: { suggestions: [] }
        });
      }

      const searchRegex = new RegExp(query, 'i');
      let suggestions = {};

      switch (type) {
        case 'jobs':
          suggestions.jobs = await Job.find({ 
            title: searchRegex 
          })
            .select('title')
            .limit(5);
          break;

        case 'companies':
          suggestions.companies = await Company.find({ 
            name: searchRegex 
          })
            .select('name')
            .limit(5);
          break;

        case 'skills':
          suggestions.skills = await Skill.find({ 
            $or: [
              { name: searchRegex },
              { aliases: searchRegex }
            ]
          })
            .select('name')
            .limit(5);
          break;

        default:
          // 모든 타입의 제안
          const [jobs, companies, skills] = await Promise.all([
            Job.find({ title: searchRegex })
              .select('title')
              .limit(3),
            Company.find({ name: searchRegex })
              .select('name')
              .limit(3),
            Skill.find({
              $or: [
                { name: searchRegex },
                { aliases: searchRegex }
              ]
            })
              .select('name')
              .limit(3)
          ]);

          suggestions = { jobs, companies, skills };
      }

      res.json({
        status: 'success',
        data: { suggestions }
      });
    } catch (error) {
      next(error);
    }
  }
}

module.exports = new SearchController();