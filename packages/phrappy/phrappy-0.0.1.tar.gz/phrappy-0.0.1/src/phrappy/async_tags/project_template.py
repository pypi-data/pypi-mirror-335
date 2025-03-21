from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Union, Any

if TYPE_CHECKING:
    from ..client import SyncPhraseTMSClient

from ..models import (
    EditQASettingsDtoV2,
    FileImportSettingsDto,
    SetProjectTemplateTermBaseDto,
    AsyncRequestWrapperV2Dto,
    ProjectTemplateTermBaseListDto,
    EditProjectSecuritySettingsDtoV2,
    PageDtoProjectTemplateReference,
    UpdateCustomFieldInstancesDto,
    AbstractProjectDtoV2,
    MTSettingsPerLanguageListDto,
    ProjectTemplateEditDto,
    PageDtoCustomFieldInstanceDto,
    CustomFieldInstanceDto,
    CreateCustomFieldInstancesDto,
    CreateProjectFromTemplateV2Dto,
    QASettingsDtoV2,
    ProjectTemplateTransMemoryListV2Dto,
    ProjectTemplateTransMemoryListDtoV3,
    EditAnalyseSettingsDto,
    AssignableTemplatesDto,
    ProjectTemplateEditV2Dto,
    PageDtoTransMemoryDto,
    JobPartReferences,
    CreateProjectFromTemplateAsyncV2Dto,
    PreTranslateSettingsV4Dto,
    ProjectTemplate,
    JobPartsDto,
    ProjectTemplateCreateActionDto,
    FileImportSettingsCreateDto,
    SetProjectTemplateTransMemoriesV2Dto,
    AbstractAnalyseSettingsDto,
    ProjectSecuritySettingsDtoV2,
    CustomFieldInstancesDto,
    UpdateCustomFieldInstanceDto
    
)


class ProjectTemplateOperations:
    def __init__(self, client: SyncPhraseTMSClient):
        self.client = client


    async def assign_linguists_from_template(
        self,
        project_uid: str,
        template_uid: str,
        phrase_token: Optional[str] = None,
) -> JobPartsDto:
        """
        Operation id: assignLinguistsFromTemplate
        Assigns providers from template
        
        :param project_uid: str (required), path. 
        :param template_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: JobPartsDto
        """
        endpoint = f"/api2/v1/projects/{project_uid}/applyTemplate/{template_uid}/assignProviders"
        params = {
            
        }
        headers = {
            
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

        
        return JobPartsDto(**r.json())
        


    async def assign_linguists_from_template_to_job_parts(
        self,
        job_part_references: JobPartReferences,
        project_uid: str,
        template_uid: str,
        phrase_token: Optional[str] = None,
) -> JobPartsDto:
        """
        Operation id: assignLinguistsFromTemplateToJobParts
        Assigns providers from template (specific jobs)
        
        :param job_part_references: JobPartReferences (required), body. 
        :param project_uid: str (required), path. 
        :param template_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: JobPartsDto
        """
        endpoint = f"/api2/v1/projects/{project_uid}/applyTemplate/{template_uid}/assignProviders/forJobParts"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = job_part_references

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

        
        return JobPartsDto(**r.json())
        


    async def assignable_templates(
        self,
        project_uid: str,
        phrase_token: Optional[str] = None,
) -> AssignableTemplatesDto:
        """
        Operation id: assignableTemplates
        List assignable templates
        
        :param project_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AssignableTemplatesDto
        """
        endpoint = f"/api2/v1/projects/{project_uid}/assignableTemplates"
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

        
        return AssignableTemplatesDto(**r.json())
        


    async def create_custom_fields_on_project_template(
        self,
        create_custom_field_instances_dto: CreateCustomFieldInstancesDto,
        project_template_uid: str,
        phrase_token: Optional[str] = None,
) -> CustomFieldInstancesDto:
        """
        Operation id: createCustomFieldsOnProjectTemplate
        Create custom field instances
        
        :param create_custom_field_instances_dto: CreateCustomFieldInstancesDto (required), body. 
        :param project_template_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: CustomFieldInstancesDto
        """
        endpoint = f"/api2/v1/projectTemplates/{project_template_uid}/customFields"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = create_custom_field_instances_dto

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

        
        return CustomFieldInstancesDto(**r.json())
        


    async def create_project_from_template_v2(
        self,
        create_project_from_template_v2_dto: CreateProjectFromTemplateV2Dto,
        template_uid: str,
        phrase_token: Optional[str] = None,
) -> AbstractProjectDtoV2:
        """
        Operation id: createProjectFromTemplateV2
        Create project from template
        
        :param create_project_from_template_v2_dto: CreateProjectFromTemplateV2Dto (required), body. 
        :param template_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AbstractProjectDtoV2
        """
        endpoint = f"/api2/v2/projects/applyTemplate/{template_uid}"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = create_project_from_template_v2_dto

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

        
        return AbstractProjectDtoV2(**r.json())
        


    async def create_project_from_template_v2_async(
        self,
        create_project_from_template_async_v2_dto: CreateProjectFromTemplateAsyncV2Dto,
        template_uid: str,
        phrase_token: Optional[str] = None,
) -> AsyncRequestWrapperV2Dto:
        """
        Operation id: createProjectFromTemplateV2Async
        Create project from template (async)
        
        :param create_project_from_template_async_v2_dto: CreateProjectFromTemplateAsyncV2Dto (required), body. 
        :param template_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AsyncRequestWrapperV2Dto
        """
        endpoint = f"/api2/v2/projects/applyTemplate/async/{template_uid}"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = create_project_from_template_async_v2_dto

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
        


    async def create_project_template(
        self,
        project_template_create_action_dto: ProjectTemplateCreateActionDto,
        phrase_token: Optional[str] = None,
) -> ProjectTemplate:
        """
        Operation id: createProjectTemplate
        Create project template
        
        :param project_template_create_action_dto: ProjectTemplateCreateActionDto (required), body. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProjectTemplate
        """
        endpoint = f"/api2/v1/projectTemplates"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = project_template_create_action_dto

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

        
        return ProjectTemplate(**r.json())
        


    async def delete_custom_field_of_project_template(
        self,
        field_instance_uid: str,
        project_template_uid: str,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: deleteCustomFieldOfProjectTemplate
        Delete custom field of project template
        
        :param field_instance_uid: str (required), path. 
        :param project_template_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/projectTemplates/{project_template_uid}/customFields/{field_instance_uid}"
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
        


    async def delete_project_template(
        self,
        project_template_uid: str,
        phrase_token: Optional[str] = None,
) -> None:
        """
        Operation id: deleteProjectTemplate
        Delete project template
        
        :param project_template_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: None
        """
        endpoint = f"/api2/v1/projectTemplates/{project_template_uid}"
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
        


    async def edit_custom_field_on_project_template(
        self,
        update_custom_field_instance_dto: UpdateCustomFieldInstanceDto,
        field_instance_uid: str,
        project_template_uid: str,
        phrase_token: Optional[str] = None,
) -> CustomFieldInstanceDto:
        """
        Operation id: editCustomFieldOnProjectTemplate
        Edit custom field of project template
        
        :param update_custom_field_instance_dto: UpdateCustomFieldInstanceDto (required), body. 
        :param field_instance_uid: str (required), path. 
        :param project_template_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: CustomFieldInstanceDto
        """
        endpoint = f"/api2/v1/projectTemplates/{project_template_uid}/customFields/{field_instance_uid}"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = update_custom_field_instance_dto

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

        
        return CustomFieldInstanceDto(**r.json())
        


    async def edit_custom_fields_on_project_template(
        self,
        update_custom_field_instances_dto: UpdateCustomFieldInstancesDto,
        project_template_uid: str,
        phrase_token: Optional[str] = None,
) -> CustomFieldInstancesDto:
        """
        Operation id: editCustomFieldsOnProjectTemplate
        Edit custom fields of the project template (batch)
        
        :param update_custom_field_instances_dto: UpdateCustomFieldInstancesDto (required), body. 
        :param project_template_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: CustomFieldInstancesDto
        """
        endpoint = f"/api2/v1/projectTemplates/{project_template_uid}/customFields"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = update_custom_field_instances_dto

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

        
        return CustomFieldInstancesDto(**r.json())
        


    async def edit_project_template(
        self,
        project_template_edit_dto: ProjectTemplateEditDto,
        project_template_uid: str,
        phrase_token: Optional[str] = None,
) -> ProjectTemplate:
        """
        Operation id: editProjectTemplate
        Edit project template
        
        :param project_template_edit_dto: ProjectTemplateEditDto (required), body. 
        :param project_template_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProjectTemplate
        """
        endpoint = f"/api2/v1/projectTemplates/{project_template_uid}"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = project_template_edit_dto

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

        
        return ProjectTemplate(**r.json())
        


    async def edit_project_template_access_settings(
        self,
        edit_project_security_settings_dto_v2: EditProjectSecuritySettingsDtoV2,
        project_template_uid: str,
        phrase_token: Optional[str] = None,
) -> ProjectSecuritySettingsDtoV2:
        """
        Operation id: editProjectTemplateAccessSettings
        Edit project template access and security settings
        
        :param edit_project_security_settings_dto_v2: EditProjectSecuritySettingsDtoV2 (required), body. 
        :param project_template_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProjectSecuritySettingsDtoV2
        """
        endpoint = f"/api2/v1/projectTemplates/{project_template_uid}/accessSettings"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = edit_project_security_settings_dto_v2

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

        
        return ProjectSecuritySettingsDtoV2(**r.json())
        


    async def edit_project_template_import_settings(
        self,
        file_import_settings_create_dto: FileImportSettingsCreateDto,
        project_template_uid: str,
        phrase_token: Optional[str] = None,
) -> FileImportSettingsDto:
        """
        Operation id: editProjectTemplateImportSettings
        Edit project template import settings
        
        :param file_import_settings_create_dto: FileImportSettingsCreateDto (required), body. 
        :param project_template_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: FileImportSettingsDto
        """
        endpoint = f"/api2/v1/projectTemplates/{project_template_uid}/importSettings"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = file_import_settings_create_dto

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

        
        return FileImportSettingsDto(**r.json())
        


    async def edit_project_template_v2(
        self,
        project_template_edit_v2_dto: ProjectTemplateEditV2Dto,
        project_template_uid: str,
        phrase_token: Optional[str] = None,
) -> ProjectTemplate:
        """
        Operation id: editProjectTemplateV2
        Edit project template
        
        :param project_template_edit_v2_dto: ProjectTemplateEditV2Dto (required), body. 
        :param project_template_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProjectTemplate
        """
        endpoint = f"/api2/v2/projectTemplates/{project_template_uid}"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = project_template_edit_v2_dto

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

        
        return ProjectTemplate(**r.json())
        


    async def get_analyse_settings_for_project_template(
        self,
        project_template_uid: str,
        phrase_token: Optional[str] = None,
) -> AbstractAnalyseSettingsDto:
        """
        Operation id: getAnalyseSettingsForProjectTemplate
        Get analyse settings
        
        :param project_template_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AbstractAnalyseSettingsDto
        """
        endpoint = f"/api2/v1/projectTemplates/{project_template_uid}/analyseSettings"
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

        
        return AbstractAnalyseSettingsDto(**r.json())
        


    async def get_custom_field_of_project_template(
        self,
        field_instance_uid: str,
        project_template_uid: str,
        phrase_token: Optional[str] = None,
) -> CustomFieldInstanceDto:
        """
        Operation id: getCustomFieldOfProjectTemplate
        Get custom field of project template
        
        :param field_instance_uid: str (required), path. 
        :param project_template_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: CustomFieldInstanceDto
        """
        endpoint = f"/api2/v1/projectTemplates/{project_template_uid}/customFields/{field_instance_uid}"
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

        
        return CustomFieldInstanceDto(**r.json())
        


    async def get_custom_fields_page_of_project_template(
        self,
        project_template_uid: str,
        created_by: Optional[List[str]] = None,
        modified_by: Optional[List[str]] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 20,
        sort_field: Optional[str] = None,
        sort_trend: Optional[str] = "ASC",
        phrase_token: Optional[str] = None,
) -> PageDtoCustomFieldInstanceDto:
        """
        Operation id: getCustomFieldsPageOfProjectTemplate
        Get custom fields of project template (page)
        
        :param project_template_uid: str (required), path. 
        :param created_by: Optional[List[str]] = None (optional), query. Filter by webhook creators UIDs.
        :param modified_by: Optional[List[str]] = None (optional), query. Filter by webhook updaters UIDs.
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 20 (optional), query. Page size, accepts values between 1 and 50, default 20.
        :param sort_field: Optional[str] = None (optional), query. Sort by this field.
        :param sort_trend: Optional[str] = "ASC" (optional), query. Sort direction.
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoCustomFieldInstanceDto
        """
        endpoint = f"/api2/v1/projectTemplates/{project_template_uid}/customFields"
        params = {
            "pageNumber": page_number,
            "pageSize": page_size,
            "createdBy": created_by,
            "modifiedBy": modified_by,
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

        
        return PageDtoCustomFieldInstanceDto(**r.json())
        


    async def get_import_settings_for_project_template(
        self,
        project_template_uid: str,
        phrase_token: Optional[str] = None,
) -> FileImportSettingsDto:
        """
        Operation id: getImportSettingsForProjectTemplate
        Get import settings
        
        :param project_template_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: FileImportSettingsDto
        """
        endpoint = f"/api2/v1/projectTemplates/{project_template_uid}/importSettings"
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

        
        return FileImportSettingsDto(**r.json())
        


    async def get_machine_translate_settings_for_project_template(
        self,
        project_template_uid: str,
        phrase_token: Optional[str] = None,
) -> MTSettingsPerLanguageListDto:
        """
        Operation id: getMachineTranslateSettingsForProjectTemplate
        Get project template machine translate settings
        
        :param project_template_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: MTSettingsPerLanguageListDto
        """
        endpoint = f"/api2/v1/projectTemplates/{project_template_uid}/mtSettings"
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

        
        return MTSettingsPerLanguageListDto(**r.json())
        


    async def get_project_template(
        self,
        project_template_uid: str,
        phrase_token: Optional[str] = None,
) -> ProjectTemplate:
        """
        Operation id: getProjectTemplate
        Get project template
        Note: importSettings in response is deprecated and will be always null
        :param project_template_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProjectTemplate
        """
        endpoint = f"/api2/v1/projectTemplates/{project_template_uid}"
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

        
        return ProjectTemplate(**r.json())
        


    async def get_project_template_access_settings(
        self,
        project_template_uid: str,
        phrase_token: Optional[str] = None,
) -> ProjectSecuritySettingsDtoV2:
        """
        Operation id: getProjectTemplateAccessSettings
        Get project template access and security settings
        
        :param project_template_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProjectSecuritySettingsDtoV2
        """
        endpoint = f"/api2/v1/projectTemplates/{project_template_uid}/accessSettings"
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

        
        return ProjectSecuritySettingsDtoV2(**r.json())
        


    async def get_project_template_pre_translate_settings_v4(
        self,
        project_template_uid: str,
        phrase_token: Optional[str] = None,
) -> PreTranslateSettingsV4Dto:
        """
        Operation id: getProjectTemplatePreTranslateSettingsV4
        Get project template pre-translate settings
        
        :param project_template_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PreTranslateSettingsV4Dto
        """
        endpoint = f"/api2/v4/projectTemplates/{project_template_uid}/preTranslateSettings"
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

        
        return PreTranslateSettingsV4Dto(**r.json())
        


    async def get_project_template_qa_settings(
        self,
        project_template_uid: str,
        phrase_token: Optional[str] = None,
) -> QASettingsDtoV2:
        """
        Operation id: getProjectTemplateQASettings
        Get quality assurance settings
        
        :param project_template_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: QASettingsDtoV2
        """
        endpoint = f"/api2/v1/projectTemplates/{project_template_uid}/qaSettings"
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

        
        return QASettingsDtoV2(**r.json())
        


    async def get_project_template_term_bases(
        self,
        project_template_uid: str,
        phrase_token: Optional[str] = None,
) -> ProjectTemplateTermBaseListDto:
        """
        Operation id: getProjectTemplateTermBases
        Get term bases
        
        :param project_template_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProjectTemplateTermBaseListDto
        """
        endpoint = f"/api2/v1/projectTemplates/{project_template_uid}/termBases"
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

        
        return ProjectTemplateTermBaseListDto(**r.json())
        


    async def get_project_template_trans_memories_2(
        self,
        project_template_uid: str,
        target_lang: Optional[str] = None,
        wf_step_uid: Optional[str] = None,
        phrase_token: Optional[str] = None,
) -> ProjectTemplateTransMemoryListDtoV3:
        """
        Operation id: getProjectTemplateTransMemories_2
        Get translation memories
        
        :param project_template_uid: str (required), path. 
        :param target_lang: Optional[str] = None (optional), query. Filter project translation memories by target language.
        :param wf_step_uid: Optional[str] = None (optional), query. Filter project translation memories by workflow step.
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProjectTemplateTransMemoryListDtoV3
        """
        endpoint = f"/api2/v3/projectTemplates/{project_template_uid}/transMemories"
        params = {
            "targetLang": target_lang,
            "wfStepUid": wf_step_uid
            
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

        
        return ProjectTemplateTransMemoryListDtoV3(**r.json())
        


    async def get_project_templates(
        self,
        business_unit_name: Optional[str] = None,
        client_id: Optional[int] = None,
        client_name: Optional[str] = None,
        cost_center_id: Optional[int] = None,
        cost_center_name: Optional[str] = None,
        created_by_uid: Optional[str] = None,
        created_in_last_hours: Optional[int] = None,
        direction: Optional[str] = "desc",
        domain_name: Optional[str] = None,
        name: Optional[str] = None,
        owner_uid: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        sort: Optional[str] = "dateCreated",
        source_langs: Optional[List[str]] = None,
        sub_domain_name: Optional[str] = None,
        target_langs: Optional[List[str]] = None,
        phrase_token: Optional[str] = None,
) -> PageDtoProjectTemplateReference:
        """
        Operation id: getProjectTemplates
        List project templates
        
API call to list [project templates](https://support.phrase.com/hc/en-us/articles/5709647439772-Project-Templates-TMS-).

Use the query parameters below to refine your search criteria for project templates:

- **name** - The full project template name or a portion of it. For example, using `name=GUI` or `name=02`
will locate project templates named `GUI02`.
- **clientId** - The client's ID within the system, not interchangeable with its UID.
- **clientName** - The complete or partial name of the client. For instance, using `clientName=GUI` or `clientName=02`
will find project templates associated with the client `GUI02`.
- **ownerUid** - The user UID who owns the project template within the system, interchangeable with its ID.
- **domainName** - The complete or partial name of the domain. Using `domainName=GUI` or `domainName=02` will find
project templates associated with the domain `GUI02`.
- **subDomainName** - The complete or partial name of the subdomain. For instance, using `subDomainName=GUI` or
`subDomainName=02` will locate project templates linked to the subdomain `GUI02`.
- **costCenterId** - The cost center's ID within the system, not interchangeable with its UID.
- **costCenterName** - The complete or partial name of the cost center. For example, using `costCenterName=GUI` or
`costCenterName=02` will find project templates associated with the cost center `GUI02`.
- **businessUnitName** - The complete or partial name of the business unit. For instance, using `businessUnitName=GUI`
or `businessUnitName=02` will locate project templates linked to the business unit `GUI02`.
- **sort** - Determines if the resulting list of project templates should be sorted by their names or the date they
were created. This field supports either `dateCreated` or `templateName` as values.
- **direction** - Indicates the sorting order for the resulting list by using either `asc` (ascending) or `desc`
(descending) values.
- **pageNumber** - Indicates the desired page number (zero-based) to retrieve. The total number of pages is returned in
the `totalPages` field within each response.
- **pageSize** - Indicates the page size, affecting the `totalPages` retrieved in each response and potentially
impacting the number of iterations needed to obtain all project templates.

        :param business_unit_name: Optional[str] = None (optional), query. 
        :param client_id: Optional[int] = None (optional), query. 
        :param client_name: Optional[str] = None (optional), query. 
        :param cost_center_id: Optional[int] = None (optional), query. 
        :param cost_center_name: Optional[str] = None (optional), query. 
        :param created_by_uid: Optional[str] = None (optional), query. 
        :param created_in_last_hours: Optional[int] = None (optional), query. 
        :param direction: Optional[str] = "desc" (optional), query. 
        :param domain_name: Optional[str] = None (optional), query. 
        :param name: Optional[str] = None (optional), query. 
        :param owner_uid: Optional[str] = None (optional), query. 
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param sort: Optional[str] = "dateCreated" (optional), query. 
        :param source_langs: Optional[List[str]] = None (optional), query. 
        :param sub_domain_name: Optional[str] = None (optional), query. 
        :param target_langs: Optional[List[str]] = None (optional), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoProjectTemplateReference
        """
        endpoint = f"/api2/v1/projectTemplates"
        params = {
            "name": name,
            "clientId": client_id,
            "clientName": client_name,
            "ownerUid": owner_uid,
            "createdByUid": created_by_uid,
            "domainName": domain_name,
            "subDomainName": sub_domain_name,
            "costCenterId": cost_center_id,
            "costCenterName": cost_center_name,
            "businessUnitName": business_unit_name,
            "sourceLangs": source_langs,
            "targetLangs": target_langs,
            "createdInLastHours": created_in_last_hours,
            "sort": sort,
            "direction": direction,
            "pageNumber": page_number,
            "pageSize": page_size
            
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

        
        return PageDtoProjectTemplateReference(**r.json())
        


    async def relevant_trans_memories_for_project_template(
        self,
        project_template_uid: str,
        client_name: Optional[str] = None,
        domain_name: Optional[str] = None,
        name: Optional[str] = None,
        page_number: Optional[int] = 0,
        page_size: Optional[int] = 50,
        strict_lang_matching: Optional[bool] = False,
        sub_domain_name: Optional[str] = None,
        target_langs: Optional[List[str]] = None,
        phrase_token: Optional[str] = None,
) -> PageDtoTransMemoryDto:
        """
        Operation id: relevantTransMemoriesForProjectTemplate
        List project template relevant translation memories
        
        :param project_template_uid: str (required), path. 
        :param client_name: Optional[str] = None (optional), query. 
        :param domain_name: Optional[str] = None (optional), query. 
        :param name: Optional[str] = None (optional), query. 
        :param page_number: Optional[int] = 0 (optional), query. Page number, starting with 0, default 0.
        :param page_size: Optional[int] = 50 (optional), query. Page size, accepts values between 1 and 50, default 50.
        :param strict_lang_matching: Optional[bool] = False (optional), query. 
        :param sub_domain_name: Optional[str] = None (optional), query. 
        :param target_langs: Optional[List[str]] = None (optional), query. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PageDtoTransMemoryDto
        """
        endpoint = f"/api2/v1/projectTemplates/{project_template_uid}/transMemories/relevant"
        params = {
            "name": name,
            "domainName": domain_name,
            "clientName": client_name,
            "subDomainName": sub_domain_name,
            "targetLangs": target_langs,
            "strictLangMatching": strict_lang_matching,
            "pageNumber": page_number,
            "pageSize": page_size
            
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

        
        return PageDtoTransMemoryDto(**r.json())
        


    async def set_project_template_qa_settings(
        self,
        edit_qa_settings_dto_v2: EditQASettingsDtoV2,
        project_template_uid: str,
        phrase_token: Optional[str] = None,
) -> QASettingsDtoV2:
        """
        Operation id: setProjectTemplateQASettings
        Edit quality assurance settings
        
        :param edit_qa_settings_dto_v2: EditQASettingsDtoV2 (required), body. 
        :param project_template_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: QASettingsDtoV2
        """
        endpoint = f"/api2/v1/projectTemplates/{project_template_uid}/qaSettings"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = edit_qa_settings_dto_v2

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

        
        return QASettingsDtoV2(**r.json())
        


    async def set_project_template_term_bases(
        self,
        set_project_template_term_base_dto: SetProjectTemplateTermBaseDto,
        project_template_uid: str,
        phrase_token: Optional[str] = None,
) -> ProjectTemplateTermBaseListDto:
        """
        Operation id: setProjectTemplateTermBases
        Edit term bases in project template
        
        :param set_project_template_term_base_dto: SetProjectTemplateTermBaseDto (required), body. 
        :param project_template_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProjectTemplateTermBaseListDto
        """
        endpoint = f"/api2/v1/projectTemplates/{project_template_uid}/termBases"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = set_project_template_term_base_dto

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

        
        return ProjectTemplateTermBaseListDto(**r.json())
        


    async def set_project_template_trans_memories_v2(
        self,
        set_project_template_trans_memories_v2_dto: SetProjectTemplateTransMemoriesV2Dto,
        project_template_uid: str,
        phrase_token: Optional[str] = None,
) -> ProjectTemplateTransMemoryListV2Dto:
        """
        Operation id: setProjectTemplateTransMemoriesV2
        Edit translation memories
        If user wants to edit “All target languages” or "All workflow steps”, 
                       but there are already varied TM settings for individual languages or steps, 
                       then the user risks to overwrite these individual choices.
        :param set_project_template_trans_memories_v2_dto: SetProjectTemplateTransMemoriesV2Dto (required), body. 
        :param project_template_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: ProjectTemplateTransMemoryListV2Dto
        """
        endpoint = f"/api2/v2/projectTemplates/{project_template_uid}/transMemories"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = set_project_template_trans_memories_v2_dto

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

        
        return ProjectTemplateTransMemoryListV2Dto(**r.json())
        


    async def update_analyse_settings_for_project_template(
        self,
        edit_analyse_settings_dto: EditAnalyseSettingsDto,
        project_template_uid: str,
        phrase_token: Optional[str] = None,
) -> AbstractAnalyseSettingsDto:
        """
        Operation id: updateAnalyseSettingsForProjectTemplate
        Edit analyse settings
        
        :param edit_analyse_settings_dto: EditAnalyseSettingsDto (required), body. 
        :param project_template_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: AbstractAnalyseSettingsDto
        """
        endpoint = f"/api2/v1/projectTemplates/{project_template_uid}/analyseSettings"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = edit_analyse_settings_dto

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

        
        return AbstractAnalyseSettingsDto(**r.json())
        


    async def update_project_template_pre_translate_settings_v4(
        self,
        pre_translate_settings_v4_dto: PreTranslateSettingsV4Dto,
        project_template_uid: str,
        phrase_token: Optional[str] = None,
) -> PreTranslateSettingsV4Dto:
        """
        Operation id: updateProjectTemplatePreTranslateSettingsV4
        Update project template pre-translate settings
        
        :param pre_translate_settings_v4_dto: PreTranslateSettingsV4Dto (required), body. 
        :param project_template_uid: str (required), path. 
        
        :param phrase_token: string (optional) - if not supplied, client will look for token from init

        :return: PreTranslateSettingsV4Dto
        """
        endpoint = f"/api2/v4/projectTemplates/{project_template_uid}/preTranslateSettings"
        params = {
            
        }
        headers = {
            
        }

        content = None

        files = None

        payload = pre_translate_settings_v4_dto

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

        
        return PreTranslateSettingsV4Dto(**r.json())
        



if __name__ == '__main__':
    print("This module is not intended to be run directly.")