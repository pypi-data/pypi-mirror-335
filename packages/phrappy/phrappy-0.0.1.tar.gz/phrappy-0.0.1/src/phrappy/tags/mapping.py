from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union, Any

if TYPE_CHECKING:
    from ..client import SyncPhraseTMSClient

from ..models import (
    TaskMappingDto
    
)


class MappingOperations:
    def __init__(self, client: SyncPhraseTMSClient):
        self.client = client


    def get_mapping_for_task(
        self,
        id: str,
        workflow_level: Optional[int] = 1,
        phrase_token: Optional[str] = None,
) -> TaskMappingDto:
        """
        Operation id: getMappingForTask
        Returns mapping for taskId (mxliff)
        
        :param id: str (required), path. 
        :param workflow_level: Optional[int] = 1 (optional), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TaskMappingDto
        """
        endpoint = f"/api2/v1/mappings/tasks/{id}"
        params = {
            "workflowLevel": workflow_level
            
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

        
        return TaskMappingDto(**r.json())
        



if __name__ == '__main__':
    print("This module is not intended to be run directly.")