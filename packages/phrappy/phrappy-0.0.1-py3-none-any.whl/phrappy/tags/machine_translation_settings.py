from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union, Any

if TYPE_CHECKING:
    from ..client import SyncPhraseTMSClient

from ..models import (
    PageDtoMachineTranslateSettingsPbmDto,
    TypesDto,
    MachineTranslateStatusDto,
    MachineTranslateSettingsPbmDto,
    TranslationResourcesDto
    
)


class MachineTranslationSettingsOperations:
    def __init__(self, client: SyncPhraseTMSClient):
        self.client = client


    def get_list(
        self,
        name: Optional[str] = None,
        order: Optional[str] = "asc",
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        sort: Optional[str] = "NAME",
        phrase_token: Optional[str] = None,
) -> PageDtoMachineTranslateSettingsPbmDto:
        """
        Operation id: getList
        List machine translate settings
        
        :param name: Optional[str] = None (optional), query. 
        :param order: Optional[str] = "asc" (optional), query. 
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param sort: Optional[str] = "NAME" (optional), query. Sorting field.
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoMachineTranslateSettingsPbmDto
        """
        endpoint = f"/api2/v1/machineTranslateSettings"
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

        
        return PageDtoMachineTranslateSettingsPbmDto(**r.json())
        


    def get_mt_settings(
        self,
        mts_uid: str,
        phrase_token: Optional[str] = None,
) -> MachineTranslateSettingsPbmDto:
        """
        Operation id: getMTSettings
        Get machine translate settings
        
        :param mts_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: MachineTranslateSettingsPbmDto
        """
        endpoint = f"/api2/v1/machineTranslateSettings/{mts_uid}"
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

        
        return MachineTranslateSettingsPbmDto(**r.json())
        


    def get_mt_types(
        self,
        phrase_token: Optional[str] = None,
) -> TypesDto:
        """
        Operation id: getMTTypes
        Get machine translate settings types
        
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TypesDto
        """
        endpoint = f"/api2/v1/machineTranslateSettings/types"
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

        
        return TypesDto(**r.json())
        


    def get_status(
        self,
        mts_uid: str,
        phrase_token: Optional[str] = None,
) -> MachineTranslateStatusDto:
        """
        Operation id: getStatus
        Get status of machine translate engine
        
        :param mts_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: MachineTranslateStatusDto
        """
        endpoint = f"/api2/v1/machineTranslateSettings/{mts_uid}/status"
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

        
        return MachineTranslateStatusDto(**r.json())
        


    def get_third_party_engines_list(
        self,
        name: Optional[str] = None,
        order: Optional[str] = "asc",
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        sort: Optional[str] = "NAME",
        phrase_token: Optional[str] = None,
) -> PageDtoMachineTranslateSettingsPbmDto:
        """
        Operation id: getThirdPartyEnginesList
        List third party machine translate settings
        
        :param name: Optional[str] = None (optional), query. 
        :param order: Optional[str] = "asc" (optional), query. 
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 100, default 50.
        :param sort: Optional[str] = "NAME" (optional), query. Sorting field.
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoMachineTranslateSettingsPbmDto
        """
        endpoint = f"/api2/v1/machineTranslateSettings/thirdPartyEngines"
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

        
        return PageDtoMachineTranslateSettingsPbmDto(**r.json())
        


    def get_translation_resources(
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

        
        return TranslationResourcesDto(**r.json())
        



if __name__ == '__main__':
    print("This module is not intended to be run directly.")