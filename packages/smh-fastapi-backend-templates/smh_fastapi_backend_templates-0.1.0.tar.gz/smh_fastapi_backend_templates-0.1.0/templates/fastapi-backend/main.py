import uvicorn
import logging
import logging.config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.logging_config import LOGGING_CONFIG
from app.config.orjsonConfig import ORJSONResponse
from app.helpers.utilities.envVar import envConfig
from app.routers import health

logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger(__name__)

description = """
FastAPI Backend API helps you do awesome stuff. 🚀
"""
app = FastAPI(
    title="FastAPI Backend",
    description=description,
    summary="FastAPI Backend project",
    version="0.0.1",
    terms_of_service="http://dummy.com",
    contact={
        "name": "Fast Api Backend",
        "url": "http://x-force.example.com/contact/",
        "email": "email@gmail.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
        "identifier": "MIT",
    },
    root_path="/de",
    default_response_class=ORJSONResponse,
)
logger.info("Initializing Middlewares...")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
logger.info("Middlewares Initialized")

logger.info("Initializing Routers...")
app.include_router(health.router)
logger.info("Routers Initialized")

def main() -> None:
    uvicorn.run(
        "main:app",
        host=envConfig.app_ip,
        port=envConfig.app_port,
        reload=envConfig.app_reload,
        workers=envConfig.app_workers,
        reload_excludes=["logs/*"]
    )


if __name__ == "__main__":
    main()
