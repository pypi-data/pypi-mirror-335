from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union, Any

if TYPE_CHECKING:
    from ..client import SyncPhraseTMSClient

from ..models import (
    MachineTranslateResponse,
    TranslationRequestExtendedDto
    
)


class MachineTranslationOperations:
    def __init__(self, client: SyncPhraseTMSClient):
        self.client = client


    def machine_translation(
        self,
        translation_request_extended_dto: TranslationRequestExtendedDto,
        mt_settings_uid: str,
        phrase_token: Optional[str] = None,
) -> MachineTranslateResponse:
        """
        Operation id: machineTranslation
        Translate with MT
        
        :param translation_request_extended_dto: TranslationRequestExtendedDto (required), body. 
        :param mt_settings_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: MachineTranslateResponse
        """
        endpoint = f"/api2/v1/machineTranslations/{mt_settings_uid}/translate"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = translation_request_extended_dto

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

        
        return MachineTranslateResponse(**r.json())
        



if __name__ == '__main__':
    print("This module is not intended to be run directly.")