import os
from typing import Optional

from aiohttp import web

from slack_sdk.socket_mode.aiohttp import SocketModeClient
from slack_bolt.app.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

from db import Mongo
from flux import flux
from healthcheck import healthcheck
from app_home import update_home_tab, create_event_blocks
from app_messaging import message_hello, message_button_click


class App:

    slack_app = AsyncApp(
        token=os.environ.get("SLACK_BOT_TOKEN"),
        signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
    )
    socket_mode_client: Optional[SocketModeClient] = None

    def __init__(self, db: Mongo, port: int = 3000) -> None:
        self.port = port
        self.web_app = self.slack_app.web_app()
        self.db = db
        self.web_app["db"] = db

        self.web_app.add_routes(
            [web.get("/health", healthcheck), web.post("/flux", flux)]
        )

    def events(self) -> None:
        self.slack_app.event(
            "app_home_opened",
            middleware=[self.db.fetch_deployment_info, create_event_blocks],
        )(update_home_tab)

    def actions(self) -> None:
        self.slack_app.action("button_click")(message_button_click)

    def messages(self) -> None:
        self.slack_app.message("hello")(message_hello)

    def run(self) -> None:
        self.events()
        self.actions()
        self.messages()

        self.web_app.on_startup.append(self.start_socket_mode)
        self.web_app.on_shutdown.append(self.shutdown_socket_mode)
        web.run_app(app=self.web_app, port=self.port)

    async def start_socket_mode(self, _web_app: web.Application):
        handler = AsyncSocketModeHandler(self.slack_app, os.environ["SLACK_APP_TOKEN"])
        await handler.connect_async()
        self.web_app["socket_mode_client"] = self.socket_mode_client = handler.client

    async def shutdown_socket_mode(self, _web_app: web.Application):
        await self.socket_mode_client.close()
        del self.web_app["socket_mode_client"]
