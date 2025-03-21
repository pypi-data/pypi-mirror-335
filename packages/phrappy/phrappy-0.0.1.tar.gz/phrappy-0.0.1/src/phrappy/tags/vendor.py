from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union, Any

if TYPE_CHECKING:
    from ..client import SyncPhraseTMSClient

from ..models import (
    PageDtoVendorDto,
    CreateVendorDto,
    VendorDto,
    DeleteVendorsDto
    
)


class VendorOperations:
    def __init__(self, client: SyncPhraseTMSClient):
        self.client = client


    def create_vendor(
        self,
        create_vendor_dto: CreateVendorDto,
        phrase_token: Optional[str] = None,
) -> VendorDto:
        """
        Operation id: createVendor
        Create vendor
        
        :param create_vendor_dto: CreateVendorDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: VendorDto
        """
        endpoint = f"/api2/v1/vendors"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = create_vendor_dto

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

        
        return VendorDto(**r.json())
        


    def delete_vendors(
        self,
        delete_vendors_dto: DeleteVendorsDto,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: deleteVendors
        Delete vendors (batch)
        
        :param delete_vendors_dto: DeleteVendorsDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/vendors"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = delete_vendors_dto

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
        


    def get_vendor(
        self,
        vendor_uid: str,
        phrase_token: Optional[str] = None,
) -> VendorDto:
        """
        Operation id: getVendor
        Get vendor
        
        :param vendor_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: VendorDto
        """
        endpoint = f"/api2/v1/vendors/{vendor_uid}"
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

        
        return VendorDto(**r.json())
        


    def list_vendors(
        self,
        name: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        phrase_token: Optional[str] = None,
) -> PageDtoVendorDto:
        """
        Operation id: listVendors
        List vendors
        
        :param name: Optional[str] = None (optional), query. Name or the vendor, for filtering.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoVendorDto
        """
        endpoint = f"/api2/v1/vendors"
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

        
        return PageDtoVendorDto(**r.json())
        



if __name__ == '__main__':
    print("This module is not intended to be run directly.")