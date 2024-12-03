const mongoose = require('mongoose');

const companySchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    unique: true,
    index: true
  },
  description: {
    type: String
  },
  industry: {
    type: String,
    index: true
  },
  size: {
    type: String,
    enum: ['startup', 'small', 'medium', 'large', 'enterprise']
  },
  foundedYear: Number,
  employeeCount: Number,
  location: {
    address: String,
    city: String,
    country: String
  },
  website: String,
  logo: String,
  contacts: {
    email: String,
    phone: String
  },
  socialMedia: {
    linkedin: String,
    twitter: String,
    facebook: String
  },
  jobPostings: [{
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Job'
  }],
  totalJobCount: {
    type: Number,
    default: 0
  },
  originalUrl: {
    type: String,
    unique: true
  }
}, {
  timestamps: true
});

// 회사명 검색을 위한 텍스트 인덱스
companySchema.index({ name: 'text', description: 'text' });

const Company = mongoose.model('Company', companySchema);
module.exports = Company;