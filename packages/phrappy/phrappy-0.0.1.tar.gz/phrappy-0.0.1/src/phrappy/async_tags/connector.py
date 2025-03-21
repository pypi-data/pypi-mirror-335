from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union, Any

if TYPE_CHECKING:
    from ..client import SyncPhraseTMSClient

from ..models import (
    UploadResultDto,
    FileListDto,
    ConnectorDto,
    ConnectorAsyncTaskStatesDto,
    ConnectorListDto,
    InputStreamLength,
    GetFileRequestParamsDto,
    UploadFileV2Meta,
    AsyncFileOpResponseDto
    
)


class ConnectorOperations:
    def __init__(self, client: SyncPhraseTMSClient):
        self.client = client


    async def get_connector(
        self,
        connector_id: str,
        phrase_token: Optional[str] = None,
) -> ConnectorDto:
        """
        Operation id: getConnector
        Get a connector
        
        :param connector_id: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ConnectorDto
        """
        endpoint = f"/api2/v1/connectors/{connector_id}"
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

        
        return ConnectorDto(**r.json())
        


    async def get_connector_async_task_states(
        self,
        project_uid: str,
        date_created_from: Optional[str] = None,
        date_created_to: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 100,
        task_processing_type: Optional[List[str]] = None,
        task_type: Optional[List[str]] = None,
        phrase_token: Optional[str] = None,
) -> ConnectorAsyncTaskStatesDto:
        """
        Operation id: getConnectorAsyncTaskStates
        Get Connector async task states.
        
        :param project_uid: str (required), query. Filter by projectUid.
        :param date_created_from: Optional[str] = None (optional), query. Date range from, based on dateCreated.
        :param date_created_to: Optional[str] = None (optional), query. Date range to, based on dateCreated.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 100 (optional), query. Page size, accepts values between 1 and 1000, default 50.
        :param task_processing_type: Optional[List[str]] = None (optional), query. 
        :param task_type: Optional[List[str]] = None (optional), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ConnectorAsyncTaskStatesDto
        """
        endpoint = f"/api2/v1/connectorAsyncTasks"
        params = {
            "projectUid": project_uid,
            "taskType": task_type,
            "taskProcessingType": task_processing_type,
            "dateCreatedFrom": date_created_from,
            "dateCreatedTo": date_created_to,
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

        
        return ConnectorAsyncTaskStatesDto(**r.json())
        


    async def get_connector_list(
        self,
        type: Optional[str] = None,
        phrase_token: Optional[str] = None,
) -> ConnectorListDto:
        """
        Operation id: getConnectorList
        List connectors
        
        :param type: Optional[str] = None (optional), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ConnectorListDto
        """
        endpoint = f"/api2/v1/connectors"
        params = {
            "type": type
            
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

        
        return ConnectorListDto(**r.json())
        


    async def get_file_for_connector(
        self,
        connector_id: str,
        file: str,
        folder: str,
        phrase_token: Optional[str] = None,
) -> InputStreamLength:
        """
        Operation id: getFileForConnector
        Download file
        Download a file from a subfolder of the selected connector
        :param connector_id: str (required), path. 
        :param file: str (required), path. 
        :param folder: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: InputStreamLength
        """
        endpoint = f"/api2/v1/connectors/{connector_id}/folders/{folder}/files/{file}"
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

        
        return InputStreamLength(**r.json())
        


    async def get_file_for_connector_v2(
        self,
        get_file_request_params_dto: GetFileRequestParamsDto,
        connector_id: str,
        file: str,
        folder: str,
        phrase_token: Optional[str] = None,
) -> AsyncFileOpResponseDto:
        """
        Operation id: getFileForConnectorV2
        Download file (async)
        
Create an asynchronous request to download a file from a (sub)folder of the selected connector. 
After a callback with successful response is received, prepared file can be downloaded by [Download prepared file](#operation/getPreparedFile) 
or [Create job from connector asynchronous download task](#operation/createJobFromAsyncDownloadTask).

        :param get_file_request_params_dto: GetFileRequestParamsDto (required), body. 
        :param connector_id: str (required), path. 
        :param file: str (required), path. 
        :param folder: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AsyncFileOpResponseDto
        """
        endpoint = f"/api2/v2/connectors/{connector_id}/folders/{folder}/files/{file}"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = get_file_request_params_dto

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

        
        return AsyncFileOpResponseDto(**r.json())
        


    async def get_folder(
        self,
        connector_id: str,
        folder: str,
        direction: Optional[str] = "ASCENDING",
        file_type: Optional[str] = "ALL",
        project_uid: Optional[str] = None,
        sort: Optional[str] = "NAME",
        source_locale: Optional[str] = None,
        phrase_token: Optional[str] = None,
) -> FileListDto:
        """
        Operation id: getFolder
        List files in a subfolder
        List files in a subfolder of the selected connector
        :param connector_id: str (required), path. 
        :param folder: str (required), path. 
        :param direction: Optional[str] = "ASCENDING" (optional), query. 
        :param file_type: Optional[str] = "ALL" (optional), query. 
        :param project_uid: Optional[str] = None (optional), query. 
        :param sort: Optional[str] = "NAME" (optional), query. 
        :param source_locale: Optional[str] = None (optional), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: FileListDto
        """
        endpoint = f"/api2/v1/connectors/{connector_id}/folders/{folder}"
        params = {
            "projectUid": project_uid,
            "sourceLocale": source_locale,
            "fileType": file_type,
            "sort": sort,
            "direction": direction
            
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

        
        return FileListDto(**r.json())
        


    async def get_prepared_file(
        self,
        connector_id: str,
        file: str,
        folder: str,
        task_id: str,
        phrase_token: Optional[str] = None,
) -> InputStreamLength:
        """
        Operation id: getPreparedFile
        Download prepared file
        Download the file by referencing successfully finished async download request [Connector - Download file (async)](#operation/getFile_1).
        :param connector_id: str (required), path. 
        :param file: str (required), path. 
        :param folder: str (required), path. 
        :param task_id: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: InputStreamLength
        """
        endpoint = f"/api2/v2/connectors/{connector_id}/folders/{folder}/files/{file}/tasks/{task_id}"
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

        
        return InputStreamLength(**r.json())
        


    async def get_root_folder(
        self,
        connector_id: str,
        direction: Optional[str] = "ASCENDING",
        file_type: Optional[str] = "ALL",
        project_uid: Optional[str] = None,
        sort: Optional[str] = "NAME",
        source_locale: Optional[str] = None,
        phrase_token: Optional[str] = None,
) -> FileListDto:
        """
        Operation id: getRootFolder
        List files in root
        List files in a root folder of the selected connector
        :param connector_id: str (required), path. 
        :param direction: Optional[str] = "ASCENDING" (optional), query. 
        :param file_type: Optional[str] = "ALL" (optional), query. 
        :param project_uid: Optional[str] = None (optional), query. 
        :param sort: Optional[str] = "NAME" (optional), query. 
        :param source_locale: Optional[str] = None (optional), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: FileListDto
        """
        endpoint = f"/api2/v1/connectors/{connector_id}/folders"
        params = {
            "projectUid": project_uid,
            "sourceLocale": source_locale,
            "fileType": file_type,
            "sort": sort,
            "direction": direction
            
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

        
        return FileListDto(**r.json())
        


    async def upload_file(
        self,
        connector_id: str,
        file: bytes,
        folder: str,
        content_type: str = "multipart/form-data",
        commit_message: Optional[str] = None,
        mime_type: Optional[str] = None,
        source_file_name: Optional[str] = None,
        subfolder_name: Optional[str] = None,
        phrase_token: Optional[str] = None,
) -> UploadResultDto:
        """
        Operation id: uploadFile
        Upload a file to a subfolder of the selected connector
        Upload a file to a subfolder of the selected connector
        :param connector_id: str (required), path. 
        :param file: bytes (required), formData. Translated file to upload.
        :param folder: str (required), path. 
        :param content_type: str = "multipart/form-data" (required), header. 
        :param commit_message: Optional[str] = None (optional), formData. Commit message for upload to Git, etc..
        :param mime_type: Optional[str] = None (optional), formData. Mime type of the file to upload.
        :param source_file_name: Optional[str] = None (optional), formData. Name or ID of the original file.
        :param subfolder_name: Optional[str] = None (optional), formData. Optional subfolder to upload the file to.
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: UploadResultDto
        """
        endpoint = f"/api2/v1/connectors/{connector_id}/folders/{folder}"
        params = {
            
        }
        headers = {
            "Content-Type": content_type
            
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

        
        return UploadResultDto(**r.json())
        


    async def upload_file_v2(
        self,
        memsource: UploadFileV2Meta,
        connector_id: str,
        file: bytes,
        file_name: str,
        folder: str,
        content_type: str = "multipart/form-data",
        mime_type: Optional[str] = None,
        phrase_token: Optional[str] = None,
) -> AsyncFileOpResponseDto:
        """
        Operation id: uploadFileV2
        Upload file (async)
        Upload a file to a subfolder of the selected connector
        :param memsource: UploadFileV2Meta (required), header. 
        :param connector_id: str (required), path. 
        :param file: bytes (required), formData. Translated file to upload.
        :param file_name: str (required), path. 
        :param folder: str (required), path. 
        :param content_type: str = "multipart/form-data" (required), header. 
        :param mime_type: Optional[str] = None (optional), query. Mime type of the file to upload.
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AsyncFileOpResponseDto
        """
        endpoint = f"/api2/v2/connectors/{connector_id}/folders/{folder}/files/{file_name}/upload"
        params = {
            "mimeType": mime_type
            
        }
        headers = {
            "Memsource": memsource.model_dump_json(),
            "Content-Type": content_type
            
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

        
        return AsyncFileOpResponseDto(**r.json())
        



if __name__ == '__main__':
    print("This module is not intended to be run directly.")