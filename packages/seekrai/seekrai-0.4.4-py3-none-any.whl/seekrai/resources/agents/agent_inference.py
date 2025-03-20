from typing import Any, Dict, Iterator, Union

from seekrai.abstract import api_requestor
from seekrai.seekrflow_response import SeekrFlowResponse
from seekrai.types import SeekrFlowRequest


class AgentInference:
    def __init__(self, client: Any) -> None:
        self._client = client

    def run(
        self,
        agent_id: Union[int, str],
        query: str,
        *,
        stream: bool = False,
        thread_id: Union[str, None] = None,
        headers: Union[Dict[str, str], None] = None,
        **model_settings: Any,
    ) -> Union[Dict[str, Any], Iterator[Dict[str, Any]]]:
        """
        Run an inference call on a deployed agent.

        Args:
            agent_id (Union[int, str]): The unique identifier of the deployed agent.
            query (str): The user query or prompt.
            stream (bool, optional): Whether to stream the response. Defaults to False.
            thread_id (str, optional): An optional thread identifier.
            headers (dict, optional): Optional HTTP headers to include in the request.
                                    If provided, these will be merged with default headers.
            **model_settings: Additional parameters (such as temperature, max_tokens, etc).

        Returns:
            A dictionary with the response (if non-streaming) or an iterator over response chunks.
        """
        payload: Dict[str, Any] = {"prompt": query}
        if thread_id is not None:
            payload["thread_id"] = thread_id
        payload.update(model_settings)

        default_headers = {}
        if self._client.api_key:
            default_headers["x-api-key"] = self._client.api_key
        if self._client.supplied_headers:
            default_headers.update(self._client.supplied_headers)

        request_headers = default_headers.copy()
        if headers:
            request_headers.update(headers)

        requestor = api_requestor.APIRequestor(client=self._client)
        endpoint = f"agents/{agent_id}/run"

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="POST",
                url=endpoint,
                params=payload,
                headers=request_headers,
            ),
            stream=stream,
        )

        if stream:
            assert not isinstance(response, SeekrFlowResponse)
            return (chunk.data for chunk in response)
        else:
            assert isinstance(response, SeekrFlowResponse)
            return response.data
