import json
import time
from bs4 import BeautifulSoup
from selenium import webdriver
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


    def get_cookies(self):
        try:
            self.driver.get("https://ca.indeed.com")
            with open("cookies.json", "r") as cookie_file:
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
            pass


    def get_source(self, url: str) -> str:
        """use webdriver to open page and get source, load get_cookies first"""
        self.driver.get(url)
        time.sleep(3)
        return self.driver.page_source


    def find_job(self, keywords, locations, radii, data):
        known_id = [data[y]['id'] for y in range(len(data))]
        for keyword in keywords:
            for location in locations:
                for radius in radii:
                    page = 0
                    while page <= 50:
                        search_url = f"{INDEED_URL}/jobs?q={keyword}&l={location}%2C%20QC&radius={radius}&start={page}"
                        _soup = BeautifulSoup(self.get_source(url=search_url), 'html.parser')
                        jobs = _soup.find_all("li", class_="css-1ac2h1w eu4oa1w0")
                        for job in jobs:
                            a_tag = job.find("a", attrs={"data-jk": True})
                            if not a_tag:
                                continue
                            job_id = a_tag["data-jk"]
                            if not job_id:
                                continue
                            job_link = a_tag.get("href")
                            if not job_link:
                                continue
                            title = job.find("a", class_="jcs-JobTitle").get_text()
                            company = job.find("span", attrs={"data-testid": "company-name"}).get_text()
                            job_location = job.find("div", attrs={"data-testid": "text-location"}).get_text()
                            if job_id not in known_id:
                                data.append({
                                    "id": job_id,
                                    "link": INDEED_URL + job_link,
                                    "title": title,
                                    "company": company,
                                    "location": job_location
                                })
                                known_id.append(job_id)
                        page += 10
        return data


    @staticmethod
    def get_text_from_selector(soup, css_selector):
        element = soup.select_one(css_selector)
        if element is None:
            return None
        return element.get_text()


    def parse_job_detail(self, job_data):
        try:
            show_more = self.driver.find_element(
                By.CSS_SELECTOR,
                '[aria-label="Skills"] button.js-match-insights-provider-1s05l8k'
            )
            self.driver.execute_script("arguments[0].click();", show_more)
        except Exception as e:
            print(e)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        job_type = self.get_text_from_selector(soup, "#salaryInfoAndJobType")
        description = self.get_text_from_selector(soup, "#jobDescriptionText")
        skills = ""
        for btn in soup.select('[aria-label="Skills"] button[data-testid$="-tile"]'):
            label = btn.get_text(strip=True)
            skills += label + ", "
        skills = skills[:-2] if skills else None
        job_data.update({
            "job_type": job_type,
            "skills": skills,
            "description": description,
            "time_stamp": int(str(time.time()).split('.')[0]),
            "is_applied": False
        })
        return job_data


    @staticmethod
    def load_job_data() -> list:
        try:
            with open("jobs.json", "r", encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            data = []
        return data


    def get_job(self, search_keywords, search_locations, search_radii):
        data = self.load_job_data()
        self.find_job(search_keywords, search_locations, search_radii, data)
        if len(data) == 0:
            return None
        else:
            for x in range(len(data)):
                if data[x].get('description'):
                    continue
                self.get_source(data[x]["link"])
                data[x] = self.parse_job_detail(data[x])
            data = [job for job in data if job.get("description")]
            with open("jobs.json", "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            return None


    def job_finder(self, search_keywords, search_locations, search_radii,):
        """run the job finder"""
        self.get_cookies()
        self.get_job(search_keywords, search_locations, search_radii)
        self.driver.quit()
        return