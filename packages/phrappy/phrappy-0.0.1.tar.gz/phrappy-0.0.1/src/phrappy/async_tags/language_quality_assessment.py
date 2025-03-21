from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union, Any

if TYPE_CHECKING:
    from ..client import SyncPhraseTMSClient

from ..models import (
    PageDtoLqaReportRecipientDto,
    LqaReportLinkDto,
    AssessmentRequestDto,
    AssessmentResultsDto,
    FinishAssessmentsDto,
    LqaReportEmailRequestDto,
    RunAutoLqaDto,
    AssessmentDetailDto,
    AssessmentDetailsDto,
    FinishAssessmentDto,
    AssessmentBasicDto,
    AssessmentResultDto,
    ScoringResultDto
    
)


class LanguageQualityAssessmentOperations:
    def __init__(self, client: SyncPhraseTMSClient):
        self.client = client


    async def discard_assessment_results(
        self,
        assessment_request_dto: AssessmentRequestDto,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: discardAssessmentResults
        Discard multiple finished LQA Assessment results
        
        :param assessment_request_dto: AssessmentRequestDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/lqa/assessments/scorings"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = assessment_request_dto

        r = await self.client.make_request(
            "DELETE",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return
        


    async def discard_ongoing_assessment(
        self,
        job_uid: str,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: discardOngoingAssessment
        Discard ongoing LQA Assessment
        
        :param job_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/lqa/assessments/{job_uid}"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = None

        r = await self.client.make_request(
            "DELETE",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return
        


    async def discard_ongoing_assessments(
        self,
        assessment_request_dto: AssessmentRequestDto,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: discardOngoingAssessments
        Discard multiple ongoing LQA Assessments
        
        :param assessment_request_dto: AssessmentRequestDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/lqa/assessments"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = assessment_request_dto

        r = await self.client.make_request(
            "DELETE",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return
        


    async def download_lqa_reports(
        self,
        job_parts: str,
        phrase_token: Optional[str] = None,
) -> bytes:
        """
        Operation id: downloadLqaReports
        Download LQA Assessment XLSX reports
        Returns a single xlsx report or ZIP archive with multiple reports.
If any given jobPart is not from LQA workflow step, reports from successive workflow steps may be returned
If none were found returns 404 error, otherwise returns those that were found.
        :param job_parts: str (required), query. Comma separated list of JobPart UIDs, between 1 and 100 UIDs .
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """
        endpoint = f"/api2/v1/lqa/assessments/reports"
        params = {
            "jobParts": job_parts
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = None

        r = await self.client.make_request(
            "GET",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return r.content
        


    async def finish_assessment(
        self,
        finish_assessment_dto: FinishAssessmentDto,
        job_uid: str,
        phrase_token: Optional[str] = None,
) -> ScoringResultDto:
        """
        Operation id: finishAssessment
        Finish LQA Assessment
        Finishing LQA Assessment will calculate score
        :param finish_assessment_dto: FinishAssessmentDto (required), body. 
        :param job_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ScoringResultDto
        """
        endpoint = f"/api2/v1/lqa/assessments/{job_uid}/scorings"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = finish_assessment_dto

        r = await self.client.make_request(
            "PUT",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return ScoringResultDto(**r.json())
        


    async def finish_assessments(
        self,
        finish_assessments_dto: FinishAssessmentsDto,
        phrase_token: Optional[str] = None,
) -> AssessmentResultsDto:
        """
        Operation id: finishAssessments
        Finish multiple LQA Assessments
        Finishing LQA Assessments will calculate scores
        :param finish_assessments_dto: FinishAssessmentsDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AssessmentResultsDto
        """
        endpoint = f"/api2/v1/lqa/assessments/scorings"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = finish_assessments_dto

        r = await self.client.make_request(
            "PUT",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return AssessmentResultsDto(**r.json())
        


    async def get_assessment(
        self,
        job_uid: str,
        phrase_token: Optional[str] = None,
) -> AssessmentDetailDto:
        """
        Operation id: getAssessment
        Get LQA Assessment
        Returns Assessment status and the results.
If given job is not from LQA workflow step, result from successive workflow steps may be returned
        :param job_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AssessmentDetailDto
        """
        endpoint = f"/api2/v1/lqa/assessments/{job_uid}"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = None

        r = await self.client.make_request(
            "GET",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return AssessmentDetailDto(**r.json())
        


    async def get_assessment_results(
        self,
        assessment_request_dto: AssessmentRequestDto,
        phrase_token: Optional[str] = None,
) -> AssessmentResultDto:
        """
        Operation id: getAssessmentResults
        Get LQA Assessment results
        
        :param assessment_request_dto: AssessmentRequestDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AssessmentResultDto
        """
        endpoint = f"/api2/v1/lqa/assessments/results"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = assessment_request_dto

        r = await self.client.make_request(
            "POST",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return AssessmentResultDto(**r.json())
        


    async def get_assessments(
        self,
        assessment_request_dto: AssessmentRequestDto,
        phrase_token: Optional[str] = None,
) -> AssessmentDetailsDto:
        """
        Operation id: getAssessments
        Get multiple LQA Assessments
        Returns Assessment results for given jobs.
If any given job is not from LQA workflow step, result from successive workflow steps may be returned
        :param assessment_request_dto: AssessmentRequestDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AssessmentDetailsDto
        """
        endpoint = f"/api2/v1/lqa/assessments"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = assessment_request_dto

        r = await self.client.make_request(
            "POST",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return AssessmentDetailsDto(**r.json())
        


    async def get_lqa_report_link(
        self,
        job_parts: str,
        phrase_token: Optional[str] = None,
) -> LqaReportLinkDto:
        """
        Operation id: getLqaReportLink
        Get sharable link of LQA reports
        
        :param job_parts: str (required), query. Comma separated list of JobPart UIDs.
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LqaReportLinkDto
        """
        endpoint = f"/api2/v1/lqa/assessments/reports/link"
        params = {
            "jobParts": job_parts
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = None

        r = await self.client.make_request(
            "GET",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return LqaReportLinkDto(**r.json())
        


    async def get_lqa_report_recipients(
        self,
        job_parts: str,
        name_or_email: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        phrase_token: Optional[str] = None,
) -> PageDtoLqaReportRecipientDto:
        """
        Operation id: getLqaReportRecipients
        Get recipients of email with LQA reports
        
        :param job_parts: str (required), query. Comma separated list of JobPart UIDs.
        :param name_or_email: Optional[str] = None (optional), query. 
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoLqaReportRecipientDto
        """
        endpoint = f"/api2/v1/lqa/assessments/reports/recipients"
        params = {
            "pageNumber": page_number,
            "pageSize": page_size,
            "jobParts": job_parts,
            "nameOrEmail": name_or_email
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = None

        r = await self.client.make_request(
            "GET",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return PageDtoLqaReportRecipientDto(**r.json())
        


    async def run_auto_lqa(
        self,
        run_auto_lqa_dto: RunAutoLqaDto,
        project_uid: str,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: runAutoLqa
        Run Auto LQA
        Runs Auto LQA either for job parts listed in `jobParts`
                    or for all job parts in the given `projectWorkflowStep`.
                    Both fields are mutually exclusive. If the project has no steps,
                    then all job parts in the project accessible to the user are used.
        :param run_auto_lqa_dto: RunAutoLqaDto (required), body. 
        :param project_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/projects/{project_uid}/runAutoLqa"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = run_auto_lqa_dto

        r = await self.client.make_request(
            "POST",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return
        


    async def send_lqa_report_email(
        self,
        lqa_report_email_request_dto: LqaReportEmailRequestDto,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: sendLqaReportEmail
        Send email(s) with LQA reports
        
        :param lqa_report_email_request_dto: LqaReportEmailRequestDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/lqa/assessments/reports/emails"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = lqa_report_email_request_dto

        r = await self.client.make_request(
            "POST",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return
        


    async def start_assessments(
        self,
        assessment_request_dto: AssessmentRequestDto,
        phrase_token: Optional[str] = None,
) -> AssessmentDetailsDto:
        """
        Operation id: startAssessments
        Start multiple LQA Assessments
        Starts LQA assessments for the given job parts.
                    If any of them have the assessment already started or finished, they are left unchanged.
        :param assessment_request_dto: AssessmentRequestDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AssessmentDetailsDto
        """
        endpoint = f"/api2/v1/lqa/assessments"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = assessment_request_dto

        r = await self.client.make_request(
            "PUT",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return AssessmentDetailsDto(**r.json())
        


    async def start_new_assessment(
        self,
        job_uid: str,
        phrase_token: Optional[str] = None,
) -> AssessmentBasicDto:
        """
        Operation id: startNewAssessment
        Start LQA Assessment
        Starts LQA assessment for the given job part.
                    If the assessment has already been started or finished, it's discarded and started fresh.
        :param job_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AssessmentBasicDto
        """
        endpoint = f"/api2/v1/lqa/assessments/{job_uid}"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = None

        r = await self.client.make_request(
            "POST",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return AssessmentBasicDto(**r.json())
        



if __name__ == '__main__':
    print("This module is not intended to be run directly.")