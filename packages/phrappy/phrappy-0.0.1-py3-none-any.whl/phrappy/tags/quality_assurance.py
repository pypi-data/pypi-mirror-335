from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union, Any

if TYPE_CHECKING:
    from ..client import SyncPhraseTMSClient

from ..models import (
    PageDtoLqaProfileReferenceDto,
    QualityAssuranceRunDtoV3,
    UserReference,
    QualityAssuranceBatchRunDtoV3,
    LqaProfileDetailDto,
    UpdateIgnoredWarningsDto_2,
    LqaProfileReferenceDto,
    QualityAssuranceSegmentsRunDtoV3,
    InputStream,
    UpdateLqaProfileDto,
    QualityAssuranceResponseDto,
    QualityAssuranceChecksDtoV2,
    PageDtoUserReference,
    CreateLqaProfileDto,
    UpdateIgnoredChecksDto,
    UpdateIgnoredWarningsDto,
    QualityAssuranceChecksDtoV4
    
)


class QualityAssuranceOperations:
    def __init__(self, client: SyncPhraseTMSClient):
        self.client = client


    def add_ignored_warnings(
        self,
        update_ignored_warnings_dto: UpdateIgnoredWarningsDto,
        job_uid: str,
        project_uid: str,
        phrase_token: Optional[str] = None,
) -> UpdateIgnoredWarningsDto:
        """
        Operation id: addIgnoredWarnings
        Add ignored warnings
        
        :param update_ignored_warnings_dto: UpdateIgnoredWarningsDto (required), body. 
        :param job_uid: str (required), path. 
        :param project_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: UpdateIgnoredWarningsDto
        """
        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_uid}/qualityAssurances/ignoredWarnings"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = update_ignored_warnings_dto

        r = self.client.make_request(
            "POST",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return UpdateIgnoredWarningsDto(**r.json())
        


    def add_ignored_warnings_v2(
        self,
        update_ignored_warnings_dto_2: UpdateIgnoredWarningsDto_2,
        project_uid: str,
        phrase_token: Optional[str] = None,
) -> UpdateIgnoredWarningsDto_2:
        """
        Operation id: addIgnoredWarningsV2
        Add ignored warnings
        
        :param update_ignored_warnings_dto_2: UpdateIgnoredWarningsDto_2 (required), body. 
        :param project_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: UpdateIgnoredWarningsDto_2
        """
        endpoint = f"/api2/v2/projects/{project_uid}/jobs/qualityAssurances/ignoredWarnings"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = update_ignored_warnings_dto_2

        r = self.client.make_request(
            "POST",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return UpdateIgnoredWarningsDto_2(**r.json())
        


    def create_lqa_profile(
        self,
        create_lqa_profile_dto: CreateLqaProfileDto,
        phrase_token: Optional[str] = None,
) -> LqaProfileDetailDto:
        """
        Operation id: createLqaProfile
        Create LQA profile
        
        :param create_lqa_profile_dto: CreateLqaProfileDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LqaProfileDetailDto
        """
        endpoint = f"/api2/v1/lqa/profiles"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = create_lqa_profile_dto

        r = self.client.make_request(
            "POST",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return LqaProfileDetailDto(**r.json())
        


    def delete_ignored_warnings(
        self,
        update_ignored_warnings_dto: UpdateIgnoredWarningsDto,
        job_uid: str,
        project_uid: str,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: deleteIgnoredWarnings
        Delete ignored warnings
        
        :param update_ignored_warnings_dto: UpdateIgnoredWarningsDto (required), body. 
        :param job_uid: str (required), path. 
        :param project_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_uid}/qualityAssurances/ignoredWarnings"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = update_ignored_warnings_dto

        r = self.client.make_request(
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
        


    def delete_ignored_warnings_v2(
        self,
        update_ignored_warnings_dto_2: UpdateIgnoredWarningsDto_2,
        project_uid: str,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: deleteIgnoredWarningsV2
        Delete ignored warnings
        
        :param update_ignored_warnings_dto_2: UpdateIgnoredWarningsDto_2 (required), body. 
        :param project_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v2/projects/{project_uid}/jobs/qualityAssurances/ignoredWarnings"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = update_ignored_warnings_dto_2

        r = self.client.make_request(
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
        


    def delete_lqa_profile(
        self,
        profile_uid: str,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: deleteLqaProfile
        Delete LQA profile
        
        :param profile_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/lqa/profiles/{profile_uid}"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = None

        r = self.client.make_request(
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
        


    def duplicate_profile(
        self,
        profile_uid: str,
        phrase_token: Optional[str] = None,
) -> LqaProfileReferenceDto:
        """
        Operation id: duplicateProfile
        Duplicate LQA profile
        
        :param profile_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LqaProfileReferenceDto
        """
        endpoint = f"/api2/v1/lqa/profiles/{profile_uid}/duplicate"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = None

        r = self.client.make_request(
            "POST",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return LqaProfileReferenceDto(**r.json())
        


    def enabled_quality_checks_for_job(
        self,
        job_uid: str,
        project_uid: str,
        phrase_token: Optional[str] = None,
) -> QualityAssuranceChecksDtoV2:
        """
        Operation id: enabledQualityChecksForJob
        Get QA settings for job
        Returns enabled quality assurance checks and settings for job.
        :param job_uid: str (required), path. 
        :param project_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: QualityAssuranceChecksDtoV2
        """
        endpoint = f"/api2/v2/projects/{project_uid}/jobs/{job_uid}/qualityAssurances/settings"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = None

        r = self.client.make_request(
            "GET",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return QualityAssuranceChecksDtoV2(**r.json())
        


    def enabled_quality_checks_for_project(
        self,
        project_uid: str,
        phrase_token: Optional[str] = None,
) -> QualityAssuranceChecksDtoV2:
        """
        Operation id: enabledQualityChecksForProject
        Get QA settings
        Returns enabled quality assurance checks and settings.
        :param project_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: QualityAssuranceChecksDtoV2
        """
        endpoint = f"/api2/v2/projects/{project_uid}/jobs/qualityAssurances/settings"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = None

        r = self.client.make_request(
            "GET",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return QualityAssuranceChecksDtoV2(**r.json())
        


    def get_lqa_profile(
        self,
        profile_uid: str,
        phrase_token: Optional[str] = None,
) -> LqaProfileDetailDto:
        """
        Operation id: getLqaProfile
        Get LQA profile details
        
        :param profile_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LqaProfileDetailDto
        """
        endpoint = f"/api2/v1/lqa/profiles/{profile_uid}"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = None

        r = self.client.make_request(
            "GET",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return LqaProfileDetailDto(**r.json())
        


    def get_lqa_profile_authors(
        self,
        phrase_token: Optional[str] = None,
) -> UserReference:
        """
        Operation id: getLqaProfileAuthors
        Get list of LQA profile authors
        
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: UserReference
        """
        endpoint = f"/api2/v1/lqa/profiles/authors"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = None

        r = self.client.make_request(
            "GET",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return UserReference(**r.json())
        


    def get_lqa_profile_authors_v2(
        self,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 20,
        phrase_token: Optional[str] = None,
) -> PageDtoUserReference:
        """
        Operation id: getLqaProfileAuthorsV2
        Get list of LQA profile authors
        
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 20 (optional), query. Page size, accepts values between 1 and 50, default 20.
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoUserReference
        """
        endpoint = f"/api2/v2/lqa/profiles/authors"
        params = {
            "pageNumber": page_number,
            "pageSize": page_size
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = None

        r = self.client.make_request(
            "GET",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return PageDtoUserReference(**r.json())
        


    def get_lqa_profile_default_values(
        self,
        phrase_token: Optional[str] = None,
) -> LqaProfileDetailDto:
        """
        Operation id: getLqaProfileDefaultValues
        Get LQA profile default values
        
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LqaProfileDetailDto
        """
        endpoint = f"/api2/v1/lqa/profiles/defaultValues"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = None

        r = self.client.make_request(
            "GET",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return LqaProfileDetailDto(**r.json())
        


    def get_lqa_profiles(
        self,
        created_by: Optional[str] = None,
        date_created: Optional[str] = None,
        name: Optional[str] = None,
        order: Optional[List[str]] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 20,
        sort: Optional[List[str]] = None,
        phrase_token: Optional[str] = None,
) -> PageDtoLqaProfileReferenceDto:
        """
        Operation id: getLqaProfiles
        GET list LQA profiles
        
        :param created_by: Optional[str] = None (optional), query. It is used for filter the list by who created the profile.
        :param date_created: Optional[str] = None (optional), query. It is used for filter the list by date created.
        :param name: Optional[str] = None (optional), query. Name of LQA profiles, it is used for filter the list by name.
        :param order: Optional[List[str]] = None (optional), query. 
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 20 (optional), query. Page size, accepts values between 1 and 50, default 20.
        :param sort: Optional[List[str]] = None (optional), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoLqaProfileReferenceDto
        """
        endpoint = f"/api2/v1/lqa/profiles"
        params = {
            "name": name,
            "createdBy": created_by,
            "dateCreated": date_created,
            "pageNumber": page_number,
            "pageSize": page_size,
            "sort": sort,
            "order": order
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = None

        r = self.client.make_request(
            "GET",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return PageDtoLqaProfileReferenceDto(**r.json())
        


    def get_qa_settings_for_job_part_v4(
        self,
        job_uid: str,
        project_uid: str,
        phrase_token: Optional[str] = None,
) -> QualityAssuranceChecksDtoV4:
        """
        Operation id: getQaSettingsForJobPartV4
        Get QA settings for job part
        Returns enabled quality assurance checks and settings for job.
        :param job_uid: str (required), path. 
        :param project_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: QualityAssuranceChecksDtoV4
        """
        endpoint = f"/api2/v4/projects/{project_uid}/jobs/{job_uid}/qualityAssurances/settings"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = None

        r = self.client.make_request(
            "GET",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return QualityAssuranceChecksDtoV4(**r.json())
        


    def get_qa_settings_for_project_v4(
        self,
        project_uid: str,
        phrase_token: Optional[str] = None,
) -> QualityAssuranceChecksDtoV4:
        """
        Operation id: getQaSettingsForProjectV4
        Get QA settings for project
        Returns enabled quality assurance checks and settings.
        :param project_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: QualityAssuranceChecksDtoV4
        """
        endpoint = f"/api2/v4/projects/{project_uid}/jobs/qualityAssurances/settings"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = None

        r = self.client.make_request(
            "GET",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return QualityAssuranceChecksDtoV4(**r.json())
        


    def make_default(
        self,
        profile_uid: str,
        phrase_token: Optional[str] = None,
) -> LqaProfileReferenceDto:
        """
        Operation id: makeDefault
        Make LQA profile default
        
        :param profile_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LqaProfileReferenceDto
        """
        endpoint = f"/api2/v1/lqa/profiles/{profile_uid}/default"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = None

        r = self.client.make_request(
            "POST",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return LqaProfileReferenceDto(**r.json())
        


    def run_qa_and_save_v4(
        self,
        input_stream: bytes,
        project_uid: str,
        segment_id: str,
        phrase_token: Optional[str] = None,
) -> QualityAssuranceResponseDto:
        """
        Operation id: runQaAndSaveV4
        Run quality assurance on selected segments and save segments
        By default runs only fast running checks.
        :param input_stream: bytes (required), body. 
        :param project_uid: str (required), path. 
        :param segment_id: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: QualityAssuranceResponseDto
        """
        endpoint = f"/api2/v4/projects/{project_uid}/jobs/qualityAssurances/segments/{segment_id}/runWithUpdate"
        params = {
            
        }
        headers = {
            
        }

        content = input_stream

        files = None

        payload = None

        r = self.client.make_request(
            "POST",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return QualityAssuranceResponseDto(**r.json())
        


    def run_qa_for_job_part_v3(
        self,
        quality_assurance_run_dto_v3: QualityAssuranceRunDtoV3,
        job_uid: str,
        project_uid: str,
        phrase_token: Optional[str] = None,
) -> QualityAssuranceResponseDto:
        """
        Operation id: runQaForJobPartV3
        Run quality assurance
        Call "Get QA settings" endpoint to get the list of enabled QA checks
        :param quality_assurance_run_dto_v3: QualityAssuranceRunDtoV3 (required), body. 
        :param job_uid: str (required), path. 
        :param project_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: QualityAssuranceResponseDto
        """
        endpoint = f"/api2/v3/projects/{project_uid}/jobs/{job_uid}/qualityAssurances/run"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = quality_assurance_run_dto_v3

        r = self.client.make_request(
            "POST",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return QualityAssuranceResponseDto(**r.json())
        


    def run_qa_for_job_part_v4(
        self,
        quality_assurance_run_dto_v3: QualityAssuranceRunDtoV3,
        job_uid: str,
        project_uid: str,
        phrase_token: Optional[str] = None,
) -> QualityAssuranceResponseDto:
        """
        Operation id: runQaForJobPartV4
        Run quality assurance
        Call "Get QA settings" endpoint to get the list of enabled QA checks
        :param quality_assurance_run_dto_v3: QualityAssuranceRunDtoV3 (required), body. 
        :param job_uid: str (required), path. 
        :param project_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: QualityAssuranceResponseDto
        """
        endpoint = f"/api2/v4/projects/{project_uid}/jobs/{job_uid}/qualityAssurances/run"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = quality_assurance_run_dto_v3

        r = self.client.make_request(
            "POST",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return QualityAssuranceResponseDto(**r.json())
        


    def run_qa_for_job_parts_v3(
        self,
        quality_assurance_batch_run_dto_v3: QualityAssuranceBatchRunDtoV3,
        project_uid: str,
        phrase_token: Optional[str] = None,
) -> QualityAssuranceResponseDto:
        """
        Operation id: runQaForJobPartsV3
        Run quality assurance (batch)
        Call "Get QA settings" endpoint to get the list of enabled QA checks
        :param quality_assurance_batch_run_dto_v3: QualityAssuranceBatchRunDtoV3 (required), body. 
        :param project_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: QualityAssuranceResponseDto
        """
        endpoint = f"/api2/v3/projects/{project_uid}/jobs/qualityAssurances/run"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = quality_assurance_batch_run_dto_v3

        r = self.client.make_request(
            "POST",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return QualityAssuranceResponseDto(**r.json())
        


    def run_qa_for_job_parts_v4(
        self,
        quality_assurance_batch_run_dto_v3: QualityAssuranceBatchRunDtoV3,
        project_uid: str,
        phrase_token: Optional[str] = None,
) -> QualityAssuranceResponseDto:
        """
        Operation id: runQaForJobPartsV4
        Run quality assurance (batch)
        Call "Get QA settings" endpoint to get the list of enabled QA checks
        :param quality_assurance_batch_run_dto_v3: QualityAssuranceBatchRunDtoV3 (required), body. 
        :param project_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: QualityAssuranceResponseDto
        """
        endpoint = f"/api2/v4/projects/{project_uid}/jobs/qualityAssurances/run"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = quality_assurance_batch_run_dto_v3

        r = self.client.make_request(
            "POST",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return QualityAssuranceResponseDto(**r.json())
        


    def run_qa_for_segments_v3(
        self,
        quality_assurance_segments_run_dto_v3: QualityAssuranceSegmentsRunDtoV3,
        project_uid: str,
        phrase_token: Optional[str] = None,
) -> QualityAssuranceResponseDto:
        """
        Operation id: runQaForSegmentsV3
        Run quality assurance on selected segments
        By default runs only fast running checks. Source and target language of jobs have to match.
        :param quality_assurance_segments_run_dto_v3: QualityAssuranceSegmentsRunDtoV3 (required), body. 
        :param project_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: QualityAssuranceResponseDto
        """
        endpoint = f"/api2/v3/projects/{project_uid}/jobs/qualityAssurances/segments/run"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = quality_assurance_segments_run_dto_v3

        r = self.client.make_request(
            "POST",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return QualityAssuranceResponseDto(**r.json())
        


    def run_qa_for_segments_v4(
        self,
        quality_assurance_segments_run_dto_v3: QualityAssuranceSegmentsRunDtoV3,
        project_uid: str,
        phrase_token: Optional[str] = None,
) -> QualityAssuranceResponseDto:
        """
        Operation id: runQaForSegmentsV4
        Run quality assurance on selected segments
        By default runs only fast running checks. Source and target language of jobs have to match.
        :param quality_assurance_segments_run_dto_v3: QualityAssuranceSegmentsRunDtoV3 (required), body. 
        :param project_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: QualityAssuranceResponseDto
        """
        endpoint = f"/api2/v4/projects/{project_uid}/jobs/qualityAssurances/segments/run"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = quality_assurance_segments_run_dto_v3

        r = self.client.make_request(
            "POST",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return QualityAssuranceResponseDto(**r.json())
        


    def update_ignored_checks(
        self,
        update_ignored_checks_dto: UpdateIgnoredChecksDto,
        job_uid: str,
        project_uid: str,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: updateIgnoredChecks
        Edit ignored checks
        
        :param update_ignored_checks_dto: UpdateIgnoredChecksDto (required), body. 
        :param job_uid: str (required), path. 
        :param project_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_uid}/qualityAssurances/ignoreChecks"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = update_ignored_checks_dto

        r = self.client.make_request(
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
        


    def update_lqa_profile(
        self,
        update_lqa_profile_dto: UpdateLqaProfileDto,
        profile_uid: str,
        phrase_token: Optional[str] = None,
) -> LqaProfileDetailDto:
        """
        Operation id: updateLqaProfile
        Update LQA profile
        
        :param update_lqa_profile_dto: UpdateLqaProfileDto (required), body. 
        :param profile_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LqaProfileDetailDto
        """
        endpoint = f"/api2/v1/lqa/profiles/{profile_uid}"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = update_lqa_profile_dto

        r = self.client.make_request(
            "PUT",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return LqaProfileDetailDto(**r.json())
        



if __name__ == '__main__':
    print("This module is not intended to be run directly.")