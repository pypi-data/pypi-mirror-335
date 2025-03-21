from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union, Any

if TYPE_CHECKING:
    from ..client import SyncPhraseTMSClient

from ..models import (
    PageDtoTranslationPriceListDto,
    TranslationPriceSetBulkDeleteDto,
    PageDtoTranslationPriceSetDto,
    TranslationPriceSetBulkMinimumPricesDto,
    TranslationPriceListDto,
    TranslationPriceListCreateDto,
    TranslationPriceSetListDto,
    TranslationPriceSetBulkPricesDto,
    TranslationPriceSetCreateDto
    
)


class PriceListOperations:
    def __init__(self, client: SyncPhraseTMSClient):
        self.client = client


    async def create_language_pair(
        self,
        translation_price_set_create_dto: TranslationPriceSetCreateDto,
        price_list_uid: str,
        phrase_token: Optional[str] = None,
) -> TranslationPriceSetListDto:
        """
        Operation id: createLanguagePair
        Add language pairs
        
        :param translation_price_set_create_dto: TranslationPriceSetCreateDto (required), body. 
        :param price_list_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TranslationPriceSetListDto
        """
        endpoint = f"/api2/v1/priceLists/{price_list_uid}/priceSets"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = translation_price_set_create_dto

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

        
        return TranslationPriceSetListDto(**r.json())
        


    async def create_price_list(
        self,
        translation_price_list_create_dto: TranslationPriceListCreateDto,
        phrase_token: Optional[str] = None,
) -> TranslationPriceListDto:
        """
        Operation id: createPriceList
        Create price list
        
        :param translation_price_list_create_dto: TranslationPriceListCreateDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TranslationPriceListDto
        """
        endpoint = f"/api2/v1/priceLists"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = translation_price_list_create_dto

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

        
        return TranslationPriceListDto(**r.json())
        


    async def delete_language_pair(
        self,
        price_list_uid: str,
        source_language: str,
        target_language: str,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: deleteLanguagePair
        Remove language pair
        
        :param price_list_uid: str (required), path. 
        :param source_language: str (required), path. 
        :param target_language: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/priceLists/{price_list_uid}/priceSets/{source_language}/{target_language}"
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
        


    async def delete_language_pairs(
        self,
        translation_price_set_bulk_delete_dto: TranslationPriceSetBulkDeleteDto,
        price_list_uid: str,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: deleteLanguagePairs
        Remove language pairs
        
        :param translation_price_set_bulk_delete_dto: TranslationPriceSetBulkDeleteDto (required), body. 
        :param price_list_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/priceLists/{price_list_uid}/priceSets"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = translation_price_set_bulk_delete_dto

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
        


    async def delete_price_list(
        self,
        price_list_uid: str,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: deletePriceList
        Delete price list
        
        :param price_list_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/priceLists/{price_list_uid}"
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
        


    async def get_list_of_price_list(
        self,
        name: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        phrase_token: Optional[str] = None,
) -> PageDtoTranslationPriceListDto:
        """
        Operation id: getListOfPriceList
        List price lists
        
        :param name: Optional[str] = None (optional), query. Filter for name.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoTranslationPriceListDto
        """
        endpoint = f"/api2/v1/priceLists"
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

        
        return PageDtoTranslationPriceListDto(**r.json())
        


    async def get_price_list(
        self,
        price_list_uid: str,
        phrase_token: Optional[str] = None,
) -> TranslationPriceListDto:
        """
        Operation id: getPriceList
        Get price list
        
        :param price_list_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TranslationPriceListDto
        """
        endpoint = f"/api2/v1/priceLists/{price_list_uid}"
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

        
        return TranslationPriceListDto(**r.json())
        


    async def get_prices_with_workflow_steps(
        self,
        price_list_uid: str,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        source_languages: Optional[List[str]] = None,
        target_languages: Optional[List[str]] = None,
        phrase_token: Optional[str] = None,
) -> PageDtoTranslationPriceSetDto:
        """
        Operation id: getPricesWithWorkflowSteps
        List price sets
        
        :param price_list_uid: str (required), path. 
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param source_languages: Optional[List[str]] = None (optional), query. 
        :param target_languages: Optional[List[str]] = None (optional), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoTranslationPriceSetDto
        """
        endpoint = f"/api2/v1/priceLists/{price_list_uid}/priceSets"
        params = {
            "pageNumber": page_number,
            "pageSize": page_size,
            "sourceLanguages": source_languages,
            "targetLanguages": target_languages
            
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

        
        return PageDtoTranslationPriceSetDto(**r.json())
        


    async def set_minimum_price_for_set(
        self,
        translation_price_set_bulk_minimum_prices_dto: TranslationPriceSetBulkMinimumPricesDto,
        price_list_uid: str,
        phrase_token: Optional[str] = None,
) -> TranslationPriceListDto:
        """
        Operation id: setMinimumPriceForSet
        Edit minimum prices
        
        :param translation_price_set_bulk_minimum_prices_dto: TranslationPriceSetBulkMinimumPricesDto (required), body. 
        :param price_list_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TranslationPriceListDto
        """
        endpoint = f"/api2/v1/priceLists/{price_list_uid}/priceSets/minimumPrices"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = translation_price_set_bulk_minimum_prices_dto

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

        
        return TranslationPriceListDto(**r.json())
        


    async def set_prices(
        self,
        translation_price_set_bulk_prices_dto: TranslationPriceSetBulkPricesDto,
        price_list_uid: str,
        phrase_token: Optional[str] = None,
) -> TranslationPriceListDto:
        """
        Operation id: setPrices
        Edit prices
        If object contains only price, all languages and workflow steps will be updated
        :param translation_price_set_bulk_prices_dto: TranslationPriceSetBulkPricesDto (required), body. 
        :param price_list_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TranslationPriceListDto
        """
        endpoint = f"/api2/v1/priceLists/{price_list_uid}/priceSets/prices"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = translation_price_set_bulk_prices_dto

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

        
        return TranslationPriceListDto(**r.json())
        


    async def update_price_list(
        self,
        translation_price_list_create_dto: TranslationPriceListCreateDto,
        price_list_uid: str,
        phrase_token: Optional[str] = None,
) -> TranslationPriceListDto:
        """
        Operation id: updatePriceList
        Update price list
        
        :param translation_price_list_create_dto: TranslationPriceListCreateDto (required), body. 
        :param price_list_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: TranslationPriceListDto
        """
        endpoint = f"/api2/v1/priceLists/{price_list_uid}"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = translation_price_list_create_dto

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

        
        return TranslationPriceListDto(**r.json())
        



if __name__ == '__main__':
    print("This module is not intended to be run directly.")