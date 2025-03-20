from __future__ import annotations

from typing import List

from seekrai.abstract import api_requestor
from seekrai.seekrflow_response import SeekrFlowResponse
from seekrai.types import (
    EmbeddingRequest,
    EmbeddingResponse,
    SeekrFlowClient,
    SeekrFlowRequest,
)


class Embeddings:
    def __init__(self, client: SeekrFlowClient) -> None:
        self._client = client

    def create(
        self,
        *,
        input: str | List[str],
        model: str,
    ) -> EmbeddingResponse:
        """
        Method to generate completions based on a given prompt using a specified model.

        Args:
            input (str | List[str]): A string or list of strings to embed
            model (str): The name of the model to query.

        Returns:
            EmbeddingResponse: Object containing embeddings
        """
        raise NotImplementedError("Function not implemented yet")

        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        parameter_payload = EmbeddingRequest(
            input=input,
            model=model,
        ).model_dump()

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="POST",
                url="inference/embeddings",
                params=parameter_payload,
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return EmbeddingResponse(**response.data)


class AsyncEmbeddings:
    def __init__(self, client: SeekrFlowClient) -> None:
        self._client = client

    async def create(
        self,
        *,
        input: str | List[str],
        model: str,
    ) -> EmbeddingResponse:
        """
        Async method to generate completions based on a given prompt using a specified model.

        Args:
            input (str | List[str]): A string or list of strings to embed
            model (str): The name of the model to query.

        Returns:
            EmbeddingResponse: Object containing embeddings
        """
        raise NotImplementedError("Function not implemented yet")

        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        parameter_payload = EmbeddingRequest(
            input=input,
            model=model,
        ).model_dump()

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="POST",
                url="inference/embeddings",
                params=parameter_payload,
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return EmbeddingResponse(**response.data)
