import json
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import NoSuchElementException, InvalidCookieDomainException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By



class JobFinder:
    def __init__(self, indeed_url):
        self.options = Options()
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option("useAutomationExtension", False)
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.execute_script("""Object.defineProperty(navigator, 'webdriver', {get: () => undefined})""")
        self.num_of_pages = 10
        self.url = indeed_url


    def is_security_check(self) -> bool:
        html = self.driver.page_source.lower()
        title = self.driver.title.lower()
        return (
                "security check" in title
                or "additional verification required" in html
                or "cf-box-container" in html
                )


    def wait_for_manual_resolution(self):
        print("Security check detected → waiting for manual solve...")
        while self.is_security_check():
            time.sleep(2)
        print("Security check cleared → resuming")


    def get_cookies(self):
        try:
            self.driver.get(self.url + "/")
            if self.is_security_check():
                self.wait_for_manual_resolution()
            with open("user/cookies/cookies.json", "r") as cookie_file:
                cookies = json.load(cookie_file)
            for cookie in cookies:
                cookie_dict = {
                    "name": cookie["name"],
                    "value": cookie["value"],
                    "domain": cookie.get("domain", ".indeed.com"),
                    "path": cookie.get("path", "/"),
                }
                if "expirationDate" in cookie:
                    cookie_dict["expiry"] = int(cookie["expirationDate"])
                self.driver.add_cookie(cookie_dict)
            self.driver.refresh()
        except FileNotFoundError:
            print("cookies not found")
        except InvalidCookieDomainException:
            pass


    def get_source(self, url: str) -> str:
        """use webdriver to open page and get source, must load get_cookies to log in"""
        self.driver.get(url)
        if self.is_security_check():
            self.wait_for_manual_resolution()
        return self.driver.page_source


    @staticmethod
    def get_text_from_selector(soup, css_selector):
        element = soup.select_one(css_selector)
        if element is None:
            return None
        return element.get_text()


    def parse_job_detail(self, job_details: dict) -> dict:
        """Browse a job description page to extract its data and complete its entry with the missing information"""
        try:
            show_more = self.driver.find_element(
                By.CSS_SELECTOR,
                '[aria-label="Skills"] button.js-match-insights-provider-1s05l8k'
            )
            self.driver.execute_script("arguments[0].click();", show_more)
        except NoSuchElementException:
            pass
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        job_type = self.get_text_from_selector(soup, "#salaryInfoAndJobType")
        description = self.get_text_from_selector(soup, "#jobDescriptionText")
        skills = ""
        for btn in soup.select('[aria-label="Skills"] button[data-testid$="-tile"]'):
            label = btn.get_text(strip=True)
            skills += label + ", "
        skills = skills[:-2] if skills else None
        job_details.update({
            "job_type": job_type,
            "skills": skills,
            "description": description,
            "time_stamp": int(time.time()),
            "is_applied": False
        })
        return job_details


    def search(self, data: list[dict], keyword: str, location: str, radius: str, known_ids, evaluator, db) -> None:
        page = 0
        repeated_pages = 0
        while page < self.num_of_pages * 10:
            search_url = f"{self.url}/jobs?q={keyword}&l={location}%2C%20QC&radius={radius}&start={page}"
            soup = BeautifulSoup(self.get_source(search_url), "html.parser")
            time.sleep(3)
            jobs = soup.find_all("li", class_="css-1ac2h1w eu4oa1w0")
            if not jobs:
                break
            new_jobs_this_page = 0
            page_ids = set()
            for job in jobs:
                a_tag = job.find("a", attrs={"data-jk": True})
                if not a_tag:
                    continue
                job_id = a_tag.get("data-jk")
                if not job_id or job_id in page_ids or job_id in known_ids:
                    continue
                page_ids.add(job_id)
                job_link = a_tag.get("href")
                if not job_link:
                    continue
                title_tag = job.find("a", class_="jcs-JobTitle")
                company_tag = job.find("span", attrs={"data-testid": "company-name"})
                location_tag = job.find("div", attrs={"data-testid": "text-location"})
                if not title_tag or not company_tag or not location_tag:
                    continue
                job_location = location_tag.get_text(strip=True).split("·")[-1].strip()
                job_data = {
                    "indeed_id": job_id,
                    "link": self.url + job_link,
                    "title": title_tag.get_text(strip=True),
                    "company": company_tag.get_text(strip=True),
                    "location": job_location,
                    "city": job_location.split(",")[0].strip() if job_location else "",
                }
                self.get_source(job_data["link"])
                job_data = self.parse_job_detail(job_data)
                if not job_data.get("description"):
                    continue
                evaluated_job = evaluator.get_advice(job_data)
                db.save_job(evaluated_job)
                data.append(evaluated_job)
                known_ids.add(job_id)
                new_jobs_this_page += 1
            if new_jobs_this_page == 0:
                repeated_pages += 1
            else:
                repeated_pages = 0
            if repeated_pages >= 3:
                 break
            page += 10


    def get_job(self, *, keywords: list, locations: list, radii: list, evaluator, db):
        self.get_cookies()
        data = db.load_jobs()
        known_ids = {job["indeed_id"] for job in data}
        try:
            for location in locations:
                for radius in radii:
                    for keyword in keywords:
                        self.search(data, keyword, location, radius, known_ids, evaluator, db)
        finally:
            self.driver.quit()
        return data