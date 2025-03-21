from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union, Any

if TYPE_CHECKING:
    from ..client import SyncPhraseTMSClient

from ..models import (
    BuyerDto,
    BuyerEditDto,
    PageDtoBuyerDto
    
)


class BuyerOperations:
    def __init__(self, client: SyncPhraseTMSClient):
        self.client = client


    def list_buyers(
        self,
        order: Optional[str] = "ASC",
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        sort: Optional[str] = "NAME",
        phrase_token: Optional[str] = None,
) -> PageDtoBuyerDto:
        """
        Operation id: listBuyers
        List buyers
        
        :param order: Optional[str] = "ASC" (optional), query. 
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param sort: Optional[str] = "NAME" (optional), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoBuyerDto
        """
        endpoint = f"/api2/v1/buyers"
        params = {
            "sort": sort,
            "order": order,
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

        
        return PageDtoBuyerDto(**r.json())
        


    def update_buyer(
        self,
        buyer_edit_dto: BuyerEditDto,
        buyer_uid: str,
        phrase_token: Optional[str] = None,
) -> BuyerDto:
        """
        Operation id: updateBuyer
        Edit buyer
        
        :param buyer_edit_dto: BuyerEditDto (required), body. 
        :param buyer_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: BuyerDto
        """
        endpoint = f"/api2/v1/buyers/{buyer_uid}"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = buyer_edit_dto

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

        
        return BuyerDto(**r.json())
        



if __name__ == '__main__':
    print("This module is not intended to be run directly.")