from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union, Any

if TYPE_CHECKING:
    from ..client import SyncPhraseTMSClient

from ..models import (
    PageDtoCustomFieldOptionDto,
    UpdateCustomFieldDto,
    PageDtoCustomFieldDto,
    CreateCustomFieldDto,
    CustomFieldDto
    
)


class CustomFieldsOperations:
    def __init__(self, client: SyncPhraseTMSClient):
        self.client = client


    async def create_custom_field(
        self,
        create_custom_field_dto: CreateCustomFieldDto,
        phrase_token: Optional[str] = None,
) -> CustomFieldDto:
        """
        Operation id: createCustomField
        Create custom field
        
        :param create_custom_field_dto: CreateCustomFieldDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: CustomFieldDto
        """
        endpoint = f"/api2/v1/customFields"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = create_custom_field_dto

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

        
        return CustomFieldDto(**r.json())
        


    async def delete_custom_field(
        self,
        field_uid: str,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: deleteCustomField
        Delete custom field
        
        :param field_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/customFields/{field_uid}"
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
        


    async def get_custom_field(
        self,
        field_uid: str,
        phrase_token: Optional[str] = None,
) -> CustomFieldDto:
        """
        Operation id: getCustomField
        Get custom field
        
        :param field_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: CustomFieldDto
        """
        endpoint = f"/api2/v1/customFields/{field_uid}"
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

        
        return CustomFieldDto(**r.json())
        


    async def get_custom_field_list(
        self,
        allowed_entities: Optional[List[str]] = None,
        created_by: Optional[List[str]] = None,
        modified_by: Optional[List[str]] = None,
        name: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        required: Optional[bool] = None,
        sort_field: Optional[str] = None,
        sort_trend: Optional[str] = "ASC",
        types: Optional[List[str]] = None,
        uids: Optional[List[str]] = None,
        phrase_token: Optional[str] = None,
) -> PageDtoCustomFieldDto:
        """
        Operation id: getCustomFieldList
        Lists custom fields
        
        :param allowed_entities: Optional[List[str]] = None (optional), query. Filter by custom field allowed entities.
        :param created_by: Optional[List[str]] = None (optional), query. Filter by custom field creators UIDs.
        :param modified_by: Optional[List[str]] = None (optional), query. Filter by custom field updaters UIDs.
        :param name: Optional[str] = None (optional), query. Filter by custom field name.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param required: Optional[bool] = None (optional), query. Filter by custom field required parameter.
        :param sort_field: Optional[str] = None (optional), query. Sort by this field.
        :param sort_trend: Optional[str] = "ASC" (optional), query. Sort direction.
        :param types: Optional[List[str]] = None (optional), query. Filter by custom field types.
        :param uids: Optional[List[str]] = None (optional), query. Filter by custom field UIDs.
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoCustomFieldDto
        """
        endpoint = f"/api2/v1/customFields"
        params = {
            "pageNumber": page_number,
            "pageSize": page_size,
            "name": name,
            "allowedEntities": allowed_entities,
            "types": types,
            "createdBy": created_by,
            "modifiedBy": modified_by,
            "uids": uids,
            "required": required,
            "sortField": sort_field,
            "sortTrend": sort_trend
            
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

        
        return PageDtoCustomFieldDto(**r.json())
        


    async def get_custom_field_option_list(
        self,
        field_uid: str,
        name: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        sort_field: Optional[str] = "NAME",
        sort_trend: Optional[str] = "ASC",
        phrase_token: Optional[str] = None,
) -> PageDtoCustomFieldOptionDto:
        """
        Operation id: getCustomFieldOptionList
        Lists options of custom field
        
        :param field_uid: str (required), path. 
        :param name: Optional[str] = None (optional), query. Filter by option name.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param sort_field: Optional[str] = "NAME" (optional), query. Sort by this field.
        :param sort_trend: Optional[str] = "ASC" (optional), query. Sort direction.
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoCustomFieldOptionDto
        """
        endpoint = f"/api2/v1/customFields/{field_uid}/options"
        params = {
            "pageNumber": page_number,
            "pageSize": page_size,
            "name": name,
            "sortField": sort_field,
            "sortTrend": sort_trend
            
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

        
        return PageDtoCustomFieldOptionDto(**r.json())
        


    async def update_custom_field(
        self,
        update_custom_field_dto: UpdateCustomFieldDto,
        field_uid: str,
        phrase_token: Optional[str] = None,
) -> CustomFieldDto:
        """
        Operation id: updateCustomField
        Edit custom field
        
        :param update_custom_field_dto: UpdateCustomFieldDto (required), body. 
        :param field_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: CustomFieldDto
        """
        endpoint = f"/api2/v1/customFields/{field_uid}"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = update_custom_field_dto

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

        
        return CustomFieldDto(**r.json())
        



if __name__ == '__main__':
    print("This module is not intended to be run directly.")