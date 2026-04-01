import requests
import os
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
LINKEDIN_HOST = os.getenv('RAPIDAPI_HOST_LINKEDIN')


def normalize_job_list(raw_data):
    if isinstance(raw_data, list):
        return raw_data
    if isinstance(raw_data, dict):
        for key in ('jobs', 'data', 'items', 'results'):
            if key in raw_data and isinstance(raw_data[key], list):
                return raw_data[key]
    return []


def extract_job_value(job, keys, default=None):
    for key in keys:
        if isinstance(job, dict) and key in job and job[key]:
            return job[key]
    return default


def extract_job_link(job):
    return extract_job_value(job, [
        'job_url', 'url', 'link', 'redirect_url', 'apply_url', 'jobPostingUrl'
    ], 'https://www.linkedin.com')


def fetch_linkedin_jobs(query='Software Engineer', location='Remote'):
    if not RAPIDAPI_KEY or not LINKEDIN_HOST:
        return []

    url = f'https://{LINKEDIN_HOST}/active-jb-1h'
    params = {
        'keywords': query,
        'location': location,
        'limit': '10',
        'offset': '0',
        'description_type': 'text',
    }

    headers = {
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': LINKEDIN_HOST,
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code == 200:
            return normalize_job_list(response.json())
        return []
    except Exception:
        return []


def get_job_recommendations(user_domain, user_accuracy):
    jobs_data = fetch_linkedin_jobs(query=user_domain)
    recommendations = []

    if isinstance(jobs_data, list) and jobs_data:
        for job in jobs_data[:10]:
            title = extract_job_value(job, ['job_title', 'title', 'position', 'role'], 'Interview Role')
            company = extract_job_value(job, ['company_name', 'company', 'employer', 'companyName'], 'Unknown Company')
            link = extract_job_link(job)
            eligibility = 'Eligible' if user_accuracy >= 65 else 'Needs Improvement'
            recommendations.append({
                'title': title,
                'company': company,
                'link': link,
                'eligibility': eligibility,
                'skills_matched': [user_domain],
            })

    if not recommendations:
        recommendations = [
            {
                'title': f'{user_domain} Engineer',
                'company': 'Acme Talent Partners',
                'link': 'https://www.linkedin.com/jobs',
                'eligibility': 'Eligible' if user_accuracy >= 65 else 'Needs Improvement',
                'skills_matched': [user_domain],
            },
            {
                'title': f'{user_domain} Specialist',
                'company': 'TalentForge',
                'link': 'https://www.indeed.com',
                'eligibility': 'Eligible' if user_accuracy >= 65 else 'Needs Improvement',
                'skills_matched': [user_domain],
            },
            {
                'title': f'{user_domain} Associate',
                'company': 'Recruit Labs',
                'link': 'https://www.example.com',
                'eligibility': 'Eligible' if user_accuracy >= 65 else 'Needs Improvement',
                'skills_matched': [user_domain],
            },
        ]

    return recommendations
