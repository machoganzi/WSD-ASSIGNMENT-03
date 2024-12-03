const puppeteer = require('puppeteer');
const Job = require('../models/job.model');
const Company = require('../models/company.model');
require('dotenv').config();
require('../config/database')();

class Crawler {
  constructor() {
    this.baseUrl = 'https://www.saramin.co.kr/zf_user/jobs/list/job-category';
    this.browser = null;
    this.page = null;
  }

  async initialize() {
    this.browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    this.page = await this.browser.newPage();
    await this.page.setViewport({ width: 1920, height: 1080 });
  }

  async close() {
    if (this.browser) {
      await this.browser.close();
    }
  }

  async extractJobDetails(url) {
    try {
      await this.page.goto(url, { waitUntil: 'networkidle0' });
      
      // 채용공고 상세 정보 추출
      const jobDetails = await this.page.evaluate(() => {
        const title = document.querySelector('.job_tit')?.textContent.trim() || '';
        const company = document.querySelector('.corp_name')?.textContent.trim() || '';
        const location = document.querySelector('.job_condition .work_place')?.textContent.trim() || '';
        const experience = document.querySelector('.job_condition .experience')?.textContent.trim() || '';
        const education = document.querySelector('.job_condition .education')?.textContent.trim() || '';
        
        // 기술스택 추출
        const skills = Array.from(document.querySelectorAll('.skill_wrap .stack'))
          .map(skill => skill.textContent.trim());

        // 상세요구사항 추출
        const requirements = Array.from(document.querySelectorAll('.recruitment-detail__box .recruitment-detail__text'))
          .map(req => req.textContent.trim())
          .filter(Boolean);

        return {
          title,
          company,
          location,
          experience,
          education,
          skills,
          requirements,
          url
        };
      });

      return jobDetails;
    } catch (error) {
      console.error(`Error extracting job details from ${url}:`, error);
      return null;
    }
  }

  async crawlJobListings(maxJobs = 100) {
    try {
      console.log('Starting to crawl job listings...');
      const jobUrls = new Set();
      let page = 1;

      while (jobUrls.size < maxJobs) {
        const pageUrl = `${this.baseUrl}?page=${page}`;
        await this.page.goto(pageUrl, { waitUntil: 'networkidle0' });

        // 채용공고 URL 수집
        const newUrls = await this.page.evaluate(() => {
          return Array.from(document.querySelectorAll('.notification_info .job_tit a'))
            .map(a => a.href)
            .filter(Boolean);
        });

        newUrls.forEach(url => jobUrls.add(url));
        
        if (newUrls.length === 0) break;
        page++;
        
        console.log(`Collected ${jobUrls.size} job URLs so far...`);
        await new Promise(r => setTimeout(r, 1000)); // 1초 대기
      }

      console.log(`Starting to process ${jobUrls.size} jobs...`);
      const jobs = [];

      for (const url of jobUrls) {
        // URL이 이미 DB에 있는지 확인
        const existingJob = await Job.findOne({ url });
        if (existingJob) {
          console.log(`Job already exists: ${url}`);
          continue;
        }

        const jobDetails = await this.extractJobDetails(url);
        if (jobDetails) {
          // 회사 정보 저장
          const company = await Company.findOneAndUpdate(
            { name: jobDetails.company },
            { 
              name: jobDetails.company,
              location: jobDetails.location 
            },
            { upsert: true, new: true }
          );

          // 채용공고 저장
          const job = new Job({
            ...jobDetails,
            company: company._id
          });
          await job.save();
          jobs.push(job);

          console.log(`Saved job: ${jobDetails.title}`);
          await new Promise(r => setTimeout(r, 1000)); // 1초 대기
        }

        if (jobs.length >= maxJobs) break;
      }

      console.log(`Successfully crawled and saved ${jobs.length} jobs`);
      return jobs;
    } catch (error) {
      console.error('Error crawling job listings:', error);
      throw error;
    }
  }
}

// 크롤러 실행 함수
async function runCrawler() {
  const crawler = new Crawler();
  try {
    await crawler.initialize();
    await crawler.crawlJobListings();
  } catch (error) {
    console.error('Crawler failed:', error);
  } finally {
    await crawler.close();
    process.exit(0);
  }
}

// 스크립트가 직접 실행될 때만 크롤러 실행
if (require.main === module) {
  runCrawler();
}

module.exports = Crawler;