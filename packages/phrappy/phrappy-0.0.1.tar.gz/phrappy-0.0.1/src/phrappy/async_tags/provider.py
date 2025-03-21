from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union, Any

if TYPE_CHECKING:
    from ..client import SyncPhraseTMSClient

from ..models import (
    ProviderListDtoV2,
    PageDtoProviderReference
    
)


class ProviderOperations:
    def __init__(self, client: SyncPhraseTMSClient):
        self.client = client


    async def get_project_assignments(
        self,
        project_uid: str,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        provider_name: Optional[str] = None,
        phrase_token: Optional[str] = None,
) -> PageDtoProviderReference:
        """
        Operation id: getProjectAssignments
        List project providers
        
        :param project_uid: str (required), path. 
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param provider_name: Optional[str] = None (optional), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoProviderReference
        """
        endpoint = f"/api2/v1/projects/{project_uid}/providers"
        params = {
            "providerName": provider_name,
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

        
        return PageDtoProviderReference(**r.json())
        


    async def list_providers_3(
        self,
        project_uid: str,
        phrase_token: Optional[str] = None,
) -> ProviderListDtoV2:
        """
        Operation id: listProviders_3
        Get suggested providers
        
        :param project_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProviderListDtoV2
        """
        endpoint = f"/api2/v2/projects/{project_uid}/providers/suggest"
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

        
        return ProviderListDtoV2(**r.json())
        


    async def list_providers_4(
        self,
        job_uid: str,
        project_uid: str,
        phrase_token: Optional[str] = None,
) -> ProviderListDtoV2:
        """
        Operation id: listProviders_4
        Get suggested providers
        
        :param job_uid: str (required), path. 
        :param project_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProviderListDtoV2
        """
        endpoint = f"/api2/v2/projects/{project_uid}/jobs/{job_uid}/providers/suggest"
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

        
        return ProviderListDtoV2(**r.json())
        



if __name__ == '__main__':
    print("This module is not intended to be run directly.")