# mypy: disable-error-code="override"
from typing import Any, List, Optional

import aiohttp
from aiohttp import ClientResponseError

from klu.common.client import KluClientBase
from klu.common.errors import (
    InvalidUpdateParamsError,
    UnknownKluAPIError,
    UnknownKluError,
)
from klu.common.models import TaskStatusEnum
from klu.context.constants import (
    CONTEXT_DOCUMENTS_ENDPOINT,
    CONTEXT_ENDPOINT,
    CONTEXT_PROMPT_ENDPOINT,
    CONTEXT_SEARCH_ENDPOINT,
    CONTEXT_STATUS_ENDPOINT,
    GENERATE_EMBEDDINGS,
    UPDATE_CONTEXT_DOCUMENT_ENDPOINT,
    UPLOAD_PRE_SIGNED_URL_ENDPOINT,
)
from klu.context.errors import ContextNotFoundError
from klu.context.models import (
    AddContextDocumentResponse,
    Context,
    ContextDocument,
    ContextPromptResponse,
    DeleteContextDocumentResponse,
    FileData,
    PreSignUrlPostData,
)
from klu.utils.dict_helpers import dict_no_empty
from klu.utils.file_upload import upload_to_pre_signed_url
from klu.workspace.errors import WorkspaceOrUserNotFoundError


class ContextClient(KluClientBase):
    def __init__(self, api_key: str):
        super().__init__(api_key, CONTEXT_ENDPOINT, Context)

    async def create(
        self,
        name: str,
        description: str,
        type: Optional[str] = None,
        loader: Optional[str] = None,
        filter: Optional[str] = None,
        meta_data: Optional[dict] = None,
        file_data: Optional[List[FileData]] = None,
        files: Optional[List[str]] = None,
    ) -> Context:
        """
        Creates a new context based on the provided data.

        Args:
            name (str): The name of the context.
            description (str): The description of the context.
            type (Optional[str]): The type of Context.
                Can be one of: [Simple, File, API, Loader]
            filter (Optional[str]): The filter to be used on Context
            loader (Optional[str]): The loader to be used on Context.
                Can be one of: [gmail, notion, intercom, github, redis, crawler, database, elastic, zendesk, file, custom]
                If missing, the API will use 'custom' as the default loader
            meta_data (Optional[dict]): The meta_data to be assigned to a created context
            file_data (Optional[FileData]): Metadata of the file to be uploaded.
                Can be omitted if only the context skeleton has to be created.
            files (Optional[List[str]]): List of s3 urls to be processed.

        Returns:
            The created Context object
        """
        file_urls = (
            [await self.upload_file(data) for data in file_data] if file_data else None
        )
        context = {
            "name": name,
            "type": type,
            "loader": loader,
            "filter": filter,
            "meta_data": meta_data,
            "description": description,
        }
        if file_urls:
            context["files"] = file_urls  # type: ignore
        elif files:
            context["files"] = files  # type: ignore

        return await super().create(**context)

    # type: ignore
    async def get(self, guid: str) -> Context:
        """
        Retrieves context information based on the id.

        Args:
            guid (str): id of a context object to fetch.

        Returns:
            Context object found by provided id
        """
        return await super().get(guid)

    # type: ignore
    async def update(
        self,
        guid: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        meta_data: Optional[dict] = None,
    ) -> Context:
        """
        Update context data. At least one of the params has to be provided

        Args:
            guid (str): ID of a context to update.
            name: Optional[str]. New context name
            meta_data: Optional[dict]. New context meta_data. Can be used to update the files list on a context
            description: Optional[str]. New context description

        Returns:
            Updated app instance
        """

        if not name and not description and not meta_data:
            raise InvalidUpdateParamsError()

        return await super().update(
            **{
                "guid": guid,
                **dict_no_empty(
                    {"name": name, "meta_data": meta_data, "description": description}
                ),
            }
        )

    # type: ignore
    async def add_files(self, context: str, files: List[str]) -> Context:
        """
        Add files to a context

        Args:
            context (str): guid of the context to update.
            files: List[str]. List of files to add to a context

        Returns:
            Updated context
        """

        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            try:
                response = await client.post(
                    CONTEXT_ENDPOINT + f"{context}/add_files",
                    {"files": files},
                )
            except ClientResponseError as e:
                # TODO differentiate between missing context and missing user 404. Change the engine accordingly
                if e.status == 404:
                    raise WorkspaceOrUserNotFoundError()

                raise UnknownKluAPIError(e.status, e.message)
            except Exception as e:
                raise UnknownKluError(e)

            return Context._from_engine_format(response)

    # type: ignore
    async def delete(self, guid: str) -> Context:
        """
        Deletes a context based on the provided guid.

        Args:
            guid (str): The guid of a context to delete.

        Returns:
            Deleted Context object
        """
        return await super().delete(guid=guid)

    async def list(self) -> List[Context]:
        """
        Retrieves all contexts for a workpace.

        Returns:
            List[Context]: An array of all contexts
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            response = await client.get(CONTEXT_ENDPOINT)

            return [Context._from_engine_format(context) for context in response]

    async def get_status(self, context: str) -> TaskStatusEnum:
        """
        Retrieves the status of an context creation task based on the provided context guid.

        Args:
            context (str): The guid of the context.

        Returns:
            string representing te context status
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            try:
                response = await client.post(CONTEXT_STATUS_ENDPOINT.format(id=context))
            except ClientResponseError as e:
                if e.status == 404:
                    raise ContextNotFoundError(context)

                raise UnknownKluAPIError(e.status, e.message)

            return TaskStatusEnum.get(response.get("status"))  # type: ignore

    async def embed(
        self,
        guid: str,
    ) -> dict:
        """
        Generates embeddings for the data in the context

        Args:
            guid (str): Guid of context to process
        Returns:
            dict with a message about successful index creation
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            try:
                response = await client.post(
                    GENERATE_EMBEDDINGS,
                    {
                        "guid": guid,
                    },
                )
            except ClientResponseError as e:
                # TODO differentiate between missing context and missing user 404. Change the engine accordingly
                if e.status == 404:
                    raise WorkspaceOrUserNotFoundError()

                raise UnknownKluAPIError(e.status, e.message)
            except Exception as e:
                raise UnknownKluError(e)

            return {"message": response.get("msg")}

    async def upload_file(self, file_data: FileData) -> str:
        """
        Upload system file to Klu storage for later usage in context creation. Maximum supported file size is 50 MB.

        Args:
            file_data (FileData): Metadata of the file to be uploaded. For more details, see the FileData class docs.

        Returns:
            URL to the uploaded file. This URL can be used during the context update flow by passing it into the context meta_data.
        """
        async with aiohttp.ClientSession() as session:
            pre_signed_url_data = await self.get_pre_signed_url(file_data.file_name)
            await upload_to_pre_signed_url(
                session, pre_signed_url_data, file_data.file_path
            )

            return pre_signed_url_data.object_url

    async def get_pre_signed_url(self, file_name: str) -> PreSignUrlPostData:
        """
        Get pre-signed url to upload files to use for contexts creation. Maximum supported file size is 50 MB.
        This method should only be used if you don't want to use `upload_model_file` function to upload the file without
        the need to get into pre_signed_url upload flow.

        Args:
            file_name (str): The name of the file to be uploaded. Has to be unique among the files you uploaded before.
                Otherwise, the new file will override the previously uploaded one by the same file_name

        Returns:
            pre-signed url data including url, which is the pre-signed url that can be used to upload the file.
            Also includes 'fields' property that contains dict with data that
            has to be passed alongside the file during the upload
            And object_url property that contains the url that can be used to access the file location after the upload.
            This same object_url can be used during the context creation.
            For a usage example check out the `upload_index_file` function
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            try:
                response = await client.post(
                    UPLOAD_PRE_SIGNED_URL_ENDPOINT,
                    {
                        "file_name": file_name,
                    },
                )
            except ClientResponseError as e:
                # TODO differentiate between missing context and missing user 404. Change the engine accordingly
                if e.status == 404:
                    raise WorkspaceOrUserNotFoundError()

                raise UnknownKluAPIError(e.status, e.message)

            return PreSignUrlPostData(**response)

    async def add_doc(
        self,
        guid: str,
        content: str,
        filter: Optional[str] = "",
        meta_data: Optional[Any] = None,
    ) -> AddContextDocumentResponse:
        """
        Add a document to a context.

        Args:
            guid (str): The guid of the context to which the document is being added.
            content (str): The text of the document.
            filter (Optional[str]): The filter for the document.
            meta_data (Optional[Any]): The metadata for the document. Can be a dictionary or an array.

        Returns:
            An AddContextDocumentResponse object with the context guid and status.
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            try:
                response = await client.post(
                    CONTEXT_DOCUMENTS_ENDPOINT.format(id=guid),
                    {
                        "content": content,
                        "filter": filter,
                        "meta_data": meta_data,
                    },
                )
            except ClientResponseError as e:
                # TODO differentiate between missing context and missing user 404. Change the engine accordingly
                if e.status == 404:
                    raise ContextNotFoundError(guid)

                raise UnknownKluAPIError(e.status, e.message)

            return AddContextDocumentResponse._create_instance(**response)

    async def list_docs(
        self,
        guid: str,
    ) -> List[ContextDocument]:
        """
        List documents on a context

        Args:
            guid(str): Guid of the context to fetch documents for

        Returns: response with the list of the documents on a context
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            try:
                response = await client.get(
                    CONTEXT_DOCUMENTS_ENDPOINT.format(id=guid),
                )
            except ClientResponseError as e:
                # TODO differentiate between missing context and missing user 404. Change the engine accordingly
                if e.status == 404:
                    raise ContextNotFoundError(guid)

                raise UnknownKluAPIError(e.status, e.message)

            return [
                ContextDocument._from_engine_format(context_doc)
                for context_doc in response.get("data")
            ]

    async def delete_all_docs(
        self,
        guid: str,
    ) -> DeleteContextDocumentResponse:
        """
        Delete all documents from a context. Executes in a task, so results will not be available immediately

        Args:
            guid (str): Guid of the context to delete documents from

        Returns: response with a status message
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            try:
                response = await client.delete(
                    CONTEXT_DOCUMENTS_ENDPOINT.format(id=guid),
                )
            except ClientResponseError as e:
                # TODO differentiate between missing context and missing user 404. Change the engine accordingly
                if e.status == 404:
                    raise ContextNotFoundError(guid)

                raise UnknownKluAPIError(e.status, e.message)

            return DeleteContextDocumentResponse(**response)

    async def update_doc(
        self,
        doc_guid: str,
        context_guid: str,
        content: Optional[str],
        filter: Optional[str] = None,
        meta_data: Optional[Any] = None,
    ) -> ContextDocument:
        """
        Update a single document on a context

        Args:
            doc_guid (str): Guid of the doc to update
            context_guid (str): Guid of the context the doc belongs to
            content (str): New content of a doc
            embedding (list[float]): New embedding list of a doc
            filter (Optional[str]): New filter of a doc
            meta_data (Optional[Any]): new meta_data of a doc

        Returns: updated context object
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            try:
                response = await client.put(
                    UPDATE_CONTEXT_DOCUMENT_ENDPOINT.format(
                        id=context_guid, doc_id=doc_guid
                    ),
                    {
                        **dict_no_empty(
                            {
                                "content": content,
                                "filter": filter,
                                "meta_data": meta_data,
                            }
                        ),
                    },
                )
            except ClientResponseError as e:
                # TODO differentiate between missing context and missing user 404. Change the engine accordingly
                if e.status == 404:
                    raise ContextNotFoundError(context_guid)

                raise UnknownKluAPIError(e.status, e.message)

            return ContextDocument._from_engine_format(response)

    async def search(
        self,
        guid: str,
        prompt: str,
        similarity_score: Optional[float] = 0,
        number_of_results: Optional[int] = 10,
        filter: Optional[str] = None,
        metadata: Optional[Any] = None,
    ) -> List[ContextDocument]:
        """
        Search for relevant documents in a context.

        Args:
            guid (str): The guid of the context to search.
            prompt (str): The prompt to search.
            similarity_score (Optional[float]): The minimum similarity score to return.
            number_of_results (Optional[int]): The number of results to return.
            filter (Optional[str]): Simple string filter to apply to the search.
            metadata (Optional[Any]): The metadata filter to apply to the search.

        Returns:
            List[ContextDocument]: A list of relevant documents.
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            try:
                response = await client.post(
                    CONTEXT_SEARCH_ENDPOINT.format(id=guid),
                    {
                        "prompt": prompt,
                        "similarity_score": similarity_score,
                        "number_of_results": number_of_results,
                        "filter": filter,
                        "metadata_filter": metadata,
                    },
                )
            except ClientResponseError as e:
                # TODO differentiate between missing context and missing user 404. Change the engine accordingly
                if e.status == 404:
                    raise ContextNotFoundError(guid)

                raise UnknownKluAPIError(e.status, e.message)

            return [
                ContextDocument._from_engine_format(context_doc)
                for context_doc in response
            ]

    async def prompt(
        self,
        guid: str,
        prompt: str,
        response_mode: Optional[str] = "search",
        response_length: Optional[int] = 1024,
        number_of_results: Optional[int] = 5,
    ) -> ContextPromptResponse:
        """
        Search Context

        Args:
            guid (str): Guid of the context to search
            prompt (str): Prompt to search
            similarity_score (Optional[float]): Minimum similarity score to return
            number_of_results (Optional[int]): Number of results to return

        Returns: List of relevant documents
        """
        async with aiohttp.ClientSession() as session:
            client = self._get_api_client(session)
            try:
                response = await client.post(
                    CONTEXT_PROMPT_ENDPOINT,
                    {
                        "context": guid,
                        "prompt": prompt,
                        "responseMode": response_mode,
                        "responseLength": response_length,
                        "similarityTopK": number_of_results,
                    },
                )
            except ClientResponseError as e:
                # TODO differentiate between missing context and missing user 404. Change the engine accordingly
                if e.status == 404:
                    raise ContextNotFoundError(guid)

                raise UnknownKluAPIError(e.status, e.message)

            return ContextPromptResponse(**response)
