from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union, Any

if TYPE_CHECKING:
    from ..client import SyncPhraseTMSClient

from ..models import (
    LanguageListDto
    
)


class SupportedLanguagesOperations:
    def __init__(self, client: SyncPhraseTMSClient):
        self.client = client


    def list_of_languages(
        self,
        active: Optional[bool] = None,
        phrase_token: Optional[str] = None,
) -> LanguageListDto:
        """
        Operation id: listOfLanguages
        List supported languages
        
        :param active: Optional[bool] = None (optional), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LanguageListDto
        """
        endpoint = f"/api2/v1/languages"
        params = {
            "active": active
            
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

        
        return LanguageListDto(**r.json())
        



if __name__ == '__main__':
    print("This module is not intended to be run directly.")