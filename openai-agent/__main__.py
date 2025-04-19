"""This file serves as the main entry point for the application.

It initializes the A2A server, defines the agent's capabilities,
and starts the server to handle incoming requests.
"""

from agent import OpenAiAgent
from common.server import A2AServer
import click
from common.types import AgentCapabilities, AgentCard, AgentSkill, MissingAPIKeyError
from starlette.applications import Starlette
from common.server.task_manager import TaskManager
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
from starlette.requests import Request

from common.types import (
    A2ARequest,
    JSONRPCResponse,
    InvalidRequestError,
    JSONParseError,
    GetTaskRequest,
    CancelTaskRequest,
    SendTaskRequest,
    SetTaskPushNotificationRequest,
    GetTaskPushNotificationRequest,
    InternalError,
    AgentCard,
    TaskResubscriptionRequest,
    SendTaskStreamingRequest,
)
from pydantic import ValidationError
import json
from typing import AsyncIterable, Any
from common.server.task_manager import TaskManager

import logging


import os
from task_manager import AgentTaskManager
from dotenv import load_dotenv
import os
import contextlib
from typing import AsyncIterator, TypedDict
from agents.mcp import MCPServer, MCPServerStdio

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class State(TypedDict):
    mcp_server: MCPServer


@contextlib.asynccontextmanager
async def lifespan(app: Starlette) -> AsyncIterator[State]:
    """
    This lifespan function is called during the startup of starlette app and yields all values untill all
    Yield statement. Once the starlette app shuts down, it executes the staement after the Yield statement

    This function start's the MCP server with below command locally and closes it once the starlette server shuts down

    """
    root_dir = os.path.dirname(os.getcwd())
    async with MCPServerStdio(
        name="AWS ec2 agent",
        params={
            "command": "uv",
            "args": [
                "--directory",
                root_dir,
                "run",
                "aws.py",
            ],
        },
    ) as server:

        yield {"mcp_server": server}


class MyA2AServer:

    def __init__(
        self,
        host="0.0.0.0",
        port=10001,
        endpoint="/",
        agent_card: AgentCard = None,
        task_manager: TaskManager = None,
    ):
        self.host = host
        self.port = port
        self.endpoint = endpoint
        self.task_manager = None

        self.agent_card = agent_card
        self.app = Starlette(lifespan=lifespan)

        self.app.add_route(self.endpoint, self._process_request, methods=["POST"])
        self.app.add_route(
            "/.well-known/agent.json", self._get_agent_card, methods=["GET"]
        )

    def start(self):
        if self.agent_card is None:
            raise ValueError("agent_card is not defined")

        import uvicorn

        uvicorn.run(self.app, host=self.host, port=self.port)

    def _get_agent_card(self, request: Request) -> JSONResponse:
        ##instantiate the mcp server on first request and initialize the AgemntManager

        mcp_server = request.state.mcp_server
        self.task_manager = AgentTaskManager(agent=OpenAiAgent(mcp_server))

        return JSONResponse(self.agent_card.model_dump(exclude_none=True))

    async def _process_request(self, request: Request):
        try:
            body = await request.json()
            json_rpc_request = A2ARequest.validate_python(body)
            logger.info(f"Request recvd on <process_request>....{json_rpc_request}")

            if isinstance(json_rpc_request, GetTaskRequest):
                result = await self.task_manager.on_get_task(json_rpc_request)
            elif isinstance(json_rpc_request, SendTaskRequest):
                result = await self.task_manager.on_send_task(json_rpc_request)
            elif isinstance(json_rpc_request, SendTaskStreamingRequest):
                result = await self.task_manager.on_send_task_subscribe(
                    json_rpc_request
                )
            elif isinstance(json_rpc_request, CancelTaskRequest):
                result = await self.task_manager.on_cancel_task(json_rpc_request)
            elif isinstance(json_rpc_request, SetTaskPushNotificationRequest):
                result = await self.task_manager.on_set_task_push_notification(
                    json_rpc_request
                )
            elif isinstance(json_rpc_request, GetTaskPushNotificationRequest):
                result = await self.task_manager.on_get_task_push_notification(
                    json_rpc_request
                )
            elif isinstance(json_rpc_request, TaskResubscriptionRequest):
                result = await self.task_manager.on_resubscribe_to_task(
                    json_rpc_request
                )
            else:
                logger.warning(f"Unexpected request type: {type(json_rpc_request)}")
                raise ValueError(f"Unexpected request type: {type(request)}")

            return self._create_response(result)

        except Exception as e:
            return self._handle_exception(e)

    def _handle_exception(self, e: Exception) -> JSONResponse:
        if isinstance(e, json.decoder.JSONDecodeError):
            json_rpc_error = JSONParseError()
        elif isinstance(e, ValidationError):
            json_rpc_error = InvalidRequestError(data=json.loads(e.json()))
        else:
            logger.error(f"Unhandled exception: {e}")
            json_rpc_error = InternalError()

        response = JSONRPCResponse(id=None, error=json_rpc_error)
        return JSONResponse(response.model_dump(exclude_none=True), status_code=400)

    def _create_response(self, result: Any) -> JSONResponse | EventSourceResponse:
        if isinstance(result, AsyncIterable):

            async def event_generator(result) -> AsyncIterable[dict[str, str]]:
                async for item in result:
                    yield {"data": item.model_dump_json(exclude_none=True)}

            return EventSourceResponse(event_generator(result))
        elif isinstance(result, JSONRPCResponse):
            return JSONResponse(result.model_dump(exclude_none=True))
        else:
            logger.error(f"Unexpected result type: {type(result)}")
            raise ValueError(f"Unexpected result type: {type(result)}")


@click.command()
@click.option("--host", "host", default="localhost")
@click.option("--port", "port", default=10001)
def main(host, port):
    """Entry point for the A2A + OpenAI ec2 init sample."""

    try:
        if not os.getenv("OPENAI_API_KEY"):
            raise MissingAPIKeyError("OPENAI_API_KEY environment variable not set.")

        capabilities = AgentCapabilities(streaming=False)

        skill = AgentSkill(
            id="aws_ec2_initializer_or_terminator",
            name="AWS EC2 initializer or terminator",
            description=(
                "Create new instances of ec2 in aws or terminate ec2 instance if the user request's so"
            ),
            tags=["Initialize ec2 instance", "terminate ec2 instance"],
            examples=[
                "Create an instance of ec2",
                "terminate the instance with id xxxxxxx",
            ],
        )

        agent_card = AgentCard(
            name="AWS ec2 instance manager",
            description="Create or terminate ec2 instance in aws",
            url=f"http://{host}:{port}/",
            version="1.0.0",
            defaultInputModes=OpenAiAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=OpenAiAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )

        server = MyA2AServer(
            agent_card=agent_card, task_manager=AgentTaskManager(agent=OpenAiAgent())
        )

        logger.info(f"Starting server on {host}:{port}")
        server.start()
        print("started...")

    except MissingAPIKeyError as e:
        logger.error(f"Error: {e}")
        exit(1)
    except Exception as e:
        logger.error(f"An error occurred during server startup: {e}")
        exit(1)


if __name__ == "__main__":
    main()
