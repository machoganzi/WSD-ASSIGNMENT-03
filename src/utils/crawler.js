require('dotenv').config();
const mongoose = require('mongoose');
const CrawlerService = require('../services/crawler.service');
const logger = require('./logger');

async function runCrawler() {
  try {
    // DB 연결
    await mongoose.connect(process.env.MONGODB_URI);
    logger.info('Connected to MongoDB');

    const crawler = new CrawlerService();
    await crawler.initialize();

    // 크롤링 시작
    const targetCount = process.env.CRAWL_TARGET || 100;
    await crawler.crawlJobs(parseInt(targetCount));

    await crawler.close();
    await mongoose.connection.close();
    
    logger.info('Crawler process completed successfully');
    process.exit(0);
  } catch (error) {
    logger.error('Crawler process failed', { error: error.message });
    process.exit(1);
  }
}

// 스크립트가 직접 실행될 때만 크롤러 실행
if (require.main === module) {
  runCrawler();
}

module.exports = runCrawler;