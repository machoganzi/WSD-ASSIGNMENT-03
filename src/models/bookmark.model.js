const mongoose = require('mongoose');

const bookmarkSchema = new mongoose.Schema({
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  job: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Job',
    required: true
  },
  note: {
    type: String
  },
  tags: [{
    type: String
  }],
  isActive: {
    type: Boolean,
    default: true,
    index: true
  },
  bookmarkedAt: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true
});

// 사용자별 중복 북마크 방지를 위한 복합 unique 인덱스
bookmarkSchema.index({ user: 1, job: 1 }, { unique: true });

const Bookmark = mongoose.model('Bookmark', bookmarkSchema);
module.exports = Bookmark;