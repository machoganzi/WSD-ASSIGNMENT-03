const { Job, Company, Skill } = require('../models');
const { NotFoundError, ValidationError } = require('../utils/errors');
const logger = require('../utils/logger');

class JobController {
  // 채용공고 목록 조회 (필터링, 페이징 포함)
  async getJobs(req, res, next) {
    try {
      const { 
        page = 1, 
        limit = 20,
        location,
        jobType,
        experience,
        skills,
        q: searchQuery,
        sort = '-createdAt'
      } = req.query;

      // 쿼리 객체 생성
      const query = {};
      
      // 필터 조건 추가
      if (location) query.location = new RegExp(location, 'i');
      if (jobType) query.jobType = jobType;
      if (experience) query.experience = experience;
      if (skills) {
        const skillIds = Array.isArray(skills) ? skills : [skills];
        query.skills = { $in: skillIds };
      }
      if (searchQuery) {
        query.$or = [
          { title: new RegExp(searchQuery, 'i') },
          { description: new RegExp(searchQuery, 'i') }
        ];
      }

      // 페이지네이션 설정
      const skip = (page - 1) * limit;

      // 채용공고 조회
      const [jobs, total] = await Promise.all([
        Job.find(query)
          .sort(sort)
          .skip(skip)
          .limit(parseInt(limit))
          .populate('company', 'name location')
          .populate('skills', 'name'),
        Job.countDocuments(query)
      ]);

      logger.info('Jobs fetched successfully', { 
        filters: req.query,
        totalJobs: total,
        page,
        limit 
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

  // 채용공고 상세 조회
  async getJob(req, res, next) {
    try {
      const job = await Job.findById(req.params.id)
        .populate('company')
        .populate('skills');

      if (!job) {
        throw new NotFoundError('Job not found');
      }

      // 조회수 증가
      job.viewCount += 1;
      await job.save();

      res.json({
        status: 'success',
        data: { job }
      });
    } catch (error) {
      next(error);
    }
  }

  // 연관 채용공고 조회
  async getRelatedJobs(req, res, next) {
    try {
      const job = await Job.findById(req.params.id);
      if (!job) {
        throw new NotFoundError('Job not found');
      }

      // 같은 회사의 다른 채용공고나 비슷한 기술스택을 가진 채용공고 조회
      const relatedJobs = await Job.find({
        $and: [
          { _id: { $ne: job._id } },
          {
            $or: [
              { company: job.company },
              { skills: { $in: job.skills } }
            ]
          }
        ]
      })
      .limit(5)
      .populate('company', 'name')
      .populate('skills', 'name');

      res.json({
        status: 'success',
        data: { relatedJobs }
      });
    } catch (error) {
      next(error);
    }
  }

  // 채용공고 검색
  async searchJobs(req, res, next) {
    try {
      const { q: searchQuery, page = 1, limit = 20 } = req.query;
      
      if (!searchQuery) {
        throw new ValidationError('Search query is required');
      }

      const query = {
        $text: { $search: searchQuery }
      };

      const [jobs, total] = await Promise.all([
        Job.find(query, { score: { $meta: 'textScore' } })
          .sort({ score: { $meta: 'textScore' } })
          .skip((page - 1) * limit)
          .limit(parseInt(limit))
          .populate('company', 'name location')
          .populate('skills', 'name'),
        Job.countDocuments(query)
      ]);

      logger.info('Jobs searched successfully', { 
        searchQuery,
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

  // 관리자: 채용공고 생성
  async createJob(req, res, next) {
    try {
      const {
        title,
        companyId,
        description,
        requirements,
        benefits,
        skillIds,
        location,
        jobType,
        salary,
        deadline
      } = req.body;

      // 회사 존재 여부 확인
      const company = await Company.findById(companyId);
      if (!company) {
        throw new NotFoundError('Company not found');
      }

      // 기술 스택 존재 여부 확인
      if (skillIds?.length > 0) {
        const skills = await Skill.find({ _id: { $in: skillIds } });
        if (skills.length !== skillIds.length) {
          throw new ValidationError('Some skills not found');
        }
      }

      const job = await Job.create({
        title,
        company: companyId,
        description,
        requirements,
        benefits,
        skills: skillIds,
        location,
        jobType,
        salary,
        deadline,
        status: 'active'
      });

      logger.info('Job created successfully', { jobId: job._id });

      res.status(201).json({
        status: 'success',
        data: { job }
      });
    } catch (error) {
      next(error);
    }
  }

  // 관리자: 채용공고 수정
  async updateJob(req, res, next) {
    try {
      const job = await Job.findByIdAndUpdate(
        req.params.id,
        req.body,
        { new: true, runValidators: true }
      );

      if (!job) {
        throw new NotFoundError('Job not found');
      }

      logger.info('Job updated successfully', { jobId: job._id });

      res.json({
        status: 'success',
        data: { job }
      });
    } catch (error) {
      next(error);
    }
  }

  // 관리자: 채용공고 삭제
  async deleteJob(req, res, next) {
    try {
      const job = await Job.findByIdAndDelete(req.params.id);

      if (!job) {
        throw new NotFoundError('Job not found');
      }

      logger.info('Job deleted successfully', { jobId: req.params.id });

      res.status(204).json({
        status: 'success',
        data: null
      });
    } catch (error) {
      next(error);
    }
  }
}

module.exports = new JobController();