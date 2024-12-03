const { Application, Job, User } = require('../models');
const { NotFoundError, ValidationError } = require('../utils/errors');
const logger = require('../utils/logger');

class ApplicationController {
  // 지원서 제출
  async apply(req, res, next) {
    try {
      const { jobId } = req.params;
      const { coverLetter } = req.body;
      const userId = req.user._id;

      // 채용공고 존재 여부 확인
      const job = await Job.findById(jobId);
      if (!job) {
        throw new NotFoundError('Job not found');
      }

      // 이미 지원했는지 확인
      const existingApplication = await Application.findOne({
        user: userId,
        job: jobId
      });

      if (existingApplication) {
        throw new ValidationError('You have already applied for this job');
      }

      // 지원서 생성
      const application = await Application.create({
        user: userId,
        job: jobId,
        company: job.company,
        coverLetter,
        status: 'pending',
        history: [{
          status: 'pending',
          date: new Date(),
          note: 'Application submitted'
        }]
      });

      // 사용자와 채용공고의 지원 정보 업데이트
      await Promise.all([
        User.findByIdAndUpdate(userId, {
          $push: { applications: application._id }
        }),
        Job.findByIdAndUpdate(jobId, {
          $inc: { applicationCount: 1 }
        })
      ]);

      logger.info('Application submitted successfully', {
        applicationId: application._id,
        userId,
        jobId
      });

      res.status(201).json({
        status: 'success',
        data: { application }
      });
    } catch (error) {
      next(error);
    }
  }

  // 내 지원 목록 조회
  async getMyApplications(req, res, next) {
    try {
      const { status, sort = '-appliedAt', page = 1, limit = 10 } = req.query;
      const query = { user: req.user._id };

      if (status) {
        query.status = status;
      }

      const skip = (page - 1) * limit;

      const [applications, total] = await Promise.all([
        Application.find(query)
          .sort(sort)
          .skip(skip)
          .limit(parseInt(limit))
          .populate('job', 'title company deadline')
          .populate('company', 'name'),
        Application.countDocuments(query)
      ]);

      res.json({
        status: 'success',
        data: {
          applications,
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

  // 지원서 상세 조회
  async getApplication(req, res, next) {
    try {
      const application = await Application.findOne({
        _id: req.params.id,
        user: req.user._id
      })
        .populate('job')
        .populate('company');

      if (!application) {
        throw new NotFoundError('Application not found');
      }

      res.json({
        status: 'success',
        data: { application }
      });
    } catch (error) {
      next(error);
    }
  }

  // 지원 취소
  async withdrawApplication(req, res, next) {
    try {
      const application = await Application.findOne({
        _id: req.params.id,
        user: req.user._id
      });

      if (!application) {
        throw new NotFoundError('Application not found');
      }

      if (application.status !== 'pending') {
        throw new ValidationError('Cannot withdraw application at current status');
      }

      // 상태 업데이트
      application.status = 'withdrawn';
      application.history.push({
        status: 'withdrawn',
        date: new Date(),
        note: 'Application withdrawn by candidate'
      });

      await application.save();

      // 채용공고의 지원자 수 감소
      await Job.findByIdAndUpdate(application.job, {
        $inc: { applicationCount: -1 }
      });

      logger.info('Application withdrawn successfully', {
        applicationId: application._id,
        userId: req.user._id
      });

      res.json({
        status: 'success',
        message: 'Application withdrawn successfully'
      });
    } catch (error) {
      next(error);
    }
  }

  // 지원서 업데이트 (커버레터 수정)
  async updateApplication(req, res, next) {
    try {
      const { coverLetter } = req.body;
      const application = await Application.findOne({
        _id: req.params.id,
        user: req.user._id
      });

      if (!application) {
        throw new NotFoundError('Application not found');
      }

      if (application.status !== 'pending') {
        throw new ValidationError('Cannot update application at current status');
      }

      application.coverLetter = coverLetter;
      application.history.push({
        status: application.status,
        date: new Date(),
        note: 'Cover letter updated'
      });

      await application.save();

      logger.info('Application updated successfully', {
        applicationId: application._id,
        userId: req.user._id
      });

      res.json({
        status: 'success',
        data: { application }
      });
    } catch (error) {
      next(error);
    }
  }

  // 관리자: 지원 상태 변경
  async updateApplicationStatus(req, res, next) {
    try {
      const { status, note } = req.body;
      const application = await Application.findById(req.params.id);

      if (!application) {
        throw new NotFoundError('Application not found');
      }

      application.status = status;
      application.history.push({
        status,
        date: new Date(),
        note: note || `Status updated to ${status}`
      });

      await application.save();

      logger.info('Application status updated', {
        applicationId: application._id,
        status
      });

      res.json({
        status: 'success',
        data: { application }
      });
    } catch (error) {
      next(error);
    }
  }
}

module.exports = new ApplicationController();