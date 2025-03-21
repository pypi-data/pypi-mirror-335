from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union, Any

if TYPE_CHECKING:
    from ..client import SyncPhraseTMSClient

from ..models import (
    ProjectJobPartsDto,
    InputStream,
    UploadBilingualFileRequestDto,
    ComparedSegmentsDto,
    GetBilingualFileDto,
    QualityAssuranceResponseDto
    
)


class BilingualFileOperations:
    def __init__(self, client: SyncPhraseTMSClient):
        self.client = client


    def compare_bilingual_file(
        self,
        input_stream: bytes,
        workflow_level: Optional[int] = 1,
        phrase_token: Optional[str] = None,
) -> ComparedSegmentsDto:
        """
        Operation id: compareBilingualFile
        Compare bilingual file
        Compares bilingual file to job state. Returns list of compared segments.
        :param input_stream: bytes (required), body. 
        :param workflow_level: Optional[int] = 1 (optional), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ComparedSegmentsDto
        """
        endpoint = f"/api2/v1/bilingualFiles/compare"
        params = {
            "workflowLevel": workflow_level
            
        }
        headers = {
            
        }

        content = input_stream

        files = None

        payload = None

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

        
        return ComparedSegmentsDto(**r.json())
        


    def convert_bilingual_file(
        self,
        input_stream: bytes,
        frm: str,
        to: str,
        phrase_token: Optional[str] = None,
) -> bytes:
        """
        Operation id: convertBilingualFile
        Convert bilingual file
        
        :param input_stream: bytes (required), body. 
        :param frm: str (required), query. 
        :param to: str (required), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """
        endpoint = f"/api2/v1/bilingualFiles/convert"
        params = {
            "from": frm,
            "to": to
            
        }
        headers = {
            
        }

        content = input_stream

        files = None

        payload = None

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

        
        return r.content
        


    def get_bilingual_file(
        self,
        get_bilingual_file_dto: GetBilingualFileDto,
        project_uid: str,
        format: Optional[str] = "MXLF",
        preview: Optional[bool] = True,
        phrase_token: Optional[str] = None,
) -> bytes:
        """
        Operation id: getBilingualFile
        Download bilingual file
        
This API call generates a bilingual file in the chosen format by merging all submitted jobs together.
Note that all submitted jobs must belong to the same project; it's not feasible to merge jobs from multiple projects.

When dealing with MXLIFF or DOCX files, modifications made externally can be imported back into the Phrase TMS project.
Any changes will be synchronized into the editor, allowing actions like confirming or locking segments.

Unlike the user interface (UI), the APIs also support XLIFF as a bilingual format.

While MXLIFF files are editable using various means, their primary intended use is with the
[CAT Desktop Editor](https://support.phrase.com/hc/en-us/articles/5709683873052-CAT-Desktop-Editor-TMS-).
It's crucial to note that alterations to the file incompatible with the CAT Desktop Editor's features may result in
a corrupted file, leading to potential loss or duplication of work.

        :param get_bilingual_file_dto: GetBilingualFileDto (required), body. 
        :param project_uid: str (required), path. 
        :param format: Optional[str] = "MXLF" (optional), query. 
        :param preview: Optional[bool] = True (optional), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """
        endpoint = f"/api2/v1/projects/{project_uid}/jobs/bilingualFile"
        params = {
            "format": format,
            "preview": preview
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = get_bilingual_file_dto

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

        
        return r.content
        


    def get_preview_file(
        self,
        input_stream: bytes,
        phrase_token: Optional[str] = None,
) -> bytes:
        """
        Operation id: getPreviewFile
        Download preview
        Supports mxliff format
        :param input_stream: bytes (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: bytes
        """
        endpoint = f"/api2/v1/bilingualFiles/preview"
        params = {
            
        }
        headers = {
            
        }

        content = input_stream

        files = None

        payload = None

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

        
        return r.content
        


    def run_qa_and_save_v4(
        self,
        input_stream: bytes,
        project_uid: str,
        segment_id: str,
        phrase_token: Optional[str] = None,
) -> QualityAssuranceResponseDto:
        """
        Operation id: runQaAndSaveV4
        Run quality assurance on selected segments and save segments
        By default runs only fast running checks.
        :param input_stream: bytes (required), body. 
        :param project_uid: str (required), path. 
        :param segment_id: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: QualityAssuranceResponseDto
        """
        endpoint = f"/api2/v4/projects/{project_uid}/jobs/qualityAssurances/segments/{segment_id}/runWithUpdate"
        params = {
            
        }
        headers = {
            
        }

        content = input_stream

        files = None

        payload = None

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

        
        return QualityAssuranceResponseDto(**r.json())
        


    def upload_bilingual_file_v2(
        self,
        multipart: UploadBilingualFileRequestDto,
        save_to_trans_memory: Optional[str] = "Confirmed",
        set_completed: Optional[bool] = False,
        phrase_token: Optional[str] = None,
) -> ProjectJobPartsDto:
        """
        Operation id: uploadBilingualFileV2
        Upload bilingual file
        Returns updated job parts and projects
        :param multipart: UploadBilingualFileRequestDto (required), body. Multipart request with files.
        :param save_to_trans_memory: Optional[str] = "Confirmed" (optional), query. 
        :param set_completed: Optional[bool] = False (optional), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProjectJobPartsDto
        """
        endpoint = f"/api2/v2/bilingualFiles"
        params = {
            "saveToTransMemory": save_to_trans_memory,
            "setCompleted": set_completed
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = multipart

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

        
        return ProjectJobPartsDto(**r.json())
        



if __name__ == '__main__':
    print("This module is not intended to be run directly.")