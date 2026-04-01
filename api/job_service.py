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


def fetch_linkedin_jobs(query='Software Engineer', location='Remote'):
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
            title = job.get('job_title') or job.get('title') or 'Interview Role'
            company = job.get('company_name') or job.get('company') or 'Unknown Company'
            link = job.get('job_url') or job.get('url') or '#'
            eligibility = 'You are Eligible' if user_accuracy >= 65 else 'Needs Improvement'
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
                'title': f'{user_domain} Analyst',
                'company': 'AI Ready Labs',
                'link': 'https://www.example.com/apply',
                'eligibility': 'You are Eligible' if user_accuracy >= 65 else 'Needs Improvement',
                'skills_matched': [user_domain],
            }
        ]

    return recommendations
