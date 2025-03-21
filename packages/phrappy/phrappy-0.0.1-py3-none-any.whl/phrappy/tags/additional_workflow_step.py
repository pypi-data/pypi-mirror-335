from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union, Any

if TYPE_CHECKING:
    from ..client import SyncPhraseTMSClient

from ..models import (
    PageDtoAdditionalWorkflowStepDto,
    AdditionalWorkflowStepDto,
    AdditionalWorkflowStepRequestDto
    
)


class AdditionalWorkflowStepOperations:
    def __init__(self, client: SyncPhraseTMSClient):
        self.client = client


    def create_awf_step(
        self,
        additional_workflow_step_request_dto: AdditionalWorkflowStepRequestDto,
        phrase_token: Optional[str] = None,
) -> AdditionalWorkflowStepDto:
        """
        Operation id: createAWFStep
        Create additional workflow step
        
        :param additional_workflow_step_request_dto: AdditionalWorkflowStepRequestDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AdditionalWorkflowStepDto
        """
        endpoint = f"/api2/v1/additionalWorkflowSteps"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = additional_workflow_step_request_dto

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

        
        return AdditionalWorkflowStepDto(**r.json())
        


    def delete_awf_step(
        self,
        id: str,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: deleteAWFStep
        Delete additional workflow step
        
        :param id: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/additionalWorkflowSteps/{id}"
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
        


    def list_awf_steps(
        self,
        name: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        phrase_token: Optional[str] = None,
) -> PageDtoAdditionalWorkflowStepDto:
        """
        Operation id: listAWFSteps
        List additional workflow steps
        
        :param name: Optional[str] = None (optional), query. Name of the additional workflow step to filter.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoAdditionalWorkflowStepDto
        """
        endpoint = f"/api2/v1/additionalWorkflowSteps"
        params = {
            "pageNumber": page_number,
            "pageSize": page_size,
            "name": name
            
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

        
        return PageDtoAdditionalWorkflowStepDto(**r.json())
        



if __name__ == '__main__':
    print("This module is not intended to be run directly.")