import re

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
    """Filter jobs using query-string filters from the current request."""
    decision_filter = request.args.get("decision", "")
    title_filter = request.args.get("title", "").lower().strip()
    company_filter = request.args.get("company", "").lower().strip()
    city_filters = request.args.getlist("city")
    applied_filter = request.args.get("applied", "")
    filtered_results = []
    for job in job_list:

        # Skip jobs hidden from the UI
        if job.get("is_hidden"):
            continue

        # Decision-specific views exclude already applied jobs
        if decision_filter == "apply":
            if job.get("should_apply") != "apply" or job.get("is_applied"):
                continue
        if decision_filter == "pass":
            if job.get("should_apply") != "pass" or job.get("is_applied"):
                continue
        if decision_filter == "applied" and not job.get("is_applied"):
            continue

        # Case-insensitive text filters
        if title_filter and title_filter not in job.get("title", "").lower():
            continue
        if company_filter and company_filter not in job.get("company", "").lower():
            continue

        # Multi-select city filter
        if city_filters and job.get("city") not in city_filters:
            continue

        # Applied state filter
        if applied_filter == "yes" and not job.get("is_applied"):
            continue
        if applied_filter == "no" and job.get("is_applied"):
            continue
        filtered_results.append(job)

    filtered_results.sort(key=lambda job_item: int(job_item.get("time_stamp", 0)), reverse=True)
    return filtered_results


def normalize_job_list(job_list, field="description"):
    for job in job_list:
        text = job.get(field)
        if isinstance(text, str):
            # Collapse 3+ newlines into a single blank line
            job[field] = re.sub(r"\n{3,}", "\n\n", text).strip()
    return job_list