import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

class JobPostingParserTest(unittest.TestCase):
    def setUp(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument('--ignore-certificate-errors')
        self.chrome_options.add_argument('--ignore-ssl-errors')
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.implicitly_wait(10)

    def tearDown(self):
        if self.driver:
            self.driver.quit()

    def test_job_summary_info(self):
        url = "https://www.saramin.co.kr/zf_user/jobs/relay/view?view_type=search&rec_idx=49458119"
        
        try:
            print(f"\n=== URL 테스트 시작: {url} ===")
            self.driver.get(url)
            time.sleep(2)

            # jv_summary 영역 찾기
            summary_section = self.driver.find_element(By.CLASS_NAME, "jv_summary")
            
            print("\n=== 핵심 정보 섹션 분석 ===")
            
            # dl 태그들 찾기
            dl_elements = summary_section.find_elements(By.TAG_NAME, "dl")
            print(f"\n발견된 dl 태그 수: {len(dl_elements)}")
            
            for dl in dl_elements:
                try:
                    dt = dl.find_element(By.TAG_NAME, "dt").text
                    dd = dl.find_element(By.TAG_NAME, "dd").text
                    print(f"\n{dt}:")
                    print(f"- {dd}")
                except Exception as e:
                    print(f"정보 추출 실패: {str(e)}")
            
            print("\n=== 전체 HTML 구조 ===")
            print(summary_section.get_attribute('outerHTML'))

        except Exception as e:
            print(f"테스트 실행 중 오류 발생: {str(e)}")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)