from celery import Celery
import requests
from PyPDF2 import PdfReader, errors
from io import BytesIO
import re
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)

# Get Redis URL from environment variables
redis_url = os.getenv('REDIS_URL', 'redis://red-cpl0d6ol6cac73als9s0:6379')

app = Celery('tasks', broker=redis_url)

# List of all possible technologies to check for in the resumes
ALL_TECHNOLOGIES = [
    'Python', 'Java', 'JavaScript', 'C#', 'C++', 'SQL', 'React.js', 'Node.js', 'HTML', 'CSS', 'Bootstrap', 'Express',
    'SQLite', 'Flexbox', 'MongoDB', 'OOPs', 'Redux', 'Git', 'SpringBoot', 'Data', 'Analytics', 'Manual', 'Testing',
    'Selenium', 'Testing', 'User', 'Interface', 'UI', 'XR', 'AI', 'ML', 'AWS', 'Cyber', 'Security', 'Data', 'Structures',
    'Algorithms', 'Django', 'Flask', 'Linux', 'NumPy', 'SAP', 'AngularJS', 'Flutter', 'UX', 'design', 'jQuery', 'Angular',
    'REST', 'API', 'Calls', 'node', 'Nodejs', 'Reactjs', 'Rails', 'Vue', 'WordPress', 'Science', 'AR', 'VR', 'MR', 'Next.js', 'Nexjs', 'Kubernetes', 'Microsoft', 'Azure', 'DevOps'
]  # Add more as needed

@app.task
def process_pdf(entry, keywords, total_keywords):
    url = entry['resume_link']
    user_id = entry['user_id']
    pdf_file = download_pdf(url)
    if not pdf_file:
        return None  # Skip if the PDF could not be downloaded
    
    text = extract_text_from_pdf(pdf_file)
    if not text:
        return None  # Skip if the text could not be extracted
    
    match_count = 0
    matched_technologies = []
    existing_technologies = [tech for tech in ALL_TECHNOLOGIES if re.search(r'\b' + re.escape(tech) + r'\b', text, re.IGNORECASE)]
    
    for keyword in keywords:
        pattern = r'\b' + re.escape(keyword).replace(' ', r'\s+') + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            match_count += 1
            matched_technologies.append(keyword)
    
    if match_count > 0:
        percentage = (match_count / total_keywords) * 100
        return {
            'user_id': user_id,
            'resume_link': url,
            'percentage': round(percentage, 2),
            'matched_technologies': matched_technologies,
            'existing_technologies': existing_technologies
        }
    return None

def download_pdf(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BytesIO(response.content)
    except requests.RequestException as e:
        logging.error(f"Error downloading PDF from {url}: {e}")
        return None

def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except errors.PdfReadError as e:
        logging.error(f"Error reading PDF file: {e}")
        return ""
