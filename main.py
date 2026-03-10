from core import JobFinder, Evaluator, JobRepository
import json


evaluator = Evaluator()
finder = JobFinder()
db = JobRepository()

#TODO implement a tick for recurring automated searches

job_data = db.load_jobs()

with open('search_config.json', 'r') as file:
    search_config = json.load(file)

updated_data = finder.get_job(
    data=job_data,
    keywords=search_config['keywords'],
    locations=search_config['locations'],
    radii=search_config['radii']
    )

if updated_data:
    evaluated_data = evaluator.get_advice(updated_data)
    db.save_jobs(evaluated_data)


#TODO for job labeled as "apply" but not yet applied use selenium to apply with indeed cv

#TODO in the database: log the job applied, the job pending for manual offsite application and n/a if ai answered no

#TODO add an  additional route/page for jobs with interviews, allow to move from where they are to here

#TODO make a search route/page to target specific job data for interview/response