from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union, Any

if TYPE_CHECKING:
    from ..client import SyncPhraseTMSClient

from ..models import (
    PageDtoMemsourceTranslateProfileDto
    
)


class LanguageAIOperations:
    def __init__(self, client: SyncPhraseTMSClient):
        self.client = client


    def list_memsource_translate_profile(
        self,
        include_projects: Optional[bool] = True,
        name: Optional[str] = None,
        order: Optional[str] = "desc",
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 10,
        sort: Optional[str] = "name",
        phrase_token: Optional[str] = None,
) -> PageDtoMemsourceTranslateProfileDto:
        """
        Operation id: listMemsourceTranslateProfile
        List of Language AI profiles
        
        :param include_projects: Optional[bool] = True (optional), query. 
        :param name: Optional[str] = None (optional), query. Filter by name.
        :param order: Optional[str] = "desc" (optional), query. desc.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 10 (optional), query. Page size, accepts values between 1 and 50, default 10.
        :param sort: Optional[str] = "name" (optional), query. Sort by.
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoMemsourceTranslateProfileDto
        """
        endpoint = f"/api2/v1/memsourceTranslateProfiles"
        params = {
            "name": name,
            "sort": sort,
            "order": order,
            "pageNumber": page_number,
            "pageSize": page_size,
            "includeProjects": include_projects
            
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

        
        return PageDtoMemsourceTranslateProfileDto(**r.json())
        



if __name__ == '__main__':
    print("This module is not intended to be run directly.")