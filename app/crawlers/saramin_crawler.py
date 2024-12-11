import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import time
import random
import re
from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By 
# Chrome 옵션 설정
chrome_options = Options()
service = Service()  # ChromeDriver 경로를 자동으로 관리

# WebDriver 초기화
driver = webdriver.Chrome(service=service, options=chrome_options)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SaraminCrawler:
    def __init__(self, db):
        """크롤러 초기화"""
        self.db = db
        self.base_url = "https://www.saramin.co.kr/zf_user/search/recruit"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.saramin.co.kr'
        }
    def _get_job_list_page(self, page: int = 1) -> Optional[BeautifulSoup]:
        """
        사람인 채용공고 목록 페이지를 가져오는 메서드입니다.
        
        이 메서드는 지정된 페이지 번호의 채용공고 목록을 가져오며,
        서버에 과도한 부하를 주지 않기 위해 요청 간격을 조절합니다.
        
        Args:
            page (int): 가져올 페이지 번호 (기본값: 1)
            
        Returns:
            Optional[BeautifulSoup]: 파싱된 HTML 페이지. 실패시 None 반환
        """
        try:
            # 검색 매개변수 설정
            params = {
                'searchword': '개발자',           # 검색어
                'recruitPage': page,              # 페이지 번호
                'searchType': 'search',           # 검색 유형
                'recruitPageCount': '40',         # 페이지당 결과 수
                'recruitSort': 'relation',        # 정렬 기준
                'loc_mcd': '101000',             # 지역 코드 
                'job_type': ''                  # 직종 코드 
            }
            
            # 요청 시도 전 로깅
            logger.info(f"페이지 {page} 데이터 요청 중...")
            
            # HTTP GET 요청 수행
            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers,
                timeout=10                        # 10초 타임아웃 설정
            )
            
            # 응답 상태 확인
            response.raise_for_status()
            
            # 서버 부하 방지를 위한 요청 간격 조절
            time.sleep(random.uniform(1, 2))      # 1~2초 무작위 대기
            
            # 응답 성공 로깅
            logger.info(f"페이지 {page} 데이터 수신 완료")
            
            # HTML 파싱 후 반환
            return BeautifulSoup(response.text, 'html.parser')
            
        except requests.RequestException as e:
            # HTTP 요청 관련 예외 처리
            logger.error(f"페이지 {page} 요청 실패: {str(e)}")
            return None
            
        except Exception as e:
            # 기타 예외 처리
            logger.error(f"페이지 {page} 처리 중 오류 발생: {str(e)}")
            return None


    def _get_normal_page_info(self, url: str) -> Optional[Dict]:
        """Selenium을 사용하여 채용공고의 상세 내용과 주요 정보를 추출합니다."""
        try:
            normal_info = {
                'salary_text': '',
                'conditions': {
                    'location': '',
                    'job_type': '',
                    'work_shift': ''
                }
            }

            chrome_options = Options()
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument('--ignore-ssl-errors')
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.implicitly_wait(10)
            
            try:
                driver.get(url)
                time.sleep(2)
                
                # jv_summary 영역에서 정보 추출
                summary_section = driver.find_element(By.CLASS_NAME, "jv_summary")
                dl_elements = summary_section.find_elements(By.TAG_NAME, "dl")
                
                try:
                    for dl in dl_elements:
                        # 제목(dt)과 내용(dd) 추출
                        dt = dl.find_element(By.TAG_NAME, "dt").text.strip()
                        dd = dl.find_element(By.TAG_NAME, "dd").text.strip()
                        
                        # 각 정보 매핑
                        if "급여" in dt:
                            normal_info['salary_text'] = dd
                        elif "근무형태" in dt:
                            normal_info['conditions']['job_type'] = dd
                        elif "근무지역" in dt:
                            # '지도' 텍스트 제거
                            location = dd.replace('지도', '').strip()
                            normal_info['conditions']['location'] = location
                        elif any(keyword in dt for keyword in ["근무일시", "근무시간"]):  # 근무일시 정보 추가
                            normal_info['conditions']['work_shift'] = dd

                    # 기본값 설정
                    if not normal_info['salary_text']:
                        normal_info['salary_text'] = "급여 정보 없음"
                    if not normal_info['conditions']['location']:
                        normal_info['conditions']['location'] = "지역 정보 없음"
                    if not normal_info['conditions']['job_type']:
                        normal_info['conditions']['job_type'] = "근무형태 정보 없음"
                    if not normal_info['conditions']['work_shift']:
                        normal_info['conditions']['work_shift'] = "근무시간 정보 없음"

                except Exception as e:
                    print(f"상세 정보 추출 중 오류 발생: {str(e)}")
                    
                return normal_info

            except Exception as e:
                print(f"페이지 로드 중 오류 발생: {str(e)}")
                return None
                
            finally:
                driver.quit()

        except Exception as e:
            print(f"채용공고 정보 추출 실패: {str(e)}")
            return None
        

    def _get_job_detail(self, url: str) -> Optional[Dict]:
        """채용공고 상세 정보를 가져옵니다"""
        try:
            detail_info = {
                'detail_location': '',
                'description': '',
                'requirements': [],
                'preferred': [],
                'benefits': [],
                'tasks': [],
                'process': []
            }

            chrome_options = Options()
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument('--ignore-ssl-errors')
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.implicitly_wait(10)
            
            try:
                driver.get(url)
                time.sleep(2)
                
                # iframe으로 전환
                driver.switch_to.frame("iframe_content_0")
                
                # 상세 내용 가져오기
                content = driver.find_element(By.CLASS_NAME, "user_content")
                if content:
                    content_text = content.text
                    lines = [line.strip() for line in content_text.split('\n') if line.strip()]
                    
                    current_section = None
                    section_content = []
                    description_lines = []
                    skip_keywords = [
                        '모집부문', '기타사항','근무조건', '근무 조건', '근무형태', '근무 형태', '마감일 및 근무지', '근무시간', '근무지역', '근무일시','유의사항', '기타안내', '상세정보', '채용정보','참고사항', '문의사항', '안내사항', '접수안내','지원안내', '담당자', '문의처', '기업정보', '회사정보','채용담당', '보훈', '장애'
                    ]

                    for line in lines:
                        # 불필요한 키워드 포함 시 건너뛰기
                        if any(keyword in line for keyword in skip_keywords):
                            continue
                        
                        # 근무지 정보 추출
                        if '근무지역' in line and ':' in line:
                            detail_info['detail_location'] = line.split(':', 1)[1].strip()
                            continue
                        
                        # 섹션 구분자 매칭
                        if re.search(r'(담당업무|주요업무|직무내용)', line):
                            if current_section and section_content:
                                detail_info[current_section] = section_content
                            current_section = 'tasks'
                            section_content = []
                        elif re.search(r'(자격요건|필수사항|공통 자격요건)', line):
                            if current_section and section_content:
                                detail_info[current_section] = section_content
                            current_section = 'requirements'
                            section_content = []
                        elif re.search(r'(우대사항|공통 우대사항)', line):
                            if current_section and section_content:
                                detail_info[current_section] = section_content
                            current_section = 'preferred'
                            section_content = []
                        elif re.search(r'(복리후생|복지|혜택|제도 및 환경|복지제도)', line):
                            if current_section and section_content:
                                detail_info[current_section] = section_content
                            current_section = 'benefits'
                            section_content = []
                        elif re.search(r'(전형절차|접수기간 및 방법|함께하기 위한 방법)', line):
                            if current_section and section_content:
                                detail_info[current_section] = section_content
                            current_section = 'process'
                            section_content = []

                        # 섹션 내 내용 추가
                        if current_section:
                            section_content.append(line)
                        else:
                            # 섹션이 정해지지 않은 경우 설명(description)에 추가
                            description_lines.append(line)

                    # 마지막 섹션 저장
                    if current_section and section_content:
                        detail_info[current_section] = section_content

                    # 설명(description) 저장
                    if description_lines:
                        detail_info['description'] = '\n'.join(description_lines)

                    return detail_info

            except Exception as e:
                print(f"상세 내용 추출 중 오류 발생: {str(e)}")
                return None
                    
            finally:
                driver.quit()

        except Exception as e:
            print(f"채용공고 상세 정보 추출 실패: {str(e)}")
            return None




    def _parse_job_condition(self, condition_element) -> Dict:
        """직무 조건 정보를 파싱합니다"""
        conditions = {
            'experience': '',
            'education': '',
            'location': '',
            'job_type': '',
        }
        
        try:
            # 기본 조건 정보 수집 (지역, 경력, 학력, 고용형태)
            condition_spans = condition_element.select('span')
            if len(condition_spans) > 0:
                conditions['location'] = condition_spans[0].text.strip()
            if len(condition_spans) > 1:
                conditions['experience'] = condition_spans[1].text.strip()
            if len(condition_spans) > 2:
                conditions['education'] = condition_spans[2].text.strip()
            if len(condition_spans) > 3:
                conditions['job_type'] = condition_spans[3].text.strip()
                
        except Exception as e:
            logger.error(f"직무 조건 파싱 실패: {str(e)}")
        
        return conditions

    def _save_job_posting(self, job_data: Dict) -> bool:
        """채용공고 정보를 데이터베이스에 저장합니다"""
        try:
            # 회사 정보 저장
            company_result = self.db.companies.update_one(
                {'name': job_data['company_name']},
                {'$set': {
                    'name': job_data['company_name'],
                    'location': job_data.get('location', ''),
                    'updated_at': datetime.now()
                }},
                upsert=True
            )

            company_id = str(company_result.upserted_id or 
                        self.db.companies.find_one({'name': job_data['company_name']})['_id'])

            # 마감일 처리
            deadline = job_data.get('deadline', '')
            try:
                if deadline and '~' in deadline:
                    deadline_date = datetime.strptime(
                        deadline.split('~')[1].strip(),
                        '%Y.%m.%d'
                    )
                else:
                    deadline_date = None
            except:
                deadline_date = None

            # 채용공고 저장 
            job_posting = {
                'company_id': company_id,
                'company_name': job_data['company_name'],
                'title': job_data['title'],
                'description': job_data.get('description', ''),
                'requirements': job_data.get('requirements', []),
                'preferred': job_data.get('preferred', []),
                'benefits': job_data.get('benefits', []),
                'tasks': job_data.get('tasks', []),
                'process': job_data.get('process', []), 
                'salary_text': job_data.get('salary_text', ''),
                'location': job_data.get('location', ''),
                'job_type': job_data.get('job_type', ''),
                'experience_level': job_data.get('experience', ''),
                'education': job_data.get('education', ''),
                'detail_location': job_data.get('detail_location', ''),
                'skills': job_data.get('skills', []),
                'sector': job_data.get('sector', ''),
                'deadline': deadline,
                'deadline_timestamp': deadline_date,
                'original_url': job_data.get('original_url', ''),
                'status': 'active',
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'conditions': {  # 근무조건 상세 정보 추가
                    'location': job_data.get('conditions', {}).get('location', ''),
                    'job_type': job_data.get('conditions', {}).get('job_type', ''),
                    'work_shift': job_data.get('conditions', {}).get('work_shift', '')
                }
            }

            result = self.db.job_postings.update_one(
                {
                    'company_id': company_id,
                    'title': job_data['title']
                },
                {'$set': job_posting},
                upsert=True
            )

            return bool(result.upserted_id or result.modified_count)

        except Exception as e:
            logger.error(f"채용공고 저장 실패: {str(e)}")
            return False

    def crawl(self, max_pages: int = 5) -> int:
        """채용공고를 크롤링합니다"""
        total_jobs = 0
        page = 1
        
        while page <= max_pages:
            soup = self._get_job_list_page(page)
            if not soup:
                page += 1
                continue

            job_elements = soup.select('.item_recruit')
            if not job_elements:
                logger.info("더 이상 채용공고가 없습니다.")
                break

            for job_element in job_elements:
                try:
                    # 기본 정보 추출
                    title_element = job_element.select_one('.job_tit a')
                    company_element = job_element.select_one('.corp_name a')
                    condition_element = job_element.select_one('.job_condition')
                    sector_element = job_element.select_one('.job_sector')
                    deadline_element = job_element.select_one('.job_date .date')
                    
                    if not all([title_element, company_element, condition_element]):
                        continue

                    # 상세/노멀 페이지 URL과 상세 정보
                    job_url = 'https://www.saramin.co.kr' + title_element['href']
                    detail_info = self._get_job_detail(job_url) or {}
                    normal_info = self._get_normal_page_info(job_url) or {}

                    # 직무 조건 파싱
                    conditions = self._parse_job_condition(condition_element)

                    # 채용공고 데이터 구성
                    job_data = {
                        'title': title_element.text.strip(),
                        'company_name': company_element.text.strip(),
                        'description': detail_info.get('description', ''),
                        'requirements': detail_info.get('requirements', []),
                        'preferred': detail_info.get('preferred', []),
                        'benefits': detail_info.get('benefits', []),
                        'process': detail_info.get('process', []),
                        'original_url': job_url,
                        'salary_text': normal_info.get('salary_text', ''),
                        'sector': sector_element.text.strip() if sector_element else '',
                        'skills': [skill.strip() for skill in sector_element.text.split(',')] if sector_element else [],
                        'deadline': deadline_element.text.strip() if deadline_element else '',
                        'detail_location': detail_info.get('detail_location', ''),
                        # normal_info의 conditions 정보도 추가
                        'conditions': normal_info.get('conditions', {}),  # conditions 정보 직접 할당
                        **conditions
                    }

                    # 상세 페이지에서 가져온 추가 정보로 업데이트
                    detailed_conditions = detail_info.get('conditions', {})
                    if detailed_conditions.get('location'):
                        job_data['location'] = detailed_conditions['location']
                    if detailed_conditions.get('job_type'):
                        job_data['job_type'] = detailed_conditions['job_type']
                    if detailed_conditions.get('work_shift'):
                        job_data['work_shift'] = detailed_conditions['work_shift']
                    
                    # 마감일 정보가 상세 페이지에 있으면 업데이트
                    if detail_info.get('deadline'):
                        job_data['deadline'] = detail_info['deadline']

                    # 데이터베이스에 저장하고 결과 로깅
                    if self._save_job_posting(job_data):
                        total_jobs += 1
                        logger.info(
                            f"채용공고 저장 완료: {job_data['title']} at {job_data['company_name']}\n"
                            f"- 지역: {job_data.get('location', 'N/A')}\n"
                            f"- 경력: {job_data.get('experience', 'N/A')}\n"
                            f"- 연봉: {job_data.get('salary_text', 'N/A')}\n"
                            f"- 마감일: {job_data.get('deadline', 'N/A')}"
                        )

                    # 수집 제한에 도달하면 종료
                    if total_jobs >= 100:
                        logger.info(f"목표 수집량({total_jobs}개) 달성")
                        return total_jobs

                except Exception as e:
                    logger.error(f"채용공고 처리 중 오류 발생: {str(e)}")
                    continue

            # 다음 페이지로 이동 전 대기
            page += 1
            time.sleep(random.uniform(2, 4))

        logger.info(f"크롤링 완료. 총 {total_jobs}개의 채용공고 수집")
        return total_jobs