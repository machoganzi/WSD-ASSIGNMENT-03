const mongoose = require('mongoose');

const skillSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    unique: true,
    trim: true
  },
  category: {
    type: String,
    enum: ['programming', 'framework', 'database', 'devops', 'tool', 'language', 'other'],
    required: true
  },
  aliases: [{
    type: String,
    trim: true
  }],
  description: String,
  useCount: {
    type: Number,
    default: 0,
    index: true
  },
  isActive: {
    type: Boolean,
    default: true
  },
  relatedSkills: [{
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Skill'
  }]
}, {
  timestamps: true
});

// 스킬 검색을 위한 텍스트 인덱스
skillSchema.index({ name: 'text', aliases: 'text' });

const Skill = mongoose.model('Skill', skillSchema);
module.exports = Skill;