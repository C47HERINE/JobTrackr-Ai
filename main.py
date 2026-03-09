import json
from core import JobFinder, Evaluator

search_keywords = ['python', 'informatique', 'developer', 'flask']
search_locations = ["Chambly"]
search_radii = ["15, 25"]

evaluator = Evaluator()
find_job = JobFinder()


find_job.job_finder(search_keywords, search_locations, search_radii)

job_data = find_job.load_job_data()

evaluated_data = evaluator.get_advice(job_data)


with open("jobs.json", "w", encoding="utf-8") as file:
    json.dump(evaluated_data, file, indent=4, ensure_ascii=False)


#TODO log th ai response in the database for each application base on its id

#TODO for job labeled as "apply" but not yet applied use selenium to apply
#       with indeed cv

#TODO in the database: log the job applied, the job pending for manual offsite application
#       and n/a if ai answered no

#TODO save the data in a SQLite database

#TODO implement a tick for recurring  automated searches

#TODO create a flask app to see all the jobs applied on and those that were rejected using flask

#TODO make a bootstrap/html site for a dashboard showing applied/rejected with title, date, etc

#TODO create a template  to display all details for each job and a apply (linking to the post link)

#TODO make a "is applied" route to edit pending and rejected jobs

#TODO add an  additional route/page for jobs with interviews, allow to move from where
#       they are to here

#TODO make a search route/page to target specific job data for interview/response