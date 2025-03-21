from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union, Any

if TYPE_CHECKING:
    from ..client import SyncPhraseTMSClient

from ..models import (
    QuoteCreateV2Dto,
    EmailQuotesRequestDto,
    EmailQuotesResponseDto,
    QuoteDto,
    QuoteV2Dto
    
)


class QuoteOperations:
    def __init__(self, client: SyncPhraseTMSClient):
        self.client = client


    async def create_quote_v2(
        self,
        quote_create_v2_dto: QuoteCreateV2Dto,
        phrase_token: Optional[str] = None,
) -> QuoteV2Dto:
        """
        Operation id: createQuoteV2
        Create quote
        Either WorkflowSettings or Units must be sent for billingUnit "Hour".
        :param quote_create_v2_dto: QuoteCreateV2Dto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: QuoteV2Dto
        """
        endpoint = f"/api2/v2/quotes"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = quote_create_v2_dto

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

        
        return QuoteV2Dto(**r.json())
        


    async def delete_quote(
        self,
        quote_uid: str,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: deleteQuote
        Delete quote
        
        :param quote_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/quotes/{quote_uid}"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = None

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
        


    async def email_quotes(
        self,
        email_quotes_request_dto: EmailQuotesRequestDto,
        phrase_token: Optional[str] = None,
) -> EmailQuotesResponseDto:
        """
        Operation id: emailQuotes
        Email quotes
        
        :param email_quotes_request_dto: EmailQuotesRequestDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: EmailQuotesResponseDto
        """
        endpoint = f"/api2/v1/quotes/email"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = email_quotes_request_dto

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

        
        return EmailQuotesResponseDto(**r.json())
        


    async def get_2(
        self,
        quote_uid: str,
        phrase_token: Optional[str] = None,
) -> QuoteDto:
        """
        Operation id: get_2
        Get quote
        
        :param quote_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: QuoteDto
        """
        endpoint = f"/api2/v1/quotes/{quote_uid}"
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

        
        return QuoteDto(**r.json())
        



if __name__ == '__main__':
    print("This module is not intended to be run directly.")