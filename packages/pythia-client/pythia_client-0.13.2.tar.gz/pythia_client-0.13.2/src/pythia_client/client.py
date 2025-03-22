"""A client for interacting with the API.

This module provides a client class for interacting with the API, including
indexing documents, listing them, deleting them, get S3 URL to a document,
querying them and extracting structured json data from text.

Classes:
    APIClient: Client for interacting with the API.
"""

import io
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Tuple
from urllib.parse import urljoin

import requests

from .schema import (
    ApiKeys,
    ChatMessage,
    DataExtractResponse,
    DataExtractTask,
    DeleteDocResponse,
    DocInfos,
    FilterDocStoreResponse,
    FilterRequest,
    GetFileS3Reponse,
    IndexingResponse,
    IndexingTask,
    Permissions,
    QueryFeedbackResponse,
    QueryMetricsResponse,
    QueryRequest,
    QueryResponse,
    SearchParams,
    ThreadResponse,
    ThreadListResponse,
)


class APIClient:
    """Client for interacting with the API.

    This class provides methods for interacting with the API, including
    indexing documents, listing them, deleting them, get S3 URL to a document,
    querying them and extracting structured json data from text.

    Attributes:
        url: The base URL for the API.
        api-key: The api key for the API.
        files_endpoint: The endpoint for files operation (upload, get).
        indexing_tasks_endpoint: The endpoint for indexing tasks.
        documents_by_filter_endpoint: The endpoint for documents operation by filters.
        documents_by_s3_key_endpoint: The endpoint for documents operation by S3 key.
        search_endpoint: The endpoint for querying.
        data_extraction_endpoint: The endpoint for extracting JSON data from text.
    """

    def __init__(self, url: str, api_key: str):
        """Initializes the API client with the given URL and the API key.

        Args:
            url: The base URL for the API.
            api_key: The api key for the API.

        Usage:
        ```python
        from pythia_client.client import APIClient
        client = APIClient("http://localhost:8000", "api-key")
        ```
        """
        self.url = url
        self.api_key = api_key
        self.files_endpoint = urljoin(str(self.url), "files")
        self.facets_endpoint = urljoin(str(self.url), "/documents/facets")
        self.indexing_tasks_endpoint = urljoin(str(self.url), "files/indexing-tasks")
        self.file_infos_endpoint = urljoin(str(self.url), "files/infos")
        self.documents_by_filter_endpoint = urljoin(str(self.url), "documents/filters")
        self.documents_by_s3_key_endpoint = urljoin(str(self.url), "documents/s3-key")
        self.chat_endpoint = urljoin(str(self.url), "chat/query")
        self.search_endpoint = urljoin(str(self.url), "search/query")
        self.data_extraction_endpoint = urljoin(
            str(self.url), "/data-extraction/extract-structured-data"
        )
        self.api_keys_endpoint = urljoin(str(self.url), "/api-keys")
        self.feedback_endpoint = urljoin(str(self.url), "/feedback")
        self.draw_endpoint = urljoin(str(self.url), "/draw")

    def _process_error_response(self, response):
        try:
            # Try to parse the response as JSON
            error_detail = response.json()["detail"]
            return error_detail
        except requests.exceptions.JSONDecodeError:
            # If JSON parsing fails, capture the raw response content
            error_detail = response.text
            return error_detail
        except Exception as e:
            # Catch any other exceptions
            error_detail = str(e)
            return error_detail

    def chat(
            self,
            query: str,
            chat_history: List[ChatMessage] | None = None,
            filters: Dict[str, Any] | None = None,
            top_k=30,
            group_id: str = None,
            custom_system_prompt: str = None,
            threshold: float = 0.1,
            return_embedding: bool = False,
            group_by: str = None,
            group_size: int = None,
            return_content: bool = True,
            user_id: str = None,
            thread_id: str = None,
            len_chat_history: int = 3,
            raw_mode: bool = False,
    ) -> QueryResponse:
        """Query the Chat API endpoint with a user question to get a LLM-generated answer based
            on context from the document store. The difference with the query method is that the chat method can do "quick-answer" based on user history and doesn't always perform RAG search.

            Args:
                query: The user question to be answered.
                chat_history: The chat history to provide context to the model. Should be a list of ChatMessage objects.
                filters: Qdrant native filter dict (https://qdrant.tech/documentation/concepts/filtering/) OR Haystack 2.0 filter dict (https://docs.haystack.deepset.ai/v2.0/docs/metadata-filtering#filters).
                top_k: The number of document to fetch to answer the query.
                group_id: The name of the group_id the client making the request, for logging. Defaults to "api".
                custom_system_prompt: A custom system prompt to use for the LLM.
                threshold: The threshold to use for the LLM.
                return_embedding: If True, the response will include the embeddings of the documents that were used to generate the answer.
                return_content: If True, the response will include the content of the documents that were used to generate the answer.
                user_id: Optional parameter to tag the query in database with a user id on top of group_id. Useful for threads feature.
                thread_id: Optional thread ID to use for the query. If not provided, a new thread will be created.
                len_chat_history: The number of messages to keep in the chat history for the query (retrieved automatically based on thread ID. Default is 3.
                raw_mode: If True, the RAG mechanism is deactivated producing raw LLM response.

            Returns:
                The response from the API as a Pydantic model. You can use response.model_dump() to get a Dict. Raise an exception with API status code and error message if the status code is not 200.

            Usage:
            ```python
            # Haystack Filter Style
            filters = {
                "operator": "AND",
                "conditions": [
                    {
                        "field": "meta.source",
                        "operator": "==",
                        "value": "Salesforce"
                    }
                ]
            }
            # Qdrant Filter Style
            filters =  {
                "must":[
                    {
                        "key":"meta.source",
                        "match":{
                            "value": "Salesforce"
                        }
                    }
                ]
            }
            query_response = client.chat("Hey how are you", filters=filters)
            query_response.model_dump()
            ```
            Can also be used with chat history:
            ```python
            chat_history = [
                {
                    "content": "Hello Chatbot. My name is Corentin !",
                    "role": "user",
                    "name": None,
                    "meta": {},
                }
            ]
            response = client.query(
                query="Given our previous exchange of messages, what is my name ?",
                chat_history=chat_history,
            )
        ```
        """
        params = SearchParams(
            top_k=top_k,
            group_id=group_id,
            filters=filters,
            system_prompt=custom_system_prompt,
            return_embedding=return_embedding,
            return_content=return_content,
            threshold=threshold,
            group_by=group_by,
            group_size=group_size,
            len_chat_history=len_chat_history
        ).model_dump()
        request = QueryRequest(
            query=query,
            chat_history=chat_history,
            params=params,
            user_id=user_id,
            thread_id=thread_id,
            raw=raw_mode,
        )
        with requests.Session() as session:
            payload = json.loads(request.model_dump_json())
            headers = {
                "accept": "application/json",
                "Content-Type": "application/json",
                "X-API-Key": self.api_key,
            }
            with session.post(
                    self.chat_endpoint, headers=headers, json=payload
            ) as response:
                if response.status_code == 200:
                    api_response = QueryResponse(**response.json())
                else:
                    raise Exception(
                        f"Pythia API Error {response.status_code}: {self._process_error_response(response)}"
                    )
        return api_response


    def query(
            self,
            query: str,
            chat_history: List[ChatMessage] | None = None,
            filters: Dict[str, Any] | None = None,
            top_k=30,
            group_id: str = None,
            custom_system_prompt: str = None,
            threshold: float = 0.1,
            return_embedding: bool = False,
            group_by: str = None,
            group_size: int = None,
            return_content: bool = True,
            user_id: str = None,
            thread_id: str = None,
            len_chat_history: int = 3,
    ) -> QueryResponse:
        """Query the API with a user question to get a LLM-generated answer based
            on context from the document store.

            Args:
                query: The user question to be answered.
                chat_history: The chat history to provide context to the model. Should be a list of ChatMessage objects.
                filters: Qdrant native filter dict (https://qdrant.tech/documentation/concepts/filtering/) OR Haystack 2.0 filter dict (https://docs.haystack.deepset.ai/v2.0/docs/metadata-filtering#filters).
                top_k: The number of document to fetch to answer the query.
                group_id: The name of the group_id the client making the request, for logging. Defaults to "api".
                custom_system_prompt: A custom system prompt to use for the LLM.
                threshold: The threshold to use for the LLM.
                return_embedding: If True, the response will include the embeddings of the documents that were used to generate the answer.
                return_content: If True, the response will include the content of the documents that were used to generate the answer.
                user_id: Optional parameter to tag the query in database with a user id on top of group_id. Useful for threads feature.
                thread_id: Optional thread ID to use for the query. If not provided, a new thread will be created.
                len_chat_history: The number of messages to keep in the chat history for the query (retrieved automatically based on thread ID. Default is 3.

            Returns:
                The response from the API as a Pydantic model. You can use response.model_dump() to get a Dict. Raise an exception with API status code and error message if the status code is not 200.

            Usage:
            ```python
            # Haystack Filter Style
            filters = {
                "operator": "AND",
                "conditions": [
                    {
                        "field": "meta.source",
                        "operator": "==",
                        "value": "Salesforce"
                    }
                ]
            }
            # Qdrant Filter Style
            filters =  {
                "must":[
                    {
                        "key":"meta.source",
                        "match":{
                            "value": "Salesforce"
                        }
                    }
                ]
            }
            query_response = client.query("Hey how are you", filters=filters)
            query_response.model_dump()
            ```
            Can also be used with chat history:
            ```python
            chat_history = [
                {
                    "content": "Hello Chatbot. My name is Corentin !",
                    "role": "user",
                    "name": None,
                    "meta": {},
                }
            ]
            response = client.query(
                query="Given our previous exchange of messages, what is my name ?",
                chat_history=chat_history,
            )
        ```
        """
        params = SearchParams(
            top_k=top_k,
            group_id=group_id,
            filters=filters,
            system_prompt=custom_system_prompt,
            return_embedding=return_embedding,
            return_content=return_content,
            threshold=threshold,
            group_by=group_by,
            group_size=group_size,
            len_chat_history=len_chat_history
        ).model_dump()
        request = QueryRequest(
            query=query,
            chat_history=chat_history,
            params=params,
            user_id=user_id,
            thread_id=thread_id,
        )
        with requests.Session() as session:
            payload = json.loads(request.model_dump_json())
            headers = {
                "accept": "application/json",
                "Content-Type": "application/json",
                "X-API-Key": self.api_key,
            }
            with session.post(
                    self.search_endpoint, headers=headers, json=payload
            ) as response:
                if response.status_code == 200:
                    api_response = QueryResponse(**response.json())
                else:
                    raise Exception(
                        f"Pythia API Error {response.status_code}: {self._process_error_response(response)}"
                    )
        return api_response


    def upload_files(
            self,
            files: List[str | Tuple[str, io.IOBase]],
            meta: List[dict] | None = None,
            indexing_mode: Literal["unstructured", "tika"] = "unstructured",
            priority_queue: bool = False,
    ) -> IndexingResponse:
        """Index one or multiples files (documents) to the document store through the Pythia-API upload-file endpoint.
        It is recommended to add the following minimum metadata fields:
            - pythia_document_category (string, category name tag)
            - document_date (datetime)
            - language (string)
            - keywords (list)
            Example of value for meta field for the indexing of two files:
            ```json
            {
              "meta": [
                {
                    "pythia_document_category":"TDL Document",
                    "document_date":"2024-01-19 14:56",
                    "keywords":["ALE 400", "ALE 500"],
                    "language":"English",
                },
                {
                    "pythia_document_category":"Marketing Document
                    "document_date":"2024-01-19 14:58",
                    "keywords":["OXE 8", "OXE 9"],
                    "language":"Français",
                }
              ]
            }
            ```
        Args:
            files: The paths to the files OR tuples of filename and file object to index.
            meta: The list of metadata for the files.
            indexing_mode: The indexing mode between Unstructured and Apache Tika.
            priority_queue: If the indexing should use the priority queue (more workers). Only working with admin API Key.

        Returns:
            The response from the API. Raise an exception with API status code and error message if the status code is not 202.

        Usage:
        ```python
        index_response = client.upload_files(["path/to/file.pdf"], meta=[{"source": "Salesforce"}])
        {"message": "Files Submitted. Indexing task created."}
        index_response = client.upload_files([("file.pdf", file)], meta=[{"source": "Salesforce"}])
        {"message": "Files Submitted. Indexing task created."}
        ```
        """
        prepared_files = []
        for file in files:
            if isinstance(file, str):
                file_name = os.path.basename(file)
                with open(file, "rb") as f:
                    file_content = f.read()
            elif (
                    isinstance(file, tuple)
                    and len(file) == 2
                    and isinstance(file[1], io.IOBase)
            ):
                file_name, file_object = file
                file_content = file_object.read()
            else:
                raise ValueError(
                    "Each file must be a file path or a tuple of (filename, fileIObyte)"
                )

            prepared_files.append(("files", (file_name, file_content)))

        with requests.Session() as session:
            payload = {
                "meta": json.dumps(meta),
                "priority_queue": priority_queue,
                "indexing_mode": indexing_mode,
            }
            headers = {
                "X-API-Key": self.api_key,
            }
            with session.post(
                    self.files_endpoint,
                    files=prepared_files,
                    data=payload,
                    headers=headers,
            ) as response:
                if response.status_code == 202:
                    api_response = response.json()
                else:
                    raise Exception(
                        f"Pythia API Error {response.status_code}: {self._process_error_response(response)}"
                    )
        return api_response

    def get_indexing_tasks_by_group_id(
            self, group_id: str, top: int = 20
    ) -> List[IndexingTask]:
        """Get the indexing tasks from the API.

        Args:
            group_id: The name of the group_id the client making the request, for logging. If none, the default group_id is "api" (set by the API itself).
            top: The number of top most recent indexing tasks to return.

        Returns:
            The response from the API. Raise an exception with API status code and error message if the status code is not 200.

        Usage:
        ```python
        indexing_tasks = client.get_indexing_tasks(group_id="api", top=20)
        indexing_tasks.model_dump()
        ```
        """
        with requests.Session() as session:
            params = {"top": top}
            headers = {
                "X-API-Key": self.api_key,
            }
            with session.get(
                    self.indexing_tasks_endpoint + "/" + group_id,
                    params=params,
                    headers=headers,
            ) as response:
                if response.status_code == 200:
                    api_response = [IndexingTask(**resp) for resp in response.json()]
                else:
                    raise Exception(
                        f"Pythia API Error {response.status_code}: {self._process_error_response(response)}"
                    )
        return api_response

    def get_indexing_task_by_s3_key(self, group_id: str, s3_key: str) -> IndexingTask:
        with requests.Session() as session:
            headers = {
                "X-API-Key": self.api_key,
            }
            with session.get(
                    self.indexing_tasks_endpoint + "/" + group_id + "/" + s3_key,
                    headers=headers,
            ) as response:
                if response.status_code == 200:
                    api_response = IndexingTask(**response.json())
                else:
                    raise Exception(
                        f"Pythia API Error {response.status_code}: {self._process_error_response(response)}"
                    )
        return api_response

    def get_file_infos_by_group_id(
            self, group_id: str, limit: int = 20
    ) -> List[DocInfos]:
        """Get all the file infos from the API for a specific group_id (owner).

        Args:
            group_id: The name of the group_id the client making the request (who indexed the file).
            limit: The number of top most recent indexed documents to return.

        Returns:
            The response from the API. Raise an exception with API status code and error message if the status code is not 200.

        Usage:
        ```python
        document_list = client.get_file_infos_by_group_id(group_id="api", limit=20)
        for doc in document_list:
            doc.model_dump()
        ```
        """
        with requests.Session() as session:
            params = {"limit": limit}
            headers = {
                "X-API-Key": self.api_key,
            }
            with session.get(
                    self.file_infos_endpoint + "/" + group_id,
                    params=params,
                    headers=headers,
            ) as response:
                if response.status_code == 200:
                    api_response = [DocInfos(**resp) for resp in response.json()]
                else:
                    raise Exception(
                        f"Pythia API Error {response.status_code}: {self._process_error_response(response)}"
                    )
        return api_response

    def get_file_infos_by_s3_key(self, group_id: str, s3_key: str) -> DocInfos:
        """Get the file infos from the API for a single file and a specific owner.

        Args:
            group_id: The name of the group_id the client making the request (who indexed the file).
            s3_key: The S3 Key of the file.

        Returns:
            The response from the API. Raise an exception with API status code and error message if the status code is not 200.

        Usage:
        ```python
        document = client.get_file_infos_by_s3_key(group_id="api", s3_key="abc_sample.pdf")
        document.model_dump()
        ```
        """
        with requests.Session() as session:
            headers = {
                "X-API-Key": self.api_key,
            }
            with session.get(
                    self.file_infos_endpoint + "/" + group_id + "/" + s3_key,
                    headers=headers,
            ) as response:
                if response.status_code == 200:
                    api_response = DocInfos(**response.json())
                else:
                    raise Exception(
                        f"Pythia API Error {response.status_code}: {self._process_error_response(response)}"
                    )
        return api_response

    def get_file_url(self, s3_key: str, page: int | None = 1) -> GetFileS3Reponse:
        """Get a pre-signed URL to a file located on S3.

        Args:
            s3_key: The filename of the file to get.
            page: The page to directly point the URL.

        Returns:
            The response from the API as a Pydantic model. You can use response.model_dump() to get a Dict. Raise an exception with API status code and error message if the status code is not 200.

        Usage:
        ```python
        get_doc_response = client.get_file_url("s3fd_sample.pdf", page=2)
        s3_url = get_doc_response.url
        ```
        """
        with requests.Session() as session:
            params = {"page": page}
            url = self.files_endpoint + "/" + s3_key
            headers = {
                "X-API-Key": self.api_key,
            }
            with session.get(
                    url,
                    params=params,
                    headers=headers,
            ) as response:
                if response.status_code == 200:
                    api_response = GetFileS3Reponse(**response.json())
                else:
                    raise Exception(
                        f"Pythia API Error {response.status_code}: {self._process_error_response(response)}"
                    )
        return api_response

    def get_docs_by_filters(
            self,
            filters: Dict[str, Any] = None,
            return_content: bool = False,
    ) -> List[FilterDocStoreResponse]:
        """List all documents in the document store that match the filter provided.

        Args:
            filters: Qdrant native filter dict (https://qdrant.tech/documentation/concepts/filtering/) OR Haystack 2.0 filter dict (https://docs.haystack.deepset.ai/v2.0/docs/metadata-filtering#filters).
            return_content: If True, the content of the documents will be returned.

        Returns:
            The response from the API. Raise an exception with API status code and error message if the status code is not 200.

        Usage:
        ```python
        # Haystack Filter Style
        filters = {
            "operator": "AND",
            "conditions": [
                {
                    "field": "meta.source",
                    "operator": "==",
                    "value": "Salesforce"
                }
            ]
        }
        # Qdrant Filter Style
        filters =  {
            "must":[
                {
                    "key":"meta.source",
                    "match":{
                        "value": "Salesforce"
                    }
                }
            ]
        }
        list_response = client.get_docs_by_filters(filters=filters)
        list_response.model_dump()
        ```
        """
        request = FilterRequest(filters=filters)
        with requests.Session() as session:
            payload = json.loads(request.model_dump_json())
            headers = {
                "accept": "application/json",
                "Content-Type": "application/json",
                "X-API-Key": self.api_key,
            }
            if return_content:
                endpoint = f"{self.documents_by_filter_endpoint}?return_content=true"
            else:
                endpoint = self.documents_by_filter_endpoint

            with session.post(endpoint, headers=headers, json=payload) as response:
                if response.status_code == 200:
                    responses = response.json()
                    api_response = [
                        FilterDocStoreResponse(**resp) for resp in responses
                    ]
                else:
                    raise Exception(
                        f"Pythia API Error {response.status_code}: {self._process_error_response(response)}"
                    )
        return api_response

    def delete_docs_by_filters(
            self,
            filters: Dict[str, Any] = None,
    ) -> DeleteDocResponse:
        """Remove documents from the API document store.

        Args:
            filters: Qdrant native filter dict (https://qdrant.tech/documentation/concepts/filtering/) OR Haystack 2.0 filter dict (https://docs.haystack.deepset.ai/v2.0/docs/metadata-filtering#filters).

        Returns:
            The response from the API as a Pydantic model. You can use response.model_dump() to get a Dict. Raise an exception with API status code and error message if the status code is not 200.
        Usage:
        ```python
        # Haystack Filter Style
        filters = {
            "operator": "AND",
            "conditions": [
                {
                    "field": "meta.source",
                    "operator": "==",
                    "value": "Salesforce"
                }
            ]
        }
        # Qdrant Filter Style
        filters =  {
            "must":[
                {
                    "key":"meta.source",
                    "match":{
                        "value": "Salesforce"
                    }
                }
            ]
        }
        remove_response = client.delete_docs_by_filters(filters=filters)
        remove_response.model_dump()
        ```
        """
        request = FilterRequest(filters=filters)
        with requests.Session() as session:
            payload = json.loads(request.model_dump_json())
            headers = {
                "accept": "application/json",
                "Content-Type": "application/json",
                "X-API-Key": self.api_key,
            }
            with session.delete(
                    self.documents_by_filter_endpoint, headers=headers, json=payload
            ) as response:
                if response.status_code == 200:
                    api_response = DeleteDocResponse(**response.json())
                else:
                    raise Exception(
                        f"Pythia API Error {response.status_code}: {self._process_error_response(response)}"
                    )
        return api_response

    def get_docs_by_s3_key(self, s3_key: str) -> List[FilterDocStoreResponse]:
        """Get documents (chunk of files in the Vector DB) from the API document store based on its S3 key.

        Args:
            s3_key: the S3 key of the file

        Returns:
            The response from the API as a Pydantic model. You can use response.model_dump() to get a Dict. Raise an exception with API status code and error message if the status code is not 200.
        Usage:
        ```python
        chunks_list = client.get_docs_by_s3_key(s3_key="abc_sample.pdf")
        for chunk in chunks_list:
            chunk.model_dump()
        ```
        """
        with requests.Session() as session:
            url = self.documents_by_s3_key_endpoint + "/" + s3_key
            headers = {"X-API-Key": self.api_key}
            with session.get(url, headers=headers) as response:
                if response.status_code == 200:
                    api_response = [
                        FilterDocStoreResponse(**resp) for resp in response.json()
                    ]
                else:
                    raise Exception(
                        f"Pythia API Error {response.status_code}: {self._process_error_response(response)}"
                    )
        return api_response

    def get_document_metadata(self, s3_key: str) -> Dict[str, Any]:
        """Get a single document metadata based on its S3 key.

        Args:
            s3_key: the S3 key of the file

        Returns:
            The response from the API as a Pydantic model. You can use response.model_dump() to get a Dict. Raise an exception with API status code and error message if the status code is not 200.
        Usage:
        ```python
        metadata_dict = client.get_document_metadata(s3_key="abc_sample.pdf")
        ```
        """
        with requests.Session() as session:
            url = self.documents_by_s3_key_endpoint + "/" + s3_key + "/metadata"
            headers = {"X-API-Key": self.api_key}
            with session.get(url, headers=headers) as response:
                if response.status_code == 200:
                    api_response = response.json()
                else:
                    raise Exception(
                        f"Pythia API Error {response.status_code}: {self._process_error_response(response)}"
                    )
        return api_response

    def update_document_metadata(self, s3_key: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Update a single document metadata based on its S3 key. Metadata that can't be changed such as S3 eky are ignored. Metadata values that are set to null (None) are deleted.

        Args:
            s3_key: the S3 key of the file
            metadata: new metadata to replace/update/delete.

        Returns:
            The response from the API as a Pydantic model. You can use response.model_dump() to get a Dict. Raise an exception with API status code and error message if the status code is not 200.
        Usage:
        ```python
        new_metadata = client.update_document_metadata(s3_key="abc_sample.pdf", metadata={"keywords": ["ALE 400","OXO Connect"], "language": None})
        ```
        """
        with requests.Session() as session:
            url = self.documents_by_s3_key_endpoint + "/" + s3_key + "/metadata"
            headers = {"X-API-Key": self.api_key}
            new_metadata = {"metadata": metadata}
            with session.post(url, headers=headers, data=json.dumps(new_metadata)) as response:
                if response.status_code == 200:
                    api_response = response.json()
                else:
                    raise Exception(
                        f"Pythia API Error {response.status_code}: {self._process_error_response(response)}"
                    )
        return api_response


    def delete_docs_by_s3_key(self, s3_key: str) -> DeleteDocResponse:
        """Delete documents (chunk of files in the Vector DB) from the API document store based on its S3 key.

        Args:
            s3_key: the S3 key of the file

        Returns:
            The response from the API as a Pydantic model. You can use response.model_dump() to get a Dict. Raise an exception with API status code and error message if the status code is not 200.
        Usage:
        ```python
        delete_response = client.delete_docs_by_s3_key(s3_key="abc_sample.pdf")
        delete_response.model_dump()
        ```
        """
        with requests.Session() as session:
            url = self.documents_by_s3_key_endpoint + "/" + s3_key
            headers = {"X-API-Key": self.api_key}
            with session.delete(url, headers=headers) as response:
                if response.status_code == 200:
                    api_response = DeleteDocResponse(**response.json())
                else:
                    raise Exception(
                        f"Pythia API Error {response.status_code}: {self._process_error_response(response)}"
                    )
        return api_response


    def get_facets_count(
            self,
            filters: Dict[str, Any] | None = None,
    ) -> int:
        """This method allows you to retrieve the number of unique file/document for a specific [Qdrant filter](https://qdrant.tech/documentation/concepts/filtering/).
        You can only use Qdrant filters for this endpoint, and we recommend to only filter on field that have an index in Qdrant.

        Args:
            filters: Optional Qdrant filters to restrict the document facets counting.

        Returns:
            The response from the API as a Pydantic model. You can use response.model_dump() to get a Dict. Raise an exception with API status code and error message if the status code is not 200.

        Usage:
        ```python
        filters =  {
            "must":[
                {
                    "key":"meta.pythia_document_category",
                    "match":{
                        "value": "KCS"
                    }
                }
            ]
        }
        client.get_facets_count(filters=filters)
        > 123
        ```
        """
        if filters is None:
            filters = {}
        request = FilterRequest(filters=filters)
        payload = json.loads(request.model_dump_json())
        with requests.Session() as session:
            headers = {
                "X-API-Key": self.api_key,
            }
            with session.post(
                    self.facets_endpoint + f"/count",
                    headers=headers,
                    json=payload,
            ) as response:
                if response.status_code == 200:
                    count = int(response.text)
                else:
                    raise Exception(
                        f"Pythia API Error {response.status_code}: {self._process_error_response(response)}"
                    )
        return count

    def get_facets_values(
            self,
            metadata_field: str,
            filters: Dict[str, Any] | None = None,
    ) -> List[str]:
        """This method allows you to retrieve the unique values for a specific metadata field with an optional [Qdrant filter](https://qdrant.tech/documentation/concepts/filtering/).
        You can only use Qdrant filters for this method, and we recommend to only filter on field that have an index in Qdrant.
        For the metadata_field value, an error will be raised if the field corresponding to the metadata_field does not have an index in Qdrant.
        Example of metadata_field: `meta.keywords`

        Args:
            metadata_field: The metadata field to get the unique values form. Will raise an error if the field does not have an index in Qdrant.
            filters: Optional Qdrant filters to restrict the document facets counting.

        Returns:
            The response from the API as a Pydantic model. You can use response.model_dump() to get a Dict. Raise an exception with API status code and error message if the status code is not 200.

        Usage:
        ```python
        filters =  {
            "must":[
                {
                    "key":"meta.pythia_document_category",
                    "match":{
                        "value": "KCS"
                    }
                }
            ]
        }
        client.get_facets_values("meta.keywords", filters=filters)
        > ["ALE 400", "OXO Connect"]
        ```
        """
        if filters is None:
            filters = {}
        request = FilterRequest(filters=filters)
        payload = json.loads(request.model_dump_json())
        with requests.Session() as session:
            headers = {
                "X-API-Key": self.api_key,
            }
            with session.post(
                    self.facets_endpoint
                    + f"/values",
                    headers=headers,
                    params={"metadata_field": metadata_field},
                    json=payload,
            ) as response:
                if response.status_code == 200:
                    response = response.json()
                else:
                    raise Exception(
                        f"Pythia API Error {response.status_code}: {self._process_error_response(response)}"
                    )
        return response

    def create_api_key(
            self,
            name: str,
            creator_id: str,
            group_id: str,
            permission: Permissions,
    ) -> ApiKeys:
        """Create an API key for a group_id.

        Args:
            name: The name of the API key.
            creator_id: The creator_id of the API key (streamlit user often).
            group_id: The group_id of the API key (cognito group name).
            permission: The permission of the API key  (full or read).

        Returns:
            The response from the API as a Pydantic model. You can use response.model_dump() to get a Dict. Raise an exception with API status code and error message if the status code is not 200.

        Usage:
        ```python
        api_response = client.create_api_key("my key", "e9824-d710c-f9018-82jh", "btq-group", "full")
        api_response.model_dump()
        ```
        """
        with requests.Session() as session:
            headers = {
                "X-API-Key": self.api_key,
            }
            data = {
                "name": name,
                "creator_id": creator_id,
                "group_id": group_id,
                "permission": permission,
            }
            with session.post(
                    self.api_keys_endpoint + "/create", headers=headers, json=data
            ) as response:
                if response.status_code == 200:
                    api_response = ApiKeys(**response.json())
                else:
                    raise Exception(
                        f"Pythia API Error {response.status_code}: {self._process_error_response(response)}"
                    )
        return api_response

    def revoke_api_key(
            self,
            api_key_to_revoke: str,
            creator_id: str,
    ) -> ApiKeys:
        """Revoke and API key.

        Args:
            api_key_to_revoke: The API key to revoke
            creator_id: The creator_id of the API key (streamlit user often).

        Returns:
            The response from the API as a Pydantic model. You can use response.model_dump() to get a Dict. Raise an exception with API status code and error message if the status code is not 200.

        Usage:
        ```python
        api_response = client.revoke_api_key(api_key_to_revoke="abe4arg84are9g4bear65gb16DS61", creator_id="e9824-d710c-f9018-82jh")
        api_response.model_dump()
        ```
        """
        with requests.Session() as session:
            headers = {
                "X-API-Key": self.api_key,
            }
            data = {"creator_id": creator_id}
            with session.delete(
                    self.api_keys_endpoint + f"/revoke/{api_key_to_revoke}",
                    params=data,
                    headers=headers,
            ) as response:
                if response.status_code == 200:
                    api_response = ApiKeys(**response.json())
                else:
                    raise Exception(
                        f"Pythia API Error {response.status_code}: {self._process_error_response(response)}"
                    )
        return api_response

    def list_api_keys_by_group_id(
            self,
            group_id: str,
    ) -> List[ApiKeys]:
        """List API Keys for a specific group_id.

        Args:
            group_id: Group ID to list the API keys from

        Returns:
            The response from the API as a Pydantic model. You can use response.model_dump() to get a Dict. Raise an exception with API status code and error message if the status code is not 200.

        Usage:
        ```python
        api_response = client.list_api_keys_by_group_id(group_id="btq-group")
        api_response.model_dump()
        ```
        """
        with requests.Session() as session:
            headers = {
                "X-API-Key": self.api_key,
            }
            with session.get(
                    self.api_keys_endpoint + f"/list/by-group-id/{group_id}",
                    headers=headers,
            ) as response:
                if response.status_code == 200:
                    api_response = [ApiKeys(**resp) for resp in response.json()]
                else:
                    raise Exception(
                        f"Pythia API Error {response.status_code}: {self._process_error_response(response)}"
                    )
        return api_response

    def list_api_keys_by_creator_id(
            self,
            creator_id: str,
    ) -> List[ApiKeys]:
        """List API Keys for a specific group_id.

        Args:
            creator_id: Group ID to list the API keys from

        Returns:
            The response from the API as a Pydantic model. You can use response.model_dump() to get a Dict. Raise an exception with API status code and error message if the status code is not 200.

        Usage:
        ```python
        api_response = client.list_api_keys_by_creator_id(creator_id="e9824-d710c-f9018-82jh")
        api_response.model_dump()
        ```
        """
        with requests.Session() as session:
            headers = {
                "X-API-Key": self.api_key,
            }
            with session.get(
                    self.api_keys_endpoint + f"/list/by-creator-id/{creator_id}",
                    headers=headers,
            ) as response:
                if response.status_code == 200:
                    api_response = [ApiKeys(**resp) for resp in response.json()]
                else:
                    raise Exception(
                        f"Pythia API Error {response.status_code}: {self._process_error_response(response)}"
                    )
        return api_response

    def list_query_history_by_group_id(
            self,
            group_id: str,
            limit: int = 50,
            offset: int = 0,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            min_feedback: Optional[int] = None,
            max_feedback: Optional[int] = None,
            has_comments: Optional[bool] = False,
            category: Optional[str] = None,
    ) -> List[QueryFeedbackResponse]:
        """List the query history for a specific group_id with advanced filtering options.

        Args:
            group_id: Group ID (user ID) to list the query history from
            limit: The number of top most recent queries to return.
            offset: Number of queries to skip (for pagination purpose).
            start_date: Optional datetime to filter queries from this date (inclusive)
            end_date: Optional datetime to filter queries until this date (inclusive)
            min_feedback: Filter queries with feedback greater than or equal to this value
            max_feedback: Filter queries with feedback less than or equal to this value
            has_comments: Filter queries that have comments
            category: Filter queries by Pythia document category

        Returns:
            The response from the API as a Pydantic model. You can use response.model_dump() to get a Dict. 
            Raises an exception with API status code and error message if the status code is not 200.

        Usage:
        ```python
        # List all queries
        query_history = client.list_query_history_by_group_id(group_id="ec878-bc91398-j8092")
        
        # List queries with advanced filters
        from datetime import datetime, timedelta
        start = datetime.now() - timedelta(days=7)  # Last 7 days
        end = datetime.now()
        query_history = client.list_query_history_by_group_id(
            group_id="UMC",
            start_date=start,
            end_date=end,
            min_feedback=3,  # Only queries with feedback >= 3
            has_comments=True,  # Only queries with comments
            category="KCS"  # Only KCS documents
        )
        query_history.model_dump()
        ```
        """
        with requests.Session() as session:
            headers = {
                "X-API-Key": self.api_key,
            }
            with session.get(
                    self.feedback_endpoint + f"/query-history/{group_id}",
                    headers=headers,
                    params={
                        "limit": limit,
                        "offset": offset,
                        "start_date": start_date.isoformat() if start_date else None,
                        "end_date": end_date.isoformat() if end_date else None,
                        "min_feedback": min_feedback,
                        "max_feedback": max_feedback,
                        "has_comments": has_comments,
                        "category": category,
                    },
            ) as response:
                if response.status_code == 200:
                    api_response = [
                        QueryFeedbackResponse(**resp) for resp in response.json()
                    ]
                else:
                    raise Exception(
                        f"Pythia API Error {response.status_code}: {self._process_error_response(response)}"
                    )
        return api_response

    def get_query_metrics_by_group_id(
            self,
            group_id: str,
            start_date: Optional[datetime] = None,
            end_date: Optional[datetime] = None,
            min_feedback: Optional[int] = None,
            max_feedback: Optional[int] = None,
            has_comments: Optional[bool] = False,
            category: Optional[str] = None,
    ) -> QueryMetricsResponse:
        """Get aggregated metrics for queries with filtering options.

        Args:
            group_id: Group ID to get metrics for. Use "admin" to get metrics across all groups (requires admin API key)
            start_date: Optional datetime to filter queries from this date (inclusive)
            end_date: Optional datetime to filter queries until this date (inclusive)
            min_feedback: Filter queries with feedback greater than or equal to this value
            max_feedback: Filter queries with feedback less than or equal to this value
            has_comments: Filter queries that have comments
            category: Filter queries by Pythia document category

        Returns:
            The response from the API as a Pydantic model. You can use response.model_dump() to get a Dict.
            Raises an exception with API status code and error message if the status code is not 200.

        Usage:
        ```python
        # Get basic metrics
        metrics = client.get_query_metrics_by_group_id(group_id="ec878-bc91398-j8092")
        
        # Get metrics with filters
        from datetime import datetime, timedelta
        start = datetime.now() - timedelta(days=7)  # Last 7 days
        end = datetime.now()
        metrics = client.get_query_metrics_by_group_id(
            group_id="UMC",
            start_date=start,
            end_date=end,
            min_feedback=3,  # Only queries with feedback >= 3
            has_comments=True,  # Only queries with comments
            category="KCS"  # Only KCS documents
        )
        metrics.model_dump()
        ```
        """
        with requests.Session() as session:
            headers = {
                "X-API-Key": self.api_key,
            }
            with session.get(
                    self.feedback_endpoint + f"/query-metrics/{group_id}",
                    headers=headers,
                    params={
                        "start_date": start_date.isoformat() if start_date else None,
                        "end_date": end_date.isoformat() if end_date else None,
                        "min_feedback": min_feedback,
                        "max_feedback": max_feedback,
                        "has_comments": has_comments,
                        "category": category,
                    },
            ) as response:
                if response.status_code == 200:
                    api_response = QueryMetricsResponse(**response.json())
                else:
                    raise Exception(
                        f"Pythia API Error {response.status_code}: {self._process_error_response(response)}"
                    )
        return api_response

    def add_feedback_to_query(
            self,
            query_uuid: int | str,
            feedback: int,
            feedback_comment: str = None,
    ) -> QueryFeedbackResponse:
        """Add feedback to a specific query

        Args:
            query_uuid: UUID of the query to add feedback to. Can also be query_id (legacy)
            feedback: Feedback to add to query. From O (negative feedback) to 5 (positive feedback). Default to -1 (no feedback)
            feedback_comment: Optional text feedback (user comment)

        Returns:
            The response from the API as a Pydantic model. You can use response.model_dump() to get a Dict. Raise an exception with API status code and error message if the status code is not 200.

        Usage:
        ```python
        feedback_response = client.add_feedback_to_query(query_id=1337, feedback=0)
        feedback_response.model_dump()
        ```
        """
        with requests.Session() as session:
            headers = {
                "X-API-Key": self.api_key,
            }
            with session.get(
                    self.feedback_endpoint + f"/add/{query_uuid}",
                    headers=headers,
                    params={"feedback": feedback, "feedback_comment": feedback_comment},
            ) as response:
                if response.status_code == 200:
                    api_response = QueryFeedbackResponse(**response.json())
                else:
                    raise Exception(
                        f"Pythia API Error {response.status_code}: {self._process_error_response(response)}"
                    )
        return api_response

    def get_thread_queries(
            self,
            thread_id: str,
            group_id: Optional[str] = None
    ) -> ThreadResponse:
        """Get all queries for a specific thread ordered by creation date (oldest to newest).

        Args:
            thread_id: The ID of the thread to get queries for.
            group_id: Optional, only used if you use admin key, to get queries from a specific group.

        Returns:
            The response from the API as a Pydantic model containing thread info and queries.
            You can use response.model_dump() to get a Dict.
            Raises an exception with API status code and error message if the status code is not 200.

        Usage:
        ```python
        thread = client.get_thread_queries(thread_id="123e4567-e89b-12d3-a456-426614174000")
        thread_info = thread.thread_info
        queries = thread.queries
        ```
        """
        with requests.Session() as session:
            headers = {
                "X-API-Key": self.api_key,
            }
            request_url = self.feedback_endpoint + f"/thread/{thread_id}"
            if group_id:
                request_url += f"?group_id={group_id}"
            with session.get(request_url, headers=headers) as response:
                if response.status_code == 200:
                    api_response = ThreadResponse(**response.json())
                else:
                    raise Exception(
                        f"Pythia API Error {response.status_code}: {self._process_error_response(response)}"
                    )
        return api_response

    def list_threads(
            self,
            group_id: str,
            user_id: str | None = None,
            limit: int = 50,
            offset: int = 0,
    ) -> List[ThreadListResponse]:
        """List all threads for a group with pagination.

        Args:
            group_id: The group ID to list threads for.
            user_id: Optional user ID to filter threads by. If not provided, defaults to group_id.
            limit: Maximum number of threads to return (1-100, default 50).
            offset: Number of threads to skip for pagination (default 0).

        Returns:
            List of ThreadListResponse Pydantic models. You can use [thread.model_dump() for thread in response]
            to get a list of dicts. Raises an exception with API status code and error message if the status
            code is not 200.

        Usage:
        ```python
        # List all threads for a group
        threads = client.list_threads(group_id="my-group")

        # List threads with pagination
        threads = client.list_threads(
            group_id="my-group",
            user_id="specific-user",
            limit=20,
            offset=40  # Get threads 41-60
        )
        ```
        """
        with requests.Session() as session:
            headers = {
                "X-API-Key": self.api_key,
            }
            params = {
                "limit": limit,
                "offset": offset,
            }
            if user_id:
                params["user_id"] = user_id

            with session.get(
                    self.feedback_endpoint + f"/threads/{group_id}",
                    headers=headers,
                    params=params,
            ) as response:
                if response.status_code == 200:
                    api_response = [ThreadListResponse(**thread) for thread in response.json()]
                else:
                    raise Exception(
                        f"Pythia API Error {response.status_code}: {self._process_error_response(response)}"
                    )
        return api_response

    def draw_pipeline(
            self,
            pipeline_name: str,
    ) -> io.BytesIO:
        """Draw a PNG image of a specific Pythia pipeline.

        Args:
            pipeline_name: The name of the pipeline to draw.

        Returns:
            A BytesIO object containing the PNG image of the pipeline. Raise an exception with API status code and error message if the status code is not 200.

        Usage:
        ```python
        image = client.draw_pipeline(pipeline_name="query")
        ```
        """
        with requests.Session() as session:
            headers = {
                "X-API-Key": self.api_key,
            }
            with session.get(
                    self.draw_endpoint + f"/{pipeline_name}",
                    headers=headers,
            ) as response:
                if response.status_code == 200:
                    image = io.BytesIO(response.content)
                else:
                    raise Exception(
                        f"Pythia API Error {response.status_code}: {self._process_error_response(response)}"
                    )
        return image

    def extract_structured_data(
            self,
            file: str | Tuple[str, io.IOBase] | None = None,
            string_content: str | None = None,
            additional_instructions: str | None = None,
            json_schema: Dict[str, Any] | None = None,
            preset: Literal["esr-mail", "pk-list"] | None = None,
            extraction_mode: Literal["fast", "precise"] | None = "fast",
    ) -> DataExtractResponse:
        """This method extracts structured data according to a JSON schema. The input data can either be a text (string) or a file (such as PDF, Word, Email), but not both.

        The JSON schema to extract and additional instructions can be provided by the user, or you can use one of the presets developed by BTQ (`esr-mail`, `pk-list`). The extraction can run in two different modes: fast (single step LLM extraction) or precise (looping LLM).

        This extraction is asynchronous and the endpoint returns a 202 status with a job_uuid that can be used to check the status of the background task running. The extraction result will be a JSON validated to the provided JSON schema.

        Args:
            file: The path to the file OR tuple of filename and file object to extract the data from. Exclusive with `string_content` parameter. The file is processed with Tika.
            string_content: The string content to extract the data from. Exclusive with `file` parameter.
            additional_instructions: Additional instructions for the extraction. It will be inserted in the LLM prompt to help him extract information as expected.
            json_schema: The JSON schema to validate the extracted data, needed if no preset set. Exclusive with preset parameter
            preset: The preset to use for the extraction, it overwrites `json_schema` and add specific `additional_instructions` with our default values. Can be `esr-mail` or `pk-list`. Exclusive with `json_schema` parameter.
            extraction_mode: The extraction mode to use. Default to `fast` (single step LLM tool-use). Can also be `precise` (looping LLM requests with schema validator).

        Returns:
            The response from the API. Raise an exception with API status code and error message if the status code is not 202.

        Usage:
        ```python
        extract_structured_data_response = client.extract_structured_data("path/to/file.pdf", preset="pk-list")
        {"message": "Content Submitted. Data extract task created.", "job_uuid": "abc123-def456-ghj789"}

        extract_structured_data_response = client.extract_structured_data(("file.pdf", file), preset="pk-list")
        {"message": "Content Submitted. Data extract task created.", "job_uuid": "abc123-def456-ghj789"}


        string_content = "Hey, I have an issue with my MyPortal access."
        additional_instructions = "If myportal issue please name the ticket_category as MP_ACCESS"
        json_schema = json.loads('''{"$schema":"http://json-schema.org/draft-04/schema#","type":"object","properties":{"ticket_category":{"type":"string"}},"required":["ticket_category"]}''')

        response = client.extract_structured_data(string_content=string_content, additional_instructions=additional_instructions, json_schema=json_schema, extraction_mode="precise")
        ```
        """
        prepared_file = []
        if file:
            if isinstance(file, str):
                file_name = os.path.basename(file)
                with open(file, "rb") as f:
                    file_content = f.read()
            elif (
                    isinstance(file, tuple)
                    and len(file) == 2
                    and isinstance(file[1], io.IOBase)
            ):
                file_name, file_object = file
                file_content = file_object.read()
            else:
                raise ValueError(
                    "File must be a file path or a tuple of (filename, fileIObyte)"
                )

            prepared_file.append(("file", (file_name, file_content)))

        if prepared_file == [] and not string_content:
            raise ValueError("You must provide a file or string content to extract the data from.")
        if not json_schema and not preset:
            raise ValueError("You must provide a json_schema or a preset.")
        if json_schema and preset:
            raise ValueError("You can't provide both a json_schema and a preset.")
        if extraction_mode not in ["fast", "precise"]:
            raise ValueError("extraction_mode must be 'fast' or 'precise'.")

        with requests.Session() as session:
            headers = {
                "X-API-Key": self.api_key,
            }
            data = {}
            if string_content:
                data["string_content"] = string_content
            data["additional_instructions"] = additional_instructions if additional_instructions else None
            data["json_schema"] = json.dumps(json_schema) if json_schema else None
            data["preset"] = preset if preset else None
            data["extraction_mode"] = extraction_mode if extraction_mode else None

            with session.post(
                    self.data_extraction_endpoint,
                    files=prepared_file if prepared_file else None,
                    data=data,
                    headers=headers,
            ) as response:
                if response.status_code == 202:
                    api_response = response.json()
                else:
                    raise Exception(
                        f"Pythia API Error {response.status_code}: {self._process_error_response(response)}"
                    )
        return api_response

    def get_extract_structured_data_job(
            self,
            job_uuid: str,
    ) -> DataExtractTask:
        """Get the status and result of a data extract task based on its job UUID. When the `status` is `completed`, The resulting extracted JSON is under the `result_json` key of the return response.

        Args:
            job_uuid: The job UUID from the data extract task.

        Returns:
            The response from the API. Raise an exception with API status code and error message if the status code is not 200.

        Usage:
        ```python
        data_extract_task_result = client.get_extract_structured_data_job("abc123-def456-ghj789")
        data_extract_task_result.model_dump()["result_json"]
        ```
        """
        with requests.Session() as session:
            headers = {
                "X-API-Key": self.api_key,
            }
            with session.get(
                    self.data_extraction_endpoint + f"/{job_uuid}",
                    headers=headers,
            ) as response:
                if response.status_code == 200:
                    api_response = DataExtractTask(**response.json())
                else:
                    raise Exception(
                        f"Pythia API Error {response.status_code}: {self._process_error_response(response)}"
                    )
        return api_response
