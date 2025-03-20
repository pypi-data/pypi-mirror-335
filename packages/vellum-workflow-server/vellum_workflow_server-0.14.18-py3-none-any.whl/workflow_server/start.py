import os
from typing import Optional

import gunicorn.app.base

from workflow_server.server import app


class StandaloneApplication(gunicorn.app.base.BaseApplication):
    def __init__(self, app_param: gunicorn.app.base.BaseApplication, options: Optional[dict] = None) -> None:
        self.options = options or {}
        self.application = app_param
        super().__init__()

    def load_config(self) -> None:
        config = {key: value for key, value in self.options.items() if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self) -> None:
        return self.application


def start() -> None:
    # gevent didn't play nice with pebble and processes so just gthread here
    options = {
        "bind": "0.0.0.0:8000",
        "workers": int(os.getenv("GUNICORN_WORKERS", 2)),
        "threads": int(os.getenv("GUNICORN_THREADS", 8)),
        "worker_class": "gthread",
        "timeout": int(os.getenv("GUNICORN_TIMEOUT", 1800)),
    }
    StandaloneApplication(app, options).run()
