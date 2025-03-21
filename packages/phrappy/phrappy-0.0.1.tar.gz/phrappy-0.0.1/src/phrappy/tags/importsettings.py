from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union, Any

if TYPE_CHECKING:
    from ..client import SyncPhraseTMSClient

from ..models import (
    ImportSettingsDto,
    PageDtoImportSettingsReference,
    ImportSettingsEditDto,
    ImportSettingsCreateDto
    
)


class ImportsettingsOperations:
    def __init__(self, client: SyncPhraseTMSClient):
        self.client = client


    def create_import_settings(
        self,
        import_settings_create_dto: ImportSettingsCreateDto,
        phrase_token: Optional[str] = None,
) -> ImportSettingsDto:
        """
        Operation id: createImportSettings
        Create import settings
        Pre-defined import settings is handy for [Create Job](#operation/createJob).
                  See [supported file types](https://wiki.memsource.com/wiki/API_File_Type_List)
        :param import_settings_create_dto: ImportSettingsCreateDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ImportSettingsDto
        """
        endpoint = f"/api2/v1/importSettings"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = import_settings_create_dto

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

        
        return ImportSettingsDto(**r.json())
        


    def delete_import_settings(
        self,
        uid: str,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: deleteImportSettings
        Delete import settings
        
        :param uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/importSettings/{uid}"
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
        


    def edit_default_import_settings(
        self,
        import_settings_edit_dto: ImportSettingsEditDto,
        phrase_token: Optional[str] = None,
) -> ImportSettingsDto:
        """
        Operation id: editDefaultImportSettings
        Edit organization's default import settings
        
        :param import_settings_edit_dto: ImportSettingsEditDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ImportSettingsDto
        """
        endpoint = f"/api2/v1/importSettings/default"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = import_settings_edit_dto

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

        
        return ImportSettingsDto(**r.json())
        


    def edit_import_settings(
        self,
        import_settings_edit_dto: ImportSettingsEditDto,
        phrase_token: Optional[str] = None,
) -> ImportSettingsDto:
        """
        Operation id: editImportSettings
        Edit import settings
        
        :param import_settings_edit_dto: ImportSettingsEditDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ImportSettingsDto
        """
        endpoint = f"/api2/v1/importSettings"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = import_settings_edit_dto

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

        
        return ImportSettingsDto(**r.json())
        


    def get_import_settings_by_uid(
        self,
        uid: str,
        phrase_token: Optional[str] = None,
) -> ImportSettingsDto:
        """
        Operation id: getImportSettingsByUid
        Get import settings
        
        :param uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ImportSettingsDto
        """
        endpoint = f"/api2/v1/importSettings/{uid}"
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

        
        return ImportSettingsDto(**r.json())
        


    def get_import_settings_default(
        self,
        phrase_token: Optional[str] = None,
) -> ImportSettingsDto:
        """
        Operation id: getImportSettingsDefault
        Get organization's default import settings
        
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ImportSettingsDto
        """
        endpoint = f"/api2/v1/importSettings/default"
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

        
        return ImportSettingsDto(**r.json())
        


    def list_import_settings(
        self,
        name: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        phrase_token: Optional[str] = None,
) -> PageDtoImportSettingsReference:
        """
        Operation id: listImportSettings
        List import settings
        
        :param name: Optional[str] = None (optional), query. 
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoImportSettingsReference
        """
        endpoint = f"/api2/v1/importSettings"
        params = {
            "name": name,
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

        
        return PageDtoImportSettingsReference(**r.json())
        



if __name__ == '__main__':
    print("This module is not intended to be run directly.")