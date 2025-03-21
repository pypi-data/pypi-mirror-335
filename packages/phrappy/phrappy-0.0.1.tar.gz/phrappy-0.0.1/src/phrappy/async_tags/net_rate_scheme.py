from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union, Any

if TYPE_CHECKING:
    from ..client import SyncPhraseTMSClient

from ..models import (
    PageDtoNetRateSchemeWorkflowStepReference,
    NetRateSchemeEdit,
    NetRateSchemeWorkflowStepEdit,
    NetRateScheme,
    DiscountSchemeCreateDto,
    PageDtoNetRateSchemeReference,
    NetRateSchemeWorkflowStep
    
)


class NetRateSchemeOperations:
    def __init__(self, client: SyncPhraseTMSClient):
        self.client = client


    async def create_discount_scheme(
        self,
        discount_scheme_create_dto: DiscountSchemeCreateDto,
        phrase_token: Optional[str] = None,
) -> NetRateScheme:
        """
        Operation id: createDiscountScheme
        Create net rate scheme
        
        :param discount_scheme_create_dto: DiscountSchemeCreateDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: NetRateScheme
        """
        endpoint = f"/api2/v1/netRateSchemes"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = discount_scheme_create_dto

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

        
        return NetRateScheme(**r.json())
        


    async def edit_discount_scheme_workflow_step(
        self,
        net_rate_scheme_workflow_step_edit: NetRateSchemeWorkflowStepEdit,
        net_rate_scheme_uid: str,
        net_rate_scheme_workflow_step_id: int,
        phrase_token: Optional[str] = None,
) -> NetRateSchemeWorkflowStep:
        """
        Operation id: editDiscountSchemeWorkflowStep
        Edit scheme for workflow step
        
        :param net_rate_scheme_workflow_step_edit: NetRateSchemeWorkflowStepEdit (required), body. 
        :param net_rate_scheme_uid: str (required), path. 
        :param net_rate_scheme_workflow_step_id: int (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: NetRateSchemeWorkflowStep
        """
        endpoint = f"/api2/v1/netRateSchemes/{net_rate_scheme_uid}/workflowStepNetSchemes/{net_rate_scheme_workflow_step_id}"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = net_rate_scheme_workflow_step_edit

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

        
        return NetRateSchemeWorkflowStep(**r.json())
        


    async def get_discount_scheme(
        self,
        net_rate_scheme_uid: str,
        phrase_token: Optional[str] = None,
) -> NetRateScheme:
        """
        Operation id: getDiscountScheme
        Get net rate scheme
        
        :param net_rate_scheme_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: NetRateScheme
        """
        endpoint = f"/api2/v1/netRateSchemes/{net_rate_scheme_uid}"
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

        
        return NetRateScheme(**r.json())
        


    async def get_discount_scheme_workflow_step(
        self,
        net_rate_scheme_uid: str,
        net_rate_scheme_workflow_step_id: int,
        phrase_token: Optional[str] = None,
) -> NetRateSchemeWorkflowStep:
        """
        Operation id: getDiscountSchemeWorkflowStep
        Get scheme for workflow step
        
        :param net_rate_scheme_uid: str (required), path. 
        :param net_rate_scheme_workflow_step_id: int (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: NetRateSchemeWorkflowStep
        """
        endpoint = f"/api2/v1/netRateSchemes/{net_rate_scheme_uid}/workflowStepNetSchemes/{net_rate_scheme_workflow_step_id}"
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

        
        return NetRateSchemeWorkflowStep(**r.json())
        


    async def get_discount_scheme_workflow_steps(
        self,
        net_rate_scheme_uid: str,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        phrase_token: Optional[str] = None,
) -> PageDtoNetRateSchemeWorkflowStepReference:
        """
        Operation id: getDiscountSchemeWorkflowSteps
        List schemes for workflow step
        
        :param net_rate_scheme_uid: str (required), path. 
        :param page_number: Optional[int] = 0 (optional), query. 
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoNetRateSchemeWorkflowStepReference
        """
        endpoint = f"/api2/v1/netRateSchemes/{net_rate_scheme_uid}/workflowStepNetSchemes"
        params = {
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

        
        return PageDtoNetRateSchemeWorkflowStepReference(**r.json())
        


    async def get_discount_schemes(
        self,
        created_in_last_hours: Optional[int] = None,
        is_default: Optional[bool] = None,
        name: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        phrase_token: Optional[str] = None,
) -> PageDtoNetRateSchemeReference:
        """
        Operation id: getDiscountSchemes
        List net rate schemes
        
        :param created_in_last_hours: Optional[int] = None (optional), query. Filter for those created within given hours.
        :param is_default: Optional[bool] = None (optional), query. Filter for default attribute.
        :param name: Optional[str] = None (optional), query. Filter by name.
        :param page_number: Optional[int] = 0 (optional), query. 
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoNetRateSchemeReference
        """
        endpoint = f"/api2/v1/netRateSchemes"
        params = {
            "pageNumber": page_number,
            "pageSize": page_size,
            "name": name,
            "isDefault": is_default,
            "createdInLastHours": created_in_last_hours
            
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

        
        return PageDtoNetRateSchemeReference(**r.json())
        


    async def update_discount_scheme(
        self,
        net_rate_scheme_edit: NetRateSchemeEdit,
        net_rate_scheme_uid: str,
        phrase_token: Optional[str] = None,
) -> NetRateScheme:
        """
        Operation id: updateDiscountScheme
        Edit net rate scheme
        
        :param net_rate_scheme_edit: NetRateSchemeEdit (required), body. 
        :param net_rate_scheme_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: NetRateScheme
        """
        endpoint = f"/api2/v1/netRateSchemes/{net_rate_scheme_uid}"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = net_rate_scheme_edit

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

        
        return NetRateScheme(**r.json())
        



if __name__ == '__main__':
    print("This module is not intended to be run directly.")