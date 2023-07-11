import asyncio
import sys

import click
from uvicorn.server import Server, logger

from uvicorn.lifespan import on


def ev_log_started_message(self, listeners) -> None:
    cfg = self.config
    if cfg.fd is not None:
        sock = listeners[0]
        logger.info(i18n.web_start.format(sock.getsockname()))
    elif cfg.uds is not None:
        logger.info(i18n.web_start.format(cfg.uds))
    else:
        addr_format = "%s://%s:%d"
        host = "0.0.0.0" if cfg.host is None else cfg.host
        if ":" in host:
            addr_format = "%s://[%s]:%d"
        port = cfg.port
        if port == 0:
            port = listeners[0].getsockname()[1]
        protocol_name = "https" if cfg.ssl else "http"
        message = i18n.web_start.format(addr_format)
        color_message = (i18n.web_start.format(click.style(addr_format, bold=True)))
        logger.info(message, protocol_name, host, port, extra={"color_message": color_message})


async def ev_shutdown(self, sockets=None) -> None:
    logger.debug("Shutting down")
    for server in self.servers:
        server.close()
    for sock in sockets or []:
        sock.close()
    for server in self.servers:
        await server.wait_closed()
    for connection in list(self.server_state.connections):
        connection.shutdown()
    await asyncio.sleep(0.1)
    try:
        await asyncio.wait_for(self._wait_tasks_to_complete(), timeout=self.config.timeout_graceful_shutdown)
    except asyncio.TimeoutError:
        logger.error("Cancel %s running task(s), timeout graceful shutdown exceeded",len(self.server_state.tasks))
        for t in self.server_state.tasks:
            if sys.version_info < (3, 9):
                t.cancel()
            else:
                t.cancel(msg="Task cancelled, timeout graceful shutdown exceeded")
    if not self.force_exit:
        await self.lifespan.shutdown()


async def on_startup(self) -> None:
    self.logger.debug("Waiting for application startup.")
    loop = asyncio.get_event_loop()
    main_lifespan_task = loop.create_task(self.main())  # noqa: F841
    startup_event = {"type": "lifespan.startup"}
    await self.receive_queue.put(startup_event)
    await self.startup_event.wait()
    if self.startup_failed or (self.error_occured and self.config.lifespan == "on"):
        self.logger.error("Application startup failed. Exiting.")
        self.should_exit = True
    else:
        self.logger.debug("Application startup complete.")


async def on_shutdown(self) -> None:
    if self.error_occured:
        return
    self.logger.debug("Waiting for application shutdown.")
    shutdown_event = {"type": "lifespan.shutdown"}
    await self.receive_queue.put(shutdown_event)
    await self.shutdown_event.wait()
    if self.shutdown_failed or (self.error_occured and self.config.lifespan == "on"):
        self.logger.error("Application shutdown failed. Exiting.")
        self.should_exit = True
    else:
        self.logger.debug("Application shutdown complete.")


def hack_fastapi():
    Server.shutdown = ev_shutdown
    Server._log_started_message = ev_log_started_message
    on.LifespanOn.startup = on_startup
    on.LifespanOn.shutdown = on_shutdown
