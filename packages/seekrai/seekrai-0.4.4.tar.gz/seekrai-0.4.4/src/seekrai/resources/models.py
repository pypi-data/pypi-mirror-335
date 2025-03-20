from __future__ import annotations

import os
from pathlib import Path
from typing import Any, List

from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper

from seekrai.abstract import api_requestor
from seekrai.constants import DISABLE_TQDM
from seekrai.seekrflow_response import SeekrFlowResponse
from seekrai.types import ModelList, ModelResponse, SeekrFlowClient, SeekrFlowRequest
from seekrai.types.models import ModelType


class Models:
    def __init__(self, client: SeekrFlowClient) -> None:
        self._client = client

    def upload(
        self,
        file: Path | str,
        *,
        model_type: ModelType | str = ModelType.OBJECT_DETECTION,
    ) -> ModelResponse:
        if isinstance(file, str):
            file = Path(file)

        requestor = api_requestor.APIRequestor(
            client=self._client,
        )
        file_size = os.stat(file.as_posix()).st_size

        with tqdm(
            total=file_size,
            unit="B",
            unit_scale=True,
            desc=f"Uploading model file {file.name}",
            disable=bool(DISABLE_TQDM),
        ) as t:
            with file.open("rb") as f:
                reader_wrapper = CallbackIOWrapper(t.update, f, "read")
                response, _, _ = requestor.request(
                    options=SeekrFlowRequest(
                        method="PUT",
                        url="flow/pt-models",
                        files={"files": reader_wrapper, "filename": file.name},
                        params={"purpose": model_type},
                    ),
                )
        return ModelResponse(**response.data)

    def list(
        self,
    ) -> ModelList:
        """
        Method to return list of models on the API

        Returns:
            List[ModelResponse]: List of model objects
        """

        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url="flow/pt-models",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return ModelList(**response.data)

    def promote(self, id: str) -> ModelResponse:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url=f"flow/pt-models/{id}/promote-model",
                params={"model_id": id},
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return ModelResponse(**response.data)

    def demote(self, id: str) -> ModelResponse:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url=f"flow/pt-models/{id}/demote-model",
                params={"model_id": id},
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return ModelResponse(**response.data)

    def predict(self, id: str, file: Path | str) -> Any:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        if isinstance(file, str):
            file = Path(file)

        file_size = os.stat(file.as_posix()).st_size

        with tqdm(
            total=file_size,
            unit="B",
            unit_scale=True,
            desc=f"Uploading file {file.name}",
            disable=bool(DISABLE_TQDM),
        ):
            with file.open("rb") as f:
                response, _, _ = requestor.request(
                    options=SeekrFlowRequest(
                        method="POST",
                        url="flow/pt-models/predict",
                        files={"files": f, "filename": file.name},
                        params={"model_id": id},
                    ),
                    stream=False,
                )

        assert isinstance(response, SeekrFlowResponse)

        return response.data


class AsyncModels:
    def __init__(self, client: SeekrFlowClient) -> None:
        self._client = client

    async def list(
        self,
    ) -> List[ModelResponse]:
        """
        Async method to return list of models on API

        Returns:
            List[ModelResponse]: List of model objects
        """

        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="GET",
                url="flow/models",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        assert isinstance(response.data, list)

        return [ModelResponse(**model) for model in response.data]
