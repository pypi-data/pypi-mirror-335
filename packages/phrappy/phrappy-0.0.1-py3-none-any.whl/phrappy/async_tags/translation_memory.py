from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union, Any

if TYPE_CHECKING:
    from ..client import SyncPhraseTMSClient

from ..models import (
    SegmentDto,
    TranslationDto,
    AsyncRequestWrapperV2Dto,
    AsyncRequestWrapperDto,
    AsyncExportTMResponseDto,
    TransMemoryCreateDto,
    BackgroundTasksTmDto,
    TranslationResourcesDto,
    ExportByQueryDto,
    SearchTMByJobRequestDto,
    WildCardSearchRequestDto,
    TransMemoryDto,
    MetadataResponse_2,
    TargetLanguageDto,
    SearchResponseListTmDto,
    ProjectTemplateTransMemoryListDtoV3,
    SearchResponseListTmDtoV3,
    SearchTMRequestDto,
    SearchTMByJobRequestDtoV3,
    WildCardSearchByJobRequestDtoV3,
    PageDtoTransMemoryDto,
    BulkDeleteTmDto,
    ExportTMDto,
    SearchRequestDto,
    InputStream,
    PageDtoAbstractProjectDto,
    CleanedTransMemoriesDto,
    TransMemoryEditDto,
    AsyncExportTMByQueryResponseDto
    
)


class TranslationMemoryOperations:
    def __init__(self, client: SyncPhraseTMSClient):
        self.client = client


    async def add_target_lang_to_trans_memory(
        self,
        target_language_dto: TargetLanguageDto,
        trans_memory_uid: str,
        phrase_token: Optional[str] = None,
) -> TransMemoryDto:
        """
        Operation id: addTargetLangToTransMemory
        Add target language to translation memory
        
        :param target_language_dto: TargetLanguageDto (required), body. 
        :param trans_memory_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TransMemoryDto
        """
        endpoint = f"/api2/v1/transMemories/{trans_memory_uid}/targetLanguages"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = target_language_dto

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

        
        return TransMemoryDto(**r.json())
        


    async def bulk_delete_trans_memories(
        self,
        bulk_delete_tm_dto: BulkDeleteTmDto,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: bulkDeleteTransMemories
        Delete translation memories (batch)
        
        :param bulk_delete_tm_dto: BulkDeleteTmDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/transMemories/bulk"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = bulk_delete_tm_dto

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
        


    async def clear_trans_memory(
        self,
        trans_memory_uid: str,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: clearTransMemory
        Delete all segments
        
        :param trans_memory_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/transMemories/{trans_memory_uid}/segments"
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
        


    async def clear_trans_memory_v2(
        self,
        trans_memory_uid: str,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: clearTransMemoryV2
        Delete all segments.
        This call is **asynchronous**, use [this API](#operation/getAsyncRequest) to check the result
        :param trans_memory_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v2/transMemories/{trans_memory_uid}/segments"
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
        


    async def create_trans_memory(
        self,
        trans_memory_create_dto: TransMemoryCreateDto,
        phrase_token: Optional[str] = None,
) -> TransMemoryDto:
        """
        Operation id: createTransMemory
        Create translation memory
        
        :param trans_memory_create_dto: TransMemoryCreateDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TransMemoryDto
        """
        endpoint = f"/api2/v1/transMemories"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = trans_memory_create_dto

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

        
        return TransMemoryDto(**r.json())
        


    async def delete_source_and_translations(
        self,
        segment_id: str,
        trans_memory_uid: str,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: deleteSourceAndTranslations
        Delete both source and translation
        Not recommended for bulk removal of segments
        :param segment_id: str (required), path. 
        :param trans_memory_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/transMemories/{trans_memory_uid}/segments/{segment_id}"
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
        


    async def delete_trans_memory(
        self,
        trans_memory_uid: str,
        purge: Optional[bool] = False,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: deleteTransMemory
        Delete translation memory
        
        :param trans_memory_uid: str (required), path. 
        :param purge: Optional[bool] = False (optional), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/transMemories/{trans_memory_uid}"
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
        


    async def delete_translation(
        self,
        lang: str,
        segment_id: str,
        trans_memory_uid: str,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: deleteTranslation
        Delete segment of given language
        Not recommended for bulk removal of segments
        :param lang: str (required), path. 
        :param segment_id: str (required), path. 
        :param trans_memory_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/transMemories/{trans_memory_uid}/segments/{segment_id}/lang/{lang}"
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
        


    async def download_cleaned_tm(
        self,
        async_request_id: str,
        phrase_token: Optional[str] = None,
) -> bytes:
        """
        Operation id: downloadCleanedTM
        Download cleaned TM
        
        :param async_request_id: str (required), path. Request ID.
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """
        endpoint = f"/api2/v1/transMemories/downloadCleaned/{async_request_id}"
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

        
        return r.content
        


    async def download_search_result(
        self,
        async_request_id: str,
        fields: Optional[List[str]] = None,
        format: Optional[str] = "TMX",
        phrase_token: Optional[str] = None,
) -> bytes:
        """
        Operation id: downloadSearchResult
        Download export
        
        :param async_request_id: str (required), path. Request ID.
        :param fields: Optional[List[str]] = None (optional), query. Fields to include in exported XLSX.
        :param format: Optional[str] = "TMX" (optional), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """
        endpoint = f"/api2/v1/transMemories/downloadExport/{async_request_id}"
        params = {
            "format": format,
            "fields": fields
            
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
        


    async def edit_trans_memory(
        self,
        trans_memory_edit_dto: TransMemoryEditDto,
        trans_memory_uid: str,
        phrase_token: Optional[str] = None,
) -> TransMemoryDto:
        """
        Operation id: editTransMemory
        Edit translation memory
        
        :param trans_memory_edit_dto: TransMemoryEditDto (required), body. 
        :param trans_memory_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TransMemoryDto
        """
        endpoint = f"/api2/v1/transMemories/{trans_memory_uid}"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = trans_memory_edit_dto

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

        
        return TransMemoryDto(**r.json())
        


    async def export_by_query_async(
        self,
        export_by_query_dto: ExportByQueryDto,
        trans_memory_uid: str,
        phrase_token: Optional[str] = None,
) -> AsyncExportTMByQueryResponseDto:
        """
        Operation id: exportByQueryAsync
        Search translation memory
        Use [this API](#operation/downloadSearchResult) to download result
        :param export_by_query_dto: ExportByQueryDto (required), body. 
        :param trans_memory_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AsyncExportTMByQueryResponseDto
        """
        endpoint = f"/api2/v1/transMemories/{trans_memory_uid}/exportByQueryAsync"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = export_by_query_dto

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

        
        return AsyncExportTMByQueryResponseDto(**r.json())
        


    async def export_cleaned_t_ms(
        self,
        cleaned_trans_memories_dto: CleanedTransMemoriesDto,
        phrase_token: Optional[str] = None,
) -> AsyncRequestWrapperDto:
        """
        Operation id: exportCleanedTMs
        Extract cleaned translation memory
        Returns a ZIP file containing the cleaned translation memories in the specified outputFormat.
        :param cleaned_trans_memories_dto: CleanedTransMemoriesDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AsyncRequestWrapperDto
        """
        endpoint = f"/api2/v1/transMemories/extractCleaned"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = cleaned_trans_memories_dto

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

        
        return AsyncRequestWrapperDto(**r.json())
        


    async def export_v2(
        self,
        export_tm_dto: ExportTMDto,
        trans_memory_uid: str,
        phrase_token: Optional[str] = None,
) -> AsyncExportTMResponseDto:
        """
        Operation id: exportV2
        Export translation memory
        Use [this API](#operation/downloadSearchResult) to download result
        :param export_tm_dto: ExportTMDto (required), body. 
        :param trans_memory_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AsyncExportTMResponseDto
        """
        endpoint = f"/api2/v2/transMemories/{trans_memory_uid}/export"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = export_tm_dto

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

        
        return AsyncExportTMResponseDto(**r.json())
        


    async def get_background_tasks_for_trans_mems(
        self,
        trans_memory_uid: str,
        phrase_token: Optional[str] = None,
) -> BackgroundTasksTmDto:
        """
        Operation id: getBackgroundTasksForTransMems
        Get last task information
        
        :param trans_memory_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: BackgroundTasksTmDto
        """
        endpoint = f"/api2/v1/transMemories/{trans_memory_uid}/lastBackgroundTask"
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

        
        return BackgroundTasksTmDto(**r.json())
        


    async def get_metadata(
        self,
        trans_memory_uid: str,
        by_language: Optional[bool] = False,
        phrase_token: Optional[str] = None,
) -> MetadataResponse_2:
        """
        Operation id: getMetadata
        Get translation memory metadata
        
        :param trans_memory_uid: str (required), path. 
        :param by_language: Optional[bool] = False (optional), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: MetadataResponse_2
        """
        endpoint = f"/api2/v1/transMemories/{trans_memory_uid}/metadata"
        params = {
            "byLanguage": by_language
            
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

        
        return MetadataResponse_2(**r.json())
        


    async def get_project_template_trans_memories_2(
        self,
        project_template_uid: str,
        target_lang: Optional[str] = None,
        wf_step_uid: Optional[str] = None,
        phrase_token: Optional[str] = None,
) -> ProjectTemplateTransMemoryListDtoV3:
        """
        Operation id: getProjectTemplateTransMemories_2
        Get translation memories
        
        :param project_template_uid: str (required), path. 
        :param target_lang: Optional[str] = None (optional), query. Filter project translation memories by target language.
        :param wf_step_uid: Optional[str] = None (optional), query. Filter project translation memories by workflow step.
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProjectTemplateTransMemoryListDtoV3
        """
        endpoint = f"/api2/v3/projectTemplates/{project_template_uid}/transMemories"
        params = {
            "targetLang": target_lang,
            "wfStepUid": wf_step_uid
            
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

        
        return ProjectTemplateTransMemoryListDtoV3(**r.json())
        


    async def get_related_projects(
        self,
        trans_memory_uid: str,
        name: Optional[str] = None,
        order: Optional[List[str]] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        sort: Optional[List[str]] = None,
        phrase_token: Optional[str] = None,
) -> PageDtoAbstractProjectDto:
        """
        Operation id: getRelatedProjects
        List related projects
        
        :param trans_memory_uid: str (required), path. 
        :param name: Optional[str] = None (optional), query. Project name to filter by.
        :param order: Optional[List[str]] = None (optional), query. 
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param sort: Optional[List[str]] = None (optional), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoAbstractProjectDto
        """
        endpoint = f"/api2/v1/transMemories/{trans_memory_uid}/relatedProjects"
        params = {
            "name": name,
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

        
        return PageDtoAbstractProjectDto(**r.json())
        


    async def get_trans_memory(
        self,
        trans_memory_uid: str,
        phrase_token: Optional[str] = None,
) -> TransMemoryDto:
        """
        Operation id: getTransMemory
        Get translation memory
        
        :param trans_memory_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TransMemoryDto
        """
        endpoint = f"/api2/v1/transMemories/{trans_memory_uid}"
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

        
        return TransMemoryDto(**r.json())
        


    async def get_translation_resources(
        self,
        job_uid: str,
        project_uid: str,
        phrase_token: Optional[str] = None,
) -> TranslationResourcesDto:
        """
        Operation id: getTranslationResources
        Get translation resources
        
        :param job_uid: str (required), path. 
        :param project_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TranslationResourcesDto
        """
        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_uid}/translationResources"
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

        
        return TranslationResourcesDto(**r.json())
        


    async def import_trans_memory_v2(
        self,
        content_disposition: str,
        input_stream: bytes,
        trans_memory_uid: str,
        content_length: Optional[int] = None,
        strict_lang_matching: Optional[bool] = False,
        strip_native_codes: Optional[bool] = True,
        phrase_token: Optional[str] = None,
) -> AsyncRequestWrapperV2Dto:
        """
        Operation id: importTransMemoryV2
        Import TMX
        
        :param content_disposition: str (required), header. must match pattern `((inline|attachment); )?filename\*=UTF-8''(.+)`.
        :param input_stream: bytes (required), body. 
        :param trans_memory_uid: str (required), path. 
        :param content_length: Optional[int] = None (optional), header. 
        :param strict_lang_matching: Optional[bool] = False (optional), query. 
        :param strip_native_codes: Optional[bool] = True (optional), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AsyncRequestWrapperV2Dto
        """
        endpoint = f"/api2/v2/transMemories/{trans_memory_uid}/import"
        params = {
            "strictLangMatching": strict_lang_matching,
            "stripNativeCodes": strip_native_codes
            
        }
        headers = {
            "Content-Length": content_length,
            "Content-Disposition": content_disposition
            
        }

        content = input_stream

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

        
        return AsyncRequestWrapperV2Dto(**r.json())
        


    async def insert_to_trans_memory(
        self,
        segment_dto: SegmentDto,
        trans_memory_uid: str,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: insertToTransMemory
        Insert segment
        
        :param segment_dto: SegmentDto (required), body. 
        :param trans_memory_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/transMemories/{trans_memory_uid}/segments"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = segment_dto

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
        


    async def list_trans_memories(
        self,
        business_unit_id: Optional[str] = None,
        client_id: Optional[str] = None,
        domain_id: Optional[str] = None,
        name: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        source_lang: Optional[str] = None,
        sub_domain_id: Optional[str] = None,
        target_lang: Optional[str] = None,
        phrase_token: Optional[str] = None,
) -> PageDtoTransMemoryDto:
        """
        Operation id: listTransMemories
        List translation memories
        
        :param business_unit_id: Optional[str] = None (optional), query. 
        :param client_id: Optional[str] = None (optional), query. 
        :param domain_id: Optional[str] = None (optional), query. 
        :param name: Optional[str] = None (optional), query. 
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param source_lang: Optional[str] = None (optional), query. 
        :param sub_domain_id: Optional[str] = None (optional), query. 
        :param target_lang: Optional[str] = None (optional), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoTransMemoryDto
        """
        endpoint = f"/api2/v1/transMemories"
        params = {
            "name": name,
            "sourceLang": source_lang,
            "targetLang": target_lang,
            "clientId": client_id,
            "domainId": domain_id,
            "subDomainId": sub_domain_id,
            "businessUnitId": business_unit_id,
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

        
        return PageDtoTransMemoryDto(**r.json())
        


    async def relevant_trans_memories_for_project(
        self,
        project_uid: str,
        client_name: Optional[str] = None,
        domain_name: Optional[str] = None,
        name: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        strict_lang_matching: Optional[bool] = False,
        sub_domain_name: Optional[str] = None,
        target_langs: Optional[List[str]] = None,
        phrase_token: Optional[str] = None,
) -> PageDtoTransMemoryDto:
        """
        Operation id: relevantTransMemoriesForProject
        List project relevant translation memories
        
        :param project_uid: str (required), path. 
        :param client_name: Optional[str] = None (optional), query. 
        :param domain_name: Optional[str] = None (optional), query. 
        :param name: Optional[str] = None (optional), query. 
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param strict_lang_matching: Optional[bool] = False (optional), query. 
        :param sub_domain_name: Optional[str] = None (optional), query. 
        :param target_langs: Optional[List[str]] = None (optional), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoTransMemoryDto
        """
        endpoint = f"/api2/v1/projects/{project_uid}/transMemories/relevant"
        params = {
            "name": name,
            "domainName": domain_name,
            "clientName": client_name,
            "subDomainName": sub_domain_name,
            "targetLangs": target_langs,
            "strictLangMatching": strict_lang_matching,
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

        
        return PageDtoTransMemoryDto(**r.json())
        


    async def relevant_trans_memories_for_project_template(
        self,
        project_template_uid: str,
        client_name: Optional[str] = None,
        domain_name: Optional[str] = None,
        name: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        strict_lang_matching: Optional[bool] = False,
        sub_domain_name: Optional[str] = None,
        target_langs: Optional[List[str]] = None,
        phrase_token: Optional[str] = None,
) -> PageDtoTransMemoryDto:
        """
        Operation id: relevantTransMemoriesForProjectTemplate
        List project template relevant translation memories
        
        :param project_template_uid: str (required), path. 
        :param client_name: Optional[str] = None (optional), query. 
        :param domain_name: Optional[str] = None (optional), query. 
        :param name: Optional[str] = None (optional), query. 
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param strict_lang_matching: Optional[bool] = False (optional), query. 
        :param sub_domain_name: Optional[str] = None (optional), query. 
        :param target_langs: Optional[List[str]] = None (optional), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoTransMemoryDto
        """
        endpoint = f"/api2/v1/projectTemplates/{project_template_uid}/transMemories/relevant"
        params = {
            "name": name,
            "domainName": domain_name,
            "clientName": client_name,
            "subDomainName": sub_domain_name,
            "targetLangs": target_langs,
            "strictLangMatching": strict_lang_matching,
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

        
        return PageDtoTransMemoryDto(**r.json())
        


    async def search(
        self,
        search_request_dto: SearchRequestDto,
        trans_memory_uid: str,
        phrase_token: Optional[str] = None,
) -> SearchResponseListTmDto:
        """
        Operation id: search
        Search translation memory (sync)
        
        :param search_request_dto: SearchRequestDto (required), body. 
        :param trans_memory_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SearchResponseListTmDto
        """
        endpoint = f"/api2/v1/transMemories/{trans_memory_uid}/search"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = search_request_dto

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

        
        return SearchResponseListTmDto(**r.json())
        


    async def search_by_job3(
        self,
        search_tm_by_job_request_dto_v3: SearchTMByJobRequestDtoV3,
        job_uid: str,
        project_uid: str,
        phrase_token: Optional[str] = None,
) -> SearchResponseListTmDtoV3:
        """
        Operation id: searchByJob3
        Search job's translation memories
        
        :param search_tm_by_job_request_dto_v3: SearchTMByJobRequestDtoV3 (required), body. 
        :param job_uid: str (required), path. 
        :param project_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SearchResponseListTmDtoV3
        """
        endpoint = f"/api2/v3/projects/{project_uid}/jobs/{job_uid}/transMemories/search"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = search_tm_by_job_request_dto_v3

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

        
        return SearchResponseListTmDtoV3(**r.json())
        


    async def search_segment_by_job(
        self,
        search_tm_by_job_request_dto: SearchTMByJobRequestDto,
        job_uid: str,
        project_uid: str,
        phrase_token: Optional[str] = None,
) -> SearchResponseListTmDto:
        """
        Operation id: searchSegmentByJob
        Search translation memory for segment by job
        Returns at most <i>maxSegments</i>
            records with <i>score >= scoreThreshold</i> and at most <i>maxSubsegments</i> records which are subsegment,
            i.e. the source text is substring of the query text.
        :param search_tm_by_job_request_dto: SearchTMByJobRequestDto (required), body. 
        :param job_uid: str (required), path. 
        :param project_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SearchResponseListTmDto
        """
        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_uid}/transMemories/searchSegment"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = search_tm_by_job_request_dto

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

        
        return SearchResponseListTmDto(**r.json())
        


    async def search_tm_segment(
        self,
        search_tm_request_dto: SearchTMRequestDto,
        project_uid: str,
        phrase_token: Optional[str] = None,
) -> SearchResponseListTmDto:
        """
        Operation id: searchTmSegment
        Search translation memory for segment in the project
        Returns at most <i>maxSegments</i>
            records with <i>score >= scoreThreshold</i> and at most <i>maxSubsegments</i> records which are subsegment,
            i.e. the source text is substring of the query text.
        :param search_tm_request_dto: SearchTMRequestDto (required), body. 
        :param project_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SearchResponseListTmDto
        """
        endpoint = f"/api2/v1/projects/{project_uid}/transMemories/searchSegmentInProject"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = search_tm_request_dto

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

        
        return SearchResponseListTmDto(**r.json())
        


    async def update_translation(
        self,
        translation_dto: TranslationDto,
        segment_id: str,
        trans_memory_uid: str,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: updateTranslation
        Edit segment
        
        :param translation_dto: TranslationDto (required), body. 
        :param segment_id: str (required), path. 
        :param trans_memory_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/transMemories/{trans_memory_uid}/segments/{segment_id}"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = translation_dto

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

        
        return
        


    async def wild_card_search_by_job3(
        self,
        wild_card_search_by_job_request_dto_v3: WildCardSearchByJobRequestDtoV3,
        job_uid: str,
        project_uid: str,
        phrase_token: Optional[str] = None,
) -> SearchResponseListTmDtoV3:
        """
        Operation id: wildCardSearchByJob3
        Wildcard search job's translation memories
        
        :param wild_card_search_by_job_request_dto_v3: WildCardSearchByJobRequestDtoV3 (required), body. 
        :param job_uid: str (required), path. 
        :param project_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SearchResponseListTmDtoV3
        """
        endpoint = f"/api2/v3/projects/{project_uid}/jobs/{job_uid}/transMemories/wildCardSearch"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = wild_card_search_by_job_request_dto_v3

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

        
        return SearchResponseListTmDtoV3(**r.json())
        


    async def wildcard_search(
        self,
        wild_card_search_request_dto: WildCardSearchRequestDto,
        trans_memory_uid: str,
        phrase_token: Optional[str] = None,
) -> SearchResponseListTmDto:
        """
        Operation id: wildcardSearch
        Wildcard search
        
        :param wild_card_search_request_dto: WildCardSearchRequestDto (required), body. 
        :param trans_memory_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SearchResponseListTmDto
        """
        endpoint = f"/api2/v1/transMemories/{trans_memory_uid}/wildCardSearch"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = wild_card_search_request_dto

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

        
        return SearchResponseListTmDto(**r.json())
        



if __name__ == '__main__':
    print("This module is not intended to be run directly.")