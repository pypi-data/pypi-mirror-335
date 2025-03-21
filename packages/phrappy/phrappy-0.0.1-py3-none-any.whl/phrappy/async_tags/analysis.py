from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union, Any

if TYPE_CHECKING:
    from ..client import SyncPhraseTMSClient

from ..models import (
    CreateAnalyseAsyncV2Dto,
    PageDtoAnalyseReference,
    AnalyseLanguagePartDto,
    AsyncAnalyseListResponseDto,
    AnalyseV3Dto,
    AnalyseV2Dto,
    AsyncAnalyseListResponseV2Dto,
    AnalyseJobDto,
    BulkEditAnalyseV2Dto,
    CreateAnalyseListAsyncDto,
    EditAnalyseV2Dto,
    AnalysesV2Dto,
    AnalyseRecalculateResponseDto,
    PageDtoAnalyseJobDto,
    AnalyseRecalculateRequestDto,
    BulkDeleteAnalyseDto
    
)


class AnalysisOperations:
    def __init__(self, client: SyncPhraseTMSClient):
        self.client = client


    async def analyses_batch_edit_v2(
        self,
        bulk_edit_analyse_v2_dto: BulkEditAnalyseV2Dto,
        phrase_token: Optional[str] = None,
) -> AnalysesV2Dto:
        """
        Operation id: analyses-batchEdit-v2
        Edit analyses (batch)
        If no netRateScheme is provided in request, then netRateScheme associated with provider will
be used if it exists, otherwise it will remain the same as it was.
        :param bulk_edit_analyse_v2_dto: BulkEditAnalyseV2Dto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AnalysesV2Dto
        """
        endpoint = f"/api2/v2/analyses/bulk"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = bulk_edit_analyse_v2_dto

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

        
        return AnalysesV2Dto(**r.json())
        


    async def bulk_delete_analyses(
        self,
        bulk_delete_analyse_dto: BulkDeleteAnalyseDto,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: bulkDeleteAnalyses
        Delete analyses (batch)
        
        :param bulk_delete_analyse_dto: BulkDeleteAnalyseDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/analyses/bulk"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = bulk_delete_analyse_dto

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
        


    async def create_analyse_async_v2(
        self,
        create_analyse_async_v2_dto: CreateAnalyseAsyncV2Dto,
        phrase_token: Optional[str] = None,
) -> AsyncAnalyseListResponseV2Dto:
        """
        Operation id: createAnalyseAsyncV2
        Create analysis
        Returns created analyses - batching analyses by number of segments (api.segment.count.approximation, default 100000), in case request contains more segments than maximum (api.segment.max.count, default 300000), returns 400 bad request.
        :param create_analyse_async_v2_dto: CreateAnalyseAsyncV2Dto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AsyncAnalyseListResponseV2Dto
        """
        endpoint = f"/api2/v2/analyses"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = create_analyse_async_v2_dto

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

        
        return AsyncAnalyseListResponseV2Dto(**r.json())
        


    async def create_analyses_for_langs(
        self,
        create_analyse_list_async_dto: CreateAnalyseListAsyncDto,
        phrase_token: Optional[str] = None,
) -> AsyncAnalyseListResponseDto:
        """
        Operation id: createAnalysesForLangs
        Create analyses by languages
        
        :param create_analyse_list_async_dto: CreateAnalyseListAsyncDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AsyncAnalyseListResponseDto
        """
        endpoint = f"/api2/v1/analyses/byLanguages"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = create_analyse_list_async_dto

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

        
        return AsyncAnalyseListResponseDto(**r.json())
        


    async def create_analyses_for_providers(
        self,
        create_analyse_list_async_dto: CreateAnalyseListAsyncDto,
        phrase_token: Optional[str] = None,
) -> AsyncAnalyseListResponseDto:
        """
        Operation id: createAnalysesForProviders
        Create analyses by providers
        
        :param create_analyse_list_async_dto: CreateAnalyseListAsyncDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AsyncAnalyseListResponseDto
        """
        endpoint = f"/api2/v1/analyses/byProviders"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = create_analyse_list_async_dto

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

        
        return AsyncAnalyseListResponseDto(**r.json())
        


    async def delete(
        self,
        analyse_uid: str,
        purge: Optional[bool] = None,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: delete
        Delete analysis
        
        :param analyse_uid: str (required), path. 
        :param purge: Optional[bool] = None (optional), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/analyses/{analyse_uid}"
        params = {
            "purge": purge
            
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
        


    async def download_analyse(
        self,
        analyse_uid: str,
        format: str,
        phrase_token: Optional[str] = None,
) -> bytes:
        """
        Operation id: downloadAnalyse
        Download analysis
        
        :param analyse_uid: str (required), path. 
        :param format: str (required), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """
        endpoint = f"/api2/v1/analyses/{analyse_uid}/download"
        params = {
            "format": format
            
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
        


    async def edit_analysis(
        self,
        analyse_uid: str,
        edit_analyse_v2_dto: EditAnalyseV2Dto,
        phrase_token: Optional[str] = None,
) -> AnalyseV2Dto:
        """
        Operation id: editAnalysis
        Edit analysis
        If no netRateScheme is provided in
request, then netRateScheme associated with provider will be used if it exists, otherwise it will remain the same
as it was.
        :param analyse_uid: str (required), path. 
        :param edit_analyse_v2_dto: EditAnalyseV2Dto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AnalyseV2Dto
        """
        endpoint = f"/api2/v2/analyses/{analyse_uid}"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = edit_analyse_v2_dto

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

        
        return AnalyseV2Dto(**r.json())
        


    async def get_analyse_language_part(
        self,
        analyse_language_part_id: int,
        analyse_uid: str,
        phrase_token: Optional[str] = None,
) -> AnalyseLanguagePartDto:
        """
        Operation id: getAnalyseLanguagePart
        Get analysis language part
        Returns analysis language pair
        :param analyse_language_part_id: int (required), path. 
        :param analyse_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AnalyseLanguagePartDto
        """
        endpoint = f"/api2/v1/analyses/{analyse_uid}/analyseLanguageParts/{analyse_language_part_id}"
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

        
        return AnalyseLanguagePartDto(**r.json())
        


    async def get_analyse_v3(
        self,
        analyse_uid: str,
        phrase_token: Optional[str] = None,
) -> AnalyseV3Dto:
        """
        Operation id: getAnalyseV3
        Get analysis
        
This API endpoint retrieves analysis results, encompassing basic information about the analysis, such as its name,
assigned provider,
[net rate scheme](https://support.phrase.com/hc/en-us/articles/5709665578908-Net-Rate-Schemes-TMS-),
[Analysis settings](https://support.phrase.com/hc/en-us/articles/5709712007708-Analysis-TMS-) settings and a subset of
[Get project](#operation/getProject) information for the project the analysis belongs to.

The analysis results consist of each analyzed language, presented as an item within the `analyseLanguageParts` array.
Each of these items contains details regarding the analyzed
[jobs](https://support.phrase.com/hc/en-us/articles/5709686763420-Jobs-TMS-),
[translation memories](https://support.phrase.com/hc/en-us/articles/5709688865692-Translation-Memories-Overview)
and the resultant data.

The analysis results are divided into two sections:

- `data` stores the raw numbers,
- `discountedData` recalculates the raw numbers using the selected net rate scheme.

Similar to the UI, both raw and net numbers are categorized based on their source into TM, MT, and NT categories,
including repetitions where applicable. These categories are then further subdivided based on the match score.

        :param analyse_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AnalyseV3Dto
        """
        endpoint = f"/api2/v3/analyses/{analyse_uid}"
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

        
        return AnalyseV3Dto(**r.json())
        


    async def get_job_part_analyse(
        self,
        analyse_uid: str,
        job_uid: str,
        phrase_token: Optional[str] = None,
) -> AnalyseJobDto:
        """
        Operation id: getJobPartAnalyse
        Get jobs analysis
        Returns job's analyse
        :param analyse_uid: str (required), path. 
        :param job_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AnalyseJobDto
        """
        endpoint = f"/api2/v1/analyses/{analyse_uid}/jobs/{job_uid}"
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

        
        return AnalyseJobDto(**r.json())
        


    async def list_by_project_v3(
        self,
        project_uid: str,
        name: Optional[str] = None,
        only_owner_org: Optional[bool] = None,
        order: Optional[str] = "desc",
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        sort: Optional[str] = "DATE_CREATED",
        uid: Optional[str] = None,
        phrase_token: Optional[str] = None,
) -> PageDtoAnalyseReference:
        """
        Operation id: listByProjectV3
        List analyses by project
        
        :param project_uid: str (required), path. 
        :param name: Optional[str] = None (optional), query. Name to search by.
        :param only_owner_org: Optional[bool] = None (optional), query. 
        :param order: Optional[str] = "desc" (optional), query. Sorting order.
        :param page_number: Optional[int] = 0 (optional), query. 
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param sort: Optional[str] = "DATE_CREATED" (optional), query. Sorting field.
        :param uid: Optional[str] = None (optional), query. Uid to search by.
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoAnalyseReference
        """
        endpoint = f"/api2/v3/projects/{project_uid}/analyses"
        params = {
            "name": name,
            "uid": uid,
            "pageNumber": page_number,
            "pageSize": page_size,
            "sort": sort,
            "order": order,
            "onlyOwnerOrg": only_owner_org
            
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

        
        return PageDtoAnalyseReference(**r.json())
        


    async def list_job_parts(
        self,
        analyse_language_part_id: int,
        analyse_uid: str,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        phrase_token: Optional[str] = None,
) -> PageDtoAnalyseJobDto:
        """
        Operation id: listJobParts
        List jobs of analyses
        Returns list of job's analyses
        :param analyse_language_part_id: int (required), path. 
        :param analyse_uid: str (required), path. 
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoAnalyseJobDto
        """
        endpoint = f"/api2/v1/analyses/{analyse_uid}/analyseLanguageParts/{analyse_language_part_id}/jobs"
        params = {
            "pageNumber": page_number,
            "pageSize": page_size
            
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

        
        return PageDtoAnalyseJobDto(**r.json())
        


    async def list_part_analyse_v3(
        self,
        job_uid: str,
        project_uid: str,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        phrase_token: Optional[str] = None,
) -> PageDtoAnalyseReference:
        """
        Operation id: listPartAnalyseV3
        List analyses
        
        :param job_uid: str (required), path. 
        :param project_uid: str (required), path. 
        :param page_number: Optional[int] = 0 (optional), query. 
        :param page_size: Optional[int] = 50 (optional), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoAnalyseReference
        """
        endpoint = f"/api2/v3/projects/{project_uid}/jobs/{job_uid}/analyses"
        params = {
            "pageNumber": page_number,
            "pageSize": page_size
            
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

        
        return PageDtoAnalyseReference(**r.json())
        


    async def recalculate(
        self,
        analyse_recalculate_request_dto: AnalyseRecalculateRequestDto,
        phrase_token: Optional[str] = None,
) -> AnalyseRecalculateResponseDto:
        """
        Operation id: recalculate
        Recalculate analysis
        
        :param analyse_recalculate_request_dto: AnalyseRecalculateRequestDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AnalyseRecalculateResponseDto
        """
        endpoint = f"/api2/v1/analyses/recalculate"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = analyse_recalculate_request_dto

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

        
        return AnalyseRecalculateResponseDto(**r.json())
        



if __name__ == '__main__':
    print("This module is not intended to be run directly.")