from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union, Any

if TYPE_CHECKING:
    from ..client import SyncPhraseTMSClient

from ..models import (
    PageDtoCostCenterDto,
    CostCenterEditDto,
    CostCenterDto
    
)


class CostCenterOperations:
    def __init__(self, client: SyncPhraseTMSClient):
        self.client = client


    async def create_cost_center(
        self,
        cost_center_edit_dto: CostCenterEditDto,
        phrase_token: Optional[str] = None,
) -> CostCenterDto:
        """
        Operation id: createCostCenter
        Create cost center
        
        :param cost_center_edit_dto: CostCenterEditDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: CostCenterDto
        """
        endpoint = f"/api2/v1/costCenters"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = cost_center_edit_dto

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

        
        return CostCenterDto(**r.json())
        


    async def delete_cost_center(
        self,
        cost_center_uid: str,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: deleteCostCenter
        Delete cost center
        
        :param cost_center_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/costCenters/{cost_center_uid}"
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
        


    async def get_cost_center(
        self,
        cost_center_uid: str,
        phrase_token: Optional[str] = None,
) -> CostCenterDto:
        """
        Operation id: getCostCenter
        Get cost center
        
        :param cost_center_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: CostCenterDto
        """
        endpoint = f"/api2/v1/costCenters/{cost_center_uid}"
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

        
        return CostCenterDto(**r.json())
        


    async def list_cost_centers(
        self,
        created_by: Optional[str] = None,
        name: Optional[str] = None,
        order: Optional[str] = "ASC",
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        sort: Optional[str] = "NAME",
        phrase_token: Optional[str] = None,
) -> PageDtoCostCenterDto:
        """
        Operation id: listCostCenters
        List of cost centers
        
        :param created_by: Optional[str] = None (optional), query. Uid of user.
        :param name: Optional[str] = None (optional), query. 
        :param order: Optional[str] = "ASC" (optional), query. 
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param sort: Optional[str] = "NAME" (optional), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoCostCenterDto
        """
        endpoint = f"/api2/v1/costCenters"
        params = {
            "name": name,
            "createdBy": created_by,
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

        
        return PageDtoCostCenterDto(**r.json())
        


    async def update_cost_center(
        self,
        cost_center_edit_dto: CostCenterEditDto,
        cost_center_uid: str,
        phrase_token: Optional[str] = None,
) -> CostCenterDto:
        """
        Operation id: updateCostCenter
        Edit cost center
        
        :param cost_center_edit_dto: CostCenterEditDto (required), body. 
        :param cost_center_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: CostCenterDto
        """
        endpoint = f"/api2/v1/costCenters/{cost_center_uid}"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = cost_center_edit_dto

        r = await self.client.make_request(
            "PUT",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return CostCenterDto(**r.json())
        



if __name__ == '__main__':
    print("This module is not intended to be run directly.")