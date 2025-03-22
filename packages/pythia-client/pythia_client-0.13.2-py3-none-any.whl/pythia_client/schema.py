from __future__ import annotations

import enum
from datetime import datetime
from typing import Any, Dict, List, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatRole(str, enum.Enum):
    """Enumeration representing the roles within a chat."""

    ASSISTANT = "assistant"
    USER = "user"
    SYSTEM = "system"
    TOOL = "tool"


class ChatMessage(BaseModel):
    content: str
    role: ChatRole
    name: str | None
    meta: Dict[str, Any]


class HaystackVersion(BaseModel):
    hs_version: str = Field(..., description="Haystack Version")


class Usage(BaseModel):
    prompt_tokens: int | None = Field(default=None, description="")
    completion_tokens: int | None = Field(default=None, description="")


class Meta(BaseModel):
    id: str = Field(..., description="")
    stop_sequence: str | None = Field(default=None, description="")
    model: str = Field(..., description="")
    usage: Usage = Field(..., description="")
    index: int | None = Field(default=None, description="")
    finish_reason: str | None = Field(default=None, description="")


class WriterModel(BaseModel):
    documents_written: int = Field(..., description="")


class FilterRequest(BaseModel):
    filters: Dict[str, Any] | None = Field(default_factory=dict, description="Filters", examples=[{
        "must": [
            {
                "key": "meta.pythia_document_category",
                "match": {
                    "value": "UMC"
                }
            }
        ]
    }])


class FilterDocStoreResponse(BaseModel):
    id: str
    content: str | None = Field(default=None, description="")
    dataframe: str | Any | None = Field(default=None, description="")
    blob: str | Any | None = Field(default=None, description="")
    meta: Dict[str, Any] = Field(default_factory=dict, description="")
    score: float | None = Field(default=None, description="")
    embedding: List[float] | None = Field(default=None, description="")


class DocumentQueryResponse(BaseModel):
    id: str = Field(..., description="")
    content: str = Field(..., description="")
    dataframe: str | Any | None = Field(default=None, description="")
    blob: str | Any | None = Field(default=None, description="")
    meta: Dict[str, Any] = Field(..., description="")
    score: float | None = Field(default=None, description="")
    embedding: List[float] | None = Field(default=None, description="")


class Answer(BaseModel):
    data: str = Field(..., description="")
    query: str = Field(..., description="")
    documents: List[DocumentQueryResponse] = Field(default_factory=list, description="")
    meta: Meta = Field(..., description="")


class AnswerBuilderModel(BaseModel):
    answers: List[Answer] = Field(..., description="")


class SearchParams(BaseModel):
    group_id: str | None = Field(default=None, description="")
    top_k: int | None = Field(default=30, description="Top_K")
    threshold: float | None = Field(default=0.1, description="threshold")
    system_prompt: str | None = Field(default=None, description="System Prompt",
                                      examples=["Answer the query based on the provided documents."])
    filters: Dict[str, Any] | None = Field(default_factory=dict, description="Filters", examples=[{
        "must": [
            {
                "key": "meta.pythia_document_category",
                "match": {
                    "value": "UMC"
                }
            }
        ]
    }])
    return_embedding: bool | None = Field(default=False, description="Return embedding of chunks")
    return_content: bool | None = Field(default=True, description="Return content of chunks")
    group_by: str | None = Field(default=None, description="")
    group_size: int | None = Field(default=None, description="")
    len_chat_history: int | None = Field(default=3, description="")


class QueryRequest(BaseModel):
    query: str = Field(..., description="", examples=["How to update my OXE ?"])
    chat_history: List[ChatMessage] | None = Field(default=None, description="", examples=[
        [{"content": "Hey how are you ?", "role": "user", "name": ""},
         {"content": "I'm great, how can I help you ?", "role": "assistant", "name": ""}]])
    params: SearchParams | None = Field(default_factory=SearchParams)
    thread_id: str | None = Field(default=None, description="Thread ID to associate the query with")
    user_id: str | None = Field(default=None, description="Optional ID to associate to the thread and query. If None it will be your group ID.")
    raw: bool | None = Field(default=False, description="If True, the chat will be processed by the raw chat pipeline.")


class QueryResponse(BaseModel):
    AnswerBuilder: AnswerBuilderModel = Field(..., description="")
    thread_id: str | None = Field(default=None, description="Thread ID to associate the query with")


class GetFileS3Reponse(BaseModel):
    url: str = Field(..., description="")


class DeleteDocResponse(BaseModel):
    n_deleted_documents: int = Field(..., description="")
    n_deleted_s3: int = Field(..., description="")
    deleted_s3_keys: List[str] = Field(..., description="")


class RetrievedDoc(BaseModel):
    original_file_name: str = Field(..., description="")
    doc_id: str = Field(..., description="")
    text: str = Field(..., description="")
    score: float = Field(..., description="")


class EsrTicket(BaseModel):
    company_or_client_name: str = Field(..., description="")
    ticket_category: str = Field(..., description="")
    command_number: str = Field(..., description="")
    serial_number: str = Field(..., description="")
    my_portal_account: str = Field(..., description="")


class MetaJSON(BaseModel):
    id: str | None = Field(default=None, description="")
    model: str | None = Field(default=None, description="")
    usage: Usage | None = Field(default=None, description="")
    stop_reason: str | None = Field(default=None, description="")
    stop_sequence: str | None = Field(default=None, description="")


class CPUUsage(BaseModel):
    used: float = Field(..., description="REST API average CPU usage in percentage")

    @field_validator("used")
    @classmethod
    def used_check(cls, v):
        return round(v, 2)


class MemoryUsage(BaseModel):
    used: float = Field(..., description="REST API used memory in percentage")

    @field_validator("used")
    @classmethod
    def used_check(cls, v):
        return round(v, 2)


class GPUUsage(BaseModel):
    kernel_usage: float = Field(..., description="GPU kernel usage in percentage")
    memory_total: int = Field(..., description="Total GPU memory in megabytes")
    memory_used: int | None = Field(
        ..., description="REST API used GPU memory in megabytes"
    )

    @field_validator("kernel_usage")
    @classmethod
    def kernel_usage_check(cls, v):
        return round(v, 2)


class GPUInfo(BaseModel):
    index: int = Field(..., description="GPU index")
    usage: GPUUsage = Field(..., description="GPU usage details")


class HealthResponse(BaseModel):
    version: str = Field(..., description="Haystack version")
    cpu: CPUUsage = Field(..., description="CPU usage details")
    memory: MemoryUsage = Field(..., description="Memory usage details")
    gpus: List[GPUInfo] = Field(default_factory=list, description="GPU usage details")


class StatusEnum(str, enum.Enum):
    initialized = "initialized"
    completed = "completed"
    processing = "processing"
    failed = "failed"


class IndexingResponse(BaseModel):
    message: str = Field(..., description="")
    s3_keys: List[str] = Field(..., description="")
    group_id: str = Field(..., description="")


class IndexingTask(BaseModel):
    group_id: str = Field(..., description="")
    job_queue_uuid: str | None = Field(default=None, description="")
    description: str | None = Field(default=None, description="")
    type: str = Field(..., description="")
    id: int = Field(..., description="")
    name: str | None = Field(default=None, description="")
    status: StatusEnum = Field(..., description="")
    s3_key: str = Field(..., description="")
    task_parameters: Dict | None = Field(default=None, description="")
    result_json: Dict | None = Field(default=None, description="")
    detailed_token_consumption: List[Dict] | None = Field(..., description="")
    time_taken: float | None = Field(default=None, description="")


class DocInfos(BaseModel):
    filename: str = Field(..., description="")
    group_id: str = Field(..., description="")
    embedding_model: str = Field(..., description="")
    is_deleted: bool = Field(..., description="")
    s3_key: str = Field(..., description="")
    file_meta: dict = Field(..., description="")
    total_tokens: int = Field(..., description="")
    task_id: int = Field(..., description="")


class KeywordsAvailable(BaseModel):
    keywords: List[str] = Field(..., description="")


class DocsAvailable(BaseModel):
    s3_keys: str = Field(..., description="")
    keywords: List[str] | None = Field(default=None, description="")
    meta_subfolder: str = Field(..., description="")


Permissions = Literal["full", "read_only"]


class ApiKeys(BaseModel):
    name: str | None = Field(default=None, description="")
    creator_id: str = Field(..., description="")
    group_id: str = Field(..., description="")
    api_key: str = Field(..., description="")
    permission: Permissions = Field(..., description="")
    revoked: bool = Field(..., description="")
    revoked_at: datetime | None = Field(..., description="")


class QueryFeedbackResponse(BaseModel):
    id: int = Field(..., description="")
    query_uuid: str | None = Field(..., description="")
    thread_id: str | None = Field(..., description="")
    group_id: str = Field(..., description="")
    user_id: str | None = Field(..., description="")
    system_prompt: str = Field(..., description="")
    user_query: str = Field(..., description="")
    answer: str = Field(..., description="")
    embedding_model: str = Field(..., description="")
    chat_model: str = Field(..., description="")
    retrieved_s3_keys: List[str] = Field(..., description="")
    retrieved_chunks: List[Dict] = Field(..., description="")
    prompt_tokens: int = Field(..., description="")
    completion_tokens: int = Field(..., description="")
    total_tokens: int = Field(..., description="")
    time_taken: float = Field(..., description="")
    feedback: int = Field(..., description="")
    feedback_comment: str | None = Field(..., description="")
    detailed_token_consumption: List[Dict] | None = Field(..., description="")
    created_at: datetime = Field(..., description="")
    pythia_document_categories: List[str] | None = Field(..., description="")
    pipeline_type: str | None = Field(..., description="")


class CreateApiKeyRequest(BaseModel):
    name: str | None = Field(default=None, description="")
    creator_id: str = Field(..., description="")
    group_id: str = Field(..., description="")
    permission: Permissions = Field(..., description="")


class Part(BaseModel):
    part_no: str = Field(default="", description="")
    partner_part_no: str = Field(default="", description="")
    model_no: str = Field(default="", description="")
    HTS_code: str = Field(default="", description="")
    ECCN_code: str = Field(default="", description="")
    quantity: int | None = Field(default=None, description="")
    dimensions: str = Field(default="", description="")
    weight: float | None = Field(default=None, description="")
    description: str = Field(default="", description="")
    carton_no: str = Field(default="", description="")

    model_config = ConfigDict(protected_namespaces=())


class PkList(BaseModel):
    packing_no: str = Field(default="", description="")
    packing_date: str = Field(default="", description="")
    customer_PO: str = Field(default="", description="")
    invoice_no: str = Field(default="", description="")
    shipment_list: str = Field(default="", description="")
    no_pallets: int | None = Field(default=None, description="")
    no_cartons: int | None = Field(default=None, description="")
    list_part_number: List[Part] = Field(default_factory=list, description="")


class ListOfPkList(BaseModel):
    pk_list: List[PkList] = Field(default_factory=list, description="")

class ReplaceMetadataRequest(BaseModel):
    metadata: Dict[str, Any] = Field(default={}, description="Metadata dictionary to update current metadata.",
                                     examples=[{"keywords": ["ALE 400", "OXO Connect"]}])

class DataExtractTask(BaseModel):
    group_id: str = Field(..., description="")
    job_queue_uuid: str | None = Field(default=None, description="")
    description: str | None = Field(default=None, description="")
    type: str = Field(..., description="")
    id: int = Field(..., description="")
    name: str | None = Field(default=None, description="")
    status: StatusEnum = Field(..., description="")
    s3_key: str | None = Field(default=None, description="")
    task_parameters: Dict | None = Field(default=None, description="")
    result_json: Dict | None = Field(default=None, description="")
    detailed_token_consumption: List[Dict] | None = Field(..., description="")
    time_taken: float | None = Field(default=None, description="")

class DataExtractResponse(BaseModel):
    message: str = Field(..., description="")
    job_uuid: str = Field(..., description="")

class QueryMetricsResponse(BaseModel):
    total_queries: int
    feedback_distribution: Dict[str, int]  # Maps feedback value to count
    avg_time: float
    total_tokens: int
    estimated_cost: float

class ThreadListResponse(BaseModel):
    thread_id: str = Field(..., description="Unique identifier for the thread")
    title: str = Field(..., description="Title of the thread")
    group_id: str = Field(..., description="Group ID associated with the thread")
    user_id: str | None = Field(..., description="User ID associated with the thread")
    created_at: datetime = Field(..., description="Thread creation timestamp")
    updated_at: datetime | None = Field(..., description="Thread last update timestamp")

class ThreadResponse(BaseModel):
    thread_info: ThreadListResponse = Field(..., description="Thread details")
    queries: List[QueryFeedbackResponse] = Field(..., description="List of queries in the thread")