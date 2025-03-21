from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union, Any

if TYPE_CHECKING:
    from ..client import SyncPhraseTMSClient

from ..models import (
    LoginUserDto,
    LoginResponseDto,
    LoginToSessionV3Dto,
    LoginWithGoogleDto,
    LoginDto,
    LoginToSessionResponseDto,
    LoginWithAppleDto,
    AppleTokenResponseDto,
    LoginToSessionResponseV3Dto,
    LoginResponseV3Dto,
    LoginToSessionDto,
    LoginOtherV3Dto,
    LoginV3Dto,
    LoginOtherDto
    
)


class AuthenticationOperations:
    def __init__(self, client: SyncPhraseTMSClient):
        self.client = client


    async def login(
        self,
        login_dto: LoginDto,
        phrase_token: Optional[str] = None,
) -> LoginResponseDto:
        """
        Operation id: login
        Login
        
        :param login_dto: LoginDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LoginResponseDto
        """
        endpoint = f"/api2/v1/auth/login"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = login_dto

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

        
        return LoginResponseDto(**r.json())
        


    async def login_by_apple_with_code(
        self,
        login_with_apple_dto: LoginWithAppleDto,
        native: Optional[bool] = None,
        phrase_token: Optional[str] = None,
) -> LoginResponseDto:
        """
        Operation id: loginByAppleWithCode
        Login with Apple with code
        
        :param login_with_apple_dto: LoginWithAppleDto (required), body. 
        :param native: Optional[bool] = None (optional), query. For sign in with code from native device.
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LoginResponseDto
        """
        endpoint = f"/api2/v1/auth/loginWithApple/code"
        params = {
            "native": native
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = login_with_apple_dto

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

        
        return LoginResponseDto(**r.json())
        


    async def login_by_apple_with_refresh_token(
        self,
        login_with_apple_dto: LoginWithAppleDto,
        phrase_token: Optional[str] = None,
) -> LoginResponseDto:
        """
        Operation id: loginByAppleWithRefreshToken
        Login with Apple refresh token
        
        :param login_with_apple_dto: LoginWithAppleDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LoginResponseDto
        """
        endpoint = f"/api2/v1/auth/loginWithApple/refreshToken"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = login_with_apple_dto

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

        
        return LoginResponseDto(**r.json())
        


    async def login_by_google(
        self,
        login_with_google_dto: LoginWithGoogleDto,
        phrase_token: Optional[str] = None,
) -> LoginResponseDto:
        """
        Operation id: loginByGoogle
        Login with Google
        
        :param login_with_google_dto: LoginWithGoogleDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LoginResponseDto
        """
        endpoint = f"/api2/v1/auth/loginWithGoogle"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = login_with_google_dto

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

        
        return LoginResponseDto(**r.json())
        


    async def login_other(
        self,
        login_other_dto: LoginOtherDto,
        phrase_token: Optional[str] = None,
) -> LoginResponseDto:
        """
        Operation id: loginOther
        Login as another user
        Available only for admin
        :param login_other_dto: LoginOtherDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LoginResponseDto
        """
        endpoint = f"/api2/v1/auth/loginOther"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = login_other_dto

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

        
        return LoginResponseDto(**r.json())
        


    async def login_other_v3(
        self,
        login_other_v3_dto: LoginOtherV3Dto,
        phrase_token: Optional[str] = None,
) -> LoginResponseV3Dto:
        """
        Operation id: loginOtherV3
        Login as another user
        Available only for admin
        :param login_other_v3_dto: LoginOtherV3Dto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LoginResponseV3Dto
        """
        endpoint = f"/api2/v3/auth/loginOther"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = login_other_v3_dto

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

        
        return LoginResponseV3Dto(**r.json())
        


    async def login_to_session(
        self,
        login_to_session_dto: LoginToSessionDto,
        phrase_token: Optional[str] = None,
) -> LoginToSessionResponseDto:
        """
        Operation id: loginToSession
        Login to session
        
        :param login_to_session_dto: LoginToSessionDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LoginToSessionResponseDto
        """
        endpoint = f"/api2/v1/auth/loginToSession"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = login_to_session_dto

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

        
        return LoginToSessionResponseDto(**r.json())
        


    async def login_to_session_2(
        self,
        login_to_session_v3_dto: LoginToSessionV3Dto,
        phrase_token: Optional[str] = None,
) -> LoginToSessionResponseV3Dto:
        """
        Operation id: loginToSession_2
        Login to session
        
        :param login_to_session_v3_dto: LoginToSessionV3Dto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LoginToSessionResponseV3Dto
        """
        endpoint = f"/api2/v3/auth/loginToSession"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = login_to_session_v3_dto

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

        
        return LoginToSessionResponseV3Dto(**r.json())
        


    async def login_v3(
        self,
        login_v3_dto: LoginV3Dto,
        phrase_token: Optional[str] = None,
) -> LoginResponseV3Dto:
        """
        Operation id: loginV3
        Login
        
        :param login_v3_dto: LoginV3Dto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LoginResponseV3Dto
        """
        endpoint = f"/api2/v3/auth/login"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = login_v3_dto

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

        
        return LoginResponseV3Dto(**r.json())
        


    async def logout(
        self,
        authorization: Optional[str] = None,
        token: Optional[str] = None,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: logout
        Logout
        
        :param authorization: Optional[str] = None (optional), header. 
        :param token: Optional[str] = None (optional), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/auth/logout"
        params = {
            "token": token
            
        }
        headers = {
            "Authorization": authorization
            
        }

        content = None

        files = None

        payload = None

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
        


    async def refresh_apple_token(
        self,
        token: Optional[str] = None,
        phrase_token: Optional[str] = None,
) -> AppleTokenResponseDto:
        """
        Operation id: refreshAppleToken
        refresh apple token
        
        :param token: Optional[str] = None (optional), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AppleTokenResponseDto
        """
        endpoint = f"/api2/v1/auth/refreshAppleToken"
        params = {
            "token": token
            
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

        
        return AppleTokenResponseDto(**r.json())
        


    async def who_am_i(
        self,
        phrase_token: Optional[str] = None,
) -> LoginUserDto:
        """
        Operation id: whoAmI
        Who am I
        
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: LoginUserDto
        """
        endpoint = f"/api2/v1/auth/whoAmI"
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

        
        return LoginUserDto(**r.json())
        



if __name__ == '__main__':
    print("This module is not intended to be run directly.")