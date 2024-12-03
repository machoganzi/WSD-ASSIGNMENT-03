const puppeteer = require('puppeteer');
const { Job, Company, Category, Skill } = require('../models');
const logger = require('../utils/logger');

class CrawlerService {
  constructor() {
    this.browser = null;
    this.page = null;
    this.baseUrl = 'https://www.saramin.co.kr/zf_user/jobs/list/job-category';
    this.jobsPerPage = 20;
  }

  async initialize() {
    try {
      this.browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox']
      });
      this.page = await this.browser.newPage();
      await this.page.setViewport({ width: 1920, height: 1080 });
      await this.page.setDefaultNavigationTimeout(30000);
      
      logger.info('Browser initialized successfully');
    } catch (error) {
      logger.error('Failed to initialize browser', { error: error.message });
      throw error;
    }
  }

  async close() {
    if (this.browser) {
      await this.browser.close();
      logger.info('Browser closed successfully');
    }
  }

  async extractJobDetails(jobUrl) {
    try {
      await this.page.goto(jobUrl, { waitUntil: 'networkidle0' });
      
      const jobData = await this.page.evaluate(() => {
        const getTextContent = selector => {
          const element = document.querySelector(selector);
          return element ? element.textContent.trim() : '';
        };

        const getArrayContent = selector => {
          return Array.from(document.querySelectorAll(selector))
            .map(el => el.textContent.trim())
            .filter(Boolean);
        };

        return {
          title: getTextContent('.job_tit'),
          companyName: getTextContent('.corp_name'),
          location: getTextContent('.work_place'),
          experience: getTextContent('.experience'),
          education: getTextContent('.education'),
          workType: getTextContent('.work_type'),
          skills: getArrayContent('.skill_wrap .stack'),
          requirements: getArrayContent('.recruitment-detail__box .recruitment-detail__requirements li'),
          benefits: getArrayContent('.recruitment-detail__box .recruitment-detail__benefits li'),
          description: getTextContent('.recruitment-detail__text'),
          deadline: getTextContent('.deadline'),
          originalUrl: window.location.href
        };
      });

      // 날짜 포맷 처리
      jobData.deadline = this.parseDeadline(jobData.deadline);
      
      logger.info('Job details extracted successfully', { url: jobUrl });
      return jobData;
    } catch (error) {
      logger.error('Failed to extract job details', { url: jobUrl, error: error.message });
      return null;
    }
  }

  parseDeadline(deadlineStr) {
    // 마감일자 문자열을 Date 객체로 변환하는 로직
    try {
      const date = new Date(deadlineStr);
      return isNaN(date) ? null : date;
    } catch (error) {
      return null;
    }
  }

  async saveJobData(jobData) {
    try {
      // 회사 정보 저장 또는 업데이트
      const company = await Company.findOneAndUpdate(
        { name: jobData.companyName },
        {
          name: jobData.companyName,
          'location.address': jobData.location
        },
        { upsert: true, new: true }
      );

      // 스킬 정보 처리
      const skillPromises = jobData.skills.map(skillName =>
        Skill.findOneAndUpdate(
          { name: skillName },
          { 
            name: skillName,
            category: 'programming',
            $inc: { useCount: 1 }
          },
          { upsert: true, new: true }
        )
      );
      const skills = await Promise.all(skillPromises);

      // 채용공고 저장
      const job = new Job({
        title: jobData.title,
        company: company._id,
        description: jobData.description,
        requirements: jobData.requirements,
        benefits: jobData.benefits,
        skills: skills.map(skill => skill._id),
        location: jobData.location,
        experience: jobData.experience,
        education: jobData.education,
        jobType: this.normalizeJobType(jobData.workType),
        deadline: jobData.deadline,
        originalUrl: jobData.originalUrl,
        status: 'active'
      });

      await job.save();
      logger.info('Job data saved successfully', { jobId: job._id });
      return job;
    } catch (error) {
      logger.error('Failed to save job data', { error: error.message });
      throw error;
    }
  }

  normalizeJobType(workType) {
    // 직무형태 정규화
    if (workType.includes('정규')) return 'full-time';
    if (workType.includes('계약')) return 'contract';
    if (workType.includes('인턴')) return 'internship';
    if (workType.includes('파트')) return 'part-time';
    return 'full-time';
  }

  async crawlJobs(targetCount = 100) {
    try {
      logger.info('Starting job crawling', { targetCount });
      let jobsProcessed = 0;
      let page = 1;
      const processedUrls = new Set();

      while (jobsProcessed < targetCount) {
        const pageUrl = `${this.baseUrl}?page=${page}`;
        await this.page.goto(pageUrl, { waitUntil: 'networkidle0' });

        const jobUrls = await this.page.evaluate(() => {
          return Array.from(document.querySelectorAll('.notification_info .job_tit a'))
            .map(a => a.href)
            .filter(Boolean);
        });

        for (const url of jobUrls) {
          if (processedUrls.has(url)) continue;
          processedUrls.add(url);

          const jobData = await this.extractJobDetails(url);
          if (jobData) {
            await this.saveJobData(jobData);
            jobsProcessed++;
            
            logger.info('Job processed', { 
              processed: jobsProcessed, 
              target: targetCount 
            });

            if (jobsProcessed >= targetCount) break;
          }

          // 요청 간격 조절
          await new Promise(r => setTimeout(r, 1000));
        }

        page++;
      }

      logger.info('Job crawling completed', { 
        totalProcessed: jobsProcessed 
      });
    } catch (error) {
      logger.error('Crawling process failed', { error: error.message });
      throw error;
    }
  }
}

module.exports = CrawlerService;