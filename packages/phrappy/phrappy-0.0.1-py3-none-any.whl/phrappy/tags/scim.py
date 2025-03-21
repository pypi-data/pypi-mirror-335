from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union, Any

if TYPE_CHECKING:
    from ..client import SyncPhraseTMSClient

from ..models import (
    ScimUserCoreDto,
    ServiceProviderConfigDto,
    ScimResourceSchema,
    ScimResourceTypeSchema
    
)


class SCIMOperations:
    def __init__(self, client: SyncPhraseTMSClient):
        self.client = client


    def create_user_scim(
        self,
        scim_user_core_dto: ScimUserCoreDto,
        authorization: Optional[str] = None,
        phrase_token: Optional[str] = None,
) -> ScimUserCoreDto:
        """
        Operation id: createUserSCIM
        Create user using SCIM
        
Supported schema: `"urn:ietf:params:scim:schemas:core:2.0:User"`

Create active user:
```
{
    "schemas": [
        "urn:ietf:params:scim:schemas:core:2.0:User"
    ],
    "active": true,
    "userName": "john.doe",
    "emails": [
        {
            "primary": true,
            "value": "john.doe@example.com",
            "type": "work"
        }
    ],
    "name": {
        "givenName": "John",
        "familyName": "Doe"
    }
}
```

        :param scim_user_core_dto: ScimUserCoreDto (required), body. 
        :param authorization: Optional[str] = None (optional), header. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ScimUserCoreDto
        """
        endpoint = f"/api2/v1/scim/Users"
        params = {
            
        }
        headers = {
            "Authorization": authorization
            
        }

        content = None

        files = None

        payload = scim_user_core_dto

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

        
        return ScimUserCoreDto(**r.json())
        


    def delete_user_scim(
        self,
        user_id: int,
        authorization: Optional[str] = None,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: deleteUserScim
        Delete user using SCIM
        
        :param user_id: int (required), path. 
        :param authorization: Optional[str] = None (optional), header. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/scim/Users/{user_id}"
        params = {
            
        }
        headers = {
            "Authorization": authorization
            
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
        


    def edit_user(
        self,
        scim_user_core_dto: ScimUserCoreDto,
        user_id: int,
        authorization: Optional[str] = None,
        phrase_token: Optional[str] = None,
) -> ScimUserCoreDto:
        """
        Operation id: editUser
        Edit user using SCIM
        
        :param scim_user_core_dto: ScimUserCoreDto (required), body. 
        :param user_id: int (required), path. 
        :param authorization: Optional[str] = None (optional), header. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ScimUserCoreDto
        """
        endpoint = f"/api2/v1/scim/Users/{user_id}"
        params = {
            
        }
        headers = {
            "Authorization": authorization
            
        }

        content = None

        files = None

        payload = scim_user_core_dto

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

        
        return ScimUserCoreDto(**r.json())
        


    def get_resource_types(
        self,
        phrase_token: Optional[str] = None,
) -> ScimResourceTypeSchema:
        """
        Operation id: getResourceTypes
        List the types of SCIM Resources available
        
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ScimResourceTypeSchema
        """
        endpoint = f"/api2/v1/scim/ResourceTypes"
        params = {
            
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

        
        return ScimResourceTypeSchema(**r.json())
        


    def get_schema_by_urn(
        self,
        schema_urn: str,
        phrase_token: Optional[str] = None,
) -> ScimResourceSchema:
        """
        Operation id: getSchemaByUrn
        Get supported SCIM Schema by urn
        
        :param schema_urn: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ScimResourceSchema
        """
        endpoint = f"/api2/v1/scim/Schemas/{schema_urn}"
        params = {
            
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

        
        return ScimResourceSchema(**r.json())
        


    def get_schemas(
        self,
        phrase_token: Optional[str] = None,
) -> ScimResourceSchema:
        """
        Operation id: getSchemas
        Get supported SCIM Schemas
        
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ScimResourceSchema
        """
        endpoint = f"/api2/v1/scim/Schemas"
        params = {
            
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

        
        return ScimResourceSchema(**r.json())
        


    def get_scim_user(
        self,
        user_id: int,
        authorization: Optional[str] = None,
        phrase_token: Optional[str] = None,
) -> ScimUserCoreDto:
        """
        Operation id: getScimUser
        Get user
        
        :param user_id: int (required), path. 
        :param authorization: Optional[str] = None (optional), header. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ScimUserCoreDto
        """
        endpoint = f"/api2/v1/scim/Users/{user_id}"
        params = {
            
        }
        headers = {
            "Authorization": authorization
            
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

        
        return ScimUserCoreDto(**r.json())
        


    def get_service_provider_config_dto(
        self,
        phrase_token: Optional[str] = None,
) -> ServiceProviderConfigDto:
        """
        Operation id: getServiceProviderConfigDto
        Retrieve the Service Provider's Configuration
        
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ServiceProviderConfigDto
        """
        endpoint = f"/api2/v1/scim/ServiceProviderConfig"
        params = {
            
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

        
        return ServiceProviderConfigDto(**r.json())
        


    def patch_user(
        self,
        dict: dict,
        user_id: int,
        authorization: Optional[str] = None,
        phrase_token: Optional[str] = None,
) -> ScimUserCoreDto:
        """
        Operation id: patchUser
        Patch user using SCIM
        
        :param dict: dict (required), body. 
        :param user_id: int (required), path. 
        :param authorization: Optional[str] = None (optional), header. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ScimUserCoreDto
        """
        endpoint = f"/api2/v1/scim/Users/{user_id}"
        params = {
            
        }
        headers = {
            "Authorization": authorization
            
        }

        content = None

        files = None

        payload = dict

        r = self.client.make_request(
            "PATCH",
            endpoint,
            phrase_token,
            params=params,
            payload=payload,
            files=files,
            headers=headers,
            content=content
        )

        
        return ScimUserCoreDto(**r.json())
        


    def search_users(
        self,
        authorization: Optional[str] = None,
        attributes: Optional[str] = None,
        count: Optional[int] = 50,
        filter: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = "ascending",
        start_index: Optional[int] = 1,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: searchUsers
        Search users
        
This operation supports <a href="http://ldapwiki.com/wiki/SCIM%20Filtering" target="_blank">SCIM Filter</a>, 
<a href="http://ldapwiki.com/wiki/SCIM%20Search%20Request" target="_blank">SCIM attributes</a> and 
<a href="http://ldapwiki.com/wiki/SCIM%20Sorting" target="_blank">SCIM sort</a>

Supported attributes:
  - `id`
  - `active`
  - `userName`
  - `name.givenName`
  - `name.familyName`
  - `emails.value`
  - `meta.created`

        :param authorization: Optional[str] = None (optional), header. 
        :param attributes: Optional[str] = None (optional), query. See method description.
        :param count: Optional[int] = 50 (optional), query. Non-negative Integer. Specifies the desired maximum number of search results per page; e.g., 10..
        :param filter: Optional[str] = None (optional), query. See method description.
        :param sort_by: Optional[str] = None (optional), query. See method description.
        :param sort_order: Optional[str] = "ascending" (optional), query. See method description.
        :param start_index: Optional[int] = 1 (optional), query. The 1-based index of the first search result. Default 1.
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/scim/Users"
        params = {
            "filter": filter,
            "attributes": attributes,
            "sortBy": sort_by,
            "sortOrder": sort_order,
            "startIndex": start_index,
            "count": count
            
        }
        headers = {
            "Authorization": authorization
            
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

        
        return
        



if __name__ == '__main__':
    print("This module is not intended to be run directly.")