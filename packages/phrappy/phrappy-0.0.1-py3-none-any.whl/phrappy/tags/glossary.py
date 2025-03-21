from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union, Any

if TYPE_CHECKING:
    from ..client import SyncPhraseTMSClient

from ..models import (
    GlossaryEditDto,
    GlossaryDto,
    PageDtoGlossaryDto,
    GlossaryActivationDto
    
)


class GlossaryOperations:
    def __init__(self, client: SyncPhraseTMSClient):
        self.client = client


    def activate_glossary(
        self,
        glossary_activation_dto: GlossaryActivationDto,
        glossary_uid: str,
        phrase_token: Optional[str] = None,
) -> GlossaryDto:
        """
        Operation id: activateGlossary
        Activate/Deactivate glossary
        
        :param glossary_activation_dto: GlossaryActivationDto (required), body. 
        :param glossary_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: GlossaryDto
        """
        endpoint = f"/api2/v1/glossaries/{glossary_uid}/activate"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = glossary_activation_dto

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

        
        return GlossaryDto(**r.json())
        


    def create_glossary(
        self,
        glossary_edit_dto: GlossaryEditDto,
        phrase_token: Optional[str] = None,
) -> GlossaryDto:
        """
        Operation id: createGlossary
        Create glossary
        
        :param glossary_edit_dto: GlossaryEditDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: GlossaryDto
        """
        endpoint = f"/api2/v1/glossaries"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = glossary_edit_dto

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

        
        return GlossaryDto(**r.json())
        


    def delete_glossary(
        self,
        glossary_uid: str,
        purge: Optional[bool] = False,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: deleteGlossary
        Delete glossary
        
        :param glossary_uid: str (required), path. 
        :param purge: Optional[bool] = False (optional), query. purge=false - the Glossary can later be restored,
                    'purge=true - the Glossary is completely deleted and cannot be restored.
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/glossaries/{glossary_uid}"
        params = {
            "purge": purge
            
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
        


    def get_glossary(
        self,
        glossary_uid: str,
        phrase_token: Optional[str] = None,
) -> GlossaryDto:
        """
        Operation id: getGlossary
        Get glossary
        
        :param glossary_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: GlossaryDto
        """
        endpoint = f"/api2/v1/glossaries/{glossary_uid}"
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

        
        return GlossaryDto(**r.json())
        


    def list_glossaries(
        self,
        lang: Optional[List[str]] = None,
        name: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        phrase_token: Optional[str] = None,
) -> PageDtoGlossaryDto:
        """
        Operation id: listGlossaries
        List glossaries
        
        :param lang: Optional[List[str]] = None (optional), query. Language of the glossary.
        :param name: Optional[str] = None (optional), query. 
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoGlossaryDto
        """
        endpoint = f"/api2/v1/glossaries"
        params = {
            "name": name,
            "lang": lang,
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

        
        return PageDtoGlossaryDto(**r.json())
        


    def update_glossary(
        self,
        glossary_edit_dto: GlossaryEditDto,
        glossary_uid: str,
        phrase_token: Optional[str] = None,
) -> GlossaryDto:
        """
        Operation id: updateGlossary
        Edit glossary
        Languages can only be added, their removal is not supported
        :param glossary_edit_dto: GlossaryEditDto (required), body. 
        :param glossary_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: GlossaryDto
        """
        endpoint = f"/api2/v1/glossaries/{glossary_uid}"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = glossary_edit_dto

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

        
        return GlossaryDto(**r.json())
        



if __name__ == '__main__':
    print("This module is not intended to be run directly.")