const mongoose = require('mongoose');

const jobSchema = new mongoose.Schema({
  title: {
    type: String,
    required: true,
  },
  company: {
    type: String,
    required: true,
  },
  location: String,
  jobType: String,
  experience: String,
  education: String,
  salary: String,
  skills: [String],
  description: String,
  requirements: [String],
  benefits: [String],
  deadline: Date,
  url: {
    type: String,
    required: true,
    unique: true,
  },
  createdAt: {
    type: Date,
    default: Date.now,
  },
  updatedAt: {
    type: Date,
    default: Date.now,
  },
});

// URL을 기준으로 중복 체크를 위한 인덱스
jobSchema.index({ url: 1 });

module.exports = mongoose.model('Job', jobSchema);