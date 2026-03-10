from flask import Flask, render_template, request, redirect, url_for
from core import JobRepository


app = Flask(__name__)

db = JobRepository()


def compute_statistics(job_list):
    return {
        "total": len(job_list),
        "apply": sum(job.get("should_apply") == "apply" for job in job_list),
        "pass": sum(job.get("should_apply") == "pass" for job in job_list),
        "applied": sum(job.get("is_applied") is True for job in job_list),
    }


def list_cities(job_list):
    return sorted({job["city"] for job in job_list if job["city"]})


def filter_jobs(job_list):
    decision_filter = request.args.get("decision", "")
    title_filter = request.args.get("title", "").lower()
    company_filter = request.args.get("company", "").lower()
    city_filter = request.args.get("city", "")
    applied_filter = request.args.get("applied", "")
    filtered_results = []
    for job in job_list:
        if decision_filter == "apply" and job.get("should_apply") != "apply":
            continue
        if decision_filter == "pass" and job.get("should_apply") != "pass":
            continue
        if decision_filter == "applied" and not job.get("is_applied"):
            continue
        if title_filter and title_filter not in job.get("title", "").lower():
            continue
        if company_filter and company_filter not in job.get("company", "").lower():
            continue
        if city_filter and job.get("city") != city_filter:
            continue
        if applied_filter == "yes" and not job.get("is_applied"):
            continue
        if applied_filter == "no" and job.get("is_applied"):
            continue
        filtered_results.append(job)
    filtered_results.sort(key=lambda job_item: int(job_item.get("time_stamp", 0)), reverse=True)
    return filtered_results


@app.route("/")
def index():
    job_list = db.load_jobs()
    filtered_jobs = filter_jobs(job_list)
    selected_job_id = request.args.get("job")
    selected_job = None
    if selected_job_id:
        for job in job_list:
            if str(job.get("id")) == selected_job_id:
                selected_job = job
                break
    if not selected_job and filtered_jobs:
        selected_job = filtered_jobs[0]
    statistics = compute_statistics(job_list)
    city_list = list_cities(job_list)
    return render_template(
        "index.html",
        jobs=filtered_jobs,
        job=selected_job,
        cities=city_list,
        stats=statistics
    )


@app.route("/job/<job_id>/update", methods=["POST"])
def update_job(job_id):
    job_list = db.load_jobs()
    decision_value = request.form.get("decision", "")
    applied_value = "applied" in request.form
    for job in job_list:
        if str(job.get("id")) == job_id:
            job["should_apply"] = decision_value
            job["is_applied"] = applied_value
            break
    db.save_jobs(job_list)
    return redirect(url_for("index", job=job_id))


@app.route("/job/<job_id>")
def view_job(job_id):
    return redirect(url_for("index", job=job_id))


@app.route("/reload")
def reload_jobs():
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)