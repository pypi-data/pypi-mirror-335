from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from threading import Thread
import uvicorn


class FastAPIManager:
    __slots__ = [
        'app',
        'server_thread',
        'notify_cli',
        'server'
    ]

    def __init__(
            self,
            callback = None
    ):
        self.app = FastAPI()
        self.setup_routes()
        self.server_thread = None
        self.notify_cli = None
        self.server = None

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        if callback is not None:
            self.set_callback(callback)

    def set_callback(self, callback) -> None:
        self.notify_cli = callback

    def setup_routes(self) -> None:
        @self.app.post("/post")
        async def receive_data(request: Request):
            data = await request.json()
            if self.notify_cli:
                returned_message = self.notify_cli(data)
            return f'{returned_message}'

        @self.app.post("/shutdown")
        async def shutdown():
            if self.server:
                self.server.should_exit = True
            return {"message": "Server shutting down..."}

    def app_init(self) -> None:
        config = uvicorn.Config(self.app, host="127.0.0.1", port=5000, log_level="error")
        self.server = uvicorn.Server(config)
        self.server.run()

    def run(self) -> None:
        self.server_thread = Thread(target=self.app_init, name='fastapi_manager_thread')
        self.server_thread.start()

    def shutdown(self) -> None:
        if self.server:
            self.server.should_exit = True
