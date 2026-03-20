import json
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import NoSuchElementException, InvalidCookieDomainException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


class JobFinder:
    """Indeed scraping helpers."""
    def __init__(self, indeed_url):
        self.options = Options()

        # Configure Chrome to reduce basic automation fingerprints.
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option("useAutomationExtension", False)
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.execute_script("""Object.defineProperty(navigator, 'webdriver', {get: () => undefined})""")
        self.num_of_pages = 10
        self.url = indeed_url


    def is_security_check(self) -> bool:
        """Detect common anti-bot challenge pages before continuing."""
        html = self.driver.page_source.lower()
        title = self.driver.title.lower()
        return (
                "security check" in title
                or "additional verification required" in html
                or "cf-box-container" in html
                )


    def wait_for_manual_resolution(self):
        """Pause until the challenge page is cleared manually."""
        print("Security check detected → waiting for manual solve...")
        while self.is_security_check():
            time.sleep(2)
        print("Security check cleared → resuming")


    def get_cookies(self):
        """Load saved Indeed cookies into the browser session."""
        try:
            self.driver.get(self.url + "/")
            if self.is_security_check():
                self.wait_for_manual_resolution()
            with open("user/cookies/cookies.json", "r") as cookie_file:
                cookies = json.load(cookie_file)

            # Keep only Selenium-compatible cookie fields.
            for cookie in cookies:
                cookie_dict = {
                    "name": cookie["name"],
                    "value": cookie["value"],
                    "domain": cookie.get("domain", ".indeed.com"),
                    "path": cookie.get("path", "/"),
                }

                # Convert browser export expiry to Selenium's expected format.
                if "expirationDate" in cookie:
                    cookie_dict["expiry"] = int(cookie["expirationDate"])
                self.driver.add_cookie(cookie_dict)
            self.driver.refresh()

        # Continue without cookies if no export file exists yet.
        except FileNotFoundError:
            print("cookies not found")

        # Ignore cookies that do not match the current Indeed domain.
        except InvalidCookieDomainException:
            pass


    def get_source(self, url: str) -> str:
        """Open a page and return its HTML source."""
        self.driver.get(url)
        if self.is_security_check():
            self.wait_for_manual_resolution()
        time.sleep(3)
        return self.driver.page_source


    @staticmethod
    def get_text_from_selector(soup, css_selector):
        """Return text from the first matching selector."""
        element = soup.select_one(css_selector)
        if element is None:
            return None
        return element.get_text()


    def parse_job_detail(self, job_details: dict) -> dict:
        """Fill a job entry with data from the detail page."""

        # Expand the skills block when Indeed renders it behind a button.
        try:
            show_more = self.driver.find_element(
                By.CSS_SELECTOR,
                '[aria-label="Skills"] button.js-match-insights-provider-1s05l8k'
            )
            self.driver.execute_script("arguments[0].click();", show_more)

        # Skip silently when the detail page has no expandable skills block.
        except NoSuchElementException:
            pass
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        job_type = self.get_text_from_selector(soup, "#salaryInfoAndJobType")
        description = self.get_text_from_selector(soup, "#jobDescriptionText")
        skills = ""
        for btn in soup.select('[aria-label="Skills"] button[data-testid$="-tile"]'):

            # Flatten all rendered skill chips into one comma-separated string.
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
        """Walk paginated results until limits or repeated empty pages stop the scan."""
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

                # Read the stable Indeed id used for deduplication.
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

                # Normalize the city field from the display location string.
                job_location = location_tag.get_text(strip=True).split("·")[-1].strip()
                job_data = {
                    "indeed_id": job_id,
                    "link": self.url + job_link,
                    "title": title_tag.get_text(strip=True),
                    "company": company_tag.get_text(strip=True),
                    "location": job_location,
                    "city": job_location.split(",")[0].strip() if job_location else "",
                }

                # Open the detail page to collect description and skills.
                self.get_source(job_data["link"])
                job_data = self.parse_job_detail(job_data)
                if not job_data.get("description"):
                    continue

                # Run the evaluator before saving so the DB stores enriched data.
                evaluated_job = evaluator.get_advice(job_data)
                db.save_job(evaluated_job)
                data.append(evaluated_job)
                known_ids.add(job_id)
                new_jobs_this_page += 1

            # Count pages with no new jobs so the loop can stop early.
            if new_jobs_this_page == 0:
                repeated_pages += 1
            else:
                repeated_pages = 0
            if repeated_pages >= 3:
                 break
            page += 10


    def get_job(self, *, keywords: list, locations: list, radii: list, evaluator, db):
        """Run searches for all keyword, location, and radius combinations."""

        # Restore login state before starting the search loop.
        self.get_cookies()
        data = db.load_jobs()
        known_ids = {job["indeed_id"] for job in data}
        try:
            for location in locations:
                for radius in radii:
                    for keyword in keywords:

                        # Search each combination against the same shared cache of known ids.
                        self.search(data, keyword, location, radius, known_ids, evaluator, db)
        finally:

            # Always close the browser even if scraping fails mid-run.
            self.driver.quit()
        return data