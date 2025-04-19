from starlette.applications import Starlette
from starlette.responses import JSONResponse
from agent import OpenAiAgent
from agents.mcp import MCPServer, MCPServerStdio
from agents import gen_trace_id, trace
from typing import AsyncIterator, TypedDict
import os
import contextlib


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

        print("shutting down...")


class A2AServer:
    def __init__(self, host="0.0.0.0", port=8000, endpoint="/"):
        self.host = host
        self.port = port
        self.endpoint = endpoint
        self.app = Starlette(lifespan=lifespan)
        self.app.add_route(self.endpoint, self._get_json, methods=["GET"])

    def start(self):
        import uvicorn

        uvicorn.run(self.app)

    async def _get_json(self, request):
        mcp_server = request.state.mcp_server
        user_query = request.query_params.get("prompt")
        print(f"user prompt is : {user_query}")
        openai_agent = OpenAiAgent(user_query, mcp_server)

        return JSONResponse({"hello": await openai_agent.runAgent()})


server = A2AServer()
server.start()
