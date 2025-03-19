# Copyright 2025 IBM Corp.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Any, TYPE_CHECKING, Optional

import anyio
import anyio.abc
import anyio.to_thread
import psutil
from anyio import create_task_group
from httpx import ConnectError

from acp.client.sse import sse_client
from acp.client.stdio import get_default_environment
from pydantic import BaseModel, Field

from beeai_server.custom_types import McpClient
from beeai_server.utils.process import terminate_process

if TYPE_CHECKING:
    # Circular import
    from beeai_server.services.mcp_proxy.provider import ProviderLogsContainer

logger = logging.getLogger(__name__)


class ManagedServerParameters(BaseModel):
    command: str
    """The executable to run to start the server."""

    args: list[str] = Field(default_factory=list)  # noqa: F821
    """Command line arguments to pass to the executable."""

    env: dict[str, str] | None = None
    """
    The environment to use when spawning the process.

    If not specified, the result of get_default_environment() will be used.
    """

    cwd: Path | None = None

    headers: dict[str, Any] | None = (None,)
    timeout: float = 5
    sse_read_timeout: float = 60 * 5
    graceful_terminate_timeout: float = 1
    endpoint: str = "/sse"


@asynccontextmanager
async def managed_sse_client(
    server: ManagedServerParameters,
    logs_container: Optional["ProviderLogsContainer"] = None,
) -> McpClient:
    """
    Client transport for stdio: this will connect to a server by spawning a
    process and communicating with it over stdin/stdout.
    """
    port = await find_free_port()

    process = await anyio.open_process(
        [server.command, *server.args],
        cwd=server.cwd,
        env={"PORT": str(port), **(server.env if server.env is not None else get_default_environment())},
        start_new_session=True,
    )

    async def log_process_stdout():
        async for line in process.stdout:
            text = line.decode().strip()
            logger.info(f"stdout: {text}")
            if logs_container:
                logs_container.add_stdout(text)

    async def log_process_stderr():
        async for line in process.stderr:
            text = line.decode().strip()
            logger.info(f"stderr: {text}")
            if logs_container:
                logs_container.add_stderr(text)

    async with process:
        try:
            async with create_task_group() as tg:
                tg.start_soon(log_process_stdout)
                tg.start_soon(log_process_stderr)
                try:
                    for attempt in range(8):
                        try:
                            async with sse_client(
                                url=f"http://localhost:{port}/{server.endpoint.lstrip('/')}", timeout=60
                            ) as streams:
                                yield streams
                                break
                        except* ConnectError as ex:
                            if process.returncode or not (
                                await anyio.to_thread.run_sync(psutil.pid_exists, process.pid)
                            ):
                                raise ConnectionError(f"Provider process exited with code {process.returncode}")
                            timeout = 2**attempt
                            logger.warning(f"Failed to connect to provider. Reconnecting in {timeout} seconds: {ex!r}")
                            await asyncio.sleep(timeout)
                    else:
                        raise ConnectionError("Failed to connect to provider.")
                finally:
                    tg.cancel_scope.cancel()
        finally:
            await terminate_process(process, server.graceful_terminate_timeout)


async def find_free_port():
    """Get a random free port assigned by the OS."""
    listener = await anyio.create_tcp_listener()
    port = listener.extra(anyio.abc.SocketAttribute.local_address)[1]
    await listener.aclose()
    return port
