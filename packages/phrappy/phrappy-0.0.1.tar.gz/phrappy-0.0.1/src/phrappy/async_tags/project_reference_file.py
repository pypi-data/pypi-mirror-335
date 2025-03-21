from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union, Any

if TYPE_CHECKING:
    from ..client import SyncPhraseTMSClient

from ..models import (
    CreateReferenceFilesRequest,
    ProjectReferenceFilesRequestDto,
    ReferenceFilesDto,
    UserReferencesDto,
    ReferenceFilePageDto
    
)


class ProjectReferenceFileOperations:
    def __init__(self, client: SyncPhraseTMSClient):
        self.client = client


    async def batch_delete_reference_files(
        self,
        project_reference_files_request_dto: ProjectReferenceFilesRequestDto,
        project_uid: str,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: batchDeleteReferenceFiles
        Delete project reference files (batch)
        
        :param project_reference_files_request_dto: ProjectReferenceFilesRequestDto (required), body. 
        :param project_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/projects/{project_uid}/references"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = project_reference_files_request_dto

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
        


    async def batch_download_reference_files(
        self,
        project_reference_files_request_dto: ProjectReferenceFilesRequestDto,
        project_uid: str,
        phrase_token: Optional[str] = None,
) -> bytes:
        """
        Operation id: batchDownloadReferenceFiles
        Download project reference files (batch)
        
        :param project_reference_files_request_dto: ProjectReferenceFilesRequestDto (required), body. 
        :param project_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """
        endpoint = f"/api2/v1/projects/{project_uid}/references/download"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = project_reference_files_request_dto

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

        
        return r.content
        


    async def create_reference_files(
        self,
        multipart: CreateReferenceFilesRequest,
        project_uid: str,
        phrase_token: Optional[str] = None,
) -> ReferenceFilesDto:
        """
        Operation id: createReferenceFiles
        Create project reference files
        
The `json` request part allows sending additional data as JSON,
such as a text note that will be used for all the given reference files.
In case no `file` parts are sent, only 1 reference is created with the given note.
Either at least one file must be sent or the note must be specified.
Example:

```
{
    "note": "Sample text"
}
```

        :param multipart: CreateReferenceFilesRequest (required), body. Multipart request with files and JSON.
        :param project_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ReferenceFilesDto
        """
        endpoint = f"/api2/v2/projects/{project_uid}/references"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = multipart

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

        
        return ReferenceFilesDto(**r.json())
        


    async def download_reference(
        self,
        project_uid: str,
        reference_file_id: str,
        phrase_token: Optional[str] = None,
) -> bytes:
        """
        Operation id: downloadReference
        Download project reference file
        
        :param project_uid: str (required), path. 
        :param reference_file_id: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """
        endpoint = f"/api2/v1/projects/{project_uid}/references/{reference_file_id}"
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
        


    async def list_reference_file_creators(
        self,
        project_uid: str,
        user_name: Optional[str] = None,
        phrase_token: Optional[str] = None,
) -> UserReferencesDto:
        """
        Operation id: listReferenceFileCreators
        List project reference file creators
        The result is not paged and returns up to 50 users.
                If the requested user is not included, the search can be narrowed down with the `userName` parameter.
            
        :param project_uid: str (required), path. 
        :param user_name: Optional[str] = None (optional), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: UserReferencesDto
        """
        endpoint = f"/api2/v1/projects/{project_uid}/references/creators"
        params = {
            "userName": user_name
            
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

        
        return UserReferencesDto(**r.json())
        


    async def list_reference_files(
        self,
        project_uid: str,
        created_by: Optional[str] = None,
        date_created_since: Optional[str] = None,
        filename: Optional[str] = None,
        order: Optional[str] = "DESC",
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        sort: Optional[str] = "DATE_CREATED",
        phrase_token: Optional[str] = None,
) -> ReferenceFilePageDto:
        """
        Operation id: listReferenceFiles
        List project reference files
        
        :param project_uid: str (required), path. 
        :param created_by: Optional[str] = None (optional), query. UID of user.
        :param date_created_since: Optional[str] = None (optional), query. date time in ISO 8601 UTC format.
        :param filename: Optional[str] = None (optional), query. 
        :param order: Optional[str] = "DESC" (optional), query. 
        :param page_number: Optional[int] = 0 (optional), query. 
        :param page_size: Optional[int] = 50 (optional), query. 
        :param sort: Optional[str] = "DATE_CREATED" (optional), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ReferenceFilePageDto
        """
        endpoint = f"/api2/v1/projects/{project_uid}/references"
        params = {
            "filename": filename,
            "dateCreatedSince": date_created_since,
            "createdBy": created_by,
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

        
        return ReferenceFilePageDto(**r.json())
        



if __name__ == '__main__':
    print("This module is not intended to be run directly.")