from flask import render_template, request, redirect, url_for, Blueprint
from .web_utilis import filter_jobs, list_cities, compute_statistics, normalize_job_list


def dashboard_blueprints(job_db):
    bp = Blueprint("dashboard", __name__)


    @bp.route("/")
    def index():
        job_list = job_db.load_jobs()
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


    @bp.route("/job/<job_id>/update", methods=["POST"])
    def update_job(job_id):
        job_list = normalize_job_list(job_db.load_jobs())
        decision_value = request.form.get("decision")
        applied_clicked = request.form.get("applied") == "true"
        next_url = request.form.get("next")
        for job in job_list:
            if str(job.get("id")) == str(job_id):
                if decision_value is not None and decision_value != "":
                    job["should_apply"] = decision_value
                if applied_clicked:
                    job["is_applied"] = True
                    job["should_apply"] = "applied"
                break
        job_db.save_jobs(job_list)
        if next_url:
            return redirect(next_url)
        return redirect(url_for("dashboard.index", job=job_id))


    @bp.route("/job/<job_id>")
    def view_job(job_id):
        return redirect(url_for("dashboard.index", job=job_id))


    @bp.route("/reload")
    def reload_jobs():
        return redirect(url_for("dashboard.index"))

    return bp