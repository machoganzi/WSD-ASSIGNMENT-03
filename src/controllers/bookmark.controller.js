const { Bookmark, Job, User } = require('../models');
const { NotFoundError, ValidationError } = require('../utils/errors');
const logger = require('../utils/logger');

class BookmarkController {
  // 북마크 추가/제거 (토글)
  async toggleBookmark(req, res, next) {
    try {
      const { jobId } = req.params;
      const userId = req.user._id;

      // 채용공고 존재 확인
      const job = await Job.findById(jobId);
      if (!job) {
        throw new NotFoundError('Job not found');
      }

      // 기존 북마크 확인
      const existingBookmark = await Bookmark.findOne({
        user: userId,
        job: jobId
      });

      if (existingBookmark) {
        // 북마크 제거
        await Bookmark.findByIdAndDelete(existingBookmark._id);
        await User.findByIdAndUpdate(userId, {
          $pull: { bookmarks: existingBookmark._id }
        });

        logger.info('Bookmark removed', {
          userId,
          jobId,
          bookmarkId: existingBookmark._id
        });

        return res.json({
          status: 'success',
          message: 'Bookmark removed successfully',
          data: { isBookmarked: false }
        });
      }

      // 새 북마크 추가
      const bookmark = await Bookmark.create({
        user: userId,
        job: jobId,
        bookmarkedAt: new Date()
      });

      // 사용자의 북마크 목록 업데이트
      await User.findByIdAndUpdate(userId, {
        $push: { bookmarks: bookmark._id }
      });

      logger.info('Bookmark added', {
        userId,
        jobId,
        bookmarkId: bookmark._id
      });

      res.status(201).json({
        status: 'success',
        message: 'Bookmark added successfully',
        data: { 
          isBookmarked: true,
          bookmark 
        }
      });
    } catch (error) {
      next(error);
    }
  }

  // 북마크 목록 조회
  async getBookmarks(req, res, next) {
    try {
      const { page = 1, limit = 20, sort = '-bookmarkedAt' } = req.query;
      const skip = (page - 1) * limit;

      const [bookmarks, total] = await Promise.all([
        Bookmark.find({ user: req.user._id })
          .sort(sort)
          .skip(skip)
          .limit(parseInt(limit))
          .populate({
            path: 'job',
            populate: {
              path: 'company',
              select: 'name location'
            }
          }),
        Bookmark.countDocuments({ user: req.user._id })
      ]);

      res.json({
        status: 'success',
        data: {
          bookmarks,
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

  // 북마크 상태 확인
  async checkBookmarkStatus(req, res, next) {
    try {
      const { jobId } = req.params;
      const bookmark = await Bookmark.findOne({
        user: req.user._id,
        job: jobId
      });

      res.json({
        status: 'success',
        data: {
          isBookmarked: !!bookmark
        }
      });
    } catch (error) {
      next(error);
    }
  }

  // 북마크에 메모 추가/수정
  async updateBookmarkNote(req, res, next) {
    try {
      const { note } = req.body;
      const bookmark = await Bookmark.findOneAndUpdate(
        {
          _id: req.params.id,
          user: req.user._id
        },
        { note },
        { new: true }
      );

      if (!bookmark) {
        throw new NotFoundError('Bookmark not found');
      }

      logger.info('Bookmark note updated', {
        bookmarkId: bookmark._id,
        userId: req.user._id
      });

      res.json({
        status: 'success',
        data: { bookmark }
      });
    } catch (error) {
      next(error);
    }
  }

  // 북마크 태그 관리
  async updateBookmarkTags(req, res, next) {
    try {
      const { tags } = req.body;
      const bookmark = await Bookmark.findOneAndUpdate(
        {
          _id: req.params.id,
          user: req.user._id
        },
        { tags },
        { new: true }
      );

      if (!bookmark) {
        throw new NotFoundError('Bookmark not found');
      }

      logger.info('Bookmark tags updated', {
        bookmarkId: bookmark._id,
        userId: req.user._id
      });

      res.json({
        status: 'success',
        data: { bookmark }
      });
    } catch (error) {
      next(error);
    }
  }

  // 북마크 일괄 삭제
  async deleteBookmarks(req, res, next) {
    try {
      const { bookmarkIds } = req.body;

      if (!Array.isArray(bookmarkIds) || bookmarkIds.length === 0) {
        throw new ValidationError('Invalid bookmark IDs');
      }

      const result = await Bookmark.deleteMany({
        _id: { $in: bookmarkIds },
        user: req.user._id
      });

      // 사용자의 북마크 목록 업데이트
      await User.findByIdAndUpdate(req.user._id, {
        $pull: { bookmarks: { $in: bookmarkIds } }
      });

      logger.info('Bookmarks deleted', {
        userId: req.user._id,
        count: result.deletedCount
      });

      res.json({
        status: 'success',
        message: `${result.deletedCount} bookmarks deleted successfully`
      });
    } catch (error) {
      next(error);
    }
  }
}

module.exports = new BookmarkController();