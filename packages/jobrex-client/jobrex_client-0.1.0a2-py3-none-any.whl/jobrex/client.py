import requests
from typing import Dict, List, Optional, Any, Union
from .models import (
    Resume,
    ResumeResponse,
    JobDetailsResponse,
    ZoomMeetingResponse,
    ResumeRewriteResponse,
    IndexesListResponse,
    IndexResponse,
    SearchResponse,
    JobMatchResult,
)


class BaseClient:
    """Base class for Jobrex API clients."""

    def __init__(self, api_key: str, base_url: str = "https://api.jobrex.ai"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Api-Key {api_key}"
        })

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()


class ResumesClient(BaseClient):
    """
    Client for interacting with the Jobrex API for resumes.
    """
    

    def parse_resume(self, file_path: str) -> ResumeResponse:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            return self._make_request('POST', 'v1/resumes/extract/', files=files)

    def tailor_resume(self, user_data: Resume, job_details: Dict, sections: List[str]) -> Resume:
        data = {
            "user_data": user_data,
            "job_details": job_details,
            "sections": sections
        }
        return self._make_request('POST', 'v1/resumes/tailor/', json=data)

    def rewrite_resume_section(self, text: str, section_type: Optional[str] = "") -> ResumeRewriteResponse:
        data = {
            "text": text,
            "type": section_type
        }
        return self._make_request('POST', 'v1/resumes/rewrite/', json=data)

    def list_resume_indexes(self) -> IndexesListResponse:
        return self._make_request('GET', 'v1/resumes/list-indexes/')

    def index_resume(self, documents: List[Dict], index_name: str, id_field: str, search_fields: List[str], department_name: str|None=None) -> IndexResponse:
        extra_fields = {}
        if department_name:
            extra_fields["department_name"] = department_name
        data = {
            "documents": documents,
            "index_name": index_name,
            "id_field": id_field,
            "search_fields": search_fields,
            **extra_fields
        }
        return self._make_request('POST', 'v1/resumes/index/', json=data)

    def delete_resumes(self, documents_ids: List[str], index_name: str) -> Dict:
        data = {
            "documents_ids": documents_ids,
            "index_name": index_name
        }
        return self._make_request('POST', 'v1/resumes/delete/', json=data)

    def search_resumes(
        self, 
        query: str, 
        index_name: str, 
        filters: Optional[Dict] = None, 
        department_name: str|None=None,
        custom_query: Optional[Dict] = None,
        top_k: Optional[int] = None
    ) -> SearchResponse:
        data = {"query": query, "index_name": index_name}
        if filters:
            data["filters"] = filters
        if department_name:
            data["department_name"] = department_name
        if custom_query:
            data["custom_query"] = custom_query
        if top_k:
            data["top_k"] = top_k

        return self._make_request('POST', 'v1/resumes/search/', json=data)

    def search_jobrex_resumes(
        self, 
        query: str, 
        filters: Optional[Dict] = None,
        custom_query: Optional[Dict] = None,
        top_k: Optional[int] = None
    ) -> SearchResponse:
        data = {"query": query}
        if filters:
            data["filters"] = filters
        if custom_query:
            data["custom_query"] = custom_query
        if top_k:
            data["top_k"] = top_k
        return self._make_request('POST', 'v1/resumes/search-jobrex/', json=data)


class JobsClient(BaseClient):
    """
    Client for interacting with the Jobrex API for jobs.
    """
    # Job-related methods
    def get_candidate_score(self, job_details: Dict, resume_details: Dict,
                        threshold: float = 50.0, sections_weights: Optional[Dict] = None) -> JobMatchResult:
        data = {
            "job_details": job_details,
            "resume_details": resume_details,
            "threshold": threshold
        }
        if sections_weights:
            data["sections_weights"] = sections_weights
        return self._make_request('POST', 'v1/jobs/candidate-scoring/', json=data)

    def write_job_description(self, job_title: str, hiring_needs: str,
                             company_description: str, job_type: str,
                             job_location: str, specific_benefits: str) -> JobDetailsResponse:
        data = {
            "job_title": job_title,
            "hiring_needs": hiring_needs,
            "company_description": company_description,
            "job_type": job_type,
            "job_location": job_location,
            "specific_benefits": specific_benefits
        }
        return self._make_request('POST', 'v1/jobs/job-writing/', json=data)

    def parse_job_description(self, job_site_content: str) -> JobDetailsResponse:
        data = {
            "text": job_site_content
        }
        return self._make_request('POST', 'v1/jobs/extract-job-description/', json=data)

    def create_zoom_meeting(self, client_id: str, client_secret: str, account_id: str, duration: int, start_time: str, timezone: str, topic: str) -> ZoomMeetingResponse:
        data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "account_id": account_id,
            "duration": duration,
            "start_time": start_time,
            "timezone": timezone,
            "topic": topic
        }
        return self._make_request('POST', 'v1/jobs/create-zoom-meeting/', json=data)

    def list_job_indexes(self) -> IndexesListResponse:
        return self._make_request('GET', 'v1/jobs/list-indexes/')

    def search_jobs(
        self, 
        query: str, 
        index_name: str, 
        filters: Optional[Dict] = None, 
        department_name: str|None=None,
        custom_query: Optional[Dict] = None,
        top_k: Optional[int] = None
    ) -> SearchResponse:
        data = {"query": query, "index_name": index_name}
        if filters:
            data["filters"] = filters
        if department_name:
            data["department_name"] = department_name
        if custom_query:
            data["custom_query"] = custom_query
        if top_k:
            data["top_k"] = top_k
        return self._make_request('POST', 'v1/jobs/search/', json=data)

    def delete_job(self, documents_ids: List[str], index_name: str) -> Dict:
        data = {
            "documents_ids": documents_ids,
            "index_name": index_name
        }
        return self._make_request('POST', 'v1/jobs/delete/', json=data)

    def index_job(self, documents: List[Dict], index_name: str, id_field: str, search_fields: List[str], department_name: str|None=None) -> Dict:
        extra_fields = {}
        if department_name:
            extra_fields["department_name"] = department_name
        data = {
            "documents": documents,
            "index_name": index_name,
            "id_field": id_field,
            "search_fields": search_fields,
            **extra_fields

        }
        return self._make_request('POST', 'v1/jobs/index/', json=data)
