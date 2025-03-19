from .v_1_web_read import (
    web_reader as _web_reader,
    web_reader_async as _web_reader_async,
)
from ..models.default_error import DefaultError
from ..models.web_reader_request import WebReaderRequest
from ..models.web_reader_response import WebReaderResponse
from typing import cast
from .v_2_web_search import (
    web_search as _web_search,
    web_search_async as _web_search_async,
)
from ..models.web_search_request import WebSearchRequest
from ..models.web_search_response import WebSearchResponse
from .signature_similarity import (
    signature_similarity as _signature_similarity,
    signature_similarity_async as _signature_similarity_async,
)
from ..models.signature_similarity_response import SignatureSimilarityResponse
from .summarise import (
    summarise_text_new as _summarise_text_new,
    summarise_text_new_async as _summarise_text_new_async,
)
from ..models.summarise_text_new_request import SummariseTextNewRequest
from ..models.summarise_text_new_response import SummariseTextNewResponse
from .v1chatcompletion import (
    image_analysis as _image_analysis,
    image_analysis_async as _image_analysis_async,
)
from ..models.image_analysis_request import ImageAnalysisRequest
from ..models.image_analysis_response import ImageAnalysisResponse
from .translate import (
    translate as _translate,
    translate_async as _translate_async,
)
from ..models.translate_request import TranslateRequest
from ..models.translate_response import TranslateResponse
from .semantic_similarity import (
    semantic_similarity as _semantic_similarity,
    semantic_similarity_async as _semantic_similarity_async,
)
from ..models.semantic_similarity_request import SemanticSimilarityRequest
from ..models.semantic_similarity_response import SemanticSimilarityResponse
from .ner import (
    named_entity_recognition as _named_entity_recognition,
    named_entity_recognition_async as _named_entity_recognition_async,
)
from ..models.named_entity_recognition_request import NamedEntityRecognitionRequest
from ..models.named_entity_recognition_response import NamedEntityRecognitionResponse
from .generate_email import (
    generate_email as _generate_email,
    generate_email_async as _generate_email_async,
)
from ..models.generate_email_request import GenerateEmailRequest
from ..models.generate_email_response import GenerateEmailResponse
from .v1sentiment_analysis import (
    sentiment_analysis as _sentiment_analysis,
    sentiment_analysis_async as _sentiment_analysis_async,
)
from ..models.sentiment_analysis_request import SentimentAnalysisRequest
from ..models.sentiment_analysis_response import SentimentAnalysisResponse
from .pii_detection import (
    pii_detection as _pii_detection,
    pii_detection_async as _pii_detection_async,
)
from ..models.pii_detection_request import PIIDetectionRequest
from ..models.pii_detection_response import PIIDetectionResponse
from .rewrite import (
    rewrite as _rewrite,
    rewrite_async as _rewrite_async,
)
from ..models.rewrite_request import RewriteRequest
from ..models.rewrite_response import RewriteResponse
from .v1reformat import (
    reformat as _reformat,
    reformat_async as _reformat_async,
)
from ..models.reformat_request import ReformatRequest
from ..models.reformat_response import ReformatResponse
from .v1object_detection import (
    object_detection as _object_detection,
    object_detection_async as _object_detection_async,
)
from ..models.object_detection_request import ObjectDetectionRequest
from ..models.object_detection_response import ObjectDetectionResponse
from .image_comparison import (
    image_comparison as _image_comparison,
    image_comparison_async as _image_comparison_async,
)
from ..models.image_comparison_request import ImageComparisonRequest
from ..models.image_comparison_response import ImageComparisonResponse
from .language_detection import (
    language_detection as _language_detection,
    language_detection_async as _language_detection_async,
)
from ..models.language_detection_request import LanguageDetectionRequest
from ..models.language_detection_response import LanguageDetectionResponse
from .classification import (
    image_classification as _image_classification,
    image_classification_async as _image_classification_async,
)
from ..models.image_classification_request import ImageClassificationRequest
from ..models.image_classification_response import ImageClassificationResponse
from .v_1_web_summary import (
    web_summary as _web_summary,
    web_summary_async as _web_summary_async,
)
from ..models.web_summary_request import WebSummaryRequest
from ..models.web_summary_response import WebSummaryResponse
from .v_2_generate_chat_completion import (
    content_generation as _content_generation,
    content_generation_async as _content_generation_async,
)
from ..models.content_generation_request import ContentGenerationRequest
from ..models.content_generation_response import ContentGenerationResponse
from .categorize import (
    categorize as _categorize,
    categorize_async as _categorize_async,
)
from ..models.categorize_request import CategorizeRequest
from ..models.categorize_response import CategorizeResponse

from pydantic import Field
from typing import Any, Optional, Union

from ..client import Client
import httpx


class UiPathAirdk:
    def __init__(self, *, instance_id: str, client: httpx.Client):
        base_url = str(client.base_url).rstrip("/")
        new_headers = {
            k: v for k, v in client.headers.items() if k not in ["content-type"]
        }
        new_client = httpx.Client(
            base_url=base_url + f"/elements_/v3/element/instances/{instance_id}",
            headers=new_headers,
            timeout=100,
        )
        new_client_async = httpx.AsyncClient(
            base_url=base_url + f"/elements_/v3/element/instances/{instance_id}",
            headers=new_headers,
            timeout=100,
        )
        self.client = (
            Client(
                base_url="",  # this will be overridden by the base_url in the Client constructor
            )
            .set_httpx_client(new_client)
            .set_async_httpx_client(new_client_async)
        )

    def web_reader(
        self,
        *,
        body: WebReaderRequest,
    ) -> Optional[Union[DefaultError, WebReaderResponse]]:
        return _web_reader(
            client=self.client,
            body=body,
        )

    async def web_reader_async(
        self,
        *,
        body: WebReaderRequest,
    ) -> Optional[Union[DefaultError, WebReaderResponse]]:
        return await _web_reader_async(
            client=self.client,
            body=body,
        )

    def web_search(
        self,
        *,
        body: WebSearchRequest,
    ) -> Optional[Union[DefaultError, WebSearchResponse]]:
        return _web_search(
            client=self.client,
            body=body,
        )

    async def web_search_async(
        self,
        *,
        body: WebSearchRequest,
    ) -> Optional[Union[DefaultError, WebSearchResponse]]:
        return await _web_search_async(
            client=self.client,
            body=body,
        )

    def signature_similarity(
        self,
    ) -> Optional[Union[DefaultError, SignatureSimilarityResponse]]:
        return _signature_similarity(
            client=self.client,
        )

    async def signature_similarity_async(
        self,
    ) -> Optional[Union[DefaultError, SignatureSimilarityResponse]]:
        return await _signature_similarity_async(
            client=self.client,
        )

    def summarise_text_new(
        self,
        *,
        body: SummariseTextNewRequest,
    ) -> Optional[Union[DefaultError, SummariseTextNewResponse]]:
        return _summarise_text_new(
            client=self.client,
            body=body,
        )

    async def summarise_text_new_async(
        self,
        *,
        body: SummariseTextNewRequest,
    ) -> Optional[Union[DefaultError, SummariseTextNewResponse]]:
        return await _summarise_text_new_async(
            client=self.client,
            body=body,
        )

    def image_analysis(
        self,
        *,
        body: ImageAnalysisRequest,
        model_name: str,
        model_name_lookup: Any,
    ) -> Optional[Union[DefaultError, ImageAnalysisResponse]]:
        return _image_analysis(
            client=self.client,
            body=body,
            model_name=model_name,
            model_name_lookup=model_name_lookup,
        )

    async def image_analysis_async(
        self,
        *,
        body: ImageAnalysisRequest,
        model_name: str,
        model_name_lookup: Any,
    ) -> Optional[Union[DefaultError, ImageAnalysisResponse]]:
        return await _image_analysis_async(
            client=self.client,
            body=body,
            model_name=model_name,
            model_name_lookup=model_name_lookup,
        )

    def translate(
        self,
        *,
        body: TranslateRequest,
    ) -> Optional[Union[DefaultError, TranslateResponse]]:
        return _translate(
            client=self.client,
            body=body,
        )

    async def translate_async(
        self,
        *,
        body: TranslateRequest,
    ) -> Optional[Union[DefaultError, TranslateResponse]]:
        return await _translate_async(
            client=self.client,
            body=body,
        )

    def semantic_similarity(
        self,
        *,
        body: SemanticSimilarityRequest,
    ) -> Optional[Union[DefaultError, SemanticSimilarityResponse]]:
        return _semantic_similarity(
            client=self.client,
            body=body,
        )

    async def semantic_similarity_async(
        self,
        *,
        body: SemanticSimilarityRequest,
    ) -> Optional[Union[DefaultError, SemanticSimilarityResponse]]:
        return await _semantic_similarity_async(
            client=self.client,
            body=body,
        )

    def named_entity_recognition(
        self,
        *,
        body: NamedEntityRecognitionRequest,
    ) -> Optional[Union[DefaultError, NamedEntityRecognitionResponse]]:
        return _named_entity_recognition(
            client=self.client,
            body=body,
        )

    async def named_entity_recognition_async(
        self,
        *,
        body: NamedEntityRecognitionRequest,
    ) -> Optional[Union[DefaultError, NamedEntityRecognitionResponse]]:
        return await _named_entity_recognition_async(
            client=self.client,
            body=body,
        )

    def generate_email(
        self,
        *,
        body: GenerateEmailRequest,
    ) -> Optional[Union[DefaultError, GenerateEmailResponse]]:
        return _generate_email(
            client=self.client,
            body=body,
        )

    async def generate_email_async(
        self,
        *,
        body: GenerateEmailRequest,
    ) -> Optional[Union[DefaultError, GenerateEmailResponse]]:
        return await _generate_email_async(
            client=self.client,
            body=body,
        )

    def sentiment_analysis(
        self,
        *,
        body: SentimentAnalysisRequest,
    ) -> Optional[Union[DefaultError, SentimentAnalysisResponse]]:
        return _sentiment_analysis(
            client=self.client,
            body=body,
        )

    async def sentiment_analysis_async(
        self,
        *,
        body: SentimentAnalysisRequest,
    ) -> Optional[Union[DefaultError, SentimentAnalysisResponse]]:
        return await _sentiment_analysis_async(
            client=self.client,
            body=body,
        )

    def pii_detection(
        self,
        *,
        body: PIIDetectionRequest,
    ) -> Optional[Union[DefaultError, PIIDetectionResponse]]:
        return _pii_detection(
            client=self.client,
            body=body,
        )

    async def pii_detection_async(
        self,
        *,
        body: PIIDetectionRequest,
    ) -> Optional[Union[DefaultError, PIIDetectionResponse]]:
        return await _pii_detection_async(
            client=self.client,
            body=body,
        )

    def rewrite(
        self,
        *,
        body: RewriteRequest,
    ) -> Optional[Union[DefaultError, RewriteResponse]]:
        return _rewrite(
            client=self.client,
            body=body,
        )

    async def rewrite_async(
        self,
        *,
        body: RewriteRequest,
    ) -> Optional[Union[DefaultError, RewriteResponse]]:
        return await _rewrite_async(
            client=self.client,
            body=body,
        )

    def reformat(
        self,
        *,
        body: ReformatRequest,
    ) -> Optional[Union[DefaultError, ReformatResponse]]:
        return _reformat(
            client=self.client,
            body=body,
        )

    async def reformat_async(
        self,
        *,
        body: ReformatRequest,
    ) -> Optional[Union[DefaultError, ReformatResponse]]:
        return await _reformat_async(
            client=self.client,
            body=body,
        )

    def object_detection(
        self,
        *,
        body: ObjectDetectionRequest,
        model_name: Optional[str] = "gpt-4o-2024-05-13",
        model_name_lookup: Any,
    ) -> Optional[Union[DefaultError, ObjectDetectionResponse]]:
        return _object_detection(
            client=self.client,
            body=body,
            model_name=model_name,
            model_name_lookup=model_name_lookup,
        )

    async def object_detection_async(
        self,
        *,
        body: ObjectDetectionRequest,
        model_name: Optional[str] = "gpt-4o-2024-05-13",
        model_name_lookup: Any,
    ) -> Optional[Union[DefaultError, ObjectDetectionResponse]]:
        return await _object_detection_async(
            client=self.client,
            body=body,
            model_name=model_name,
            model_name_lookup=model_name_lookup,
        )

    def image_comparison(
        self,
        *,
        body: ImageComparisonRequest,
    ) -> Optional[Union[DefaultError, ImageComparisonResponse]]:
        return _image_comparison(
            client=self.client,
            body=body,
        )

    async def image_comparison_async(
        self,
        *,
        body: ImageComparisonRequest,
    ) -> Optional[Union[DefaultError, ImageComparisonResponse]]:
        return await _image_comparison_async(
            client=self.client,
            body=body,
        )

    def language_detection(
        self,
        *,
        body: LanguageDetectionRequest,
    ) -> Optional[Union[DefaultError, LanguageDetectionResponse]]:
        return _language_detection(
            client=self.client,
            body=body,
        )

    async def language_detection_async(
        self,
        *,
        body: LanguageDetectionRequest,
    ) -> Optional[Union[DefaultError, LanguageDetectionResponse]]:
        return await _language_detection_async(
            client=self.client,
            body=body,
        )

    def image_classification(
        self,
        *,
        body: ImageClassificationRequest,
        model_name: str,
        model_name_lookup: Any,
    ) -> Optional[Union[DefaultError, ImageClassificationResponse]]:
        return _image_classification(
            client=self.client,
            body=body,
            model_name=model_name,
            model_name_lookup=model_name_lookup,
        )

    async def image_classification_async(
        self,
        *,
        body: ImageClassificationRequest,
        model_name: str,
        model_name_lookup: Any,
    ) -> Optional[Union[DefaultError, ImageClassificationResponse]]:
        return await _image_classification_async(
            client=self.client,
            body=body,
            model_name=model_name,
            model_name_lookup=model_name_lookup,
        )

    def web_summary(
        self,
        *,
        body: WebSummaryRequest,
    ) -> Optional[Union[DefaultError, WebSummaryResponse]]:
        return _web_summary(
            client=self.client,
            body=body,
        )

    async def web_summary_async(
        self,
        *,
        body: WebSummaryRequest,
    ) -> Optional[Union[DefaultError, WebSummaryResponse]]:
        return await _web_summary_async(
            client=self.client,
            body=body,
        )

    def content_generation(
        self,
        *,
        body: ContentGenerationRequest,
        model_name: str,
        model_name_lookup: Any,
        folder_key: Optional[str] = None,
        folder_key_lookup: Any,
    ) -> Optional[Union[ContentGenerationResponse, DefaultError]]:
        return _content_generation(
            client=self.client,
            body=body,
            model_name=model_name,
            model_name_lookup=model_name_lookup,
            folder_key=folder_key,
            folder_key_lookup=folder_key_lookup,
        )

    async def content_generation_async(
        self,
        *,
        body: ContentGenerationRequest,
        model_name: str,
        model_name_lookup: Any,
        folder_key: Optional[str] = None,
        folder_key_lookup: Any,
    ) -> Optional[Union[ContentGenerationResponse, DefaultError]]:
        return await _content_generation_async(
            client=self.client,
            body=body,
            model_name=model_name,
            model_name_lookup=model_name_lookup,
            folder_key=folder_key,
            folder_key_lookup=folder_key_lookup,
        )

    def categorize(
        self,
        *,
        body: CategorizeRequest,
    ) -> Optional[Union[CategorizeResponse, DefaultError]]:
        return _categorize(
            client=self.client,
            body=body,
        )

    async def categorize_async(
        self,
        *,
        body: CategorizeRequest,
    ) -> Optional[Union[CategorizeResponse, DefaultError]]:
        return await _categorize_async(
            client=self.client,
            body=body,
        )
