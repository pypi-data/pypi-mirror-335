from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union, Any

if TYPE_CHECKING:
    from ..client import SyncPhraseTMSClient

from ..models import (
    SpellCheckResponseDto,
    DictionaryItemDto,
    SuggestResponseDto,
    SuggestRequestDto,
    SpellCheckRequestDto
    
)


class SpellCheckOperations:
    def __init__(self, client: SyncPhraseTMSClient):
        self.client = client


    def add_word(
        self,
        dictionary_item_dto: DictionaryItemDto,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: addWord
        Add word to dictionary
        
        :param dictionary_item_dto: DictionaryItemDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/spellCheck/words"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = dictionary_item_dto

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

        
        return
        


    def check(
        self,
        spell_check_request_dto: SpellCheckRequestDto,
        phrase_token: Optional[str] = None,
) -> SpellCheckResponseDto:
        """
        Operation id: check
        Spell check
        Spell check using the settings of the user's organization
        :param spell_check_request_dto: SpellCheckRequestDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SpellCheckResponseDto
        """
        endpoint = f"/api2/v1/spellCheck/check"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = spell_check_request_dto

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

        
        return SpellCheckResponseDto(**r.json())
        


    def check_by_job(
        self,
        spell_check_request_dto: SpellCheckRequestDto,
        job_uid: str,
        phrase_token: Optional[str] = None,
) -> SpellCheckResponseDto:
        """
        Operation id: checkByJob
        Spell check for job
        Spell check using the settings from the project of the job
        :param spell_check_request_dto: SpellCheckRequestDto (required), body. 
        :param job_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SpellCheckResponseDto
        """
        endpoint = f"/api2/v1/spellCheck/check/{job_uid}"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = spell_check_request_dto

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

        
        return SpellCheckResponseDto(**r.json())
        


    def suggest(
        self,
        suggest_request_dto: SuggestRequestDto,
        phrase_token: Optional[str] = None,
) -> SuggestResponseDto:
        """
        Operation id: suggest
        Suggest a word
        Spell check suggest using the users's spell check dictionary
        :param suggest_request_dto: SuggestRequestDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: SuggestResponseDto
        """
        endpoint = f"/api2/v1/spellCheck/suggest"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = suggest_request_dto

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

        
        return SuggestResponseDto(**r.json())
        



if __name__ == '__main__':
    print("This module is not intended to be run directly.")