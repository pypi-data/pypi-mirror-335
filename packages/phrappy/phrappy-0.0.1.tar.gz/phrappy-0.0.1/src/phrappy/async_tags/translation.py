from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union, Any

if TYPE_CHECKING:
    from ..client import SyncPhraseTMSClient

from ..models import (
    MachineTranslateResponse,
    TranslationRequestDto,
    AsyncRequestWrapperV2Dto,
    AsyncRequestWrapperDto,
    HumanTranslateJobsDto,
    PreTranslateJobsV3Dto
    
)


class TranslationOperations:
    def __init__(self, client: SyncPhraseTMSClient):
        self.client = client


    async def human_translate(
        self,
        human_translate_jobs_dto: HumanTranslateJobsDto,
        project_uid: str,
        phrase_token: Optional[str] = None,
) -> AsyncRequestWrapperDto:
        """
        Operation id: humanTranslate
        Human translate (Gengo or Unbabel)
        
        :param human_translate_jobs_dto: HumanTranslateJobsDto (required), body. 
        :param project_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AsyncRequestWrapperDto
        """
        endpoint = f"/api2/v1/projects/{project_uid}/jobs/humanTranslate"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = human_translate_jobs_dto

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

        
        return AsyncRequestWrapperDto(**r.json())
        


    async def machine_translation_job(
        self,
        translation_request_dto: TranslationRequestDto,
        job_uid: str,
        project_uid: str,
        phrase_token: Optional[str] = None,
) -> MachineTranslateResponse:
        """
        Operation id: machineTranslationJob
        Translate using machine translation
        Configured machine translate settings is used
        :param translation_request_dto: TranslationRequestDto (required), body. 
        :param job_uid: str (required), path. 
        :param project_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: MachineTranslateResponse
        """
        endpoint = f"/api2/v1/projects/{project_uid}/jobs/{job_uid}/translations/translateWithMachineTranslation"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = translation_request_dto

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

        
        return MachineTranslateResponse(**r.json())
        


    async def pre_translate_v3(
        self,
        pre_translate_jobs_v3_dto: PreTranslateJobsV3Dto,
        project_uid: str,
        phrase_token: Optional[str] = None,
) -> AsyncRequestWrapperV2Dto:
        """
        Operation id: preTranslateV3
        Pre-translate job
        
        :param pre_translate_jobs_v3_dto: PreTranslateJobsV3Dto (required), body. 
        :param project_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AsyncRequestWrapperV2Dto
        """
        endpoint = f"/api2/v3/projects/{project_uid}/jobs/preTranslate"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = pre_translate_jobs_v3_dto

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

        
        return AsyncRequestWrapperV2Dto(**r.json())
        



if __name__ == '__main__':
    print("This module is not intended to be run directly.")