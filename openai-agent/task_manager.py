"""Agent Task Manager."""

import logging
from typing import AsyncIterable, Union
from agent import OpenAiAgent
from common.server.task_manager import InMemoryTaskManager
from common.server import utils
from common.types import (
    Artifact,
    JSONRPCResponse,
    SendTaskRequest,
    SendTaskResponse,
    SendTaskStreamingRequest,
    SendTaskStreamingResponse,
    Task,
    TaskSendParams,
    TaskState,
    TaskStatus,
    TextPart,
)

logger = logging.getLogger(__name__)


class AgentTaskManager(InMemoryTaskManager):
    """Agent Task Manager, handles task routing and response packing."""

    def __init__(self, agent: OpenAiAgent):
        super().__init__()
        self.agent = agent

    async def _stream_generator(
        self, request: SendTaskRequest
    ) -> AsyncIterable[SendTaskResponse]:
        raise NotImplementedError("Not implemented")

    async def _update_store(
        self, task_id: str, status: TaskStatus, artifacts: list[Artifact]
    ) -> Task:
        async with self.lock:
            try:
                task = self.tasks[task_id]
            except KeyError as exc:
                logger.error("Task %s not found for updating the task", task_id)
                raise ValueError(f"Task {task_id} not found") from exc

            task.status = status

            if status.message is not None:
                self.task_messages[task_id].append(status.message)

            if artifacts is not None:
                if task.artifacts is None:
                    task.artifacts = []
                task.artifacts.extend(artifacts)

            return task

    async def on_send_task(
        self, request: SendTaskRequest
    ) -> SendTaskResponse | AsyncIterable[SendTaskResponse]:
        ## only support text output at the moment
        if not utils.are_modalities_compatible(
            request.params.acceptedOutputModes,
            OpenAiAgent.SUPPORTED_CONTENT_TYPES,
        ):
            logger.warning(
                "Unsupported output mode. Received %s, Support %s",
                request.params.acceptedOutputModes,
                OpenAiAgent.SUPPORTED_CONTENT_TYPES,
            )
            return utils.new_incompatible_types_error(request.id)
        task_send_params: TaskSendParams = request.params

        await self.upsert_task(task_send_params)
        return await self._invoke(request)

    async def on_send_task_subscribe(
        self, request: SendTaskStreamingRequest
    ) -> Union[AsyncIterable[SendTaskStreamingResponse], JSONRPCResponse]:
        pass

    async def _invoke(self, request: SendTaskRequest) -> SendTaskResponse:
        task_send_params: TaskSendParams = request.params
        query = self._get_user_query(task_send_params)

        try:
            result = await self.agent.invoke(query)
        except Exception as e:
            logger.error("Error invoking agent: %s", e)
            raise ValueError(f"Error invoking agent: {e}") from e

        if result is not None:
            parts = [{"type": "text", "text": result}]
        else:
            parts = [{"type": "text", "text": "coudnt execute OpenAI agent"}]

        task = await self._update_store(
            task_send_params.id,
            TaskStatus(state=TaskState.COMPLETED),
            [Artifact(parts=parts)],
        )
        return SendTaskResponse(id=request.id, result=task)

    def _get_user_query(self, task_send_params: TaskSendParams) -> str:
        part = task_send_params.message.parts[0]
        if not isinstance(part, TextPart):
            raise ValueError("Only text parts are supported")

        return part.text
