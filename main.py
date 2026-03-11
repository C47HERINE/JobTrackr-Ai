from core import JobFinder, Evaluator, JobRepository
from app import create_app
import json

evaluator = Evaluator()
finder = JobFinder()
db = JobRepository()
app = create_app(db)

job_data = db.load_jobs()

with open('config/search_config.json', 'r') as file:
    search_config = json.load(file)

updated_data = finder.get_job(
    data=job_data,
    keywords=search_config['keywords'],
    locations=search_config['locations'],
    radii=search_config['radii']
    )

new_jobs = [job for job in updated_data if job.get("decision") not in {"apply", "pass"}]

if new_jobs:
    evaluated_data = evaluator.get_advice(updated_data)
    db.save_jobs(evaluated_data)

app.run()

#TODO add an  additional route/page for jobs with interviews, allow to move from where they are to here

#TODO make a search route/page to target specific job data for interview/response

#TODO for job labeled as "apply" but not yet applied use selenium to apply with indeed cv

#TODO in the database: log the job applied, the job pending for manual offsite application and n/a if ai answered no

#TODO create a user login route

#TODO set a user db

#TODO  create a state function to log last time search ran

#TODO establish a run function so if last run was 6 hours + then search must run

#TODO implement a tick for recurring automated searches