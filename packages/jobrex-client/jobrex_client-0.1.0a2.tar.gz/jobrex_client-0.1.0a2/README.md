# Jobrex Client

Jobrex Client is a Python package that provides a simple interface to interact with the Jobrex API, which offers AI-powered recruitment services including resume parsing, job matching, and more.

## Features

* Resume parsing and analysis
* Job description extraction and analysis
* Resume and job matching
* Zoom meeting creation for interviews
* Indexing and searching of resumes and jobs
* Resume rewriting and tailoring for job applications

## Installation

You can install Jobrex Client using pip:
```
pip install jobrex-client
```
## Usage

### Parsing a Resume

```python
from jobrex import ResumesClient

# Initialize the client with your API key
client = ResumesClient(api_key="your_api_key_here")

# Parse a resume
resume_response = client.parse_resume("path/to/your/resume.pdf")
print(resume_response)
```


### Tailoring a Resume

```python
from jobrex import ResumesClient

# Initialize the client with your API key
client = ResumesClient(api_key="your_api_key_here")

# User data and job details
user_data = {
    "basics": {
        "name": "John Doe",
        "headline": "Senior Software Engineer",
        "email": "john.doe@example.com",
        "phone": "123-456-7890",
        "location": "San Francisco, CA",
        "url": {
            "label": "Portfolio",
            "href": "https://johndoe.com"
        }
    },
    "sections": {
        "experience": {
            "items": [
                {
                    "company": "Tech Solutions Inc",
                    "position": "Senior Software Engineer",
                    "location": "San Francisco, CA",
                    "date": "2020-Present",
                    "summary": "Led development of machine learning pipelines and APIs serving millions of users",
                    "url": {
                        "label": "Tech Solutions Inc",
                        "href": "https://techsolutions.com"
                    }
                },
                {
                    "company": "Data Analytics Co",
                    "position": "Software Engineer",
                    "location": "Seattle, WA", 
                    "date": "2018-2020",
                    "summary": "Developed Python microservices and data processing workflows",
                    "url": {
                        "label": "TData Analytics Co",
                        "href": "https://datago.com"
                    }
                }
            ]
        },
        "certifications": {
            "items": [
                {
                    "name": "AWS Certified Solutions Architect",
                    "issuer": "Amazon Web Services",
                    "date": "2022",
                    "summary": "Professional level cloud architecture certification",
                    "url": {
                        "label": "Verify",
                        "href": "https://aws.amazon.com/verification"
                    }
                },
                {
                    "name": "Professional Scrum Master I",
                    "issuer": "Scrum.org", 
                    "date": "2021",
                    "summary": "Certification in Agile project management and Scrum framework",
                    "url": {
                        "label": "Certificate",
                        "href": "https://www.scrum.org/certificates"
                    }
                }
            ]
        },
        "education": {
            "items":[
            {
                "institution": "University of Technology",
                "studyType": "Bachelor's Degree",
                "area": "Computer Science",
                "score": "3.8",
                "date": "2014-2018",
                "summary": "Focused on software development and machine learning.",
                "url": {
                    "label": "University Website",
                    "href": "https://www.universityoftechnology.edu"
                }
            },
            {
                "institution": "Online Learning Platform",
                "studyType": "Certification",
                "area": "Data Science",
                "score": "Completed",
                "date": "2020",
                "summary": "Completed a comprehensive course on data analysis and machine learning.",
                "url": {
                    "label": "Course Certificate",
                    "href": "https://www.onlinelearningplatform.com/certificate"
                }
            }
            ]
        },
        "profiles": {
            "items": [
            {
                "id": "linkedin_profile",
                "network": "LinkedIn",
                "icon": "https://example.com/linkedin-icon.png",
                "url": {
                    "label": "View Profile",
                    "href": "https://www.linkedin.com/in/yourprofile"
                }
            },
            {
                "id": "github_profile",
                "network": "GitHub",
                "icon": "https://example.com/github-icon.png",
                "url": {
                    "label": "View Profile",
                    "href": "https://github.com/yourusername"
                }
            },
            {
                "id": "personal_website",
                "network": "Personal Website",
                "icon": "https://example.com/website-icon.png",
                "url": {
                    "label": "Visit Website",
                    "href": "https://www.yourwebsite.com"
                }
            }
            ]
        },
        "summary": {
            "content": "Experienced software engineer with 5+ years in Python development."
        },
        "skills": {
            "items": [
                {
                    "name": "Python",
                    "description": "Advanced proficiency",
                    "keywords": ["Django", "Flask", "FastAPI"]
                },
                {
                    "name": "Machine Learning",
                    "description": "Intermediate level",
                    "keywords": ["TensorFlow", "scikit-learn"]
                }
            ]
        }
    }
}

job_details = {
    "title": "Senior Software Engineer",
    "company": "XYZ Corp",
    "description": "Looking for an experienced Python developer with machine learning expertise...",
    "requirements": [
        "5+ years of Python development",
        "Experience with machine learning frameworks",
        "Strong problem-solving skills"
    ]
}

# Tailor the resume
tailored_response = client.tailor_resume(user_data, job_details, ["summary", "certifications", "experience", "education", "skills"])
print(tailored_response)
```

### Rewriting a Resume Section

```python
from jobrex import ResumesClient

# Initialize the client with your API key
client = ResumesClient(api_key="your_api_key_here")

# Text to rewrite and optional prompt
text = "I have experience in software development and data analysis."
section = "summary"

# Rewrite the resume section
rewritten_response = client.rewrite_resume_section(text, section)
print(rewritten_response)
```

### Listing Resume Indexes

```python
from jobrex import ResumesClient

# Initialize the client with your API key
client = ResumesClient(api_key="your_api_key_here")

# List resume indexes
indexes_response = client.list_resume_indexes()
print(indexes_response)
```

### Searching Resumes

```python
from jobrex import ResumesClient

# Initialize the client with your API key
client = ResumesClient(api_key="your_api_key_here")

# Search for resumes
query = "Data Scientist"
index_name = "my_resume_index"
top_k = 10

search_response = client.search_resumes(query, index_name, top_k=10)
print(search_response)
```
### Indexing Resumes

```python
from jobrex import ResumesClient

# Initialize the client with your API key
client = ResumesClient(api_key="your_api_key_here")

# Documents to index
documents = [
    {"resume_id": "r123", "resume_data": """{"basics": {"name": "John Doe", "headline": "Senior Software Engineer", "email": "john.doe@example.com", "phone": "123-456-7890", "location": "San Francisco, CA", "url": {"label": "Portfolio", "href": "https://johndoe.com"}}, "sections": {"experience": {"items": [{"company": "Tech Solutions Inc", "position": "Senior Software Engineer", "location": "San Francisco, CA", "date": "2020-Present", "summary": "Led development of machine learning pipelines and APIs serving millions of users", "url": {"label": "Tech Solutions Inc", "href": "https://techsolutions.com"}}, {"company": "Data Analytics Co", "position": "Software Engineer", "location": "Seattle, WA", "date": "2018-2020", "summary": "Developed Python microservices and data processing workflows", "url": {"label": "TData Analytics Co", "href": "https://datago.com"}}]}, "certifications": {"items": [{"name": "AWS Certified Solutions Architect", "issuer": "Amazon Web Services", "date": "2022", "summary": "Professional level cloud architecture certification", "url": {"label": "Verify", "href": "https://aws.amazon.com/verification"}}, {"name": "Professional Scrum Master I", "issuer": "Scrum.org", "date": "2021", "summary": "Certification in Agile project management and Scrum framework", "url": {"label": "Certificate", "href": "https://www.scrum.org/certificates"}}]}, "education": {"items": [{"institution": "University of Technology", "studyType": "Bachelor\'s Degree", "area": "Computer Science", "score": "3.8", "date": "2014-2018", "summary": "Focused on software development and machine learning.", "url": {"label": "University Website", "href": "https://www.universityoftechnology.edu"}}, {"institution": "Online Learning Platform", "studyType": "Certification", "area": "Data Science", "score": "Completed", "date": "2020", "summary": "Completed a comprehensive course on data analysis and machine learning.", "url": {"label": "Course Certificate", "href": "https://www.onlinelearningplatform.com/certificate"}}]}, "profiles": {"items": [{"id": "linkedin_profile", "network": "LinkedIn", "icon": "https://example.com/linkedin-icon.png", "url": {"label": "View Profile", "href": "https://www.linkedin.com/in/yourprofile"}}, {"id": "github_profile", "network": "GitHub", "icon": "https://example.com/github-icon.png", "url": {"label": "View Profile", "href": "https://github.com/yourusername"}}, {"id": "personal_website", "network": "Personal Website", "icon": "https://example.com/website-icon.png", "url": {"label": "Visit Website", "href": "https://www.yourwebsite.com"}}]}, "summary": {"content": "Experienced software engineer with 5+ years in Python development."}, "skills": {"items": [{"name": "Python", "description": "Advanced proficiency", "keywords": ["Django", "Flask", "FastAPI"]}, {"name": "Machine Learning", "description": "Intermediate level", "keywords": ["TensorFlow", "scikit-learn"]}]}}}"""},
]
index_name = "my_resume_index"
id_field = "resume_id"
search_fields = ["resume_data"]
# Index the resumes
index_response = client.index_resume(documents, index_name, id_field, search_fields, department_name=None)
print(index_response)
```

### Deleting Resumes

```python
from jobrex import ResumesClient

# Initialize the client with your API key
client = ResumesClient(api_key="your_api_key_here")

# List of document IDs to delete
documents_ids = ["r123"]
index_name = "my_resume_index"

# Delete the resumes
delete_response = client.delete_resumes(documents_ids, index_name)
print(delete_response)
```

### Searching Jobrex Resumes

```python
from jobrex import ResumesClient

# Initialize the client with your API key
client = ResumesClient(api_key="your_api_key_here")

# Search for resumes in the Jobrex pool
query = "Data Scientist"
top_k = 10

search_response = client.search_jobrex_resumes(query, top_k=10)
print(search_response)
```

### Getting Candidate Score

```python
from jobrex import JobsClient

# Initialize the client with your API key
client = JobsClient(api_key="your_api_key_here")

# Job details and resume details
job_details = {
    "title": "Senior Software Engineer",
    "company": "XYZ Corp",
    "description": "Looking for an experienced Python developer with machine learning expertise...",
    "requirements": [
        "5+ years of Python development",
        "Experience with machine learning frameworks",
        "Strong problem-solving skills"
    ]
}

resume_details = {
    "basics": {
        "name": "John Doe",
        "headline": "Senior Software Engineer",
        "email": "john.doe@example.com",
        "phone": "123-456-7890",
        "location": "San Francisco, CA"
    },
    "skills": ["Python", "Machine Learning"]
}

# Get candidate score
score_response = client.get_candidate_score(job_details, resume_details)
print(score_response)
```

### Writing Job Description

```python
from jobrex import JobsClient

# Initialize the client with your API key
client = JobsClient(api_key="your_api_key_here")

# Job details
job_title = "Senior Software Engineer"
hiring_needs = "Looking for a skilled developer with experience in Python and machine learning."
company_description = "XYZ Corp is a leading tech company."
job_type = "Full-time"
job_location = "San Francisco, CA"
specific_benefits = "Health insurance, 401k, and flexible hours."

# Write job description
job_description_response = client.write_job_description(
    job_title, hiring_needs, company_description, job_type, job_location, specific_benefits
)
print(job_description_response)
```

### Parsing Job Description

```python
from jobrex import JobsClient

# Initialize the client with your API key
client = JobsClient(api_key="your_api_key_here")

# Job site content
job_site_content = "We are looking for a Senior Software Engineer with experience in Python and machine learning."

# Parse job description
parsed_job_response = client.parse_job_description(job_site_content)
print(parsed_job_response)
```

### Creating a Zoom Meeting

```python
from jobrex import JobsClient

# Initialize the client with your API key
client = JobsClient(api_key="your_api_key_here")

# Zoom meeting details
client_id = "your_zoom_client_id"
client_secret = "your_zoom_client_secret"
account_id = "your_zoom_account_id"
duration = 60  # Duration in minutes
start_time = "2023-10-01T10:00:00Z"  # ISO format
timezone = "America/Los_Angeles"
topic = "Interview for Senior Software Engineer Position"

# Create Zoom meeting
zoom_meeting_response = client.create_zoom_meeting(
    client_id, client_secret, account_id, duration, start_time, timezone, topic
)
print(zoom_meeting_response)
```

### Listing Job Indexes

```python
from jobrex import JobsClient

# Initialize the client with your API key
client = JobsClient(api_key="your_api_key_here")

# List job indexes
indexes_response = client.list_job_indexes()
print(indexes_response)
```

### Searching Jobs

```python
from jobrex import JobsClient

# Initialize the client with your API key
client = JobsClient(api_key="your_api_key_here")

# Search for jobs
query = "Software Engineer"
index_name = "my_job_index"
top_k = 10

search_response = client.search_jobs(query, index_name, top_k=10)
print(search_response)
```

### Deleting a Job

```python
from jobrex import JobsClient

# Initialize the client with your API key
client = JobsClient(api_key="your_api_key_here")

# List of document IDs to delete
documents_ids = ["job_id_1", "job_id_2"]
index_name = "my_job_index"

# Delete the jobs
delete_response = client.delete_job(documents_ids, index_name)
print(delete_response)
```

### Indexing Jobs

```python
from jobrex import JobsClient

# Initialize the client with your API key
client = JobsClient(api_key="your_api_key_here")

# Documents to index
documents = [
    {"job_id": "job_1", "job_data": """{"title": "Software Engineer", "company": "XYZ Corp"}"""},
    {"job_id": "job_2", "job_data": """{"title": "Data Scientist", "company": "ABC Inc"}"""}
]
index_name = "my_job_index"
id_field = "job_id"
search_fields = ["job_data"]
# Index the jobs
index_response = client.index_job(documents, index_name, id_field, search_fields, department_name=None)
print(index_response)
```

## License

Jobrex Client is licensed under the MIT License.

