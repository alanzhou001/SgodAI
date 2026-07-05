from __future__ import annotations

import os

import uvicorn

from app.api.server import app


def main() -> None:
    host = os.getenv("SGODAI_HOST", "127.0.0.1")
    port = int(os.getenv("SGODAI_PORT", "18765"))
    log_level = os.getenv("SGODAI_LOG_LEVEL", "info")
    uvicorn.run(app, host=host, port=port, log_level=log_level, access_log=False)


if __name__ == "__main__":
    main()
