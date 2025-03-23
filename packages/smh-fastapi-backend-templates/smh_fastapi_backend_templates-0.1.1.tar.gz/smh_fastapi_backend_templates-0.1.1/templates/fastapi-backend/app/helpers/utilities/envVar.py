import os

from dotenv import load_dotenv

env = os.getenv("ENV", "development")
env_file = f".env.{env}"

load_dotenv(env_file)

DB_NAME = os.getenv("DB_NAME", None)
DB_COLLECTION_TEST = os.getenv("DB_COLLECTION_TEST", None)


class EnvConfig:
    @property
    def app_ip(self) -> str:
        return os.getenv("APP_IP", "0.0.0.0")

    @property
    def app_port(self) -> int:
        return int(os.getenv("APP_PORT", "3030"))

    @property
    def app_reload(self) -> bool:
        return eval(os.getenv("APP_RELOAD", "True"))

    @property
    def app_workers(self) -> int:
        return int(os.getenv("APP_WORKERS", "1"))


envConfig = EnvConfig()
