import json
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import NoSuchElementException, InvalidCookieDomainException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


INDEED_URL = "https://ca.indeed.com"


class JobFinder:
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option("useAutomationExtension", False)
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.execute_script("""Object.defineProperty(navigator, 'webdriver', {get: () => undefined})""")
        self.num_of_pages = 10


    def get_cookies(self):
        """Load Chrome cookies to get session credentials"""
        try:
            self.driver.get(INDEED_URL + "/")
            time.sleep(3)
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
        except Exception as e:
            if e is FileNotFoundError:
                print("cookies not found")
                pass
            elif e is InvalidCookieDomainException:
                self.num_of_pages = 1


    def get_source(self, url: str) -> str:
        """use webdriver to open page and get source, must load get_cookies to log in"""
        self.driver.get(url)
        time.sleep(3)
        return self.driver.page_source


    def find_job(self, data: list[dict], keywords: list, locations: list, radii: list) -> list[dict]:
        """Browse result pages to get raw data including links to job details"""
        known_id = [data[y]['indeed_id'] for y in range(len(data))]
        for location in locations:
            for radius in radii:
                for keyword in keywords:
                    page = 0
                    repeated_pages = 0
                    while page < self.num_of_pages * 10:
                        search_url = f"{INDEED_URL}/jobs?q={keyword}&l={location}%2C%20QC&radius={radius}&start={page}"
                        _soup = BeautifulSoup(self.get_source(url=search_url), 'html.parser')
                        jobs = _soup.find_all("li", class_="css-1ac2h1w eu4oa1w0")
                        if not jobs:
                            break
                        new_jobs_this_page = 0
                        page_ids = []
                        for job in jobs:
                            a_tag = job.find("a", attrs={"data-jk": True})
                            if not a_tag:
                                continue
                            job_id = a_tag["data-jk"]
                            if not job_id:
                                continue
                            if job_id in page_ids:
                                continue
                            page_ids.append(job_id)
                            job_link = a_tag.get("href")
                            if not job_link:
                                continue
                            title = job.find("a", class_="jcs-JobTitle").get_text()
                            company = job.find("span", attrs={"data-testid": "company-name"}).get_text()
                            job_location = (job.find("div", attrs={"data-testid": "text-location"})
                                            .get_text().split("·")[-1].strip())
                            if job_id not in known_id:
                                data.append({
                                    "indeed_id": job_id,
                                    "link": INDEED_URL + job_link,
                                    "title": title,
                                    "company": company,
                                    "location": job_location,
                                    "city": job_location.split(",")[0].strip() if job_location else "",
                                })
                                known_id.append(job_id)
                                new_jobs_this_page += 1
                        if new_jobs_this_page == 0:
                            repeated_pages += 1
                        else:
                            repeated_pages = 0
                        if repeated_pages >= 2:
                            break
                        page += 10
        return data

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

    def get_job(self, *, data: list[dict], keywords: list, locations: list, radii: list):
        """Job finder main function/orchestrator, returns None or new data"""
        self.get_cookies()
        try:
            self.find_job(data, keywords, locations, radii)
            if len(data) == 0:
                return None
            else:
                for x in range(len(data)):
                    if data[x].get('description'):
                        continue
                    link = data[x].get("link")
                    if not link.startswith(INDEED_URL):
                        continue
                    self.get_source(data[x]["link"])
                    data[x] = self.parse_job_detail(data[x])
                data = [job for job in data if job.get("description")]
        finally:
            self.driver.quit()
        return data