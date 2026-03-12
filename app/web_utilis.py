from flask import request


def compute_statistics(job_list):
    return {
        "total": len(job_list),
        "apply": sum(job.get("should_apply") == "apply" for job in job_list),
        "pass": sum(job.get("should_apply") == "pass" for job in job_list),
        "applied": sum(job.get("is_applied") is True for job in job_list),
    }


def list_cities(job_list):
    return sorted({job.get("city") for job in job_list if job.get("city")})


def filter_jobs(job_list):
    decision_filter = request.args.get("decision", "")
    title_filter = request.args.get("title", "").lower().strip()
    company_filter = request.args.get("company", "").lower().strip()
    city_filters = request.args.getlist("city")
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
        if city_filters and job.get("city") not in city_filters:
            continue
        if applied_filter == "yes" and not job.get("is_applied"):
            continue
        if applied_filter == "no" and job.get("is_applied"):
            continue
        filtered_results.append(job)
    filtered_results.sort(key=lambda job_item: int(job_item.get("time_stamp", 0)), reverse=True)
    return filtered_results