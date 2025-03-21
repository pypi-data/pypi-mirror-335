from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union, Any

if TYPE_CHECKING:
    from ..client import SyncPhraseTMSClient

from ..models import (
    WorkflowChangesDto
    
)


class WorkflowchangesOperations:
    def __init__(self, client: SyncPhraseTMSClient):
        self.client = client


    async def download_workflow_changes(
        self,
        workflow_changes_dto: WorkflowChangesDto,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: downloadWorkflowChanges
        Download workflow changes report
        
        :param workflow_changes_dto: WorkflowChangesDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v2/jobs/workflowChanges"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = workflow_changes_dto

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

        
        return
        



if __name__ == '__main__':
    print("This module is not intended to be run directly.")