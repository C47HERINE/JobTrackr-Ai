from app import create_app
from core import JobFinder, Evaluator, JobRepository
from threading import Thread
import json
import time


db = JobRepository()
app = create_app(db)


def search():
    while True:
        try:
            with open("user/state.json", "r") as json_file:
                state = json.load(json_file)
        except FileNotFoundError:
            state = {"last_run": 0}
        if time.time() - state["last_run"] >= 21600:
            evaluator = Evaluator()
            finder = JobFinder()
            with open('user/search_config.json', 'r') as file:
                search_config = json.load(file)
            updated_data = finder.get_job(
                data=db.load_jobs(),
                keywords=search_config['keywords'],
                locations=search_config['locations'],
                radii=search_config['radii']
            )
            new_jobs = [job for job in updated_data if job.get("should_apply") not in {"apply", "pass"}]
            if new_jobs:
                evaluated_data = evaluator.get_advice(updated_data)
                db.save_jobs(evaluated_data)
            state["last_run"] = int(time.time())
            with open("user/state.json", "w") as json_file:
                json.dump(state, json_file, indent=4)
            time.sleep(900)
        else:
            time.sleep(900)

Thread(target=search, daemon=True).start()

app.run(host="0.0.0.0", port=5000)

#----------#

#INTERVIEW AND APPLICATION FOLLOW-UP MANAGEMENT

#TODO add an  additional route/page for jobs with interviews

#TODO make a search route/page to target specific job data for interview/response

#TODO in the database: log the job applied, the job pending for manual offsite application and n/a if ai answered no

#TODO A dedicated interview tracking page

#----------#

#ADDITIONAL FILTER

#TODO make an hidden job section to separate those rejected by the user

#----------#

#APPLY USING BROWSER AUTOMATION

#TODO for job labeled as "apply" but not yet applied use selenium to apply with indeed cv

#----------#

#EXTEND JOB DETAIL

#TODO LLM mock interview support

#TODO LLM-tailored CV generation based on selected job postings from the web app

#----------#

#PER USER LOGIN AND ENVIRONMENT

#TODO User authentication and per-user data separation: create a user login route and set a user db

#TODO A settings page to manage user configuration, search settings and app data from the web interface

#----------#

#ADDITIONAL PAGES

#TODO A chat tab for direct interaction with the AI for broader job-search guidance

#TODO Add an optional full page to manage job postings individually (detailed section)