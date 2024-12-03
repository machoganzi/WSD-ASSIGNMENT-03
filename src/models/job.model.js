const mongoose = require('mongoose');

const jobSchema = new mongoose.Schema({
  title: {
    type: String,
    required: true,
    index: true
  },
  company: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Company',
    required: true
  },
  category: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Category'
  },
  description: {
    type: String,
    required: true
  },
  requirements: [{
    type: String
  }],
  preferredQualifications: [{
    type: String
  }],
  benefits: [{
    type: String
  }],
  skills: [{
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Skill'
  }],
  location: {
    type: String,
    required: true,
    index: true
  },
  jobType: {
    type: String,
    enum: ['full-time', 'part-time', 'contract', 'internship'],
    required: true
  },
  salary: {
    type: String
  },
  experience: {
    type: String
  },
  education: {
    type: String
  },
  deadline: {
    type: Date,
    required: true
  },
  status: {
    type: String,
    enum: ['active', 'closed', 'draft'],
    default: 'active',
    index: true
  },
  originalUrl: {
    type: String,
    required: true,
    unique: true
  },
  viewCount: {
    type: Number,
    default: 0
  },
  applicationCount: {
    type: Number,
    default: 0
  }
}, {
  timestamps: true
});

// 검색을 위한 복합 인덱스
jobSchema.index({ title: 'text', description: 'text' });
// 위치, 직무유형 기반 검색을 위한 인덱스
jobSchema.index({ location: 1, jobType: 1 });

const Job = mongoose.model('Job', jobSchema);
module.exports = Job;