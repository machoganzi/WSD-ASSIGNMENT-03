const mongoose = require('mongoose');

const applicationSchema = new mongoose.Schema({
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
  company: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Company',
    required: true
  },
  status: {
    type: String,
    enum: ['pending', 'reviewing', 'accepted', 'rejected', 'withdrawn'],
    default: 'pending',
    index: true
  },
  resume: {
    file: String,
    version: Number
  },
  coverLetter: {
    type: String
  },
  answers: [{
    question: String,
    answer: String
  }],
  history: [{
    status: String,
    date: Date,
    note: String
  }],
  appliedAt: {
    type: Date,
    default: Date.now,
    index: true
  },
  lastUpdated: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true
});

// 사용자별 중복 지원 방지를 위한 복합 unique 인덱스
applicationSchema.index({ user: 1, job: 1 }, { unique: true });

const Application = mongoose.model('Application', applicationSchema);
module.exports = Application;