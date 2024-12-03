const mongoose = require('mongoose');

const categorySchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    unique: true,
    trim: true
  },
  code: {
    type: String,
    required: true,
    unique: true
  },
  parent: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Category',
    default: null
  },
  level: {
    type: Number,
    required: true,
    default: 1
  },
  path: [{
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Category'
  }],
  description: String,
  jobCount: {
    type: Number,
    default: 0,
    index: true
  },
  isActive: {
    type: Boolean,
    default: true
  }
}, {
  timestamps: true
});

// 카테고리 검색을 위한 텍스트 인덱스
categorySchema.index({ name: 'text', description: 'text' });
// 계층 구조 검색을 위한 인덱스
categorySchema.index({ parent: 1, level: 1 });

const Category = mongoose.model('Category', categorySchema);
module.exports = Category;