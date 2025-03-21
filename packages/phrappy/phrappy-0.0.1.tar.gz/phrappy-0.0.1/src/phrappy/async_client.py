import logging
from typing import Optional, TypeVar, Dict

import httpx
from httpx import HTTPStatusError
from httpx._types import RequestFiles
from pydantic import BaseModel

from .exceptions import PhrappyError
from .async_tags import (
    AdditionalWorkflowStepOperations,
    AnalysisOperations,
    AsyncRequestOperations,
    AuthenticationOperations,
    BilingualFileOperations,
    BusinessUnitOperations,
    BuyerOperations,
    ClientOperations,
    ConnectorOperations,
    CostCenterOperations,
    CustomFieldsOperations,
    CustomFileTypeOperations,
    DomainOperations,
    EmailTemplateOperations,
    FileOperations,
    GlossaryOperations,
    ImportsettingsOperations,
    ConversationsOperations,
    SupportedLanguagesOperations,
    LanguageQualityAssessmentOperations,
    QualityAssuranceOperations,
    MachineTranslationSettingsOperations,
    MachineTranslationOperations,
    MappingOperations,
    LanguageAIOperations,
    NetRateSchemeOperations,
    NotificationsOperations,
    PriceListOperations,
    ProjectTemplateOperations,
    TermBaseOperations,
    TranslationMemoryOperations,
    ProjectOperations,
    JobOperations,
    TranslationOperations,
    SegmentOperations,
    ProviderOperations,
    ProjectReferenceFileOperations,
    QuoteOperations,
    SCIMOperations,
    SegmentationRulesOperations,
    SpellCheckOperations,
    SubDomainOperations,
    UserOperations,
    WorkflowStepOperations,
    VendorOperations,
    WebhookOperations,
    XMLAssistantOperations,
    WorkflowchangesOperations
    
)


MEMSOURCE_BASE_URL = "https://cloud.memsource.com/web"

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class AsyncPhrappy:
    def __init__(self, token: Optional[str] = None):
        def _token_validation(token) -> str | None:
            if token and token.startswith("ApiToken "):
                return token
            elif token:
                return "ApiToken " + token
            else:
                return
        self.token = _token_validation(token)
        self.additional_workflow_step = AdditionalWorkflowStepOperations(self)
        self.analysis = AnalysisOperations(self)
        self.async_request = AsyncRequestOperations(self)
        self.authentication = AuthenticationOperations(self)
        self.bilingual_file = BilingualFileOperations(self)
        self.business_unit = BusinessUnitOperations(self)
        self.buyer = BuyerOperations(self)
        self.client = ClientOperations(self)
        self.connector = ConnectorOperations(self)
        self.cost_center = CostCenterOperations(self)
        self.custom_fields = CustomFieldsOperations(self)
        self.custom_file_type = CustomFileTypeOperations(self)
        self.domain = DomainOperations(self)
        self.email_template = EmailTemplateOperations(self)
        self.file = FileOperations(self)
        self.glossary = GlossaryOperations(self)
        self.importsettings = ImportsettingsOperations(self)
        self.conversations = ConversationsOperations(self)
        self.supported_languages = SupportedLanguagesOperations(self)
        self.language_quality_assessment = LanguageQualityAssessmentOperations(self)
        self.quality_assurance = QualityAssuranceOperations(self)
        self.machine_translation_settings = MachineTranslationSettingsOperations(self)
        self.machine_translation = MachineTranslationOperations(self)
        self.mapping = MappingOperations(self)
        self.language_ai = LanguageAIOperations(self)
        self.net_rate_scheme = NetRateSchemeOperations(self)
        self.notifications = NotificationsOperations(self)
        self.price_list = PriceListOperations(self)
        self.project_template = ProjectTemplateOperations(self)
        self.term_base = TermBaseOperations(self)
        self.translation_memory = TranslationMemoryOperations(self)
        self.project = ProjectOperations(self)
        self.job = JobOperations(self)
        self.translation = TranslationOperations(self)
        self.segment = SegmentOperations(self)
        self.provider = ProviderOperations(self)
        self.project_reference_file = ProjectReferenceFileOperations(self)
        self.quote = QuoteOperations(self)
        self.scim = SCIMOperations(self)
        self.segmentation_rules = SegmentationRulesOperations(self)
        self.spell_check = SpellCheckOperations(self)
        self.sub_domain = SubDomainOperations(self)
        self.user = UserOperations(self)
        self.workflow_step = WorkflowStepOperations(self)
        self.vendor = VendorOperations(self)
        self.webhook = WebhookOperations(self)
        self.xml_assistant = XMLAssistantOperations(self)
        self.workflowchanges = WorkflowchangesOperations(self)
        

    async def make_request(
        self,
        method: str,
        path: str,
        phrase_token: Optional[str] = None,
        params: Optional[dict] = None,
        payload: Optional[T | Dict] = None,
        files: Optional[RequestFiles] = None,
        headers: Optional[dict] = None,
        content: Optional[bytes] = None,
        timeout: float = 180.0
    ) -> httpx.Response:
        token = phrase_token or self.token

        url = f"{MEMSOURCE_BASE_URL}{path}"
        header = {}

        if token:
            header["Authorization"] = token
        if headers is not None:
            header.update(headers)

        if payload is not None and not isinstance(payload, dict):
            try:
                payload = payload.model_dump(exclude_unset=True)
            except Exception as e:
                logger.exception(f"Payload could not be cast as dict: {e}")
                raise Exception from e

        if params is not None:
            remove = []
            for k, v in params.items():
                if v is None:
                    remove.append(k)
            if remove:
                for k in remove:
                    params.pop(k)
        async with httpx.AsyncClient() as client:
            r = await client.request(
                method=method,
                url=url,
                headers=header,
                params=params,
                json=payload,
                files=files,
                content=content,
                timeout=timeout,
            )

        try:
            r.raise_for_status()
        except HTTPStatusError as exc:
            try:
                loaded_errors = r.json()
                error_code = loaded_errors.get("errorCode")
                error_detail = loaded_errors.get("errorDescription")
                msg = f"Call failed: {method=} {url=}, {r.request.content=}, {r.status_code=}, {error_code=}, {error_detail=}"
                raise PhrappyError(msg)
            except:
                logger.exception(f"Call failed: {r} // {url=} - {r.request.content=}")
                raise Exception from exc
        else:
            return r

    @classmethod
    async def from_creds(cls, username: str, password: str) -> 'Phrappy':
        pp = cls()
        login_dto = {"userName": username, "password": password}
        resp = await pp.authentication.login(login_dto)
        return cls(resp.token)
